import logging
from random import choice

import redis
from environs import Env
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext, ConversationHandler

from db_functions import get_connection, get_question_by_user_id
from db_functions import record_question_to_db
from questions_function import get_questions_and_answers


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

QUESTION, ATTEMPT = range(2)


def get_keyboard():
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счёт']
    ]

    reply_markup = ReplyKeyboardMarkup(
        custom_keyboard,
        resize_keyboard=True
    )

    return reply_markup


def start(update, context):
    update.message.reply_text(
        text='Привет! Я бот для викторин!',
        reply_markup=get_keyboard()
    )

    return QUESTION


def new_question(update, context):
    questions = context.bot_data['questions']
    questions_and_answers = context.bot_data['questions_and_answers']
    db_connection = context.bot_data['redis_connection']

    message = choice(questions)
    record_question_to_db(update.message.chat.id, message, db_connection)
    update.message.reply_text(message)

    return ATTEMPT


def check_answer(update, context):
    questions_and_answers = context.bot_data['questions_and_answers']
    db_connection = context.bot_data['redis_connection']

    question = get_question_by_user_id(update.message.chat.id, db_connection)
    answer = questions_and_answers.get(question)

    if answer.lower() == update.message.text.lower():
        message = 'Правильно! Поздравляю! '
        message += 'Для следующего вопроса нажми «Новый вопрос»'
        state = QUESTION
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
        state = ATTEMPT

    update.message.reply_text(
        text=message,
        reply_markup=get_keyboard()
    )

    return state


def to_surrender(update, context):
    questions = context.bot_data['questions']
    questions_and_answers = context.bot_data['questions_and_answers']
    db_connection = context.bot_data['redis_connection']

    question = get_question_by_user_id(update.message.chat.id, db_connection)
    answer = questions_and_answers.get(question)
    update.message.reply_text(answer)

    message = choice(questions)
    record_question_to_db(update.message.chat.id, message, db_connection)

    if message:
        update.message.reply_text(
            text=message,
            reply_markup=get_keyboard()
        )

        return ATTEMPT

    return QUESTION


def cancel(update, context):
    update.message.reply_text(
        'До свидания!',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')

    questions, questions_and_answers = get_questions_and_answers()

    updater = Updater(tg_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            QUESTION: [
                MessageHandler(Filters.regex('Новый вопрос'), new_question)
            ],

            ATTEMPT: [
                MessageHandler(Filters.regex('Сдаться'), to_surrender),
                MessageHandler(Filters.text, check_answer)
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)\

    redis_connection = get_connection()

    dp.bot_data['questions'] = questions
    dp.bot_data['questions_and_answers'] = questions_and_answers
    dp.bot_data['redis_connection'] = redis_connection

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

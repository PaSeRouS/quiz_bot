import logging
from random import choice

from environs import Env
from redis import Redis
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext, ConversationHandler

from questions import get_questions_and_answers


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


def send_new_question(update, context):
    questions = context.bot_data['questions']
    db_connection = context.bot_data['redis_connection']

    message = choice(questions)
    db_connection.set(update.message.chat.id, message)
    update.message.reply_text(message)

    return ATTEMPT


def check_answer(update, context):
    answers = context.bot_data['answers']
    db_connection = context.bot_data['redis_connection']

    question = db_connection.get(update.message.chat.id)
    answer = answers.get(question)

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


def surrender(update, context):
    questions = context.bot_data['questions']
    answers = context.bot_data['answers']
    db_connection = context.bot_data['redis_connection']

    question = db_connection.get(update.message.chat.id)
    answer = answers.get(question)
    update.message.reply_text(answer)

    message = choice(questions)
    db_connection.set(update.message.chat.id, message)

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
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')

    questions, answers = get_questions_and_answers()

    updater = Updater(tg_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            QUESTION: [
                MessageHandler(Filters.regex('Новый вопрос'), send_new_question)
            ],

            ATTEMPT: [
                MessageHandler(Filters.regex('Сдаться'), surrender),
                MessageHandler(Filters.text, check_answer)
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')

    redis_connection = Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        password=redis_password,
        decode_responses=True
    )

    dp.bot_data['questions'] = questions
    dp.bot_data['answers'] = answers
    dp.bot_data['redis_connection'] = redis_connection

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

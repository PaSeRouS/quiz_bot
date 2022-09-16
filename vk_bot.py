from random import choice, randint

import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from db_functions import get_connection, get_question_by_user_id
from db_functions import record_question_to_db
from questions_function import get_questions_and_answers


def send_message(event, vk_api, message):
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=randint(1, 1000)
    )


def quiz_handler(event, vk_api, questions, questions_and_answers, quiz_db):
    if event.text == 'Новый вопрос':
        message = choice(questions)
        record_question_to_db(event.user_id, message, quiz_db)
        send_message(event, vk_api, message)
    elif event.text == 'Сдаться':
        question = get_question_by_user_id(event.user_id, quiz_db)
        answer = questions_and_answers.get(question)
        message = 'Вот правильный ответ: ' + answer
        send_message(event, vk_api, message)

        message = choice(questions)
        record_question_to_db(event.user_id, message, quiz_db)
        send_message(event, vk_api, message)
    elif event.text == 'Привет':
        message = 'Приветствуем тебя в нашей викторине! Нажми «Новый вопрос».'
        send_message(event, vk_api, message)
    else:
        question = get_question_by_user_id(event.user_id, quiz_db)
        answer = questions_and_answers.get(question)

        if answer:
            if answer.lower() == event.text.lower():
                message = 'Правильно! Поздравляю! '
                message += 'Для следующего вопроса нажми «Новый вопрос»'
            else:
                message = 'Неправильно… Попробуешь ещё раз?'

            send_message(event, vk_api, message)

if __name__ == "__main__":
    questions, questions_and_answers = get_questions_and_answers()
    db_connection = get_connection()

    env = Env()
    env.read_env()

    vk_token = env('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            quiz_handler(
                event, vk_api, questions, questions_and_answers, db_connection
            )

from environs import Env
from redis import Redis


def get_connection():
    env = Env()
    env.read_env()

    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')

    return Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        password=redis_password,
        decode_responses=True
    )


def record_question_to_db(user_id, question, db_connection):
    db_connection.set(user_id, question)


def get_question_by_user_id(user_id, db_connection):
    return db_connection.get(user_id)

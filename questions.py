from os import listdir

def parse_questions(filename):
    questions = []
    answers = {}
    is_question = False
    is_answer = False

    with open(filename, "r", encoding="KOI8-R") as file:
        file_contents = file.read()
        file_contents = file_contents.split("\n\n")

    question = ""
    answer = ""

    for content in file_contents:
        texts = content.split("\n")

        for text in texts:
            if text[:6] == "Вопрос":
                question = ""
                is_question = True
            elif text[:5] == "Ответ":
                is_question = False
                is_answer = True
                answer = ""
            elif text[:5] == "Автор":
                is_answer = False
                questions.append(question)
                answers[question] = answer
            elif is_question:
                question += text + " "
            elif is_answer:
                answer += text + " "

    return questions, answers


def append_answers_to_all(parsed_answers, answers):
    answers.update(parsed_answers)
    return answers


def append_questions_to_all(parsed_questions, questions):
    for question in parsed_questions:
        questions.append(question)

    return questions


def get_questions_and_answers():
    questions = []
    answers = {}

    files = listdir("quiz-questions")

    for file in files:
        parsed_questions, parsed_answers = parse_questions(
            f"quiz-questions/{file}"
        )
        
        questions = append_questions_to_all(parsed_questions, questions)
        answers = append_answers_to_all(parsed_answers, answers)

    return questions, answers

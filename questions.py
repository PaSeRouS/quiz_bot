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


def append_answers_to_all(parsed_answers, all_answers):
    all_answers.update(parsed_answers)
    return all_answers


def append_questions_to_all(parsed_questions, all_questions):
    for question in parsed_questions:
        all_questions.append(question)

    return all_questions


def get_questions_and_answers():
    all_questions = []
    all_answers = {}

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/1vs1200.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/1vs1201.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/1vs1298.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/1vs1299.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/anime10.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/futb11br.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/futb11ch.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    parsed_questions, parsed_answers = parse_questions(
        "quiz-questions/futb11ek.txt"
    )
    all_questions = append_questions_to_all(parsed_questions, all_questions)
    all_answers = append_answers_to_all(parsed_answers, all_answers)

    return all_questions, all_answers

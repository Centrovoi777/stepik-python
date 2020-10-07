import requests
import telebot
from telebot import types
import random
import json
import os



token = os.environ["TELEGRAM_TOKEN"]
api_url = 'https://stepik.akentev.com/api/millionaire'

bot = telebot.TeleBot(token)

a = {}
states = {}
START = 'start'
MAIN_STATE = 'main'
QUESTION = 'question'
STATES = 'answers'

try:
    data = json.load(open('db/data.json', 'r', encoding='utf-8'))
except FileNotFoundError:
    data = {
        'states': {},
        MAIN_STATE: {

        },
        QUESTION: {

        },
        STATES: {

        }
    }


def change_data(key, user_id, value):
    data[key][user_id] = value
    json.dump(
        data,
        open('db/data.json', 'w', encoding='utf-8'),
        indent=2,
        ensure_ascii=False,
    )


def update_question():
    response = requests.get(
        api_url,
        # params=update_complexity()
        # params={'complexity': '3'}
    )
    data_api = response.json()
    print(data_api)
    question = data_api['question']
    answers = data_api['answers']
    correct_answer = answers[0]
    random.shuffle(answers)
    #    union_answers = ', '.join(answers)
    dict_update_question = {'question': question, 'answers': answers, 'correct_answer': correct_answer, }
    print(dict_update_question)
    return dict_update_question


def update_counter(a, key, value):
    if key in a:
        a[key] += [value]
    else:
        a.setdefault(key, []).append(value)


class test:
    dict_question = update_question()
    counter = 0
    quest = dict_question["question"]
    answers = dict_question["answers"]
    correct_answer = dict_question["correct_answer"]
    # complexity = {}

    def __init__(self):
        self.text = None
        self.from_user = None

    @bot.message_handler(func=lambda message: True)
    def dispatcher(message):
        user_id = str(message.from_user.id)
        state = data['states'].get(user_id, MAIN_STATE)  # если пользователь впервый раз у нас то он получит MAIN_STATE

        if state == MAIN_STATE:
            test.main_handler(message)
        elif state == QUESTION:
            test.question_handler(message)
        elif state == STATES:
            test.answer_area(message)

    def main_handler(message):
        user_id = str(message.from_user.id)
        if message.text == '/start':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('Миллионер'))
            bot.send_message(
                user_id,
                'Это игра кто хочет стать миллионером',
                reply_markup=markup
            )
            change_data('states', user_id, MAIN_STATE)

        elif message.text == 'Миллионер':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('задать вопрос'))
            bot.send_message(user_id, 'Хочешь задам вопрос?', reply_markup=markup)
            change_data('states', user_id, QUESTION)
        else:
            markup = types.ReplyKeyboardRemove()
            bot.send_message(user_id, 'Я тебя не понял', reply_markup=markup)

    def question_handler(message):
        user_id = str(message.from_user.id)
        print(message)
        if message.text == 'задать вопрос':
            if test.counter < 1:
                change_data('states', user_id, STATES)
                bot.send_message(user_id, test.quest)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add(
                    *[types.KeyboardButton(button) for button in test.answers]
                )
                bot.send_message(user_id, 'Выберите ответ', reply_markup=markup)
                test.counter = 1
                print(test.answers)
                print(test.counter)
            else:
                test.dict_question = update_question()
                test.quest = test.dict_question["question"]
                test.answers = test.dict_question["answers"]
                test.correct_answer = test.dict_question["correct_answer"]
                data['states'][user_id] = STATES
                # bot.send_message(user_id, 'Norm')
                bot.send_message(user_id, test.quest)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                markup.add(
                    *[types.KeyboardButton(button) for button in test.answers]
                )
                bot.send_message(user_id, 'Выберите ответ', reply_markup=markup)
        elif message.text == 'ответы':
            bot.send_message(user_id, text=str(len(a['victory'])) + ' правильных ответов')
            bot.send_message(user_id, text=str(len(a['defeats'])) + ' неправильных ответов')
        else:
            bot.reply_to(message, 'Я тебя не понял 2')

    def answer_area(message):
        user_id = str(message.from_user.id)
        print(states)
        if message.text == test.correct_answer:
            bot.send_message(user_id, 'Молодец, правильно!')
            update_counter(a, 'victory', 0)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(
                *[types.KeyboardButton(button) for button in ['задать вопрос', 'ответы']]
            )
            bot.send_message(user_id, 'Повторим?', reply_markup=markup)
            change_data('states', user_id, QUESTION)

        else:
            bot.send_message(user_id, 'Фу, не правильно')
            update_counter(a, 'defeats', 0)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('задать вопрос'))
            bot.send_message(user_id, 'Повторим?', reply_markup=markup)
            change_data('states', user_id, QUESTION)


bot.polling()

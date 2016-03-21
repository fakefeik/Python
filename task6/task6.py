import json
import random
import datetime
from bottle import route, view, run, static_file

signs = [
    ("Овен", "(21.03 - 20.04)"),
    ("Телец", "(21.04 - 20.05)"),
    ("Близнецы", "(21.05 - 20.06)"),
    ("Рак", "(21.06 - 22.07)"),
    ("Лев", "(23.07 - 22.08)"),
    ("Дева", "(23.08 - 23.09)"),
    ("Весы", "(24.09 - 23.10)"),
    ("Скорпион", "(24.10 - 21.11)"),
    ("Стрелец", "(22.11 - 21.12)"),
    ("Козерог", "(22.12 - 19.01)"),
    ("Водолей", "(22.01 - 18.02)"),
    ("Рыбы", "(19.02 - 20.03)"),
]

with open('sample.json', 'r', encoding='utf8') as f:
    dictionary = json.load(f)


@route('/')
@view('index')
def for_index():
    return {"signs": signs}


@route('/about')
@view('about')
def about():
    return


@route('/css/<filename>.css')
def stylesheets(filename):
    return static_file('{}.css'.format(filename), root='css')


@route('/<sign>')
@view('sign')
def for_sign(sign):
    random.seed(hash(datetime.date.today()) ^ hash(sign))
    first_words = ["Все будет", "Вас ждет", "Будем надеяться, что", "Завтра", "Вангую", "вам"]
    random.shuffle(first_words)
    text = ''
    for word in first_words:
        next_word = word.split()[-1]
        text += word + ' '
        while True:
            try:
                next_word = random.choice(dictionary[next_word])
                text += next_word + ' '
                if next_word[-1] in '().?!;':
                    break
            except KeyError:
                break
    return {"sign": sign, "text": text}

run()

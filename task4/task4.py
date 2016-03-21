from telegram import Updater, ReplyKeyboardMarkup
from random import shuffle, sample
from words import parse_urban

chats = {}
definitions = {}
words = []

keyboard = [["1", "2", "3"]]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)


class ChatInfo:
    def __init__(self, indices):
        self.current = 0
        self.indices = indices
        self.points = 0
        self.question = ""
        self.answers = []


def send_question(bot, chat_id):
    chat = chats[chat_id]
    word_index = chat.indices[chat.current]
    question = words[word_index]
    chat.current += 1
    answers = [definitions[words[x]] for x in [word_index] + sample(set(range(0, len(words))) - {word_index}, 2)]
    shuffle(answers)
    chat.question = question
    chat.answers = answers
    bot.sendMessage(chat_id, "Which definition is correct?\n{word}".format(word=question), reply_markup=reply_markup)
    for index, definition in enumerate(answers):
        bot.sendMessage(chat_id, "{0}: {1}".format(str(index + 1), definition))


def start(bot, update):
    chat_id = update.message.chat_id
    if chat_id in chats:
        bot.sendMessage(chat_id, "Game has already been started.")
    else:
        indices = list(range(0, len(words)))
        shuffle(indices)
        chats[chat_id] = ChatInfo(indices)
        bot.sendMessage(chat_id, "The game has been started! Use /stop to stop the game.")
        send_question(bot, chat_id)


def stop_game(bot, chat_id):
    if chat_id in chats:
        bot.sendMessage(
            chat_id,
            "You've finished playing the game. Your score:{points}, You answered {index} questions.".format(
                points=chats[chat_id].points,
                index=chats[chat_id].current
            )
        )
        del chats[chat_id]


def stop(bot, update):
    chat_id = update.message.chat_id
    stop_game(bot, chat_id)


def parse_int(s):
    try:
        ans = int(s)
        return ans if 1 <= ans <= 3 else None
    except ValueError:
        return None


def handle_message(bot, update):
    chat_id = update.message.chat_id
    if chat_id in chats:
        answer = parse_int(update.message.text)
        if not answer:
            bot.sendMessage(chat_id, "Please enter correct number [1-3]", reply_markup=reply_markup)
            return

        chat = chats[chat_id]
        if definitions[chat.question] == chat.answers[answer - 1]:
            bot.sendMessage(chat_id, "That's correct! You've earned 1 point")
            chat.points += 1
        else:
            bot.sendMessage(chat_id, "Wrong number")

        if len(words) <= chat.current:
            bot.sendMessage(chat_id, "Game over!")
            stop_game(bot, chat_id)
        else:
            bot.sendMessage(chat_id, "Next question:")
            send_question(bot, chat_id)


if __name__ == "__main__":
    definitions = parse_urban()
    words = list(definitions.keys())
    with open("token.txt") as f:
        token = f.read()

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.addTelegramCommandHandler("start", start)
    dispatcher.addTelegramCommandHandler("stop", stop)
    dispatcher.addTelegramMessageHandler(handle_message)

    updater.start_polling()

import telebot
import logging
import sending_queue

token = "<TOKEN>"
bot = telebot.TeleBot(token)
queue = sending_queue.SendingQueue(bot, logging)


@bot.message_handler(commands=['start', 'help'])
def help(message):
    queue.add_text_message(message.chat.id, 'Hi')


if __name__ == '__main__':
    queue.polling()
    bot.polling(none_stop=True)

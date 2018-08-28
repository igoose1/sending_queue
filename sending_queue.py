import queue
from time import time, sleep
import threading
from telebot.apihelper import ApiException
import logging


MAX_MESSAGES_LIMIT = 30
PRIORITY = dict()
PRIORITY['repeat'] = 5
PRIORITY['normal'] = 10
PRIORITY['mailing'] = 20


class TextMessage:
    def __init__(self, chat_id, text,
                 disable_web_page_preview, reply_to_message_id,
                 reply_markup, parse_mode,
                 disable_notification):
        self.chat_id = chat_id
        self.text = text
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup
        self.parse_mode = parse_mode
        self.disable_notification = disable_notification

    def __lt__(self, other):
        return self.chat_id < other.chat_id

    def send(self, bot):
        chat_id = self.chat_id
        text = self.text
        disable_web_page_preview = self.disable_web_page_preview
        reply_to_message_id = self.reply_to_message_id
        reply_markup = self.reply_markup
        parse_mode = self.parse_mode
        disable_notification = self.disable_notification

        # KILL ME PLEASE

        return bot.send_message(chat_id, text, disable_web_page_preview,
                                reply_to_message_id, reply_markup, parse_mode,
                                disable_notification)


class PhotoMessage:
    def __init__(self, chat_id, photo, caption,
                 reply_to_message_id, reply_markup,
                 parse_mode, disable_notification):
        self.chat_id = chat_id
        self.photo = photo
        self.caption = caption
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup
        self.parse_mode = parse_mode
        self.disable_notification = disable_notification

    def __lt__(self, other):
        return self.chat_id < other.chat_id

    def send(self, bot):
        chat_id = self.chat_id
        photo = self.photo
        caption = self.caption
        reply_to_message_id = self.reply_to_message_id
        reply_markup = self.reply_markup
        parse_mode = self.parse_mode
        disable_notification = self.disable_notification

        # KILL ME PLEASE 2

        return bot.send_photo(chat_id, photo, caption, reply_to_message_id,
                              reply_markup, parse_mode, disable_notification)


class SendingQueue:
    def __init__(self, bot, logger=None):
        self.logging = logger or logging
        self.queue = queue.PriorityQueue()
        self.time_queue = queue.Queue(maxsize=MAX_MESSAGES_LIMIT)
        self.bot = bot

    def add_text_message(self, chat_id, text, added_time=None,
                         disable_web_page_preview=None,
                         reply_to_message_id=None, reply_markup=None,
                         parse_mode=None, disable_notification=None,
                         priority=PRIORITY['normal']):
        added_time = added_time or time()
        text = TextMessage(chat_id, text, disable_web_page_preview,
                           reply_to_message_id, reply_markup, parse_mode,
                           disable_notification)

        self.logging.debug('Add: {}'.format(hash(text)))
        self.queue.put((priority, added_time, text))

    def add_photo_message(self, chat_id, photo, added_time=None, caption=None,
                          reply_to_message_id=None, reply_markup=None,
                          parse_mode=None, disable_notification=None,
                          priority=PRIORITY['normal']):
        added_time = added_time or time()
        photo = PhotoMessage(chat_id, photo, caption,
                             reply_to_message_id, reply_markup, parse_mode,
                             disable_notification)

        self.logging.debug('Add: {}'.format(hash(photo)))
        self.queue.put((priority, added_time, photo))

    def add_prepared_message(self, priority, added_time, message):
        print(message.text)
        self.logging.debug('Add again: {}'.format(hash(message)))
        self.queue.put((priority, added_time, message))

    def send_message(self, message):
        now_time = time()
        if not self.time_queue.full or\
                self.time_queue.empty() or\
                int(now_time - self.time_queue.queue[0]):
            try:
                self.time_queue.put(now_time, False)
            except queue.Full:
                self.time_queue.get(False)
                self.time_queue.put(now_time, False)
            try:
                self.logging.info('Send: {}'.format(hash(message)))
                message.send(self.bot)
                return True
            except ApiException as exception:
                # It's telegram errors
                self.logging.exception(exception)
                return True
        else:
            return False

    def check_queue(self):
        while True:
            while not self.queue.empty():
                last_message = self.queue.get()
                self.logging.debug('Get from queue: {}'.format(
                    hash(last_message[-1])))
                if not self.send_message(last_message[-1]):
                    self.add_prepared_message(PRIORITY['repeat'], time(),
                                              last_message[-1])

    def polling(self):
        queue_thread = threading.Thread(target=self.check_queue)
        queue_thread.daemon = True
        queue_thread.start()
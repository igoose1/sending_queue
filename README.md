Sending queue for pytelegrambotapi
==================================

It's a module for sending messages by telegram bot api using queue.

Queue sends only 30 messages per second.

> If you're sending bulk notifications to multiple users, the API will not allow more than 30 messages per second or so.
>
> [My bot is hitting limits, how do I avoid this?](https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this)

* [Preparing](#preparing)
* [Usage](#usage)
  * [Init](#init)
  * [Poll](#poll)
  * [Send text message](#send-text-message)
  * [Priority of messages](#priority-of-messages)
  * [Get status of messages](#get-status-of-messages)
  * [Send other content](#send-other-content)
  * [Logging](#logging)

Preparing
---------

Move `sending_queue.py` to your project's folder.

Usage
-----

#### Init
Init bot and queue.
```python3
import telebot
import sending_queue

token = "<TOKEN>"
bot = telebot.TeleBot(token)
queue = sending_queue.SendingQueue(bot)
```

#### Poll
Start to poll queue. It needs for checking queue's elements and sending them.
```python3
queue.polling()
```

#### Send text message
To send text message add it to queue.
```python3
queue.add_text_message(message.chat.id, 'Some strange words')
```

#### Priority of messages
You can change message priority.
Standart message's priority is 10.
Messages with lower priority will be sent earlier.

```python3
queue.add_text_message(message.chat.id, 'Important message', priority=5)
queue.add_text_message(message.chat.id, 'Not important message', priority=20)
queue.add_text_message(message.chat.id, 'Most important message', priority=1)
```

In queue if messages have the same priority they will be sent by added time.
Queue remembers time itself but you can set your own time.

```python3
import time

queue.add_text_message(message.chat.id, 'First message', priority=20, added_time=time.time())
time.sleep(2.5)
queue.add_text_message(message.chat.id, 'Second message', priority=20, added_time=time.time())
```

#### Get status of messages

You can get a status of queue.

`queue.status.succeed_count` is a number of messages that were sent without errors.

`queue.status.failed_count` is a number of messages that were not sent.

`queue.status.waiting_count` is a number of messages that are in queue now. It has to equal `queue.queue.qsize()`.


There are status dictionaries with priorities of messages.

For example `queue.status.detailed_waiting_count[10]` will return the number of messages in the queue with priority 10.

Dictionaries save in RAM.
If you use a lot of different priorities `queue.status.detailed_xyz_count` can be very slow.
To disable detailing status use `status_detailed=False`.

```python3
queue = sending_queue.SendingQueue(bot, status_detailed=False)
```

#### Send other content

To add other types of messages use these functions.

| function            | telegram method |
|---------------------|-----------------|
| `add_text_message`  | `sendMessage`     |
| will be later       | `forwardMessage`  |
| `add_photo_message` | `sendPhoto`       |
| will be later       | `sendDocument`    |
| will be later       | `sendVideo`       |
| will be later       | `sendAnimation`   |
| will be later       | `sendVoice`       |
| will be later       | `sendAudio`       |

#### Logging

If you want to use your own logger set it by argument `logger`.
```python3
queue = sending_queue.SendingQueue(bot, logger=my_logger)
```

import sys
import asyncio
import telepot
import json
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open

class MessageCounter(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0

    async def on_chat_message(self, msg):
        self._count += 1
        await self.sender.sendMessage(self._count)

with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['TOKEN']

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
import discord
import asyncio
import random
import re
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

client = discord.Client()

bot = ChatBot(
    'Fred',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database='./db.sqlite3'
)

bot.set_trainer(ChatterBotCorpusTrainer)

'''bot.train(
    "chatterbot.corpus.english",
)'''

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    clean_message = remove_mentions(message)
    if client.user in message.mentions or random.randint(0,100) < 10 or message.channel.is_private:
        print("message: " + clean_message)
        bot_reply = str(bot.get_response(clean_message))
        await client.send_message(message.channel, content=bot_reply)
        print("reply: " + bot_reply)
    else:
        msg = await client.wait_for_message(channel=message.channel)
        bot.learn_response(remove_mentions(msg),remove_mentions(msg))

def remove_mentions(message):
    return re.sub(r'@[a-zA-Z\d\S:]+','',message.clean_content).strip()

client.run('token')

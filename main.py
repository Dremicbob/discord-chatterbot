import asyncio
import re
import sys

# logging
import logging
logging.basicConfig(level=logging.INFO)

# discordpy http://discordpy.readthedocs.io/en/latest/index.html
import discord

# chatterbot https://chatterbot.readthedocs.io/en/stable/chatterbot.html
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.conversation import Statement

import config

bot = ChatBot(
    'Fred',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database='./db.sqlite3'
)

client = discord.Client()

if("-train" in sys.argv):
    train()

def remove_mentions(message):
    return re.sub(r'@[a-zA-Z\d\S:]+','',message.clean_content).strip()

def train():
    bot.set_trainer(ChatterBotCorpusTrainer)

    bot.train(
        "chatterbot.corpus.english",
    )

def learn(message, reply):
    logging.info("--- Learning ---")
    message = remove_mentions(message)
    reply = remove_mentions(reply)

    bot.set_trainer(ListTrainer)

    bot.train([
        message,
        reply,
    ])

    logging.info("learning message: " + message)
    logging.info("learning reply: " + reply)

@asyncio.coroutine  
def send_reply(message):
    logging.info("--- Sending Reply ---")
    message_without_mentions = remove_mentions(message) 
    
    reply = str( bot.generate_response( Statement(message_without_mentions) , None)[1] )
    yield from client.send_message(message.channel, content=reply)

    logging.info("message: " + message_without_mentions)
    logging.info("reply: " + reply)

@client.async_event
def on_ready():
    logging.info('Connected!')
    logging.info('Username: ' + client.user.name)
    logging.info('ID: ' + client.user.id)

@client.async_event
def on_message(message):
    if message.author == client.user:
        return
    
    if client.user in message.mentions or message.channel.is_private:
        yield from send_reply(message)
    else:
        if clean_message.endswith("?") or len(message.mentions) > 0:
            reply = yield from client.wait_for_message()
            if reply.author in [client.user, message.author]:
                logging.info("forgetting conversation")
                return
            
            learn(message, reply)
                
client.run(config.token)

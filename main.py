import asyncio
import re
import sys
import os

# logging
import logging
logging.basicConfig(level=logging.INFO)

# discordpy http://discordpy.readthedocs.io/en/latest/index.html
import discord
from discord.ext import commands

# chatterbot https://chatterbot.readthedocs.io/en/stable/chatterbot.html
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.conversation import Statement

def remove_mentions(message):
    return re.sub(r'@[a-zA-Z\d\S:]+','',message.clean_content).strip()

class MyClient(discord.Client):
    def __init__(self, *args):
        super(MyClient, self).__init__(*args)

        self.bot = ChatBot(
            'Fred',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database='./db.sqlite3'
        ) 

    @asyncio.coroutine
    def on_ready(self):
        logging.info('Connected!')
        logging.info('Username: ' + self.user.name)
        logging.info('ID: ' + self.user.id)

    def corpus_train():
        self.bot.set_trainer(ChatterBotCorpusTrainer)

        self.bot.train(
            "chatterbot.corpus.english",
        )


    def learn(self, message, reply):
        logging.info("--- Learning ---")
        message = remove_mentions(message)
        reply = remove_mentions(reply)

        self.bot.set_trainer(ListTrainer)

        self.bot.train([
            message,
            reply,
        ])

        logging.info("learning message: " + message)
        logging.info("learning reply: " + reply)

    @asyncio.coroutine  
    def send_reply(self, message):
        logging.info("--- Sending Reply ---")
        message_without_mentions = remove_mentions(message) 
        
        reply = str( self.bot.generate_response( Statement(message_without_mentions) , None)[1] )
        yield from self.send_message(message.channel, content=reply)

        logging.info("message: " + message_without_mentions)
        logging.info("reply: " + reply)
        

    @asyncio.coroutine  
    def on_message(self,message):
        if message.author == self.user or "!" in message.content:
            return
        
        if self.user in message.mentions or message.channel.is_private:
            yield from self.send_reply(message)
        elif clean_message:
            if clean_message.endswith("?") or len(message.mentions) > 0:
                reply = yield from self.wait_for_message()
                if reply.author in [self.user, message.author]:
                    logging.info("forgetting conversation")
                    return
                
                self.learn(message, reply)

if("-train" in sys.argv):
    corpus_train()

if '-token' not in sys.argv and 'token' not in os.environ:
    raise Exception("Please supply a token using '-token YOUR-TOKEN-HERE' or setting the environment variable token")
else:
    if '-token' in sys.argv: 
        token = sys.argv[sys.argv.index('-token') + 1]
    else:
        token = os.environ['token']

    logging.info("token: " + token)

    # try:
    #     client = MyClient()
    #     client.run(token)
    # finally:
    #     logging.info("token: " + token)
    

    


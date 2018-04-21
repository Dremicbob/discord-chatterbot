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

def remove_mentions(message : str):
    return re.sub(r'@[a-zA-Z\d\S:]+','',message).strip()

def get_command(message : str, prefix="!"):
    if not message.startswith(prefix):
        raise Exception("No command")
    return message.split(" ")[0].replace("!", " ").strip()
    

class ChatClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super(ChatClient, self).__init__(*args, **kwargs)

        self.bot = ChatBot(
            'Fred',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database='./db.sqlite3'
        )

        self.commands = {
            'ping': self.ping,
            'train': self.train
        }

    @asyncio.coroutine
    def ping(self, message):
        yield from self.send_message(message.channel, content="pong")

    @asyncio.coroutine
    def train(self, message):
        if not "(:)" in message.content:
            yield from self.send_message(message.channel, content=":confused: You have no reply for me to learn. Use (:) to seperate message.")
            return
        
        train_times = 1
        if "(super_train)" in message.clean_content:
            train_times = 100
            yield from self.send_message(message.channel, content=f":clock: super_train underway please be patient")
        
        learn_message, learn_reply = message.clean_content.replace("!" + get_command(message.content), "").replace("(super_train)", "").split("(:)")

        self.learn(learn_message, learn_reply, train_times=train_times)

        yield from self.send_message(message.channel, content=f"learnt: \n message = {learn_message} \n reply = {learn_reply}")
      
    
    def corpus_train():
        self.bot.set_trainer(ChatterBotCorpusTrainer)

        self.bot.train(
            "chatterbot.corpus.english",
        )

    def learn(self, message, reply, train_times=1):
        logging.info("--- Learning ---")
        message = remove_mentions(message)
        reply = remove_mentions(reply)

        self.bot.set_trainer(ListTrainer)

        self.bot.train([
            message,
            reply,
        ] * train_times)

        logging.info("learning message: " + message)
        logging.info("learning reply: " + reply)

    @asyncio.coroutine
    def on_ready(self):
        logging.info('Connected!')
        logging.info('Username: ' + self.user.name)
        logging.info('ID: ' + self.user.id)          


    @asyncio.coroutine  
    def send_reply(self, message):
        logging.info("--- Sending Reply ---")
        message_without_mentions = remove_mentions(message.clean_content) 
        
        reply = str( self.bot.generate_response( Statement(message_without_mentions) , None)[1] )
        yield from self.send_message(message.channel, content=reply)

        logging.info("message: " + message_without_mentions)
        logging.info("reply: " + reply)

    @asyncio.coroutine  
    def on_message(self,message):
        if message.author == self.user:
            return

        if message.content.startswith("!"):
            command = get_command(message.clean_content)
            try:
                yield from self.commands[command](message)
            except KeyError:
                yield from self.send_message(message.channel, content=(command + ":P is not a registered command"))

            return
        
        if self.user in message.mentions or message.channel.is_private:
            yield from self.send_reply(message)
        else:
            if message.clean_content.endswith("?") or len(message.mentions) > 0:
                reply = yield from self.wait_for_message()
                if reply.author in [self.user, message.author]:
                    logging.info("forgetting conversation")
                    return
                
                self.learn(message.clean_content, reply.clean_content)

def main():
    if("-train" in sys.argv):
        corpus_train()

    if '-token' not in sys.argv and 'token' not in os.environ:
        raise Exception("Please supply a token using '-token YOUR-TOKEN-HERE' or setting the environment variable 'token'")
    else:
        token = ""
        if '-token' in sys.argv: 
            token = sys.argv[sys.argv.index('-token') + 1]
        else:
            token = os.environ['token']

        client = ChatClient()
        client.run(token)

if __name__ == '__main__':
    main()
    
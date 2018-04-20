import discord
import asyncio
import re
import sys
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.conversation import Statement, Response

client = discord.Client()

bot = ChatBot(
    'Fred',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database='./db.sqlite3'
)

if("-train" in sys.argv):
    bot.set_trainer(ChatterBotCorpusTrainer)

    bot.train(
        "chatterbot.corpus.english",
    )

bot.set_trainer(ListTrainer)

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
    if client.user in message.mentions or message.channel.is_private:
        print("message: " + clean_message)
        bot_reply = str( bot.generate_response(Statement(clean_message), None)[1] )
        await client.send_message(message.channel, content=bot_reply)
        print("reply: " + bot_reply)
    else:
        if clean_message.endswith("?") or len(message.mentions) > 0:
            reply = await client.wait_for_message()
            print(reply.author, [client.user, message.author])
            if reply.author in [client.user, message.author]:
                print("forgetting conversation")
                return

            clean_reply = remove_mentions(reply)
            print("learning message: {0}".format(clean_message))
            print("learning reply: {0}".format(clean_reply))
            bot.train([
                clean_message,
                clean_reply,
            ])
            # bot.learn_response(Statement(clean_reply), Statement(clean_message))

def remove_mentions(message):
    return re.sub(r'@[a-zA-Z\d\S:]+','',message.clean_content).strip()

client.run('NDMzNTg5MTE2MDA2MDM5NTYz.Da-C4g.6ByagOSok2vnhlrNRDgB7gO4ang')

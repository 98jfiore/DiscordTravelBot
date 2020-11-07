import os

import discord
from dotenv import load_dotenv
import sqlalchemy
import tables
from tables import BASE

load_dotenv()


ENGINE = sqlalchemy.create_engine(os.environ["DATABASE_URL"])
BASE.metadata.create_all(ENGINE, checkfirst=True)

SESSION_MAKER = sqlalchemy.orm.sessionmaker(bind=ENGINE)
SESSION = SESSION_MAKER()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} hasconnected to Discord!')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    passport = SESSION.query(tables.Traveler).filter_by(userId=str(message.author.id)).first()
    if not passport:
        print(message)
        SESSION.add(tables.Traveler(str(message.author.id)))
        SESSION.commit()
        await message.channel.send("Hello " + message.author.nick + ", I hope you enjoy your trip on Air Discord!")
        return
    await message.channel.send(message.content)

client.run(TOKEN)

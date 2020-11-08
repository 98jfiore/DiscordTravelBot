import os

import discord
from dotenv import load_dotenv
import sqlalchemy
import tables
import requests
from tables import BASE

load_dotenv()


ENGINE = sqlalchemy.create_engine(os.environ["DATABASE_URL"])
BASE.metadata.create_all(ENGINE, checkfirst=True)

SESSION_MAKER = sqlalchemy.orm.sessionmaker(bind=ENGINE)
SESSION = SESSION_MAKER()

TOKEN = os.getenv('DISCORD_TOKEN')

CLIENT = discord.Client()

COUNTRIES_API_URL = "https://restcountries.eu/rest/v2/"

def add_country_and_borders(country):
    country = SESSION.query(tables.Country).filter_by(ccode=country).first()
    if not country:
        resp = requests.get(COUNTRIES_API_URL + "alpha?codes=" + country)
        print(resp.json()[0]["name"])
        SESSION.add(tables.Country(country, resp.json()[0]["name"]))
        SESSION.commit()

@CLIENT.event
async def on_ready():
    print(f'{CLIENT.user} hasconnected to Discord!')

@CLIENT.event
async def on_message(message):
    if message.author.bot:
        return
    passport = SESSION.query(tables.Traveler).filter_by(userId=str(message.author.id)).first()
    if not passport:
        print(message)
        try:
           
            SESSION.add(tables.Traveler(str(message.author.id), "USA"))
            SESSION.commit()
            await message.channel.send("Hello " + message.author.nick + \
                ", I hope you enjoy your trip on Air Discord! If you were just asking for something, please ask again as I may have missed it.  If you have further inquiries, please type !bot and I'll be right with you.")
            return;
        except Exception:
            return
    if(message.content[0] == '!'):
        if(message.content.startswith("!bot")):
            print("If you would like to")
    passport.miles += 1
    SESSION.commit()
    if(passport.miles % 10 == 0):
        await message.channel.send("YOU REACHED " + str(passport.miles) + " MILES!")
    await message.channel.send(message.content)

resp = requests.get(COUNTRIES_API_URL + "alpha?codes=USA")
print(resp)
print(resp.json()[0]["name"])

#CLIENT.run(TOKEN)

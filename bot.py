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

def add_borders(country):
    resp = requests.get(COUNTRIES_API_URL + "alpha?codes=" + country)
    resp_json = resp.json()[0]
    for bcountry in resp_json["borders"]:
        try:
            SESSION.add(tables.Border(country, bcountry))
            SESSION.commit()
        except Exception:
            continue

def add_country(country):
    country_exist = SESSION.query(tables.Country).filter_by(ccode=country).first()
    if not country_exist:
        resp = requests.get(COUNTRIES_API_URL + "alpha?codes=" + country)
        resp_json = resp.json()[0]
        flag_url = "https://www.countryflags.io/" + resp_json['alpha2Code'].lower() + "/flat/64.png"
        SESSION.add(tables.Country(country, resp_json["name"], flag_url))
        SESSION.commit()
        for bcountry in resp_json["borders"]:
            try:
                SESSION.add(tables.Border(country, bcountry))
                SESSION.commit()
            except Exception:
                continue
        return
    country_borders = SESSION.query(tables.Border).filter_by(ccodea=country).first()
    if not country_borders:
        add_borders(country)

def travel(message, passport):
    if passport.miles < 10:
        return ("We are sorry, but I'm afraid you do not have enough miles to travel at the time, "+\
            "please keep talking and try again after you've earned enough.  "+\
            "We thank you for your cooperation.  Enjoy your wait for Discord Airlines! :)")
    words = message.content.split()
    if len(words) < 2:
        return [("We are sorry, but we cannot allow you to travel if you have not told us where you would like to travel to, "+\
            "please try to travel again and hopefully it will go better! :)")]
    next_ccode = words[1].upper()
    if len(next_ccode) != 3:
        return [("We are sorry, but the location you entered is not valid I'm afraid :,(  But you can try again!  You've got this! :)")]
    
    borders = [
        border.ccodeb
        for border in SESSION.query(tables.Border).filter_by(ccodea=passport.location).all()
    ]
    if next_ccode not in borders:
        return ["I'm sorry, but the country you have entered is not valid, please try again with a country code bordering the country you currently are in."]
    else:
        add_country(next_ccode)
        stamp_exists = SESSION.query(tables.Stamp).filter_by(code=next_ccode, uid=str(message.author)).first()
        if not stamp_exists:
            SESSION.add(tables.Stamp(str(message.author), next_ccode))
            SESSION.commit()
            SESSION.commit()
        passport.location = next_ccode
        passport.miles -= 10
        SESSION.commit()
        country = SESSION.query(tables.Country).filter_by(ccode=passport.location).first()
        return ["You have successfully traveled to " + country.name + " please let us know when you would like to travel again", country.flag]

def jump(message, passport):
    if passport.miles < 50:
        return [("We are sorry, but I'm afraid you do not have enough miles to take a long flight at the time, "+\
            "please keep talking and try again after you've earned enough.  "+\
            "We thank you for your cooperation.  Enjoy your wait for Discord Airlines! :)")]
    words = message.content.split()
    if len(words) < 2:
        return [("We are sorry, but we cannot allow you to travel if you have not told us where you would like to travel to, "+\
            "please try to travel again and hopefully it will go better! :)")]
    next_country = message.content[6:]
    next_country.replace(" ", "-")
    resp = requests.get(COUNTRIES_API_URL + "name/" + next_country)
    if resp.status_code != 200 or len(resp.json()) < 1:
        return [("I am sorry, but the country you are requesting does not appear to exist.  "+\
            "Can you please try again?  I would be more than happy to assist you! :)")]
    next_ccode = resp.json()[0]['alpha3Code']
    next_country_name = resp.json()[0]['name']
    add_country(next_ccode)
    stamp_exists = SESSION.query(tables.Stamp).filter_by(code=next_ccode, uid=str(message.author)).first()
    if not stamp_exists:
        SESSION.add(tables.Stamp(str(message.author), next_ccode))
        SESSION.commit()
        SESSION.commit()
    passport.location = next_ccode
    passport.miles -= 50
    SESSION.commit()
    return ["You have successfully taken a long flight to " + next_country_name + " please let us know when you would like to travel again, and get some rest, jet lag can be a doozy!", 
        "https://www.countryflags.io/" + resp.json()[0]['alpha2Code'].lower() + "/flat/64.png"]

def process_text(message, passport):
    try:
        if(message.content[0] == '!'):
            if(message.content.startswith("!bot")):
                return [("If you would like to find where you've been stamped, type `!stamps`.\n" + \
                    "If you wish to know how many stamps you have, type `!stamp count`.\n" + \
                    "If you wish to spend 10 miles to travel, type `!travel` and the three letter code of the country you wish to travel to.\n" + \
                    "If you wish to spend 50 miles to take a long travel, type `!jump` and the name of the country you wish to travel to.\n" + \
                    "If you wish to know the name of the country you are currently in, type `!location`.\n" + \
                    "If you wish to know how many miles you have, type `!miles`.\n" + \
                    "If you wish to clear your miles and stamps type `!clear passport`.\n" + \
                    "Finally, if you wish to know the codes of the countries you can travel to, type `!borders`.")]
            elif(message.content.startswith("!stamps")):
                stamps = SESSION.execute('SELECT name FROM country WHERE ccode IN (SELECT code FROM stamp WHERE uid=\''+passport.uid+'\');')
                response =message.author.nick + " has stamps from: "
                for row in stamps:
                    for key, value in row.items():
                        response += value + ", "
                return [response[:-2]]
            elif(message.content.startswith("!stamp count")):
                stamps = SESSION.execute('SELECT name FROM country WHERE ccode IN (SELECT code FROM stamp WHERE uid=\''+passport.uid+'\');')
                response = message.author.nick + " has a total of "
                count = 0
                for row in stamps:
                    count += 1
                if count == 1:
                    response += "1 stamp."
                else:
                    response += str(count) + " stamps."
                return [response]
            elif(message.content.startswith("!miles")):
                response = message.author.nick + " has " + str(passport.miles) + " miles and counting!"
                return [response]
            elif(message.content.startswith("!location")):
                country = SESSION.query(tables.Country).filter_by(ccode=passport.location).first().name
                response = message.author.nick + " is in the country of " + country
                return [response]
            elif(message.content.startswith("!borders")):
                borders = SESSION.query(tables.Border).filter_by(ccodea=passport.location).all()
                response = message.author.nick + " is close to the countries: "
                for border in borders:
                    response += border.ccodeb + ", "
                return [response[:-2]]
            elif(message.content.startswith("!travel")):
                return travel(message, passport)
            elif(message.content.startswith("!jump")):
                return jump(message, passport)
            elif(message.content.startswith("!clear passport")):
                SESSION.execute('DELETE FROM stamp WHERE uid=\''+passport.uid+'\';')
                SESSION.execute('DELETE FROM traveler WHERE uid=\''+passport.uid+'\';')
                return ["Your passport has been cleared, hope you enjoy starting over!"]
                
    except Exception as err:
        print(str(err))

@CLIENT.event
async def on_ready():
    print(f'{CLIENT.user} has connected to Discord!')

@CLIENT.event
async def on_message(message):
    if message.author.bot:
        return
    passport = SESSION.query(tables.Traveler).filter_by(uid=str(message.author)).first()
    if not passport:
        try:
            add_country("USA")
            SESSION.add(tables.Traveler(str(message.author), "USA"))
            SESSION.commit()
            SESSION.add(tables.Stamp(str(message.author), "USA"))
            SESSION.commit()
            await message.channel.send("Hello " + message.author.nick + \
                ", I hope you enjoy your trip on Air Discord! If you were just asking for something, please ask again as I may have missed it.  If you have further inquiries, please type `!bot` and I'll be right with you :)")
            return;
        except Exception:
            return

    response = process_text(message, passport)
    if response and len(response) > 0:
        if len(response) == 1 and len(response[0]) > 0:
            await message.channel.send(response[0])
        elif len(response) > 1:
            em = discord.Embed()
            em.set_image(url=response[1])
            await message.channel.send(response[0], embed=em)
    else:
        passport.miles += 1
        SESSION.commit()

CLIENT.run(TOKEN)

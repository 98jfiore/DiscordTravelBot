# TravelBot

TravelBot is a discord bot that simulates going on a grand, world travelling adventure.

## Installation

The git cli should be installed for this project.
Python libraries that should be installed via pip install are: discord.py, python_dotenv.

You need to get PSQL to work with python by running these commands:
    1. `sudo yum update`, and enter yes to all prompts    
    2. `sudo pip install --upgrade pip`  
    3. `sudo pip install psycopg2-binary`    
    4. `sudo pip install Flask-SQLAlchemy==2.1`
    
If you do not already have a psql database, you need to initialize one:
    1. `sudo yum install postgresql postgresql-server postgresql-devel postgresql-contrib postgresql-docs`    
        Enter yes to all prompts.    
    2. `sudo service postgresql initdb`  
    3. `sudo service postgresql start`    
    4. Make a new superuser: `sudo -u postgres createuser --superuser $USER` 
    5. Make a new database: `sudo -u postgres createdb $USER`   
    6. Make sure your user shows up and make a new one:    
        a) `psql`    
        b) `\du` look for yourself as a user    
        c) `\l` look for yourself as a database 
        b) `create user [some_username_here] superuser password '[password]';` 
          i) Make sure you remember the quotes around password and the semicolon. 
            Check `\du` to ensure it worked.
        c) `\q` to quit out of sql
        
Finally, you need to enable SQLAlchemy to be read from and written to:
    1. `sudo vim /var/lib/pgsql9/data/pg_hba.conf`
      i) Alternative: `sudo vim $(psql -c "show hba_file;" | grep pg_hba.conf)`  
    2. Replace all values of `ident` with `md5` in Vim: `:%s/ident/md5/g`  
    3. `sudo service postgresql restart`  
    4. Using the username/password you just created, put 
        DATABASE_URL = 'postgresql://{username}:{password}@localhost/postgres' in .env

If you wish to deploy to heroku, log into heroku on your command line and run the 
  following commands to move your database over:
    0. If you do not already have a heroku project: `heroku create` and add your config variables.
    1. `heroku addons:create heroku-postgresql:hobby-dev`
    2. `heroku pg:wait`
    3. `heroku pg:push postgres DATABASE_URL`
    4. `git push heroku main`
## Set up

Go to the Discord Developers portal and create a bot.  Give it persmissions to read and write messages.  Get the bot's token and save it under a file names `.env` with the variable name `DISCORD_TOKEN`.
Use api from `https://restcountries.eu/`

## License

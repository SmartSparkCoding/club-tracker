# Hack Club Club Tracker

This is a web-app, originally designed to assist 'Ashford School Hack Club' but may be rolled out to other clubs. 
The system is very simple and helps club leaders track things that normally can't be tracked using the leaders portal. 

The app helps track allergies for specific members, especially as many of the club YSWS rewards are food. Not only this, it also tracks attendance for all users to see if they really have been showing up. 

It is hosted on nest, and uses flask. It only has one .py file, being `app.py` which hosts the app, and even creates a local database on SQLite3 to track the systems (however this may change in the future to allow for other clubs to access it and use the system and or to allow for better scaling). It also uses basic ClubAPI for Clubs, created by the Hack Club Clubs team such as to get access to club names, info, location, members, leaders etc.

To allow for the club api stuff to work, see below to define your club as an .env variable to be able to use the API system. 

The styling honestly took me ages and I have never really used flask before, so a lot of google was used to understand it + even the API! 

AI was used, however, it made minimal parts of the code. The only significant parts of the code that it made was some of the complicated member systems in `app.py ` but AI was used mainly to explain how various things work / don't work. 

I do know that my firebase details are open to the public, however, I don't really mind too much, so please don't report this (I know that you shouldn't but still, ignore it!). 

Umm, yeah ! guess that is sorta it!

## To Start Server on Nest

Run:

`cd ~/club-tracker`
`git pull`
`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`
`python3 app.py`

The server is now activated!

If `python-dotenv` is not installed, `app.py` still starts; it just skips loading `.env` automatically.

## Add Club Name for Club Details 

`export CLUB_NAME="Ashford School Hack Club"`
# CS50 Final Project - Covaccine 
## Video Demo: [Covaccine](https://youtu.be/TWaPYQj9XuA)
## About the project
This is my final project for [Harvard CS50x](https://cs50.harvard.edu/x/2020/) course. It is a flask based web application to spread awareness on COVID-19 vaccination. As India is going through an *intense COVID-19 second wave*, awareness regarding vaccination and available resources is the need of the hour. The implementation of the website is fairly simple based on the following technologies.
### Languages/libraries Used
- Python
- JS/ jquery
- HTML/CSS
- Bootstrap libraries
- sqlite3
- CS50 library
- werkzeug
- Flask
- jinja2
- other libraries and packages
### How it works?
The website home page has various resources and information regarding COVID-19 vaccination. The user can Login/Register to the website to maintain their profile where
many new resouces are available like real-time API COVID tracker update, nearest vaccination centres, donation, profile updates along with much more. 
### Routing
Different routes have different criterias for access. Few of them require the user to login and uses session id to autheticate details and access database.
### Database
All user data in stored in covaccine.db which has multiple related tables. It is access using sqlite3 and CS50 library. 
### API KEY
To run the application we need to generate an API first on [Rapid API](https://rapidapi.com/marketplace) which is used to access real-time COVID-19 data.
### How to use?
To run the web application use these commands:

```
$ export API_KEY= enter your api key
$ export FLASK_APP=application.py
$ flask run
```
### Possible Improvements
The scope of development is there in any project and in this one too. We can add the following features to make the website more user-friendly:

- Linking payment gateways to make donation feature more useful.
- Making user profile more friendly to add avatar and save resources.
- Adding real-time informaion on more resouces like COVID-19 hospitals, bed availability, etc.
- Using [NewsAPI](https://newsapi.org/) to provide embedded live news instead of redirect to google news.

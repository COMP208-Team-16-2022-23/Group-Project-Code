from datetime import timedelta

SECRET_KEY = 'COMP208_Team16'
PERMANENT_SESSION_LIFETIME = timedelta(minutes=45)

# Configuration variables for the database
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'comp208'
USERNAME = 'root'
PASSWORD = '11111111'

# Configuration variables for email
# configure the mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'lcda.team.2023@gmail.com'
MAIL_PASSWORD = 'uwiyqlxbdizognpr'
MAIL_DEFAULT_SENDER = 'lcda.team.2023@gmail.com'
MAIL_MAX_EMAILS= None
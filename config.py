from datetime import timedelta

SECRET_KEY = 'COMP208_Team16'
PERMANENT_SESSION_LIFETIME = timedelta(minutes=45)

# Configuration for the database
HOSTNAME = 'comp208-team16.ctw17gkeyu80.eu-west-2.rds.amazonaws.com'
PORT = '3306'
DATABASE = 'project'
USERNAME = 'root'
PASSWORD = '5hqYXX55sFnIirPD868G'

# Configuration variables for email
# configure the mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'lcda.team.2023@gmail.com'
MAIL_PASSWORD = 'uwiyqlxbdizognpr'
MAIL_DEFAULT_SENDER = 'LCDA Team'
MAIL_MAX_EMAILS = None

# Configuration variables for the file upload
UPLOAD_FOLDER = 'lowcodeanal/static/uploads'

# product name
PRODUCT_NAME = 'LCDA'
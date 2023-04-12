from datetime import timedelta

# DOMAIN
DOMAIN = 'https://lcda-vgnazlwvxa-uw.a.run.app'

SECRET_KEY = 'COMP208_Team16'
PERMANENT_SESSION_LIFETIME = timedelta(minutes=45)

# Configuration for the database
HOSTNAME = 'comp208-team16.ctw17gkeyu80.eu-west-2.rds.amazonaws.com'
PORT = '3306'
DATABASE = 'project'
USERNAME = 'root'
PASSWORD = '5hqYXX55sFnIirPD868G'
LOCAL_TEST = False  # set to True will ignore the above configuration and use local sqlite database called project.db

# Configuration variables for email
# configure the mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'lcda.team.2023@gmail.com'
MAIL_PASSWORD = 'uwiyqlxbdizognpr'
MAIL_DEFAULT_SENDER = 'LCDA Team'
MAIL_MAX_EMAILS = None

# Configuration variables for Google Cloud Storage
GOOGLE_APPLICATION_CREDENTIALS = {
    "type": "service_account",
    "project_id": "lcda-platform",
    "private_key_id": "b100d9a8d523dd1586b057f1bee7a98b44837537",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCT/METU+OJZ4e/\nvVv104Fmh+4vouaK1vreheZuIzE8QnHA8VBRcXsGV5Hsn8+2h5WKo1yjI0CTjHup\njkrP5L1/ZE8rCJTwZZMS+iyee60u/dJ9VQXzlkwn9mZyf4gvczmKeFN0uLNW78p3\nT8/YqWfvYrbEOfqmU7iWv/fgODaWsO/hTDLNyvfNjHDt2GL75Nw2pEdAGT+Pq4XM\nkOvEuXwPdqAjoS0KoKlBLbExZ6YWg3kC4iheXpFQKs5172Hvi9B77ig0RUGjiczS\nkmS6FVBd8fZsWqff7Anqfsd4sLitjnRXAZvw9oLZdKNsLIAMmOo2NMlzbM7KDLFo\n9YKjObWlAgMBAAECggEAFr1rk8M7vxT0FKAN3ffqte0kShifkW0YbpInxvvMaIST\nQ0ExhNpJu79AEpq6CcPK1Ftm9ECJ/0JCjFrrnwd4oPcyfRvb+xa4o11i9tVtVr+1\nFQI4IGaTfD6OHoD/Vb9Ac8kqldB96ll9hJj0iMf7Sxshl4SLQfyybCPCfKdWqA/7\nZ3Lci034Clpfdq3FSzfsGXX3WFlGNc7ULO4n3yO7tWr+gt5gJmxDXwYbeEf5CcGj\n1ehZiSNVePA7fNIIpYZS/mixykZfznCIHyYK3O5uNl8F5cux+wEcFR0fvKIsIJ8S\neDayBan4GrsMyrSlJJJx5pwHievfkiRF5xDrMQnSEQKBgQDKU4GSDT6eJCf6Sz0X\n1orOER2Jj2pQ/AHHHDDwNJcNRRVVP7w81r4wzA789oBaeI1WrAnQTuICE2nOsLwT\nEqYs7qZBXynQ/HPDO3SJUAf+NuX3sS9YfrkYdnXGcIecgwRb6iJ3VXUtJWd+InKu\nnLq1SAxfpjOoQYUmKckjf8KHOQKBgQC7PvR1QMH0MvwQnsmcZBj1DyrGBSqQfg3t\nuTnEfn1kZv4J9NCQJIUeMZcVlPIDzCjB3bxbbdbQLjVADuHMEktLzl2x6DtuFwSV\npDrF3u3o7aDGq5I4FtQFD0mQXER+iYGkBCjEr4l5rm3vSan1mvD3zf1Ywh3ZSrkJ\nfY97EHnVzQKBgHFWZfbSxIkB6AMlsotv+0GEBO/SDtRe1wAaoq9sRlGAqXqfwWqz\nQMdFCABcdXo4nbQ3mye9iI1xIoxOJIzqnXv+E9P64wnW4WI0JAvncRLO3fPqpYMF\nOdqiQUdwMgdSvVZfyf7fOEyZ72eRFH0L/usd+RB7oeRXD6dZMPtZzjbBAoGBAKEf\nmSfUY5GI1dJPcNk8YSVuubXP+EKB1eZ7/rOQzMG6xls26MlAQ7QppAKUOnT+FwxL\ni6t5JuHZAUVwCOibzWMb3xAZ8BnZgL5rpY9jN4G6CSErvhS5wBPihcDNRLtGA+Jp\nGdO14Sxt5neEAdYwT65M+PaJgznZzMPX4cFZ+hz5AoGBAIDXlk9wEkEjXEtjeJwi\njfKqWE1+m8M8HrWE0csvLYS/mGeo7qpMDDGgRdjNHk2C+rl5tIdZvt4G9plfqV3N\nsRnJW/S5wPKmbu7GF1OpPFB9jFSyq49tU/DR53MuN8oYEckDNVm6Myn1hLCZNLNn\n2iZ5gDW3QhvYaRRPQuzik3xh\n-----END PRIVATE KEY-----\n",
    "client_email": "lcda-website@lcda-platform.iam.gserviceaccount.com",
    "client_id": "107298518355135611874",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lcda-website%40lcda-platform.iam.gserviceaccount.com"
}
BUCKET_NAME = 'lcda'

# openAI api key
OPENAI_API_KEY = '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'  # invalid key

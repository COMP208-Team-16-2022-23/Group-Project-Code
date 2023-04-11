# File limitations
MAX_CONTENT_LENGTH = 3 * 1024 * 1024 # 3MB
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

# Configuration variables for the temp files
TEMP_PATH = 'temp_files'

# openAI
OPENAI_ENGINE = 'gpt-3.5-turbo'
OPENAI_MAX_TOKENS = 900

# Strings
LOGIN_REQUIRED = 'Please log in first'
NOTICE_TITLE = 'Kind tips:'
NOTICE_MESSAGE = 'Our platform is being developed and some content may change. We may delete user data for a better user experience, so back up important information regularly. Sorry for any inconvenience and thanks for your understanding. We hope you can enjoy using our platform.'
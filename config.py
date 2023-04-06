# Configuration variables for Google Cloud Storage
BUCKET_NAME = 'lcda'

# File limitations
MAX_CONTENT_LENGTH = 3 * 1024 * 1024 # 3MB
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

# Configuration variables for the temp files
TEMP_PATH = 'temp_files'

# product name
PRODUCT_NAME = 'LCDA'

# openAI
OPENAI_ENGINE = 'gpt-3.5-turbo'
OPENAI_MAX_TOKENS = 900

# Strings
LOGIN_REQUIRED = 'Please log in first'
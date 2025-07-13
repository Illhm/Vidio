import os

X_API_AUTH = os.getenv('X_API_AUTH')
if not X_API_AUTH:
    raise EnvironmentError('X_API_AUTH environment variable not set')

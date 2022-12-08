import os

SERVICE_ACCOUNT_NAME_FILE = 'service_account_ga4_nowon.json'
SERVICE_ACCOUNT_NAME_PATH = 'C:/Users/lucas/Desktop/NOWON/nowon/credentials'

def config_var_google():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_NAME_PATH+'/'+SERVICE_ACCOUNT_NAME_FILE

def config_var_flask():
    os.environ['SECRET_KEY_FLASK'] = '8f9b83f78edd2b5ba5568868dbd3133f'
    
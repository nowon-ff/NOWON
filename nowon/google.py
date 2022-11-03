import os

from Config_Inicial import config_var_google

config_var_google()

def teste():
    print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))


if __name__ == '__main__':
    teste()
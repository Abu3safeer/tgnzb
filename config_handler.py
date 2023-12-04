from configparser import ConfigParser
from pathlib import Path


class Config:
    uploads_folder = ''  # type: str
    db_address = ''  # type: str
    db_user = ''  # type: str
    db_pass = ''  # type: str

    def __init__(self):
        if not Path('config.ini').exists():
            print('file config.ini does not exists, creating new one!')
            new_config = ConfigParser()
            new_config.set('path', 'uploads_folder', 'uploads')
            new_config.set('db', 'db_address', 'localhost')
            new_config.set('db', 'db_user', 'root')
            new_config.set('db', 'db_pass', 'root')
            with open('config.ini', 'w', encoding='utf-8') as file:
                new_config.write(file)
                file.close()
        conf = ConfigParser()
        conf.read('config.ini')
        self.uploads_folder = conf.get('path', 'uploads_folder')
        self.db_address = conf.get('db', 'db_address')
        self.db_user = conf.get('db', 'db_user')
        self.db_pass = conf.get('db', 'db_pass')

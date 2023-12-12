from configparser import ConfigParser
from pathlib import Path


class Config:
    conf = ConfigParser  # type: ConfigParser

    defaults = (
        ('Uploads folder', 'uploads'),
        ('Json Folder', 'json'),
        ('Nzb folder', 'nzb'),
        ('Database Address', 'localhost'),
        ('Database User', 'root'),
        ('Database Password', 'root'),

    )

    def __init__(self):
        self.conf = ConfigParser()
        # If config file does not exist for some reason!
        if not Path('config.ini').exists():
            print('file config.ini does not exists, creating new one!')
            for key, value in self.defaults:
                self.set(key, value)
            self.update()

        # Get config values and load them to this object, if not present it will set it from defaults
        self.conf.read('config.ini')
        # Check if file exists but empty from all sections
        if not self.conf.has_section('app'):
            self.conf.add_section('app')

        for key, value in self.defaults:
            if not self.exists(key):
                print('the key ' + key + 'does not exists, and status is :' + self.exists(key).__str__())
                self.set(key, value)
            self.update()

    def exists(self, option):
        return self.conf.has_option('app', option)

    def set(self, option, value):
        return self.conf.set('app', option, value)

    def get(self, option):
        return self.conf.get('app', option)

    def update(self):
        with open('config.ini', 'w', encoding='utf-8') as file:
            self.conf.write(file)
            file.close()


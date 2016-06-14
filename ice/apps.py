from django.apps import AppConfig
from datetime import date
from data import Data


class IceConfig(AppConfig):
    name = 'ice'
    date = date.today()
    data = None

    def receive_data(self):
        print('Fetching data..')
        self.data = Data()
        print('Data received')

    def ready(self):
        if not self.data:
            self.receive_data()

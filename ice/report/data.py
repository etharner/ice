from html_parser import HTMLParser
import csv_parser
import prepare
from estimation import Estimation
import copy
import graph
import forecast
from django.apps import apps


class Data:
    seas = ['bering', 'chukchi', 'japan', 'okhotsk']

    def __init__(self):
        self.sea_data = {
            'source': {},
            'mean': {},
            'normal': {}
        }

        for sea in self.seas:
            self.sea_data['source'][sea] = self.parsed_data(sea)
            self.sea_data['mean'][sea] = self.mean_data(sea, copy.deepcopy(self.sea_data['source'][sea]))
            self.sea_data['normal'][sea] = self.normal_data(sea, copy.deepcopy(self.sea_data['mean'][sea]))

    def parsed_data(self, sea):
        return csv_parser.parse_data_csv(HTMLParser.parse_page()[sea])

    def mean_data(self, sea, parsed_data):
        mean_data = prepare.decade_average(parsed_data)
        filled_data = prepare.fill_missed(mean_data, sea)

        return filled_data

    def normal_data(self, sea, mean_data):
        return Estimation.normalize(mean_data, sea)

    def prep_data(self, sea):
        parsed_data = csv_parser.parse_data_csv(HTMLParser.parse_page()[sea])
        #self.print_data_to_file(parsed_data, 'parsed_' + sea + '.txt')

        mean_data = prepare.decade_average(parsed_data)
       # self.print_data_to_file(mean_data, 'mean_' + sea + '.txt')

        filled_data = prepare.fill_missed(mean_data, sea)
        #self.print_data_to_file(filled_data, 'filled_' + sea + '.txt')

        normalized_data = Estimation.normalize(filled_data, sea)
        #self.print_data_to_file(normalized_data, 'normalized_' + sea + '.txt')

        return normalized_data

    def data_processing(self, sea, year1, dec1, year2, dec2, prop):
        forecast_data = {}
        for year in range(year1, year2 + 1):
            start_dec = dec1 if year == year1 else 1
            end_dec = dec2 if year == year2 else 36
            forecast_decs = {}

            for dec in range(start_dec, end_dec + 1):
                cur_data = forecast.forecast(self.sea_data['mean'], prop, sea, dec, year, 10)

                month_dec = Estimation.get_month_dec(dec)
                if month_dec['month'] not in forecast_decs.keys():
                    forecast_decs[month_dec['month']] = {}
                forecast_decs[month_dec['month']][month_dec['dec']] = [cur_data[0], cur_data[1]]

            forecast_data[year] = forecast_decs

        print(forecast_data)
        return forecast_data

    def print_data_to_file(self, data, file_name):
        with open('processed/' + file_name, 'w') as f:
            for y in data.keys():
                for m in data[y].keys():
                    for d in data[y][m].keys():
                        f.write(str(y) + '/' + str(m) + '/' + str(d) + '\n' + str(data[y][m][d]) + '\n')

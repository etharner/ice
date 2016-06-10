from html_parser import HTMLParser
import csv_parser
import prepare
from estimation import Estimation
import graph
import forecast


class Data:
    seas = ['bering', 'chukchi', 'japan', 'okhotsk']

    def __init__(self):
        self._bering_data = {}
        self._chukchi_data = {}
        self._japan_data = {}
        self._okhotsk_data = {}

    def parsed_data(self, sea):
        return csv_parser.parse_data_csv(HTMLParser.parse_page()[sea])

    def mean_data(self, sea):
        parsed_data = self.parsed_data(sea)
        mean_data = prepare.decade_average(parsed_data)
        filled_data = prepare.fill_missed(mean_data, sea)

        return filled_data

    def normal_data(self, sea):
        mean_data = self.mean_data(sea)

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

    def data_processing(self):
        _bering_data = self.prep_data(self.seas[0])
        _chukchi_data = self.prep_data(self.seas[1])
        _japan_data = self.prep_data(self.seas[2])
        _okhotsk_data = self.prep_data(self.seas[3])

        sea_data = {
            'bering': self.mean_data(self.seas[0]),
            'chukchi': self.mean_data(self.seas[1]),
            'japan': self.mean_data(self.seas[2]),
            'okhotsk': self.mean_data(self.seas[3])
        }

        #print(forecast.forecast(sea_data, 'avg_conc', 'bering', 2, 2016, 10))


        #decs1 = range(1, 15 + 1)
        #decs2 = range(1, 15 + 1)
#
        #coeffs = Estimation.pirson_coeff(
        #    _bering_data, _chukchi_data, 'bering', 'chukchi', 2016, decs1, decs2, 'avg_conc'
        #)
        #graph.draw_correlation_field(coeffs, 'bering', 'chukchi', 2016, decs1, decs2, 'avg_conc')

        #coeffs = Estimation.pirson_coeff(
         #   _bering_data, _chukchi_data, 'bering', 'chukchi', 2011, decs1, decs2, 'avg_vol'
        #)
        #graph.draw_correlation_field(coeffs, 'bering', 'chukchi', 2011, decs1, decs2, 'avg_vol')


        #for i in range(len(decs1)):
         #   print(str(coeffs[i]))

    def print_data_to_file(self, data, file_name):
        with open('processed/' + file_name, 'w') as f:
            for y in data.keys():
                for m in data[y].keys():
                    for d in data[y][m].keys():
                        f.write(str(y) + '/' + str(m) + '/' + str(d) + '\n' + str(data[y][m][d]) + '\n')

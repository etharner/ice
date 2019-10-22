from ice.report.html_parser import HTMLParser
import ice.report.csv_parser as csv_parser
import ice.report.prepare as prepare
from ice.report.estimation import Estimation
import copy
import ice.report.graph as graph
from ice.report.forecast import Forecast
from django.apps import apps


class Data:
    seas = ['bering', 'chukchi', 'japan', 'okhotsk']

    def __init__(self):
        self.sea_data = {
            'source': {},
            'mean': {},
            'normal': {}
        }

        self.parsed_page = HTMLParser.parse_page()

        for sea in self.seas:
            print('Fetching ' + sea)
            self.sea_data['source'][sea] = self.parsed_data(sea)
            #self.load_to_csv('source')

            self.sea_data['mean'][sea] = self.mean_data(sea, copy.deepcopy(self.sea_data['source'][sea]))
            #self.load_to_csv('mean')

            self.sea_data['normal'][sea] = self.normal_data(sea, copy.deepcopy(self.sea_data['mean'][sea]))
            #self.load_to_csv('normal')

    def parsed_data(self, sea):
        return csv_parser.parse_data_csv(self.parsed_page[sea])

    def mean_data(self, sea, parsed_data):
        mean_data = prepare.decade_average(parsed_data)
        filled_data = prepare.fill_missed(mean_data, sea)

        return filled_data

    def normal_data(self, sea, mean_data):
        return Estimation.normalize(mean_data, sea)

    def load_to_csv(self, data_type):
        data = self.sea_data[data_type]

        for sea in data.keys():
            with open('ice/report/data/' + data_type + '/' + sea + '_' + data_type + '.csv', 'w') as fo:
                fo.write('date;area;conc;vol\n')
                for year in sorted(data[sea]):
                    for month in sorted(data[sea][year]):
                        for dec in sorted(data[sea][year][month]):
                            cur_data = data[sea][year][month][dec]
                            cur_date = str(year) + '-' + str(month) + '-' + str(dec) + ';'
                            cur_vals = str(cur_data['area' if data_type == 'source' else 'avg_area']) + ';' +\
                                       str(cur_data['conc' if data_type == 'source' else 'avg_conc']) + ';' +\
                                       str(cur_data['vol' if data_type == 'source' else 'avg_vol'])
                            fo.write(cur_date + cur_vals + '\n')

    def prep_data(self, sea):
        parsed_data = csv_parser.parse_data_csv(self.parsed_page[sea])
        #self.print_data_to_file(parsed_data, 'parsed_' + sea + '.txt')

        mean_data = prepare.decade_average(parsed_data)
       # self.print_data_to_file(mean_data, 'mean_' + sea + '.txt')

        filled_data = prepare.fill_missed(mean_data, sea)
        #self.print_data_to_file(filled_data, 'filled_' + sea + '.txt')

        normalized_data = Estimation.normalize(filled_data, sea)
        #self.print_data_to_file(normalized_data, 'normalized_' + sea + '.txt')

        return normalized_data

    def data_processing(self, sea, year1, dec1, year2, dec2, prop, prec):
        forecast_data = {}
        season_data = {}
        data = self.sea_data['mean']
        for cur_sea in data.keys():
            for cur_year in sorted(data[cur_sea]):
                if cur_year > 1996:
                    for cur_month in sorted(data[cur_sea][cur_year]):
                        for cur_dec in sorted(data[cur_sea][cur_year][cur_month]):
                            season_date = Estimation.get_season_date(cur_year, cur_month, cur_dec)
                            if cur_sea not in season_data.keys():
                                season_data[cur_sea] = {}
                            if season_date['year'] not in season_data[cur_sea].keys():
                                season_data[cur_sea][season_date['year']] = {}
                            if season_date['month'] not in season_data[cur_sea][season_date['year']].keys():
                                season_data[cur_sea][season_date['year']][season_date['month']] = {}
                            if season_date['dec'] not in season_data[cur_sea][season_date['year']][
                                season_date['month']].keys():
                                season_data[cur_sea][season_date['year']][season_date['month']][
                                    season_date['dec']] = \
                                    data[cur_sea][cur_year][cur_month][cur_dec]

        for year in range(year1, year2 + 1):
            start_dec = dec1 if year == year1 else 1
            end_dec = dec2 if year == year2 else 36
            forecast_decs = {}

            for dec in range(start_dec, end_dec + 1):
                month_dec = Estimation.get_month_dec(dec)
                season_date = Estimation.get_season_date(year, month_dec['month'], month_dec['dec'])
                season_date_glob_dec = Estimation.get_year_dec(season_date['month'], season_date['dec'])
                f = Forecast()
                cur_data = f.forecast(season_data, prop, sea, season_date_glob_dec, season_date['year'], prec)

                if season_date['year'] not in season_data[sea]:
                    season_data[sea][season_date['year']] = {}
                if season_date['month'] not in season_data[sea][season_date['year']]:
                    season_data[sea][season_date['year']][season_date['month']] = {}
                if season_date['dec'] not in season_data[sea][season_date['year']][season_date['month']]:
                    season_data[sea][season_date['year']][season_date['month']][season_date['dec']] = {prop: cur_data[0]}


                if month_dec['month'] not in forecast_decs.keys():
                    forecast_decs[month_dec['month']] = {}
                forecast_decs[month_dec['month']][month_dec['dec']] = [cur_data[0], cur_data[1]]

            forecast_data[year] = forecast_decs

        print(forecast_data)
        return forecast_data

def forecast_test(sea, year1, dec1, year2, dec2, prec):
    data = Data()
    old_data = copy.deepcopy(data.sea_data['mean'][sea])
    new_data = {}
    for year in data.sea_data['mean'][sea]:
        if int(year) < year1:
            new_data[year] = data.sea_data['mean'][sea][year]

    data.sea_data['mean'][sea] = new_data
    forecasted = data.data_processing(sea, year1, dec1, year2, dec2, 'avg_area', prec)

    test_num = dec2 - dec1 + 1
    succ_num = 0
    for month in forecasted[year1]:
        for dec in forecasted[year1][month]:
            cur_val = forecasted[year1][month][dec]
            if old_data[year1][month][dec]['avg_area'] >= cur_val[0] and old_data[year1][month][dec]['avg_area'] <= cur_val[1]:
                succ_num += 1

    print(str(year1) + ':' + '%.2f' % (succ_num / test_num * 100) + '%')
    return succ_num / test_num * 100


def test(sea, prec):
    perc_sum = 0
    for year in range(2000, 2015):
        perc_sum += forecast_test(sea, year, 1, year, 36, prec)

    print('GLOBAL ' + sea + ' prec: ' + str(prec) + ' => ' + '%.2f' % (perc_sum / 15) + '%')

#forecast_test('bering', 2012, 1, 2012, 36, 100)

#42.024
#test('bering', 10)
#57.59%
#test('chukchi', 10)
#32.78%
#test('japan', 10)
#42.78%
#test('okhotsk', 10)

#test('bering', 20)
#test('chukchi', 20)
#test('japan', 20)
#test('okhotsk', 20)

import csv
import codecs
from urllib.request import urlopen
import re
import prepare


def format_date(raw_date):
    formatted_date = {}
    formatted_date['year'] = int(raw_date.split('-')[0])
    formatted_date['month'] = int(raw_date.split('-')[1])
    formatted_date['day'] = int(raw_date.split('-')[2])

    return formatted_date


def parse_data(fname):
    data = {}

    csvfile = list(csv.reader(codecs.iterdecode(urlopen(fname), 'utf-8')))
    csvfile.pop(0)  # remove 'date;area;concentration;volume' string
    csvfile.pop(len(csvfile) - 1)  # remove empty string
    for row in csvfile:
        row_data = row[0].split(';')
        raw_date = re.match('(.*)T', row_data[0]).group(1)
        date = format_date(raw_date)

        prepare.append_to_data(data, date['year'], date['month'], date['day'], {})

        area = float(row_data[1])
        conc = 0.0
        vol = 0.0
        if len(row_data) > 2:
            conc = float(row_data[2])
            vol = float(row_data[3])

        data[date['year']][date['month']][date['day']]['conc'] = conc
        data[date['year']][date['month']][date['day']]['vol'] = vol
        data[date['year']][date['month']][date['day']]['area'] = area

    return data


def parse_data_csv(fnames):
    old_data = parse_data(fnames['old'])
    new_data = parse_data(fnames['new'])

    for year in new_data:
        for month in new_data[year]:
            for day in new_data[year][month]:
                try:
                    conc = old_data[year][month][day]['conc']
                    vol = old_data[year][month][day]['vol']
                    new_data[year][month][day]['conc'] = conc
                    new_data[year][month][day]['vol'] = vol
                except:
                    new_data[year][month][day]['conc'] = 0.0
                    new_data[year][month][day]['vol'] = 0.0
                prepare.append_to_data(old_data, year, month, day, new_data[year][month][day])

    return old_data

def parse_zeros_csv():
    data = {}

    with open('ice/report/zeros.csv') as file:
        csvfile =list(csv.reader(file))
        csvfile.pop(0)  # remove 'date;area;concentration;volume' string
        for row in csvfile:
            row_data = row[0].split(';')
            year = int(row_data[0].strip())
            sea = row_data[1].strip()
            start_dec = list(map(int, row_data[2].strip().split('/')))
            end_dec = list(map(int, row_data[3].strip().split('/')))

            if year not in data.keys():
                data[year] = {
                    sea: {
                        'start_dec': start_dec,
                        'end_dec': end_dec
                    }
                }
            elif sea not in data.keys():
                data[year][sea] = {
                    'start_dec': start_dec,
                    'end_dec': end_dec
                }
    return data
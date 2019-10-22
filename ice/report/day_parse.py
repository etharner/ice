import csv
import codecs
from urllib.request import urlopen
import re
import ice.data.estimation as est
import datetime
from datetime import date

def format_date(date):
    new_date = {}
    new_date['year'] = int(date.split('-')[0])
    new_date['month'] = int(date.split('-')[1])
    new_date['day'] = int(date.split('-')[2])

    return new_date

def parse_csv(fname):
    data = []

    csvfile = list(csv.reader(codecs.iterdecode(urlopen(fname), 'utf-8')))
    csvfile.pop(0) #remove 'date;area;concentration;volume' string
    csvfile.pop(len(csvfile) - 1) #remove empty string
    for row in csvfile:
        row_data = row[0].split(';')
        row_dict = {}
        raw_date = re.match('(.*)T', row_data[0]).group(1)
        row_dict['date'] = format_date(raw_date)
        row_dict['area'] = float(row_data[1])
        if len(row_data) > 2:
            row_dict['conc'] = float(row_data[2])
            row_dict['vol'] = float(row_data[3])
        if row_dict['area'] != 0.0 and row_dict['conc'] != 0.0 and row_dict['vol'] != 0.0:
            data.append(row_dict)
    return data

def prepare_neighbors(prev_day, prev_val, curr_day, curr_val):
    return [{
        'x': prev_day,
        'y': prev_val
        }, {
        'x': curr_day,
        'y': curr_val
        }
    ]

def fill_missed(data):
    restored_data = []

    prev_date = data[0]['date']
    prev_datetime = date(
        prev_date['year'], prev_date['month'], prev_date['day']
    )
    prev_vals = {
        'area': data[0]['area'],
        'conc': data[0]['conc'],
        'vol': data[0]['vol']
        }
    prev_missed = 1

    day_counter = 1

    for d in data:
        curr_date = d['date']
        curr_datetime = date(
            curr_date['year'], curr_date['month'], curr_date['day']
        )

        day_distance = (curr_datetime - prev_datetime).days

        for i in range(1, day_distance):
            new_datetime = prev_datetime + datetime.timedelta(days = 1)

            curr_restored_data = {
                'date': {
                    'year': new_datetime.year,
                    'month': new_datetime.month,
                    'day': new_datetime.day
                },
                'area': 0,
                'conc': 0,
                'vol': 0
                }

            for key in d.keys():
                if key != 'date' and key in prev_vals.keys():
                    neighbors = prepare_neighbors(
                        prev_missed, prev_vals[key], day_counter, d[key]
                    )
                    curr_restored_data[key] = Estimation.lin_interpolation(
                        neighbors, prev_missed + 1 / day_distance
                    )

            restored_data.append(curr_restored_data)

            prev_date = curr_restored_data['date']
            prev_datetime = new_datetime
            prev_vals = {
                'area': curr_restored_data['area'],
                'conc': curr_restored_data['conc'],
                'vol': curr_restored_data['vol']
                }
            prev_missed += 1 / day_distance

        restored_data.append(d)

        prev_date = curr_date
        prev_datetime = curr_datetime
        prev_vals = {
            'area': d['area'],
            'conc': d['conc'],
            'vol': d['vol']
            }
        prev_missed = day_counter
        day_counter += 1

    return restored_data

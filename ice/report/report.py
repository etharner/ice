# -*- coding: <utf-8> -*-

from pylatex import *
from pylatex.base_classes import *
from pylatex.utils import italic, bold
from django.apps import apps
import itertools
from estimation import Estimation as est
import graph
import re
import os
from subprocess import call

rome_num = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
months = {1: 'январе - марте ', 2: 'апреле - июне ', 3: 'июле - сентябре ', 4: 'октябре - декабре '}
num_months = {1: range(1, 4), 2: range(4, 7), 3: range(7, 10), 4: range(10, 13)}
quater_dec = {1: range(1, 7), 2: range(10, 16), 3: range(19, 25), 4: range(28, 34)}
rus_sea = {
    'bering': 'Беринг',
    'chukchi': 'Чукотск',
    'japan': 'Японск',
    'okhotsk': 'Охотск'
}
rus_months = {
    1: 'Января',
    2: 'Февраля',
    3: 'Марта',
    4: 'Апреля',
    5: 'Мая',
    6: 'Июня',
    7: 'Июля',
    8: 'Августа',
    9: 'Сентября',
    10: 'Октября',
    11: 'Ноября',
    12: 'Декабря'
}


def gen_data_table(doc, data, sea, lines, quater, year, prop):
    msg = ''
    if prop == 'source':
        msg = lines[14] + ' ' + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') + ' ' + lines[15] + '\n'
    if prop == 'mean':
        msg = lines[16] + ' ' + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') + ' ' + lines[17] + '\n'
    doc.append(msg)

    doc.append(Command('begin', arguments='center'))
    with doc.create(Tabular('|l|c|')) as table:
        table.add_hline()
        table.add_row(('Дата', 'Площадь льда, кв. км'))
        for cur_year in sorted(data[prop][sea]):
            if cur_year == year:
                for month in sorted(data[prop][sea][year]):
                    if month in num_months[quater]:
                        for dec in sorted(data[prop][sea][year][month]):
                            cur_data = data[prop][sea][year][month][dec]
                            cur_date = str(year) + '-' + str(month) + '-' + str(dec)
                            cur_vals = str(cur_data['area' if prop == 'source' else 'avg_area'])
                            table.add_hline(1, 2)
                            table.add_row((cur_date, cur_vals))
        table.add_hline(1, 2)
    doc.append(Command('end', arguments='center'))


def gen_corr_grid(doc, lines, seas_corr, sea):
    msg = lines[18] + ' ' + rus_sea[sea] + ('овом' if sea == 'bering' else 'ом') + ' ' + lines[19]
    doc.append(msg)

    doc.append(Command('begin', arguments='center'))
    for sea_pair in seas_corr:
        if sea_pair[0] == sea:
            if sea_pair[1] != sea:
                with doc.create(Figure(position='H')) as corr_pic:
                    corr_pic.add_image(seas_corr[sea_pair], width='400px')
    doc.append(Command('end', arguments='center'))


def gen_data_plot(doc, data, seas_data, sea, year, lines, quater, method):
    msg = lines[20] + ' ' + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') + ' ' + lines[21] + ' ' +\
    '1998-' + str(year) + ' ' + lines[22]
    doc.append(msg)

    fname = seas_data[sea][method]

    with doc.create(Figure(position='H')) as data_pic:
        data_pic.add_image(fname, width='400px')

    max_this_year = est.find_max_year_val(data[method][sea], year, ('area' if method == 'source' else 'avg_area'))
    max_prev_year = est.find_max_year_val(data[method][sea], year - 1, ('area' if method == 'source' else 'avg_area'))
    try:
        perc = max_this_year['max_val'] / max_prev_year['max_val']
    except:
        perc = 0.0

    perc *= 100

    comp_msg = lines[23] + ' ' + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') + ' ' + lines[24] + ' ' +\
               str(year) + lines[25] + ' ' + str(max_this_year['max_dec_day']) + ' ' + (lines[27] if method == 'source' else
               lines[26]) + ' ' + rus_months[max_this_year['max_month']] + ' ' + lines[28] + ' ' + str(max_this_year['max_val']) +\
               ' ' + lines[29] + ' ' + str("{0:.2f}".format(abs(100.0 - perc))) + (lines[30] if perc > 100.0 else lines[31]) + ' ' + lines[32]
    doc.append(comp_msg)


def gen_forecast_table(doc, data, sea, lines, quater, year, prop):
    msg = lines[33] + ' ' + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') + ' ' + lines[34] + ' ' + \
          str(quater_dec[quater][0]) + ' ' + lines[35] + ' ' + str(quater_dec[quater][-1]) + ' ' + lines[36] + ' ' +\
          str(year) + ' ' + lines[37]
    doc.append(msg)

    forecasted = apps.get_app_config('ice').data.data_processing(sea, year, quater_dec[quater][0], year, quater_dec[quater][-1], prop)

    doc.append(Command('begin', arguments='center'))
    with doc.create(Tabular('|l|c|')) as table:
        table.add_hline()
        table.add_row(('Дата', 'Площадь льда, кв. км (от - до)'))
        for month in sorted(forecasted[year]):
            for dec in sorted(forecasted[year][month]):
                cur_data = forecasted[year][month][dec]
                cur_date = str(year) + '-' + str(month) + '-' + str(dec)
                cur_vals = str(cur_data[0]) + ' - ' + str(cur_data[1])
                table.add_hline(1, 2)
                table.add_row((cur_date, cur_vals))
        table.add_hline(1, 2)
    doc.append(Command('end', arguments='center'))


def get_report(quater, year, checked):
    doc = Document(documentclass=Command('documentclass',
               options=Options('12pt', 'a4paper'),
               arguments='article'), lmodern=False)

    doc.packages.append(Package('babel', options=['russian']))
    doc.packages.append(Package('geometry', options=[
        'left=3cm', 'right=1cm', 'top=1cm', 'bottom=1cm'
    ]))
    doc.packages.append(Package('float'))

    lines = []
    with open('ice/report/report_phrase', encoding='utf8') as f:
        for line in f:
            lines.append(line.strip())

    data = apps.get_app_config('ice').data.sea_data

    seas_data = {}
    for sea in data['normal'].keys():
        norm_name = graph.draw_data(data['source'][sea], num_months[quater], range(1998, year + 1), sea, 'source', 'area')
        mean_name = graph.draw_data(data['mean'][sea], num_months[quater], range(1998, year + 1), sea, 'mean', 'avg_area')
        seas_data[sea] = {
            'source': norm_name,
            'mean': mean_name
        }

    sea_pairs = []
    for pair in itertools.product(data['normal'].keys(), repeat=2):
        sea_pairs.append(pair)

    seas_corr = {}
    for pair in sea_pairs:
        coeffs = est.pirson_coeff(
            data['normal'][pair[1]], data['normal'][pair[0]], pair[1], pair[0], year, quater_dec[quater],
            quater_dec[quater], 'avg_area'
        )
        fname = graph.draw_correlation_field(coeffs, pair[0], pair[1], year, quater_dec[quater],
                                                     quater_dec[quater], 'avg_area', '.png')
        seas_corr[pair] = re.sub(r'(.+)/correlation/(.+)', r'../../correlation/\2', fname)

    with doc.create(Section(bold(lines[0] + ' ' + rome_num[quater] + ' ' + lines[1] + ' ' + str(year) + lines[2]), numbering=False)):
        intro = lines[3] + ' ' + rome_num[quater] + ' ' + lines[4] + ' ' + str(year) + ' ' + lines[5] + ' ' + lines[6]
        purp = lines[8] + ' ' + months[quater] + str(year) + lines[9] + ' ' + lines[10] + '\n'
        task = lines[12] + ' ' + months[quater] + str(year) + lines[13] + '\n'

        with doc.create(Subsection(bold(intro), numbering=False)):
            doc.append(italic(lines[7]))
            doc.append(purp)
            doc.append(italic(lines[11]))
            doc.append(task)
            doc.append(Command('\\'))

            for sea in ['bering', 'chukchi', 'japan', 'okhotsk']:
                if checked[sea]['source']:
                    gen_data_table(doc, data, sea, lines, quater, year, 'source')
                    gen_data_plot(doc, data, seas_data, sea, year, lines, quater, 'source')
                if checked[sea]['mean']:
                    gen_data_table(doc, data, sea, lines, quater, year, 'mean')
                    gen_data_plot(doc, data, seas_data, sea, year, lines, quater, 'mean')
                if checked[sea]['corr']:
                    gen_corr_grid(doc, lines, seas_corr, sea)
                if checked[sea]['forecast']:
                    gen_forecast_table(doc, data, sea, lines, quater, year, 'avg_area')

    doc.generate_tex('ice/report/report/tex/ice-' + str(year) + '-' + str(quater))
    doc.generate_pdf('ice/report/report/pdf/ice-' + str(year) + '-' + str(quater))

    return 'ice-' + str(year) + '-' + str(quater)

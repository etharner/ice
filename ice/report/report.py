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
quater_dec = {1: range(1, 10), 2: range(10, 19), 3: range(19, 28), 4: range(28, 37)}
rus_sea = {
    'bering': 'Беринг',
    'chukchi': 'Чукотск',
    'japan': 'Японск',
    'okhotsk': 'Охотск'
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
                if checked[sea]['mean']:
                    gen_data_table(doc, data, sea, lines, quater, year, 'mean')
                if checked[sea]['corr']:
                    gen_corr_grid(doc, lines, seas_corr, sea)

    doc.generate_tex('ice/report/report/tex/ice-' + str(year) + '-' + str(quater))
    doc.generate_pdf('ice/report/report/pdf/ice-' + str(year) + '-' + str(quater))

    return 'ice-' + str(year) + '-' + str(quater)

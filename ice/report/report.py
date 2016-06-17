# -*- coding: <utf-8> -*-

from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Package, Matrix
from pylatex.utils import italic, bold
from django.apps import apps
import itertools
from estimation import Estimation as est
import graph
import re
import os
from subprocess import call

def get_report(quater, year, checked):
    doc = Document()

    doc.packages.append(Package('inputenc', options=['utf8']))
    doc.packages.append(Package('babel', options=['russian']))
    doc.packages.append(Package('geometry', options=[
        'left=3cm', 'right=2cm', 'top=2.5cm', 'bottom=2cm'
    ]))
    doc.packages.append(Package('graphicx'))

    rome_num = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
    months = {1: 'январе - марте ', 2: 'апреле - июне ', 3: 'июле - сентябре ', 4: 'октябре - декабре '}
    num_months = {1: range(1, 4), 2: range(4, 7), 3: range(7, 10), 4: range(10, 13)}
    quater_dec = {1: range(1, 10), 2: range(10, 19), 3: range(19, 28), 4: range(28, 37)}

    with doc.create(Section(bold('ОТЧЕТ за ' + rome_num[quater] + ' кв. ' + str(year) + 'г. лаборатории прикладной математики'
        ' по ледовой обстановке.'), numbering=False)):

        with open('ice/report/report_phrase') as f:
            lines = f.readlines()

        intro = lines[0] + rome_num[quater] + lines[1] + str(year) + lines[2] + lines[3]
        purp = lines[4] + lines[5] + months[quater] + str(year) + lines[6] + lines[8]
        task = lines[9] + lines[10] + months[quater] + str(year) + lines[11] + lines[12] + lines[13]

        with doc.create(Subsection(bold(intro), numbering=False)):
            doc.append(italic(lines[14]))
            doc.append(purp)
            doc.append(italic(lines[15]))
            doc.append(task)

        data = apps.get_app_config('ice').data.sea_data
        rus_sea = {
            'bering': 'Беринг',
            'chukchi': 'Чукотск',
            'japan': 'Японск',
            'okhotsk': 'Охотск'
        }

        for sea in ['bering', 'chukchi', 'japan', 'okhotsk']:
            if checked[sea]['source']:
                msg = lines[16] + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') + lines[17]
                doc.append(msg)
                with doc.create(Tabular('|l|c|')) as table:
                    table.add_hline()
                    table.add_row(('Дата', 'Площадь льда, кв. км'))
                    for cur_year in sorted(data['source'][sea]):
                        if cur_year == year:
                            for month in sorted(data['source'][sea][year]):
                                if month in num_months[quater]:
                                    for dec in sorted(data['source'][sea][year][month]):
                                        cur_data = data['source'][sea][year][month][dec]
                                        cur_date = str(year) + '-' + str(month) + '-' + str(dec)
                                        cur_vals = str(cur_data['area'])
                                        table.add_hline(1, 2)
                                        table.add_row((cur_date, cur_vals))
                    table.add_hline(1, 2)
                doc.append('\n\n')

            if checked[sea]['mean']:
                msg = lines[18] + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') + lines[19]
                doc.append(msg)
                with doc.create(Tabular('|l|c|')) as table:
                    table.add_hline()
                    table.add_row(('Дата', 'Площадь льда, кв. км'))
                    for cur_year in sorted(data['mean'][sea]):
                        if cur_year == year:
                            for month in sorted(data['mean'][sea][year]):
                                if month in num_months[quater]:
                                    for dec in sorted(data['mean'][sea][year][month]):
                                        cur_data = data['mean'][sea][year][month][dec]
                                        cur_date = str(year) + '-' + str(month) + '-' + str(dec)
                                        cur_vals = str(cur_data['avg_area'])
                                        table.add_hline(1, 2)
                                        table.add_row((cur_date, cur_vals))
                    table.add_hline(1, 2)
                doc.append('\n\n')

            if checked[sea]['corr']:
                msg = lines[20] + rus_sea[sea] + ('овом' if sea == 'bering' else 'ом') + lines[21]
                doc.append(msg)

                sea_pairs = []
                for pair in itertools.product(data['normal'].keys(), repeat=2):
                    sea_pairs.append(pair)

                for pair in sea_pairs:
                    if pair[0] == sea:
                        coeffs = est.pirson_coeff(
                            data['normal'][pair[1]], data['normal'][pair[0]], pair[1], pair[0], year, quater_dec[quater],
                            quater_dec[quater], 'avg_area'
                        )
                        fname = graph.draw_correlation_field_png(coeffs, pair[0], pair[1], year, quater_dec[quater],
                                                             quater_dec[quater], 'avg_area')

                        with doc.create(Figure(position='h')) as corr_pic:
                            corr_pic.add_image(re.sub(r'(.+)/correlation/(.+)', r'../correlation/\2', fname),
                                                        width='300px')


    doc.generate_tex('ice/report/report/ice-' + str(year) + '-' + str(quater))
    doc.generate_pdf('ice/report/report/ice-' + str(year) + '-' + str(quater))

    return 'ice-' + str(year) + '-' + str(quater)
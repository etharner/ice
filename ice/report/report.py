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

        #test
        intro = 'Информация об общей площади льда и прогнозируемых значениях в Японском, '
        'Охотском, Беринговом и Чукотском морях за ' + rome_num[quater] + ' кв. ' + str(year) + 'г.,'
        ' полученных в результате обработки данных Национального ледового центра.'
        purp = 'мониторинг состояния ледовой обстановки в Японском море, Охотском море, '
        'Беринговом и Чукотском морях в ' + months[quater] + str(year) + 'г.' + ' и прогнозирование ледовой обстановки\n'
        task = 'обработка и анализ данных о состоянии ледовой обстановки в Японском море, Охотском море, '
        'Беринговом и Чукотском морях в ' + months[quater] + str(year) + 'г.' + ' и'
        ' прогнозирование будущих значений\n'

        with doc.create(Subsection(bold(intro.encode('utf-8')), numbering=False)):
            doc.append(italic('Цель: '.encode('utf-8')))
            doc.append(purp.encode('utf-8'))
            doc.append(italic('Задачи: '.encode('utf-8')))
            doc.append(task.encode('utf-8'))

        data = apps.get_app_config('ice').data.sea_data
        rus_sea = {
            'bering': 'Беринг',
            'chukchi': 'Чукотск',
            'japan': 'Японск',
            'okhotsk': 'Охотск'
        }

        for sea in ['bering', 'chukchi', 'japan', 'okhotsk']:
            if checked[sea]['source']:
                msg = 'Была расчитана площадь ' + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') +\
                ' моря в каждой декаде\n'
                doc.append(msg.encode('utf-8'))
                with doc.create(Tabular('|l|c|')) as table:
                    table.add_hline()
                    table.add_row(('Дата'.encode('utf-8'), 'Площадь льда, кв. км'.encode('utf-8')))
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
                msg = 'Была расчитана средняя площадь ' + rus_sea[sea] + ('ова' if sea == 'bering' else 'ого') +\
                ' моря в каждой декаде\n'
                doc.append(msg.encode('utf-8'))
                with doc.create(Tabular('|l|c|')) as table:
                    table.add_hline()
                    table.add_row(('Дата'.encode('utf-8'), 'Площадь льда, кв. км'.encode('utf-8')))
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
                msg = 'Для анализа зависимостей развития ледовой обстановки в ' +\
                rus_sea[sea] + ('овом' if sea == 'bering' else 'ом') + ' море были вычислены декадные ' +\
                'корреляции попарно с остальными бассейнами'
                doc.append(msg.encode('utf-8'))

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
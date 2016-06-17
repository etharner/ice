from django.shortcuts import render
from django.apps import apps
import json
import datetime
import re
import zipfile
from os.path import basename
from ice.report.estimation import Estimation
from django.shortcuts import HttpResponse
import graph
import report as r


def prepare_response_data(method, sea_name):
    app_data = apps.get_app_config('ice')
    if datetime.datetime.today().date() > app_data.date:
        app_data.receive_data()

    data = app_data.data.sea_data

    return data[method][sea_name]


def proceed_response(request, method, cols_loc, cols):
    if request.method == "GET":
        sea_name = request.GET.get('sea_name')
        if sea_name is None:
            sea_name = 'bering'

        if request.is_ajax():
            return HttpResponse(json.dumps(
                {'data': prepare_response_data(method, sea_name)}),
                content_type="application/json"
            )

    data_types = {
        'source': 'Исходные данные',
        'mean': 'Усредненные данные',
        'normal': 'Нормализованные данные'
    }

    return render(request, 'ice/data.html', {
        'data_type': method,
        'data_type_tr': data_types[method],
        'cols_loc': cols_loc,
        'cols': cols
    })


def sources(request):
    return proceed_response(
        request,
        'source',
        json.dumps(['Год-Месяц-День', 'Площадь', 'Площадь с учетом сплоченности', 'Объем']),
        json.dumps(['area', 'conc', 'vol'])
    )


def mean(request):
    return proceed_response(
        request,
        'mean',
        json.dumps(['Год-Месяц-Декада', 'Средняя площадь', 'Средняя площадь с учетом сплоченности', 'Средний объем']),
        json.dumps(['avg_area', 'avg_conc', 'avg_vol'])
    )


def normal(request):
    return proceed_response(
        request,
        'normal',
        json.dumps(['Год-Месяц-Декада', 'Площадь', 'Площадь с учетом сплоченности', 'Объем']),
        json.dumps(['avg_area', 'avg_conc', 'avg_vol'])
    )


rus_seas = {
    'Берингово море': 'bering',
    'Чукотское море': 'chukchi',
    'Охотское море': 'okhotsk',
    'Японское море': 'japan'
}
rus_prop = {
    'Площадь': 'avg_area',
    'Площадь с учетом сплоченности': 'avg_conc',
    'Объем': 'avg_vol',
}


def correlation(request):
    if request.method == 'GET':
        if request.GET.get('action') == 'corr':
            sea1 = rus_seas[request.GET.get('sea1')]
            sea2 = rus_seas[request.GET.get('sea2')]
            year = int(request.GET.get('year'))
            dec1 = int(request.GET.get('dec1'))
            dec2 = int(request.GET.get('dec2'))
            prop = rus_prop[request.GET.get('prop')]

            sea1_data = prepare_response_data('normal', sea1)
            sea2_data = prepare_response_data('normal', sea2)

            try:
                coeffs = Estimation.pirson_coeff(
                    sea1_data, sea2_data, sea1, sea2, year, range(dec1, dec2 + 1), range(dec1, dec2 + 1), prop
                )
            except:
                coeffs = [[0 for j in range(len(range(dec1, dec2 + 1)))] for i in range(len(range(dec1, dec2 + 1)))]
            fname = graph.draw_correlation_field(coeffs, sea1, sea2, year, range(dec1, dec2 + 1), range(dec1, dec2 + 1), prop)

            real_name = re.sub(r'.+/img/(.+)\.svg', r'\1', fname)
            real_img = re.sub(r'(.+)/correlation/(.+)\.svg', r'\1/report/correlation/\2.svg', fname)
            real_csv = re.sub(r'(.+)/correlation/img/(.+)\.svg', r'\1/report/correlation/data/\2.csv', fname)

            download_csv = re.sub(r'(.+)/img/(.+)\.svg', r'\1/data/\2.csv', fname)
            with open(real_csv, 'w') as fo:
                fo.write('dec;')
                for i in range(len(range(dec1, dec2 + 1))):
                    fo.write(str(i) + ';')
                fo.write('\n')
                for i in range(len(range(dec1, dec2 + 1))):
                    fo.write(str(i) + ';')
                    for j in range(len(range(dec1, dec2 + 1))):
                        fo.write(str(coeffs[i][j]) + ';')
                    fo.write('\n')

            zip = zipfile.ZipFile('ice/report/correlation/zip/' + real_name + '.zip', 'w')
            zip.write(real_img, basename(real_img))
            zip.write(real_csv, basename(real_csv))
            zip.close()
            download_zip = 'ice/correlation/zip/' + real_name + '.zip'

            return HttpResponse(json.dumps({
                'coeffs': coeffs,
                'imgfile': fname,
                'csvfile': download_csv,
                'zipfile': download_zip,
                'decrange': list(range(dec1, dec2 + 1))
            }), content_type="application/json")

    return render(
        request,
        'ice/correlation.html',
        {
            'data_type': 'Коэффициенты корреляции между парой морей',
            'years': range(2000, datetime.date.today().year + 1),
            'decs': range(1, 37)
        }
    )


def forecast(request):
    if request.method == 'GET':
        if request.GET.get('action') == 'forecast':
            sea = rus_seas[request.GET.get('sea')]
            year1 = int(request.GET.get('year1'))
            dec1 = int(request.GET.get('dec1'))
            year2 = int(request.GET.get('year2'))
            dec2 = int(request.GET.get('dec2'))
            prop = rus_prop[request.GET.get('prop')]

            data = apps.get_app_config('ice').data.data_processing(sea, year1, dec1, year2, dec2, prop)

            real_name = 'ice/report/forecast/fcst_' + sea + '_' + str(year1) + '_' + str(dec1) + '-' +\
                str(year2) + '_' + str(dec2) + '_' + prop + '.csv'
            with open(real_name, 'w') as fo:
                fo.write('date;val\n')
                for year in sorted(data):
                    for month in sorted(data[year]):
                        for dec in sorted(data[year][month]):
                            cur_data = data[year][month][dec]
                            cur_date = str(year) + '-' + str(month) + '-' + str(dec) + ';'
                            cur_vals = str(cur_data[0]) + '-' + str(cur_data[1])
                            fo.write(cur_date + cur_vals + '\n')
            download_name = 'ice/forecast/' + re.sub(r'.+forecast/(.+)', r'\1', real_name)

            return HttpResponse(json.dumps({
                'data': data,
                'csvfile': download_name
            }), content_type="application/json")

    return render(
        request,
        'ice/forecast.html',
        {
            'data_type': 'Прогнозирование ледовой обстановки',
            'start_years': range(2000, datetime.date.today().year + 1),
            'end_years': range(2000, 2021),
            'decs': range(1, 37)
        }
    )


def report(request):
    if request.method == 'GET':
        if request.GET.get('action') == 'report':
            rome_num = {'I': 1, 'II': 2, 'III': 3, 'IV': 4}
            quater = rome_num[request.GET.get('quater')]
            year = int(request.GET.get('year'))

            checked = {}
            for sea in ['bering', 'chukchi', 'japan', 'okhotsk']:
                if sea not in checked.keys():
                    checked[sea] = {}
                for prop in ['source', 'mean', 'corr', 'forecast']:
                    checked[sea][prop] = request.GET.get('checked[' + sea + '][' + prop + ']')

            fname = r.get_report(quater, year, checked)
            return HttpResponse(json.dumps({
                'pdf': 'ice/report/' + fname + '.pdf',
                'tex': 'ice/report/' + fname + '.tex'
            }), content_type="application/json")

    return render(
        request,
        'ice/report.html',
        {
            'years': range(2000, datetime.date.today().year + 1),
            'seas': {
                'bering': 'Берингово море',
                'chukchi': 'Чукотское море',
                'japan': 'Японское море',
                'okhotsk': 'Охотское море'}
        }
    )


def get_data_src(request, sea, data_type):
    file = open('ice/report/data/' + data_type + '/' + sea + '_' + data_type + '.csv', 'r')

    return HttpResponse(content=file, content_type='application/octet-stream')


def get_corr_img(request):
    file = open('ice/report/correlation/img/' + request.path.split('/')[-1], 'rb')

    return HttpResponse(content=file)


def get_corr_src(request):
    file = open('ice/report/correlation/data/' + request.path.split('/')[-1], 'rb')

    return HttpResponse(content=file, content_type='application/octet-stream')


def get_corr_zip(request):
    file = open('ice/report/correlation/zip/' + request.path.split('/')[-1], 'rb')

    return HttpResponse(content=file, content_type='application/octet-stream')


def get_forecast(request):
    file = open('ice/report/forecast/' + request.path.split('/')[-1], 'rb')

    return HttpResponse(content=file, content_type='application/octet-stream')


def get_pdf_tex(request):
    file = open('ice/report/report/' + request.path.split('/')[-1], 'rb')

    return HttpResponse(content=file, content_type='application/octet-stream')


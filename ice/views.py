from django.shortcuts import render
from django.apps import apps
import json
import datetime
from ice.report.data import Data
from ice.report.estimation import Estimation
from django.shortcuts import HttpResponse
import graph


def prepare_response_data(method, sea_name):
    app_data = apps.get_app_config('ice')
    if datetime.datetime.today().date() > app_data.date:
        app_data.receive_data()

    data = app_data.data.sea_data

    return data.sea_data[method][sea_name]


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
        'data_type': data_types[method],
        'cols_loc': cols_loc,
        'cols': cols
    })


def sources(request):
    return proceed_response(
        request,
        "source",
        json.dumps(['Год-Месяц-День', 'Площадь', 'Площадь с учетом сплоченности', 'Объем']),
        json.dumps(['area', 'conc', 'vol'])
    )


def mean(request):
    return proceed_response(
        request,
        "mean",
        json.dumps(['Год-Месяц-Декада', 'Средняя площадь', 'Средняя площадь с учетом сплоченности', 'Средний объем']),
        json.dumps(['avg_area', 'avg_conc', 'avg_vol'])
    )


def normal(request):
    return proceed_response(
        request,
        "normal",
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

            return HttpResponse(json.dumps({
                'coeffs': coeffs,
                'imgfile': fname,
                'decrange': list(range(dec1, dec2 + 1))
            }), content_type="application/json")

    return render(
        request,
        'ice/correlation.html',
        {
            'data_type': 'Коэффициенты корреляции между парой морей',
            'years': range(1997, datetime.date.today().year + 1),
            'decs': range(1, 37)
        }
    )


def get_src(request):
    file = open('ice/report/correlation/' + request.path.split('/')[-1], 'rb')

    return HttpResponse(content=file)


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
            return HttpResponse(json.dumps({
                'data': data,
            }), content_type="application/json")

    return render(
        request,
        'ice/forecast.html',
        {
            'data_type': 'Прогнозирование ледовой обстановки',
            'start_years': range(1997, datetime.date.today().year + 1),
            'end_years': range(1997, 2021),
            'decs': range(1, 37)
        }
    )
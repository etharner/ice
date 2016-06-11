from django.shortcuts import render
import json
import datetime
from ice.report.data import Data
from ice.report.estimation import Estimation
from django.shortcuts import HttpResponse
import graph


def prepare_response_data(method, sea_name):
    data = Data()

    if method == "source":
        return data.parsed_data(sea_name)
    if method == "mean":
        return data.mean_data(sea_name)
    if method == "normal":
        return data.normal_data(sea_name)


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


def correlation(request):
    if request.method == 'GET':
        if request.GET.get('action') == 'corr':
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

            sea1 = rus_seas[request.GET.get('sea1')]
            sea2 = rus_seas[request.GET.get('sea2')]
            year = int(request.GET.get('year'))
            dec1 = int(request.GET.get('dec1'))
            dec2 = int(request.GET.get('dec2'))
            prop = rus_prop[request.GET.get('prop')]

            data = Data()
            sea1_data = data.prep_data(sea1)
            sea2_data = data.prep_data(sea2)

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
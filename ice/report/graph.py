import matplotlib
#matplotlib.use('SVG')
from matplotlib.pylab import *
from matplotlib import rc
import matplotlib.font_manager as fm
import datetime
from estimation import Estimation

def create_title(sea1, sea2, decs, field_name):
    rus_seas = {
        'bering': 'Берингова',
        'chukchi': 'Чукотского',
        'okhotsk': 'Охотского',
        'japan': 'Японского'
    }
    rus_fields = {
        'avg_area': 'площадью',
        'avg_conc': 'площадью c учетом сплоченности',
        'avg_vol': 'объемом'
    }

    return 'Поле корреляции между ' + rus_fields[field_name] + ' льда\n' + \
        rus_seas[sea1] + ' и ' + rus_seas[sea2] + ' морей\n' + \
        'в ' + str(decs[0]) + '-' + str(decs[-1]) + ' декадах'


def gen_fname(sea1, sea2, last_year, decs, field_name):
    short_seas = {
        'bering': 'ber',
        'chukchi': 'chu',
        'okhotsk': 'okh',
        'japan': 'jap'
    }

    short_fields = {
        'avg_area': 'area',
        'avg_conc': 'conc',
        'avg_vol': 'vol'
    }

    return short_seas[sea1] + '_' + short_seas[sea2] + '_' + str(last_year) + '_' + str(decs[0]) + '-' + str(decs[-1]) + \
        '_' + short_fields[field_name]


def draw_correlation_field(coeffs, sea1, sea2, last_year, decs1, decs2, field_name, ext):
    plt.figure()
    plt.hot()

    im = plt.imshow(coeffs, interpolation='bilinear',
                    origin='lower', cmap=cm.rainbow,
                    extent=(decs1[0], decs1[-1], decs2[0], decs2[-1]))

    levels = np.arange(-1.0, 1.0, 0.1)
    CS = plt.contour(coeffs, levels,
                     colors='black',
                     origin='lower',
                     linewidths=1,
                     extent=(decs1[0], decs1[-1], decs2[0], decs2[-1]))
    plt.clabel(CS, inline=1,
               fontsize=10,
              )
    CB = plt.colorbar(im, shrink=0.2,
                      extend='neither')

    l, b, w, h = plt.gca().get_position().bounds
    ll, bb, ww, hh = CB.ax.get_position().bounds
    CB.ax.set_position([ll, b + 0.1 * h, ww, h * 0.8])

    rus_seas = {
        'bering': 'Берингово море',
        'chukchi': 'Чукотское море',
        'okhotsk': 'Охотское море',
        'japan': 'Японское море'
    }

    fontprop = fm.FontProperties(fname="ice/report/DejaVuSans.ttf")
    plt.xlabel(rus_seas[sea1], fontproperties=fontprop)
    plt.ylabel(rus_seas[sea2], fontproperties=fontprop)

    plt.title(create_title(sea1, sea2, decs1, field_name), fontproperties=fontprop)
    savefig('ice/report/correlation/img/' + gen_fname(sea1, sea2, last_year, decs1, field_name) + ext, bbox_inches='tight')
    #plt.show()

    return 'ice/correlation/img/' + gen_fname(sea1, sea2, last_year, decs1, field_name) + ext


def draw_data(data, sea, method, prop):
    x = {}
    y = {}

    for year in sorted(data):
        x[year] = []
        y[year] = []
        for month in sorted(data[year]):
            for dec_day in sorted(data[year][month]):
                if method == 'source':
                    now = datetime.datetime.strptime(str(year) + '-' + str(month) + '-' + str(dec_day),'%Y-%m-%d')
                    day_dec_of_year = (now - datetime.datetime(year, 1, 1)).days + 1
                else:
                    day_dec_of_year = Estimation.get_year_dec(month, dec_day)

                print(day_dec_of_year)
                cur_data = data[year][month][dec_day][prop]
                x[year].append(day_dec_of_year)
                y[year].append(cur_data)

    for year in sorted(data):
        if year < sorted(data)[-1]:
            plt_color = '0.75'
            plt_width = 5.0
        else:
            plt_color = 'r'
            plt_width = 2.0

        params = plt.plot(x[year], y[year])
        plt.setp(params, color=plt_color, linewidth=plt_width)

    #plt.plot(*params)

    fontprop = fm.FontProperties(fname="ice/report/DejaVuSans.ttf")

    plt.xlabel('Дата', fontproperties=fontprop)
    plt.ylabel('Значение', fontproperties=fontprop)

    rus_seas = {
        'bering': 'Берингова моря',
        'chukchi': 'Чукотского моря',
        'okhotsk': 'Охотского моря',
        'japan': 'Японского моря'
    }
    rus_fields = {
        'area': 'площадь',
        'avg_area': 'площадь',
        'conc': 'площадь c учетом сплоченности',
        'avg_conc': 'площадь c учетом сплоченности',
        'vol': 'объем',
        'avg_vol': 'объем'
    }
    rus_method = {
        'source': 'Исходн',
        'mean': 'Усредненн'
    }


    plt.title(rus_method[method] + ('ый' if prop == 'vol' or prop == 'avg_vol' else 'ая') + ' ' +
        rus_fields[prop] + ' ' + rus_seas[sea] + ' в ' + str(1997) + '-' + str(sorted(data)[-1]) + ' годах',
        fontproperties = fontprop)
    plt.grid(True)
    plt.show()

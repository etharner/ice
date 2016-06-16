import matplotlib
matplotlib.use('SVG')
from matplotlib.pylab import *
from matplotlib import rc
import matplotlib.font_manager as fm


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


def draw_correlation_field(coeffs, sea1, sea2, last_year, decs1, decs2, field_name):
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
    savefig('ice/report/correlation/img/' + gen_fname(sea1, sea2, last_year, decs1, field_name), bbox_inches='tight')
    #plt.show()

    return 'ice/correlation/img/' + gen_fname(sea1, sea2, last_year, decs1, field_name) + '.svg'

import ice.report.csv_parser as csv_parser
from ice.report.estimation import Estimation as est

def append_to_data(data, year, month, day_or_dec, dict):
    if year not in data.keys():
        data[year] = { month: { day_or_dec: dict } }
    elif month not in data[year].keys():
        data[year][month] = { day_or_dec: dict }
    else:
        data[year][month][day_or_dec] = dict

def init_prev(data):
    prev = {
        'date': {
            'year': 0,  # no need to init year
            'month': 0,  # no need to init month
            'dec': est.get_first_day_or_dec(data)
        },
        'avg_area': 0,
        'avg_conc': 0,
        'avg_vol': 0
    }

    return prev

def change_prev(init, prev, d, year, month, dec):
    prev['date'] = {
        'year': year,
        'month': month,
        'dec': dec
    }
    prev['area_sum'] += d['area'] if not init else -prev['area_sum'] + d['area']
    prev['conc_sum'] += d['conc'] if not init else -prev['conc_sum'] + d['conc']
    prev['vol_sum'] += d['vol'] if not init else -prev['vol_sum'] + d['vol']
    prev['area_count'] += 1 if not init else -prev['area_count'] + 1
    prev['conc_count'] += 1 if not init else -prev['conc_count'] + 1
    prev['vol_count'] += 1 if not init else -prev['vol_count'] + 1

def decade_average(data):
    prev = {
        'date': {
            'year': 0, #no need to init year
            'month': 0, #no need to init month
            'dec': est.calc_decade(est.get_first_day_or_dec(data))
        },
        'area_sum': 0,
        'conc_sum': 0,
        'vol_sum': 0,
        'area_count': 0,
        'conc_count': 0,
        'vol_count': 0
    }

    for year in sorted(data):
        for month in sorted(data[year]):
            for day in sorted(data[year][month]):
                d = data[year][month][day]
                dec = est.calc_decade(day)

                del data[year][month][day]
                if dec == prev['date']['dec']:
                     change_prev(False, prev, d, year, month, dec)
                else:
                     data[prev['date']['year']][prev['date']['month']][prev['date']['dec']] = {
                         'avg_area': prev['area_sum'] / prev['area_count'],
                         'avg_conc': prev['conc_sum'] / prev['conc_count'],
                         'avg_vol': prev['vol_sum'] / prev['vol_count']
                     }

                     change_prev(True, prev, d, year, month, dec)
    return data

def fill_zeros(data, sea):
    zero_info = csv_parser.parse_zeros_csv()
    zero_dict = { 'avg_area': 0.0, 'avg_conc': 0.0, 'avg_vol': 0.0 }

    for year in zero_info:
        start_dec = zero_info[year][sea]['start_dec']
        end_dec = zero_info[year][sea]['end_dec']

        init_month = True
        end_month = False
        for month in range(start_dec[1], end_dec[1] + 1):
            if month == end_dec[1]:
                end_month = True

            for dec in range(start_dec[0], end_dec[0] + 1) if init_month and end_month \
                else range(start_dec[0], 3 + 1) if init_month \
                else range(1, end_dec[0] + 1) if end_month \
                else range(1, 3 + 1):
                append_to_data(data, year, month, dec, zero_dict)

            init_month = False

def interpolate_missed(data):
    prev = init_prev(data)

    decs = []
    func_data_area = []
    func_data_conc = []
    func_data_vol = []

    global_dec = 0

    for year in sorted(data):
        for month in sorted(data[year]):
            for dec in sorted(data[year][month]):
                curr_data = data[year][month][dec]

                curr_global_dec = est.get_global_dec(year, month, dec)
                prev_global_dec = est.get_global_dec(prev['date']['year'], prev['date']['month'], prev['date']['dec'])
                dist = curr_global_dec - prev_global_dec
                global_dec += dist

                decs.append(curr_global_dec)
                func_data_area.append(curr_data['avg_area'])
                func_data_conc.append(curr_data['avg_conc'])
                func_data_vol.append(curr_data['avg_vol'])

                prev['date'] = {'year': year, 'month': month, 'dec': dec}
                for key in curr_data.keys():
                    prev[key] = curr_data[key]

    interp_area = est.lin_interpolation(decs, func_data_area)
    interp_conc = est.lin_interpolation(decs, func_data_conc)
    interp_vol = est.lin_interpolation(decs, func_data_vol)

    return (interp_area, interp_conc, interp_vol)

def fill_missed(data, sea):
    if sea != 'chukchi': #this sea has ice full year
        fill_zeros(data, sea)

    interp_funcs = interpolate_missed(data)

    prev = init_prev(data)

    for year in sorted(data):
        for month in sorted(data[year]):
            for dec in sorted(data[year][month]):
                curr_global_dec = est.get_global_dec(year, month, dec)
                prev_global_dec = curr_global_dec if prev['date']['year'] == 0 else \
                    est.get_global_dec(prev['date']['year'], prev['date']['month'], prev['date']['dec'])

                dist = curr_global_dec - prev_global_dec
                if dist > 1:
                    for d in range(1, dist):
                        local_data = est.get_local_date(prev_global_dec + d)
                        #print(local_data)
                        append_to_data(data, local_data['year'], local_data['month'], local_data['dec'], {
                            'avg_area': float(interp_funcs[0](prev_global_dec + d)),
                            'avg_conc': float(interp_funcs[1](prev_global_dec + d)),
                            'avg_vol': float(interp_funcs[2](prev_global_dec + d))
                        })

                prev['date'] = {'year': year, 'month': month, 'dec': dec}

    return data

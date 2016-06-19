from scipy.interpolate import interp1d
from math import sqrt
import datetime

class Estimation:
    sea_area = {
        'bering': 2315000,
        'chukchi': 589600,
        'japan': 1008000,
        'okhotsk': 1603200
    }

    first_year = 1997

    @staticmethod
    def get_first_day_or_dec(data):
        first_year = sorted(data.keys())[0]
        first_month = sorted(data[first_year].keys())[0]
        first_day_or_dec = sorted(data[first_year][first_month].keys())[0]

        return first_day_or_dec

    @staticmethod
    def calc_decade(day):
        return 1 if day <= 10 else 2 if day <= 20 else 3

    @staticmethod
    def get_year_dec(month, dec):
        return (month - 1) * 3 + dec

    @staticmethod
    def get_global_dec(year, month, dec):
        return (year - Estimation.first_year) * 36 + month * 3 - 3 + dec

    @staticmethod
    def get_month_dec(dec):
        from math import ceil

        month = ceil(dec / 3)
        month_dec = 3 if dec % 3 == 0 else dec % 3

        return {
            'month': month,
            'dec': month_dec
        }

    @staticmethod
    def get_season_date(year, month, dec):
        cur_year = year if month >= 9 else year - 1
        cur_month = 9
        cur_dec = 1
        season_year = year if month >= 9 else year - 1
        season_month = 1
        season_dec = 1

        while 1:
            if cur_year == year and cur_month == month and cur_dec == dec:
                break
            cur_dec += 1
            season_dec += 1
            if cur_dec > 3:
                cur_month += 1
                cur_dec = 1
                if cur_month > 12:
                    cur_year += 1
                    cur_month = 1

            if season_dec > 3:
                season_month += 1
                season_dec = 1
                if season_month > 12:
                    season_year += 1
                    season_month = 1

        return {
            'year': season_year,
            'month': season_month,
            'dec': season_dec
        }

    @staticmethod
    def get_season_dec(dec):
        month = 9
        month_dec = 1
        season_dec = 1

        while Estimation.get_year_dec(month, month_dec) != dec:
            month_dec += 1
            if month_dec > 3:
                month += 1
                month_dec = 1
            if month > 12:
                month = 1
            season_dec += 1

        return season_dec

    @staticmethod
    def get_base_dec(dec):
        month = 9
        month_dec = 1
        season_dec = 1

        while season_dec < dec:
            month_dec += 1
            if month_dec > 3:
                month += 1
                month_dec = 1
            if month > 12:
                month = 1
            season_dec += 1

        return Estimation.get_year_dec(month, month_dec) - 1

    @staticmethod
    def get_local_date(global_dec):
        global_dec -= 1
        year = Estimation.first_year + global_dec // 36
        month_dec = Estimation.get_month_dec(global_dec % 36 + 1)

        return {'year': year, 'month': month_dec['month'], 'dec': month_dec['dec']}

    @staticmethod
    def lin_interpolation(x, y):
        return interp1d(x, y, kind='linear')

    @staticmethod
    def normalize(data, sea):
        for year in data:
            for month in data[year]:
                for dec in data[year][month]:
                    data[year][month][dec]['avg_area'] /= (Estimation.sea_area[sea] / 100)
                    data[year][month][dec]['avg_conc'] /= (Estimation.sea_area[sea] / 100)
                    data[year][month][dec]['avg_vol'] /= (Estimation.sea_area[sea] / 1000)

        return data

    @staticmethod
    def start_shift(data1, data2, decs1, decs2):
        earlier_dec = decs1[0] if decs1[0] < decs2[0] else decs2[0]
        month_dec = Estimation.get_month_dec(earlier_dec)
        month = month_dec['month']
        dec = month_dec['dec']

        data1_first_y = sorted(list(data1.keys()))[0]
        data2_first_y = sorted(list(data2.keys()))[0]
        data1_first_m = sorted(list(data1[data1_first_y].keys()))[0]
        data2_first_m = sorted(list(data2[data2_first_y].keys()))[0]
        data1_first_d = sorted(list(data1[data1_first_y][data1_first_m].keys()))[0]
        data2_first_d = sorted(list(data2[data2_first_y][data2_first_m].keys()))[0]

        if data1_first_m <= month and data1_first_d <= dec and data2_first_m <= month and data2_first_d <= dec:
            return Estimation.first_year

        return Estimation.first_year + 1

    @staticmethod
    def iciness(data, sea):
        if data == 0.0:
            return 0.0
        # return data
        return data / Estimation.sea_area[sea]

    @staticmethod
    def avg_iciness(data, year, month_dec, sea, param):
        sum = 0
        for t in range(Estimation.first_year, year + 1):
            try:
                sum += Estimation.iciness(data[t][month_dec['month']][month_dec['dec']][param], sea)
            except:
                print("asd")

        try:
            return sum / (year - Estimation.first_year + 1)
        except:
            print('asd')

    @staticmethod
    def avg_iciness_dev(data, year, month_dec, sea, param):
        sum = 0
        avg_iciness = Estimation.avg_iciness(data, year, month_dec, sea, param)
        for t in range(Estimation.first_year, year + 1):
            iceness = Estimation.iciness(data[t][month_dec['month']][month_dec['dec']][param], sea)
            if Estimation.first_year == year:
                sum += avg_iciness ** 2
            else:
                sum += (iceness - avg_iciness) ** 2

        n = year - Estimation.first_year + 1

        return 1 / n * sum

    @staticmethod
    def pirson_coeff(data2, data1, sea2, sea1, year, decs1, decs2, param):
        if year >= sorted(data1.keys())[-1]:
            year = sorted(data1.keys())[-1] - 1

        decs1, decs2 = sorted(decs1), sorted(decs2)

        Estimation.first_year = Estimation.start_shift(data1, data2, decs1, decs2)

        coeffs = [[0 for j in range(len(decs2))] for i in range(len(decs1))]
        for i in range(len(decs1)):
            for j in range(len(decs2)):
                month_dec1 = Estimation.get_month_dec(decs1[i])
                month_dec2 = Estimation.get_month_dec(decs2[j])

                avg_icinecc_dev1 = Estimation.avg_iciness_dev(data1, year, month_dec1, sea1, param)
                avg_icinecc_dev2 = Estimation.avg_iciness_dev(data2, year, month_dec2, sea2, param)

                n = year - Estimation.first_year + 1

                try:
                    res = 1 / ((n - 1) * sqrt(avg_icinecc_dev1 * avg_icinecc_dev2))

                    avg_icinecc1 = Estimation.avg_iciness(data1, year, month_dec1, sea1, param)
                    avg_icinecc2 = Estimation.avg_iciness(data2, year, month_dec2, sea2, param)

                    sum = 0
                    for t in range(Estimation.first_year, year + 1):
                        icinecc1 = Estimation.iciness(data1[t][month_dec1['month']][month_dec1['dec']][param], sea1)
                        icinecc2 = Estimation.iciness(data2[t][month_dec2['month']][month_dec2['dec']][param], sea2)
                        if Estimation.first_year == year:
                            sum += avg_icinecc1 * avg_icinecc2
                        else:
                            sum += (icinecc1 - avg_icinecc1) * (icinecc2 - avg_icinecc2)

                    res *= sum

                except:
                    res = 0.0

                coeffs[i][j] = res

        Estimation.first_year = 1997

        return coeffs

    @staticmethod
    def find_max_val(data, field):
        max_val = 0

        for year in data:
            for month in data[year]:
                for dec in data[year][month]:
                    if data[year][month][dec][field] > max_val:
                        max_val = data[year][month][dec][field]

        return max_val

    @staticmethod
    def find_max_year_val(data, find_year, field):
        max_val = 0
        max_month = 1
        max_dec_day = 1

        for year in data:
            if year == find_year:
                for month in data[year]:
                    for dec_day in data[year][month]:
                        if data[year][month][dec_day][field] > max_val:
                            max_val = data[year][month][dec_day][field]
                            max_month = month
                            max_dec_day = dec_day

        return {
            'max_val': max_val,
            'max_month': max_month,
            'max_dec_day': max_dec_day
        }

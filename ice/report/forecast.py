import itertools
from estimation import Estimation as est


def max_corr(data, field_name, k, t, last_year, pair_coeffs):
    max_val = 0
    for l in data.keys():
        for u in range(1, t):
            #coeffs = est.pirson_coeff(
            #    data[k], data[l], k, l, last_year, range(1, t + 2), range(1, u + 2), field_name
            #)
            coeffs = pair_coeffs[(k, l)]
            if abs(coeffs[t][u]) > max_val:
                max_val = coeffs[t][u]

    return max_val


def calc_weight(data, field_name, k, t, l ,u, last_year, pair_coeffs):
    #k_l_coeffs = est.pirson_coeff(
    #    data[k], data[l], k, l, last_year, range(1, t + 2), range(1, u + 2), field_name
    #)
    k_l_coeffs = pair_coeffs[(k, l)]

    indicator = 0
    max = max_corr(data, field_name, k, t, last_year, pair_coeffs)
    if k_l_coeffs[t][u] > 0.9 * max:
        indicator = 1

    return indicator * k_l_coeffs[t][u]**2


def get_seasons_joint(data, field_name, k, t, jb, je, l, u, ib, ie, last_year):
    k_succ, k_were, l_succ, l_were = {}, {}, {}, {}
    for year in data[k]:
        if year <= last_year:
            month_dec = est.get_month_dec(t)
            try:
                cur_data = data[k][year][month_dec['month']][month_dec['dec']][field_name]
                k_succ[year] = 1 if cur_data >= jb and cur_data < je else 0
                k_were[year] = 1
            except:
                k_succ[year] = 0
                k_were[year] = 0

    for year in data[l]:
        if year <= last_year:
            month_dec = est.get_month_dec(u)
            try:
                cur_data = data[l][year][month_dec['month']][month_dec['dec']][field_name]
                l_succ[year] = 1 if cur_data >= ib and cur_data < ie else 0
                l_were[year] = 1
            except:
                l_succ[year] = 0
                l_were[year] = 1

    start_year = est.first_year
    if abs(sorted(data[k])[0] - sorted(data[l])[0]) == 1:
        start_year += 1

    joint_seasons_count = 0
    seasons_count = 0
    for y in range(start_year, last_year + 1):
        if k_were[y] == 1 and l_were[y] == 1 and l_succ[y] == 1:
            seasons_count += 1
            if k_succ[y] == 1:
                joint_seasons_count += 1

    return {
        'seasons_count': seasons_count,
        'joint_seasons_count': joint_seasons_count
    }


def chosen_rates(data, field_name, k, t, jb, je, l, u, ib, ie, last_year):
    seasons_rates = get_seasons_joint(data, field_name, k, t, jb, je, l, u, ib, ie, last_year)

    try:
        return seasons_rates['joint_seasons_count'] / seasons_rates['seasons_count']
    except:
        return 0


def calc_rates(data, field_name, k, t, jb, je, l, u, last_year, prec, pair_coeffs, num):
    max_val_l = est.find_max_val(data[l], field_name)
    states_l = [(max_val_l / prec * i) for i in range(prec + 1)]

    rates_sum = 0
    for i in range(len(states_l) - 1):
        rates = chosen_rates(data, field_name, k, t, jb, je, l, u, states_l[i], states_l[i + 1], last_year)
        cur_prob = get_prob(data, field_name, l, u, states_l[i], states_l[i + 1], last_year, prec, pair_coeffs, num + 1)
        rates_sum += rates * cur_prob

        if cur_prob > 0:
            print(cur_prob)

    #if num == 1:
        #print('test')

    return rates_sum


def get_prob(data, field_name, sea, dec, jb, je, last_year, prec, pair_coeffs, num):
    weighted = 0
    weight_rates = 0
    #print(dec)
    for u in range(1, dec):
        for l in data.keys():#filter(lambda s: s != sea, data.keys()):
            weighted += calc_weight(data, field_name, sea, dec, l, u, last_year, pair_coeffs)
            weight_rates += weighted * calc_rates(data, field_name, sea, dec, jb, je, l, u, last_year, prec, pair_coeffs, num)
            #print(weight_rates)

    try:
        result = 1 / weighted * weight_rates
    except:
        result = 0

    return result


def forecast(data, field_name, sea, dec, last_year, prec):
    sea_pairs = []
    for pair in itertools.product(data.keys(), repeat=2):
        sea_pairs.append(pair)

    pair_coeffs = {}
    for sea_pair in sea_pairs:
        sea1, sea2 = sea_pair[0], sea_pair[1]
        pair_coeffs[sea_pair] = est.pirson_coeff(
            data[sea2], data[sea1], sea2, sea1, last_year, range(1, dec + 2), range(1, dec + 2), field_name
        )


    max_val_k = est.find_max_val(data[sea], field_name)
    print(max_val_k)
    states_k = [(max_val_k / prec * i) for i in range(prec + 1)]

    probs = {}
    for j in range(len(states_k) - 1):
        print(str(states_k[j]) + ' | ' + str(states_k[j + 1]))
        p = get_prob(data, field_name, sea, dec, states_k[j], states_k[j + 1], last_year, prec, pair_coeffs, 1)
        probs[(states_k[j], states_k[j + 1])] = p

    return max(probs, key=probs.get)

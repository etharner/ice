import itertools
from ice.report.estimation import Estimation as est


class Forecast:
    global_probs = {}

    def max_corr(self, data, k, t, last_year, pair_coeffs):
        max_val = 0
        for l in data.keys():
            #if l != k:
            for u in range(0, t):
                coeffs = pair_coeffs[(k, l)]
                if abs(coeffs[t][u]) > max_val:
                    max_val = coeffs[t][u]

        return max_val


    def calc_weight(self, data, k, t, l, u, last_year, pair_coeffs):
        k_l_coeffs = pair_coeffs[(k, l)]

        indicator = 0
        max = self.max_corr(data, k, t, last_year, pair_coeffs)
        if k_l_coeffs[t][u] > 0.9 * max:
            indicator = 1

        return indicator * k_l_coeffs[t][u]**2


    def get_seasons_joint(self, data, field_name, k, t, jb, je, l, u, ib, ie, last_year):
        k_succ, k_were, l_succ, l_were = {}, {}, {}, {}
        for year in data[k]:
            if year <= last_year:
                month_dec = est.get_month_dec(t)
                try:
                    cur_data = data[k][year][month_dec['month']][month_dec['dec']][field_name]
                    k_succ[year] = 1 if cur_data >= jb and cur_data <= je else 0
                    k_were[year] = 1
                except:
                    k_succ[year] = 0
                    k_were[year] = 0

        for year in data[l]:
            if year <= last_year:
                month_dec = est.get_month_dec(u)
                try:
                    cur_data = data[l][year][month_dec['month']][month_dec['dec']][field_name]
                    l_succ[year] = 1 if cur_data >= ib and cur_data <= ie else 0
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


    def chosen_rates(self, data, field_name, k, t, jb, je, l, u, ib, ie, last_year):
        seasons_rates = self.get_seasons_joint(data, field_name, k, t, jb, je, l, u, ib, ie, last_year)

        try:
            return seasons_rates['joint_seasons_count'] / seasons_rates['seasons_count']
        except:
            return 0.0


    def calc_rates(self, data, field_name, k, t, jb, je, l, u, last_year, prec, pair_coeffs, num):
        max_val_l = est.find_max_val(data[l], field_name)
        states_l = [(max_val_l / prec * i) for i in range(prec + 1)]

        rates_sum = 0
        for i in range(len(states_l) - 1):
            rates = self.chosen_rates(data, field_name, k, t + 1, jb, je, l, u + 1, states_l[i], states_l[i + 1], last_year)

            if (states_l[i], states_l[i + 1]) not in self.global_probs[l][u].keys():
                cur_date = est.get_local_date(u + 1)
                try:
                    known_data = data[l][cur_date['year']][cur_date['month']][cur_date['dec']][field_name]

                    cond = False
                    if i < len(states_l) - 2:
                        cond = known_data >= states_l[i] and known_data < states_l[i + 1]
                    else:
                        cond = known_data >= states_l[i] and known_data <= states_l[i + 1]
                    if cond:
                        self.global_probs[l][u][(states_l[i], states_l[i + 1])] = 1.0
                    else:
                        self.global_probs[l][u][(states_l[i], states_l[i + 1])] = 0.0

                except:
                    self.global_probs[l][u][(states_l[i], states_l[i + 1])] = \
                        self.get_prob(data, field_name, l, u, states_l[i], states_l[i + 1], last_year, prec, pair_coeffs, num + 1)

            rates_sum += rates * self.global_probs[l][u][(states_l[i], states_l[i + 1])]

        return rates_sum


    def get_prob(self, data, field_name, sea, dec, jb, je, last_year, prec, pair_coeffs, num):
        weighted = 0
        weight_rates = 0

        if dec == 0:
            if jb == 0.0:
                return 1.0
            else:
                return 0.0

        for u in range(0, dec):
            for l in data.keys():#filter(lambda s: s != sea, data.keys()):
                weighted += self.calc_weight(data, sea, dec, l, u, last_year, pair_coeffs)
                weight_rates += weighted * self.calc_rates(data, field_name, sea, dec, jb, je, l, u, last_year, prec, pair_coeffs, num)
                #print(weight_rates)

        try:
            result = 1.0 / weighted * weight_rates
        except:
            result = 0.0

        return result


    def forecast(self, data, field_name, sea, dec, last_year, prec):
        sea_pairs = []
        for pair in itertools.product(data.keys(), repeat=2):
            sea_pairs.append(pair)

        pair_coeffs = {}
        for sea_pair in sea_pairs:
            sea1, sea2 = sea_pair[0], sea_pair[1]
            pair_coeffs[sea_pair] = est.pirson_coeff(
                data[sea2], data[sea1], sea2, sea1, last_year - 1, range(1, dec + 1), range(1, dec + 1), field_name
            )


        max_val_k = est.find_max_val(data[sea], field_name)
        #print(max_val_k)
        states_k = [(max_val_k / prec * i) for i in range(prec + 1)]

        for k in data.keys():
            cur_glob_probs = {}
            for d in range(0, dec):
                cur_glob_probs[d] = {}
            self.global_probs[k] = cur_glob_probs

        probs = {}
        for j in range(len(states_k) - 1):
            p = self.get_prob(data, field_name, sea, dec - 1, states_k[j], states_k[j + 1], last_year, prec, pair_coeffs, 1)
            probs[(states_k[j], states_k[j + 1])] = p
            #print(str(states_k[j]) + ' | ' + str(states_k[j + 1]) + '| ' + str(p))

        return max(probs, key=probs.get)

coeffs = Estimation.pirson_coeff(
    _bering_data, _japan_data, 'bering', 'japan', 2011, decs1, decs2, 'avg_conc'
)
graph.draw_correlation_field(coeffs, 'bering', 'japan', 2011, decs1, decs2, 'avg_conc')

coeffs = Estimation.pirson_coeff(
    _bering_data, _japan_data, 'bering', 'japan', 2011, decs1, decs2, 'avg_vol'
)
graph.draw_correlation_field(coeffs, 'bering', 'japan', 2011, decs1, decs2, 'avg_vol')

coeffs = Estimation.pirson_coeff(
    _bering_data, _okhotsk_data, 'bering', 'okhotsk', 2011, decs1, decs2, 'avg_conc'
)
graph.draw_correlation_field(coeffs, 'bering', 'okhotsk', 2011, decs1, decs2, 'avg_conc')

coeffs = Estimation.pirson_coeff(
    _bering_data, _okhotsk_data, 'bering', 'okhotsk', 2011, decs1, decs2, 'avg_vol'
)
graph.draw_correlation_field(coeffs, 'bering', 'okhotsk', 2011, decs1, decs2, 'avg_vol')

coeffs = Estimation.pirson_coeff(
    _chukchi_data, _japan_data, 'chukchi', 'japan', 2011, decs1, decs2, 'avg_conc'
)
graph.draw_correlation_field(coeffs, 'chukchi', 'japan', 2011, decs1, decs2, 'avg_conc')

coeffs = Estimation.pirson_coeff(
    _chukchi_data, _japan_data, 'chukchi', 'japan', 2011, decs1, decs2, 'avg_vol'
)
graph.draw_correlation_field(coeffs, 'chukchi', 'japan', 2011, decs1, decs2, 'avg_vol')

coeffs = Estimation.pirson_coeff(
    _chukchi_data, _okhotsk_data, 'chukchi', 'okhotsk', 2011, decs1, decs2, 'avg_conc'
)
graph.draw_correlation_field(coeffs, 'chukchi', 'okhotsk', 2011, decs1, decs2, 'avg_conc')

coeffs = Estimation.pirson_coeff(
    _chukchi_data, _okhotsk_data, 'chukchi', 'okhotsk', 2011, decs1, decs2, 'avg_vol'
)
graph.draw_correlation_field(coeffs, 'chukchi', 'okhotsk', 2011, decs1, decs2, 'avg_vol')

coeffs = Estimation.pirson_coeff(
    _japan_data, _okhotsk_data, 'japan', 'okhotsk', 2011, decs1, decs2, 'avg_conc'
)
graph.draw_correlation_field(coeffs, 'japan', 'okhotsk', 2011, decs1, decs2, 'avg_conc')

coeffs = Estimation.pirson_coeff(
    _japan_data, _okhotsk_data, 'japan', 'okhotsk', 2011, decs1, decs2, 'avg_vol'
)
graph.draw_correlation_field(coeffs, 'japan', 'okhotsk', 2011, decs1, decs2, 'avg_vol')

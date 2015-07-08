__author__ = 'mike'
import RockPy

hys = '/Users/mike/Dropbox/experimental_data/HYS/LF4/LF4C_Ve_HYS_VSM-XX[mg]___-TEMP_20_K-STD001.000'
hys2 = '/Users/mike/Dropbox/experimental_data/HYS/LF4/LF4C_Ve_HYS_VSM-XX[mg]___-TEMP_300_K-STD001.000'
sample = RockPy.Sample(name='LF4Ve')

m = sample.add_measurement(mtype='hys', mfile=hys, machine='VSM')
m.add_sval(stype='temperature', sval=20, unit='K')
m.add_sval(stype='pressure', sval=1, unit='GPa')
m = sample.add_measurement(mtype='hys', mfile=hys2, machine='VSM')
m.add_sval(stype='temperature', sval=300, unit='K')
m.add_sval(stype='milled', sval=2, unit='hrs')
m = sample.add_measurement(mtype='hys', mfile=hys2, machine='VSM')
m.add_sval(stype='temperature', sval=400, unit='K')
m = sample.add_measurement(mtype='hys', mfile=hys2, machine='VSM')
m.add_sval(stype='temperature', sval=500, unit='K')
m.add_sval(stype='pressure', sval=2, unit='GPa')

print sample.info()


# print sample.get_measurements(sval_range='<=300', stypes='temperature')
# print sample.mdict['mtype_sval']['hys'][300]

# print m.result_methods
#
# print m.result_bc()
# print m.result_ms(saturation_percent=20) #todo passing of parameter
# print m.result_ms(saturation_percent=80)
# print m.calc_all(parameter=dict(saturation_percent=20))
print m.result_mrs()
# m.plt_hys()
# print m.calc_all(parameter=dict(saturation_percent=80))
# m.correct_hsym()
# m.correct_center()
# m.plt_hys()
m.fit_hysteresis(nfunc=2)
print m.result_mrs()

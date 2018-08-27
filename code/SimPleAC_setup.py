from gplibrary.SP.SimPleAC.SimPleAC_mission import Mission, SimPleAC
from gpkit import Model, units

def SimPleAC_setup():
    a = SimPleAC()
    m = Mission(a, 4)
    subs = {
    'h_{cruise_m}'   :5000*units('m'),
    'Range_m'        :3000*units('km'),
    'W_{p_m}'        :6250*units('N'),
    'C_m'            :120*units('1/hr'),
    'V_{min_m}'      :25*units('m/s'),
    'T/O factor_m'   :2,
    }
    m.substitutions.update(subs)
    return m, subs

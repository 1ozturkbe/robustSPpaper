from __future__ import print_function
from SimPleAC_mission import Mission, SimPleAC
from gpkit import Model, units

def SimPleAC_setup():
    a = SimPleAC()
    m = Mission(a, 4)
    subs = {
    'h_{cruise_m}'   :5000*units('m'),
    'Range_m'        :3000*units('km'),
    'W_{p_m}'        :3000*units('N'),
    '\\rho_{p_m}'    :1500*units('kg/m^3'),
    'C_m'            :120*units('1/hr'),
    'V_{min_m}'      :35*units('m/s'),
    'T/O factor_m'   :2,
    }
    m.substitutions.update(subs)
    m.cost = m['W_{f_m}']#+m['C_m']*m['t_m']*units('N')
    return m, subs

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    sol = m.localsolve()
    print(sol.table())


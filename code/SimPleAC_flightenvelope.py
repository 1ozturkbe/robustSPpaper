from SimPleAC_setup import *
from gpkit import units
from gpkit.small_scripts import mag

# for flight envelopes
from robust.robust_gp_tools import RobustGPTools
from robust.feasibility_plots import plot_feasibilities
import numpy as np

# plotting
import matplotlib.pyplot as plt

def generate_flight_envelope(m, var1, var2, var1range):
    """
    Generates the flight envelope of an optimized aircraft
    :param m: already solved model
    :param var1: independent variable
    :param var2: dependent variable (should be maximized)
    :return:
    """
    dm = RobustGPTools.DesignedModel(m, m.solution, {})
    if var2.key in m.substitutions.keys():
        del dm.substitutions[var2.key]
    dm.cost = dm.cost/var2
    dm.substitutions.update({var1.key:('sweep',var1range)})
    sol = dm.localsolve(skipsweepfailures=True)
    plt.plot(mag(sol(var1.key)),mag(sol(var2.key)) )
    plt.xlabel(var1.str_without())
    plt.ylabel(var2.str_without())
    plt.title('Flight envelope')
    plt.show()

    return sol

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    # Payload/range feasibility plot for non-robust aircraft
    x = m['W_{p_m}']
    y = m['Range_m']
    rm = None
    #plot_feasibilities(x, y, m, rm=rm, design_feasibility=True, skipfailures=True, numberofsweeps=20)
    sol = m.localsolve()
    sol = generate_flight_envelope(m, m['Range_m'], m['W_{p_m}'], np.linspace(500,5000,11))



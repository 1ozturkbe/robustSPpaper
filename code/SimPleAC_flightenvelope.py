from SimPleAC_setup import *
from gpkit import units
from gpkit.small_scripts import mag

# for flight envelopes
from robust.robust import RobustModel
from robust.simulations.simulate import generate_model_properties
from robust.robust_gp_tools import RobustGPTools
import numpy as np

# plotting
import matplotlib.pyplot as plt

def generate_flight_envelope(m, var1, var2, var1range, rm = None, rmsol = None):
    """
    Generates the flight envelope of an optimized aircraft
    :param m: already solved model
    :param var1: independent variable
    :param var2: dependent variable (should be maximized)
    :param var1range: the range of the independent var
    :param rm: robust version of m
    :param rmsol: solution of rm
    :return: nominal sweep solution, robust sweep solution
    """
    dm = RobustGPTools.DesignedModel(m, m.solution, {})
    if var2.key in m.substitutions.keys():
        del dm.substitutions[var2.key]
    dm.cost = dm.cost + 1/var2*var2.units*dm.cost.units
    dm.substitutions.update({var1.key:('sweep',var1range)})
    sol = dm.localsolve(skipsweepfailures=True)
    if rm:
        drm = RobustGPTools.DesignedModel(m, rmsol, {})
        if var2.key in rm.substitutions.keys():
            del drm.substitutions[var2.key]
        drm.cost = drm.cost + 1/var2*var2.units*drm.cost.units
        drm.substitutions.update({var1.key:('sweep',var1range)})
        robustsol = drm.localsolve(skipsweepfailures=True)
    plt.plot(mag(sol(var1.key)),mag(sol(var2.key)))
    try:
        plt.plot(mag(robustsol(var1.key)),mag(robustsol(var2.key)))
        plt.legend("Nominal", "Robust")
    except:
        pass
    plt.xlabel(var1.str_without())
    plt.ylabel(var2.str_without())
    plt.title('Flight envelope')
    plt.grid()
    plt.show()

    return sol, robustsol

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    # Payload/range feasibility plot for non-robust aircraft
    var2 = m['W_{p_m}']
    var1 = m['Range_m']
    var1range = np.linspace(500,7000,8)*units('km')
    rm = None
    #plot_feasibilities(x, y, m, rm=rm, design_feasibility=True, skipfailures=True, numberofsweeps=20)
    sol , _, _, directly_uncertain_vars_subs = generate_model_properties(m, 1, 1)  # solving the SimPleAC
    rm = RobustModel(m, 'elliptical', twoTerm=False, gamma=1)
    rmsol = rm.robustsolve()
    sol, robustsol = generate_flight_envelope(m, var1, var2, var1range, rm, rmsol)



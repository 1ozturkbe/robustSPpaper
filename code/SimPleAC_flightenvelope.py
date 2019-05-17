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
from mpl_toolkits.mplot3d import Axes3D

def generate_flight_envelope(m, var1, var2, var1range, rm = None, rmsol = None):
    """
    Generates the flight envelope of an optimized aircraft
    This is a method to compare the objective trade-off performance
    of an already designed aircraft (nominal and robust)
    Want to MAXIMIZE both var1 and var2 (bigger envelope)
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
    dm.cost = 1/var2 #*var2.units*dm.cost.units #dm.cost/var2 #
    dm.substitutions.update({var1.key:('sweep',var1range)})
    sol = dm.localsolve(skipsweepfailures=True)
    if rm:
        drm = RobustGPTools.DesignedModel(m, rmsol, {})
        if var2.key in rm.substitutions.keys():
            del drm.substitutions[var2.key]
        drm.cost = 1/var2 #drm.cost + 1/var2*var2.units*drm.cost.units #drm.cost/var2
        drm.substitutions.update({var1.key:('sweep',var1range)})
        robustsol = drm.localsolve(skipsweepfailures=True)
    plt.plot(mag(sol(var1.key)),mag(sol(var2.key)))
    try:
        plt.plot(mag(robustsol(var1.key)),mag(robustsol(var2.key)))
        plt.legend(["Nominal", "Robust"])
    except:
        pass
    plt.xlabel(var1.str_without())
    plt.ylabel(var2.str_without())
    plt.title(r'Flight envelope, $\Gamma = 1$')
    plt.grid()
    plt.show()

    return sol, robustsol

def plot_general_solutions(solarray, var1, var2, var3):
    points = ["o","*","-"]
    count = 0
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in solarray:
        ax.plot(mag(i(var1.key)), mag(i(var2.key)),mag(i(var3.key)))
        count+=1
    ax.set_xlabel(var1.str_without())
    ax.set_ylabel(var2.str_without())
    ax.set_zlabel(var3.str_without())
    plt.title('3D Flight envelope')
    plt.show()

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    # Payload/range feasibility plot for nominal and robust aircraft
    var2 = m['W_{p_m}']
    var1 = m['Range_m']
    var1range = np.linspace(500,5000,24)*units('km')
    rm = None
    #plot_feasibilities(x, y, m, rm=rm, design_feasibility=True, skipfailures=True, numberofsweeps=20)
    sol , _, _, directly_uncertain_vars_subs = generate_model_properties(m, 1, 1)  # solving the SimPleAC
    rm = RobustModel(m, 'elliptical', twoTerm=False, gamma=1)
    rmsol = rm.robustsolve()
    sol, robustsol = generate_flight_envelope(m, var1, var2, var1range, rm, rmsol)

    plot_general_solutions([sol,robustsol],var1,var2,m['W_{f_m}'])

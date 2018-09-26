# This script implements a goal programming approach with SimPleAC

from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model, Variable
from gpkit.constraints.bounded import Bounded
from gpkit.small_scripts import mag

from robust.robust import RobustModel
from robust.simulations.simulate import generate_model_properties
from robust.robust_gp_tools import RobustGPTools

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    sol , _, _, directly_uncertain_vars_subs = generate_model_properties(m, 1, 1)  # solving the SimPleAC
    Gamma = Variable('\Gamma','-','Uncertainty bound')
    m = Model(1/Gamma, [m, m.cost <= sol['cost']*1.2, Gamma <= 1e30])
    rm = RobustModel(m, 'elliptical', twoTerm=False, gamma=Gamma)
    rmsol = rm.robustsolve(verbosity=0)  # solve the robust model


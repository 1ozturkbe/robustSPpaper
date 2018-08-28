from SimPleAC_setup import *

# for flight envelopes
from robust.feasibility_plots.plot_feasibilities import plot_feasibilities

if __name__ == "__main__":
    m, subs = SimPleAC_setup()

    # Payload/range feasibility plot for non-robust aircraft
    x = m['W_{p_m}']
    y = m['Range_m']
    rm = None
    skipfailures = True
    plot_feasibilities(x, y, m, rm=rm, design_feasibility=True, skipfailures=True, numberofsweeps=20)



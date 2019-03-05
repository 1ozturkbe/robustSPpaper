import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

from gpkit.small_scripts import mag

def SimPleAC_draw(sol, color='blue', directory=None, name=None):
    # Defining variables
    AR = sol('A').magnitude
    S = sol('S').magnitude
    b = (S*AR)**0.5
    lam = 0.5
    croot = S/(1+lam)/b
    ctip = lam*croot
    CDA0 = sol('(CDA0)')
    rfuse = 50*mag((CDA0/np.pi)**0.5)
    lfuse = 6*rfuse

    patches = []

    # Creating fuselage patch
    ellipse = mpatches.Ellipse((-0.25*croot,0), lfuse, rfuse)
    patches.append(ellipse)

    # Creating wing patch
    wingCoords = np.array([[0,0], [0.25*croot - 0.25*ctip, b/2],
        [0.25*croot + 0.75*ctip, b/2], [croot, 0],
        [0.25*croot + 0.75*ctip, -b/2], [0.25*croot - 0.25*ctip, -b/2],
        [0,0]])
    Path = mpath.Path
    path_data = []
    for i in range(len(wingCoords)):
        if i == 0:
            path_data.append((Path.MOVETO, wingCoords[i]))
        elif i == len(wingCoords)-1:
            path_data.append((Path.CLOSEPOLY, wingCoords[i]))
        else:
            path_data.append((Path.LINETO, wingCoords[i]))
    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path)
    patches.append(patch)

    plt.figure(0).clf()
    fig = plt.figure(0)
    ax = fig.add_subplot(111, aspect='equal')
    fig.set_size_inches(3,3)
    ax.set_xlim(-14,14)
    ax.set_ylim(-14,14)

    for e in patches:
        ax.add_artist(e)
        e.set_clip_box(ax.bbox)
        e.set_alpha(0.8)
        e.set_facecolor(color)
    plt.axis('off')
    fig = ax.get_figure()
    if directory is not None and name is not None:
        fig.savefig(directory + '/' + name + '.pdf', transparent=True)
    else:
        plt.show()


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

from gpkit.small_scripts import mag

def SimPleAC_draw(sol):
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

    # add an ellipse for the fuselage
    ellipse = mpatches.Ellipse((-0.25*croot,0), lfuse, rfuse)
    patches.append(ellipse)

    fig = plt.figure(0)
    ax = fig.add_subplot(111, aspect='equal')
    ax.set_xlim(-0.6*b, 0.6*b)
    ax.set_ylim(-0.6*b, 0.6*b)

    for e in patches:
        ax.add_artist(e)
        e.set_clip_box(ax.bbox)
        e.set_alpha(0.4)
        e.set_facecolor('blue')
    plt.show()


    # ax.add_artist(ellipse)
    # ax.add_artist(patch)
    #
    # colors = np.linspace(0, 1, len(patches))
    # # collection = PatchCollection(patches) #cmap=plt.cm.hsv, alpha=0.3)
    # # collection.set_array(np.array(colors))
    # # ax.add_collection(collection)
    # plt.axis('equal')
    # plt.axis('off')
    # plt.show()

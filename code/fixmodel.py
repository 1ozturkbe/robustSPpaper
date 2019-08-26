from __future__ import print_function
from SimPleAC_setup import SimPleAC_setup

from gpkit import Model

# this class exists to fix the variables in a model that have the attributes fix == True.

class fixedModel(Model):
    def setup(self, model, sol):
        fixsubs = {}
        for i in model.varkeys:
            if model[i].key.fix == True:
                fixsubs.update({i:sol(i)})
        if not fixsubs:
            print("Warning: no variables were fixed.")
        newModel = Model(model.cost, model, model.substitutions)
        newModel.substitutions.update(fixsubs)
        newModel.fixsubs = fixsubs
        return newModel

# To check that the method works

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    sol = m.localsolve()
    f = fixedModel(m,sol)
    print(f.substitutions)

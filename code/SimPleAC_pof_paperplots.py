from builtins import str
from builtins import range
from robust.simulations.simulate import filter_gamma_result_dict
from SimPleAC_save import load_obj
import pickle as pickle
import numpy as np
import matplotlib.pyplot as plt
from SimPleAC_pof_simulate import pof_parameters

if __name__ == "__main__":
    # Retrieving pof parameters
    [model, methods, gammas, number_of_iterations,
    min_num_of_linear_sections, max_num_of_linear_sections, verbosity, linearization_tolerance,
    number_of_time_average_solves, uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel,
            nominal_number_of_constraints, nominal_solve_time] = pof_parameters()
    method = methods[0] # only care about Best Pairs

    # Loading results
    margin = {}
    nGammas = nmargins = len(gammas)
    margins = gammas
    margin['solutions'] = {}
    for i in range(nmargins):
        margin['solutions'][margins[i]] = pickle.load(open("marginResults/" +
                                                                    str(margins[i]), 'rb'))
    margin['number_of_constraints'] = load_obj('marginnumber_of_constraints', 'marginResults')
    margin['simulation_results'] = load_obj('marginsimulation_results', 'marginResults')

    gamma = {}
    gamma['solutions'] = {}
    for i in range(nGammas):
        for j in range(len(methods)):
            for k in range((len(uncertainty_sets))):
                gamma['solutions'][gammas[i], methods[j]['name'], uncertainty_sets[k]] = pickle.load(open(
                                        "gammaResults\\" + str((gammas[i], methods[j]['name'], uncertainty_sets[k])), 'rb'))
    gamma['solve_times'] = load_obj('gammasolve_times', 'gammaResults')
    gamma['simulation_results'] = load_obj('gammasimulation_results', 'gammaResults')
    gamma['number_of_constraints'] = load_obj('gammanumber_of_constraints', 'gammaResults')

    # Plotting of cost and probability of failure
    objective_name = 'Total fuel weight'
    objective_units = 'N'
    title = ''
    filteredResults = [margin['solutions'],
                       filter_gamma_result_dict(gamma['solutions'], 1, method['name'], 2, 'box'),
                       filter_gamma_result_dict(gamma['solutions'], 1, method['name'], 2, 'elliptical')]
    filteredSimulations = [margin['simulation_results'],
                           filter_gamma_result_dict(gamma['simulation_results'], 1, method['name'], 2, 'box'),
                            filter_gamma_result_dict(gamma['simulation_results'], 1, method['name'], 2, 'elliptical')]
    objective_varkey = 'W_{f_m}'
    legend_keys = ['margins', 'box', 'elliptical']
    edgecolors = ['#FFBF00', '#CC0000', '#008000']
    facecolors = ['#FFE135','#FF2052', '#8DB600']

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    lines = []
    mincost = 1e10
    maxcost = 0
    for i in range(len(legend_keys)):
        sims = list(filteredSimulations[i].items())
        pofs = []
        objective_costs = []
        objective_stddev = []
        for j in sims:
            pofs.append(j[1][0])
            objective_costs.append(j[1][1])
            objective_stddev.append(j[1][2])
        mincost = np.min([mincost] + objective_costs)
        maxcost = np.max([maxcost] + objective_costs)
        lines.append(ax1.plot(gammas, objective_costs, color=edgecolors[i], label=legend_keys[i] + ', cost'))
        inds = np.nonzero(np.ones(len(gammas)) - pofs)[0]
        uppers = [objective_costs[ind] + objective_stddev[ind] for ind in inds]
        lowers = [objective_costs[ind] - objective_stddev[ind] for ind in inds]
        x = [gammas[ind] for ind in inds]
        ax1.fill_between(x, lowers, uppers,
                         alpha=0.5, edgecolor = edgecolors[i], facecolor = facecolors[i])
        lines.append(ax2.plot(gammas, pofs, color=edgecolors[i], label=legend_keys[i] + ', PoF'))

    ax1.set_xlabel(r'Uncertainty Set Scaling Factor $\Gamma$', fontsize=12)
    ax1.set_ylabel('Cost [' + objective_name + ' (' + objective_units.capitalize() + ')]', fontsize=12)
    ax2.set_ylabel("Probability of Failure", fontsize=12)
    ax1.set_ylim([mincost, maxcost])
    ax2.set_ylim([0, 1])
    plt.title(title, fontsize=12)
    labs = [lines[l][0].get_label() for l in [1,3,5,0,2,4]]
    ax1.legend(labs, loc="lower right", fontsize=9, numpoints=1)
    # ax1.legend(loc="lower right", fontsize=10, numpoints=1)
    # fig.legend(loc="lower right", fontsize=10, numpoints=1)
    plt.show()

from formatting_hospital_file import read_hospital_file

import json
import numpy as np
import dynetx as dn
import dynetx.algorithms as al

import matplotlib.pyplot as plt
from matplotlib import cm


def extract_results (delta_res):
    assort_conf = {}
    for alpha, profiles in delta_res.items():
        for profile, data in profiles.items():
            for k, v in data.items():
                assort_conf[k] = v
    return assort_conf


def run_delta_conformity (file_list, delta=1, alpha=[2]):
    result_files = []
    for i, file in enumerate(file_list):
        g = read_hospital_file(file)
        #delta-conformity
        res = al.sliding_delta_conformity(g, delta, alpha, ['lab'], profile_size=1, path_type="shortest")
        #to save json
        format_res = extract_results(res)

        # save hospital results
        names = ['mond', 'tues', 'wed', 'thur', 'frid']
        output_name = "delta_conformity_hospital_ward/delta" + str(delta) + "_conf_" + str(names[i]) + ".txt"

        with open(output_name, 'w') as outfile:
            json.dump(format_res, outfile)

        result_files.append(output_name)

    return result_files


def read_and_plot_results(delta_result, g, window, label, palette='tab20', alpha=0.6, savefig=False, xticks=[]):
    # read results
    delta_conf = json.load(open(delta_result))
    # extract labels
    node_labs = dn.get_node_attributes(g, label)
    unique_labels = sorted(list(set(list(node_labs.values()))))

    categories = []
    for l in unique_labels:
        cat = [n for n in list(node_labs.keys()) if node_labs[n] == l]
        categories.append(cat)

    fig, axs = plt.subplots(len(unique_labels), sharex=True, sharey=True, gridspec_kw={'hspace': 0.2})

    min_rng = min([e[3] for e in g.stream_interactions()])
    max_rng = max([e[3] for e in g.stream_interactions()])

    col = cm.get_cmap(palette, len(unique_labels))

    tot_x = {i: [] for i in range(len(unique_labels))}
    tot_y = {i: [] for i in range(len(unique_labels))}
    tot_means = []

    for j, cat_nodes in enumerate(categories):
        mean_vals = {i: [] for i in range(max_rng)}
        for n in cat_nodes:
            try:
                pl = delta_conf[str(n)]
            except:
                pl = []

            pld = {p[0] - (window - 1): p[1] for p in pl}
            pld = dict(sorted(pld.items(), key=lambda item: item[0]))
            pl_sl = list(pld.keys())
            pl_val = list(pld.values())

            tot_x[j].append(pl_sl)
            tot_y[j].append(pl_val)

            id_tmp = {i: np.nan for i in range(max_rng)}
            for k, idt in enumerate(pl_sl):
                id_tmp[idt] = pl_val[k]
            for k in range(max_rng):
                mean_vals[k].append(id_tmp[k])

        means = []
        for v in list(mean_vals.values()):
            vv = [el for el in v if np.logical_not(np.isnan(el))]
            means.append(np.mean(vv))
        tot_means.append(means)

    max_lim = 0
    min_lim = 0
    for kj in range(len(tot_x)):
        # points
        for jj, el in enumerate(tot_x[kj]):
            axs[kj].plot(el, tot_y[kj][jj], ':', c=col(kj), marker='o', alpha=alpha, ms=5.5)

            if tot_y[kj][jj] != []:
                if max(tot_y[kj][jj]) > max_lim:
                    max_lim = max(tot_y[kj][jj])
                if min(tot_y[kj][jj]) < min_lim:
                    min_lim = min(tot_y[kj][jj])

        axs[kj].legend([unique_labels[kj]], loc='best', fontsize=11)
        # mean val
        axs[kj].plot(range(len(tot_means[kj])), tot_means[kj], c='k', alpha=alpha)

        # viz stuff
        axs[kj].grid(alpha=0.4)
        for label in axs[kj].get_yticklabels():
            label.set_fontsize(16)

    # viz stuff
    axs[len(unique_labels) // 2].set_ylabel("Δ-conformity", fontsize=15, loc='bottom')
    plt.ylim((min_lim - 0.4, max_lim + 0.4))
    val_ticks = range(min_rng, max_rng, 2)

    if xticks != []:
        plt.xticks(val_ticks, xticks, fontsize=16)
    else:
        plt.xticks(val_ticks, fontsize=16)
    plt.xlim(min(val_ticks) - 0.3, max(val_ticks) + 0.3)
    # plt.tight_layout()

    if savefig == True:
        plt.savefig('subplots_hospital.png', bbox_inches='tight', pad_inches=0.1)
        plt.savefig('subplots_hospital.pdf', bbox_inches='tight', pad_inches=0.1)

    plt.show()

    return delta_conf, categories

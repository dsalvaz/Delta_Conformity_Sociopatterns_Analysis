import numpy as np
import dynetx as dn

'''
Formatting original Hospital Ward data for DyNetx
http://www.sociopatterns.org/datasets/hospital-ward-dynamic-contact-network/
'''

original_hospital_file = "hospital_ward/detailed_list_of_contacts_Hospital.dat"
new_aggregate_file = "hospital_ward/detailed_list_of_contacts_Hospital_format.dat"


def read_hospital_file(filename):
    g = dn.DynGraph()
    with open(filename) as f:
        for l in f:
            l = l.rsplit()
            g.add_interaction(int(l[1]), int(l[2]), int(l[0]))
            g.add_node(int(l[1]), lab=l[3])
            g.add_node(int(l[2]), lab=l[4])
    return g


def aggregate_and_save_hospital_network(g, num_aggr, file_orig, file_save):
    ids = g.temporal_snapshots_ids()
    #complete = [i for i in range(min(ids), max(ids)+20, 20)]
    complete = [i for i in range(0, max(ids) + 20, 20)]
    to_split_compl = np.array_split(complete, num_aggr)
    #to_split = [(min(el), max(el)) for el in to_split_compl]
    id_ids = {}
    for i, el in enumerate(to_split_compl):
        for n in el:
            id_ids[n] = i

    out = open(file_save, 'w')
    with open(file_orig) as f:
        for l in f:
            l = l.rsplit()
            aggr = int(id_ids[int(l[0])]) + 13
            out.write(str(aggr) + " " + str(l[1]) + " " + str(l[2]) + " " + str(l[3]) + " " + str(l[4]))
            out.write("\n")
    out.close()


def daily_aggregate_hospital(g):
    #ids = g.temporal_snapshots_ids()
    node_labs = dn.get_node_attributes(g, 'lab')

    # first_day = [i for i in range(12,25)]
    first_day = [i for i in range(13, 28)]
    # second_day = [i for i in range(25,49)]
    second_day = [i for i in range(29, 46)]
    # third_day = [i for i in range(49,73)]
    third_day = [i for i in range(53, 72)]
    # fourth_day = [i for i in range(73,97)]
    fourth_day = [i for i in range(73, 99)]
    # fifth_day = [i for i in range(97,109+1)]
    fifth_day = [i for i in range(100, 109 + 1)]
    week = [first_day, second_day, third_day, fourth_day, fifth_day]

    names = ['mond', 'tues', 'wed', 'thur', 'frid']
    for i in range(5):
        days = open("hospital_ward\\" + str(names[i]) + ".txt", 'w')
        for e in g.stream_interactions():
            if e[3] in week[i]:
                days.write(str(e[3]) + " " + str(e[0]) + " " + str(e[1]) + " " + str(node_labs[e[0]]) + " " + str(
                    node_labs[e[1]]))
                days.write("\n")
        days.close()


# read original file
g = read_hospital_file(original_hospital_file)
# aggregation
aggregate_and_save_hospital_network(g, 97, original_hospital_file, new_aggregate_file)

# read aggregated file
new_g = read_hospital_file(new_aggregate_file)
# daily disaggregation
daily_aggregate_hospital(new_g)
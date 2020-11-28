#!/usr/bin/env python

import networkx as nx

import sys

from random import sample

import random

import time

import os

import math

opt_cutoff = {'Data/karate.graph': 14, 'Data/football.graph': 94, 'Data/jazz.graph': 158, 'Data/email.graph': 594,
              'Data/delaunay_n10.graph': 703, 'Data/netscience.graph': 899, 'Data/power.graph': 2203,
              'Data/as-22july06.graph': 3303, 'Data/hep-th.graph': 3926, 'Data/star2.graph': 4542,
              'Data/star.graph': 6902}


# Read the graph file

def read_graph(filename):
    # Generate a graph to store input information

    G = nx.Graph()

    f = open(filename)

    line = f.readline()  # size of vertices; size of edges; 0

    values = line.split()

    values = [int(x) for x in values]

    NumOfVer, NumOfEdge = values[0], values[1]

    for i in range(NumOfVer):

        line = f.readline()  # read graph file line by line

        values = line.split()

        values = [int(x) for x in values]

        for j in range(len(values)):
            G.add_edge(i + 1, values[j])

    return G, NumOfVer


def isVC(VC, G):
    if VC is None or G is None:
        return False

    for x in G.edges():

        if (x[0] not in VC and x[1] not in VC):
            return False

    return True


def initial_solution(G, input_file):
    temp_G = G.nodes()
    VC = sorted(list(zip(list(G.degree(temp_G).values()), temp_G)))

    # SORTED MIN TO MAX DEGREE

    VC_sol = list(temp_G)

    i = 0

    while (i < len(VC) and len(VC_sol) > opt_cutoff[str(input_file)]):

        flag = True

        for x in G.neighbors(VC[i][0]):

            if x not in temp_G:
                flag = False

        if flag:
            temp_G.remove(VC[i][0])

        i = i + 1

    print('Initial Solution:' + str(len(temp_G)))

    return temp_G


# Apply Local Search using Simulate Annealing Algorithm

def simulate_annealing(G, output, sol, cutoff, randseed, NumOfVer, start_time, input_file):
    start_time1 = time.time()

    time_end = time.time() + int(cutoff) * 60

    temp = 0.15  # set initial temperature

    update_sol = sol.copy()

    random.seed(randseed)

    uncov_edges = []

    num_eges = G.number_of_edges()

    while ((time.time() - start_time1) < cutoff and len(update_sol) > opt_cutoff[str(input_file)]):

        temp = 0.95 * temp  # update temperature every n steps

        count = 0

        while count < (NumOfVer - len(update_sol) - 1) * (NumOfVer - len(update_sol) - 1) and len(update_sol) > \
                opt_cutoff[str(input_file)]:

            count += 1

            if ((time.time() - start_time1) < cutoff) and len(update_sol) > opt_cutoff[str(input_file)]:

                while not uncov_edges:

                    update_sol = sol.copy()

                    output.write(str(time.time() - start_time) + "," + str(len(update_sol)) + "\n")

                    delete = random.choice(sol)

                    for x in G.neighbors(delete):

                        if x not in sol:
                            uncov_edges.append((x, delete))

                            uncov_edges.append((delete, x))

                    sol.remove(delete)  # decrement the size of vertex cover to find better solution

                current = sol.copy()

                uncov_curr = uncov_edges.copy()

                delete = random.choice(sol)

                for x in G.neighbors(delete):

                    if x not in sol:
                        uncov_edges.append((x, delete))

                        uncov_edges.append((delete, x))

                sol.remove(delete)  # randomly select an exiting vertex

                enter = random.choice(uncov_edges)

                if enter[0] in sol:

                    better_add = enter[1]

                else:

                    better_add = enter[0]

                sol.append(better_add)

                for x in G.neighbors(better_add):

                    if x not in sol:
                        uncov_edges.remove((better_add, x))

                        uncov_edges.remove((x, better_add))

                cost_curr = len(uncov_curr) / 2

                cost_sol = len(uncov_edges) / 2

                if cost_curr < cost_sol:  # current solution is better

                    prob = math.exp(float(cost_curr - cost_sol) / float(temp))

                    num = round(random.uniform(0, 1), 10)

                    if num > prob:  # do not accept modified solution

                        sol = current.copy()

                        uncov_edges = uncov_curr.copy()

    return update_sol


def main(graph_file, output_dir, cutoff, randSeed):
    #
    # num_args = len(sys.argv)
    #
    #
    #
    # if num_args < 4:
    #
    #     print("error: not enough input arguments")
    #
    #     exit(1)

    randseed = int(randSeed)
    # solution_file = "Results3/" + graph_file[5:-6] + "_LS2_" + cutoff+ "_" + sys.argv[3] + ".sol"

    # trace_file = "Results3/" + graph_file[5:-6] + "_LS2_" + cutoff + "_" + sys.argv[3] + ".trace"

    solution_file = "Output/" + graph_file[5:-6] + "_LS2_" + str(cutoff) + "_" + str(randseed) + ".sol"

    trace_file = "Output/" + graph_file[5:-6] + "_LS2_" + str(cutoff) + "_" + str(randseed) + ".trace"
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    output2 = open(trace_file, 'w')

    G, NumOfVer = read_graph(graph_file)

    G1 = G.copy()

    start_time = time.time()

    print("start!")

    sol = initial_solution(G1, graph_file)

    output2.write('%.2f, %i\n' % (0, len(sol)))

    final_solution = simulate_annealing(G, output2, sol, cutoff, randseed, NumOfVer, start_time, graph_file)

    size = len(final_solution)

    print(size)

    total_time = (time.time() - start_time) * 1000

    # # Write results to output file

    output1 = open(solution_file, 'w')

    output1.write(str(size) + '\n')

    for vid in range(size - 1):
        output1.write(str(final_solution[vid]) + ',')

        output1.write(str(final_solution[vid + 1]))


if __name__ == '__main__':
    graph_file = sys.argv[1]

    cutoff = float(sys.argv[2])
    output_dir = ''
    randSeed = sys.argv[3]
    # #create parser; example: python Approx.py --datafile Data/karate.graph --cutoff_time 200 --seed 10
    #     parser=argparse.ArgumentParser(description='Input parser for Approx')
    #     parser.add_argument('--datafile',action='store',type=str,required=True,help='Inputgraph datafile')
    #     parser.add_argument('--cutoff_time',action='store',default=600,type=int,required=False,help='Cutoff running time for algorithm')
    #     parser.add_argument('--seed',action='store',default=1000,type=int,required=False,help='Random Seed for algorithm')
    #     args=parser.parse_args()
    #     graph_file = args.datafile
    #     output_dir = 'Results/'
    #     cutoff = float(args.cutoff_time)
    #     randSeed = int(args.seed)
    main(graph_file, output_dir, cutoff, randSeed)
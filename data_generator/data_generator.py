#!/usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
import networkx as nx
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from scipy.stats import poisson
from collections import deque
from bisect import bisect
from copy import deepcopy


class TimeoutILP(Exception):
    pass

def get_edge(raw_edge):

    parts = raw_edge.split()
    return int(parts[0]), int(parts[1]), float(parts[2])

def get_edges_from(raw_path):

    parts = raw_path.split()

    list_of_edges = [(int(parts[i]),int(parts[i+1])) for i in range(1,len(parts)-1)]

    return list_of_edges

def get_weights_from(raw_path):

    parts = raw_path.split()

    weights = float(parts[0])

    return weights;


def get_graph(raw_graph):

    graph = {
        'n': 0,
        'edges': list()
    }

    try:
        lines = raw_graph.split('\n')[1:]
        if not lines[-1]:
            lines = lines[:-1]
        graph['n'], graph['edges'] = int(lines[0]), [get_edge(raw_e) for raw_e in lines[1:]]

    finally:
        return graph

def get_path(raw_path):
    path = {
        'n': 0,
        'paths': list(),
        'weights': list()
    }

    try:
        lines = raw_path.split("\n")[1:]
        
        if not lines[-1]:
            lines = lines[:-1]
        path['n'] = len(lines)
        path['paths'] = [get_edges_from(raw_path) for raw_path in lines]
        path['weights'] = [get_weights_from(raw_path)for raw_path in lines]

    finally:
        return path

def read_input_graphs(graph_file):

    graphs_raw = open(graph_file, 'r').read().split('#')[1:]

    return [get_graph(raw_g) for raw_g in graphs_raw]

def read_input_ground_truth(ground_file):

    paths_raw = open(ground_file, 'r').read().split('#')[1:]
    
    return [get_path(raw_g) for raw_g in paths_raw]

def read_input_graph(graph_file):

    return read_input_graphs(graph_file)

def read_input_paths(ground_file):
    return read_input_ground_truth(ground_file)


def output_paths(output,paths,weights):
    
    numberOfPaths = len(paths)

    for nP in range(0,numberOfPaths):
        nodes = set()
        for (i,j,k) in paths[nP]:
            nodes.add(i)
            nodes.add(j)
        
        output.write(str(weights[nP]))
        for i in nodes:
            output.write(' '.join([' ',str(i)]))
        output.write('\n')

def compute_graph_metadata(graph):

    # creation of NetworkX Graph
    ngraph = nx.MultiDiGraph()
    ngraph.add_weighted_edges_from(graph['edges'], weight='flow')

    # calculating source, sinks
    sources = [x for x in ngraph.nodes if ngraph.in_degree(x) == 0]
    sinks = [x for x in ngraph.nodes if ngraph.out_degree(x) == 0]

    # definition of data
    return {
        'graph': ngraph,
        'sources': sources,
        'sinks': sinks,
        'max_flow_value': max(ngraph.edges(data='flow'), key=lambda e: e[-1])[-1] if len(ngraph.edges) > 0 else -1,
    }

def building_solutions(graphs,paths,robust_file,inexact_file, epsilon,output_stats=False):

    robust = open(robust_file, 'w+')
    inexact = open(inexact_file,'w+')

    for i in range(0,len(graphs)):
        edges_from_graph = set()
        edges = graphs[i]['edges']
        for (u,v,k) in edges:
            edges_from_graph.add((u,v,))
        
        path = paths[i]['paths']
        weight = paths[i]['weights']
        N = graphs[i]['n']

        robust.write(f'# graph {i}\n')
        robust.write(''.join(str(N)))
        robust.write('\n')

        inexact.write(f'# graph {i}\n')
        inexact.write(''.join(str(N)))
        inexact.write('\n')

        f = {}

        
        for (u,v) in edges_from_graph:
            f[u,v] = 0
            for k in range(0,len(path)):
                if (u,v) in path[k]:
                    f[u,v] += weight[k]
        

            flow_range = np.arange(poisson.ppf(0.5 - epsilon/2,f[u,v]),poisson.ppf(0.5 + epsilon/2,f[u,v]))

            if flow_range.any() == False:
                flow_range = [f[u,v]]

            flow_range_max = max(flow_range)
            flow_range_min = min(flow_range)
            
            inexact.write(' '.join([str(u),str(v),str(flow_range_min),str(flow_range_max)]))
            inexact.write('\n')

            distribution = poisson.pmf(flow_range,f[u,v])
            distribution = [value/np.sum(distribution) for value in distribution]

            newWeight = max(1.0,np.random.choice(flow_range,p=distribution,size=1)[0])
            
            robust.write(' '.join([str(u),str(v),str(newWeight)]))
            robust.write('\n')
    
    return 0
    
    


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''
        Generate inputs for inexact and imperfect flow models
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-stats', '--output-stats', action='store_true', help='Output stats to file <output>.stats')
    parser.add_argument('-wt', '--weighttype', type=str, default='int+',
                        help='Type of path weights (default int+):\n   int+ (positive non-zero ints), \n   float+ (positive non-zero floats).')
    parser.add_argument('-t', '--threads', type=int, default=0,
                        help='Number of threads to use for the Gurobi solver; use 0 for all threads (default 0).')
    parser.add_argument('-ilptb', '--ilp-time-budget', type=float, help='Maximum time (in seconds) that the ilp solver is allowed to take when computing safe paths for one graph')

    
 
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', '--input', type=str, help='Exact graph filename', required=True)
    requiredNamed.add_argument('-g', '--ground', type=str, help='Exact ground truth filename', required=True)
    requiredNamed.add_argument('-r', '--robust', type=str, help='Robust ground truth filename', required=True)
    requiredNamed.add_argument('-x', '--inexact', type=str, help='Inexafct ground truth filename', required=True)
    requiredNamed.add_argument('-e', '--epsilon', type=float,help='Epsilon precision',required=True)

    args = parser.parse_args()

    threads = args.threads
    if threads == 0:
        threads = os.cpu_count()
    print(f'INFO: Using {threads} threads for the Gurobi solver')

    ilp_counter = 0
    ilp_time_budget = args.ilp_time_budget
    time_budget = args.ilp_time_budget
    building_solutions(read_input_graph(args.input),read_input_paths(args.ground),args.robust,args.inexact,args.epsilon, args.output_stats)

import os
import sys
import argparse
import networkx as nx
import gurobipy as gp
from gurobipy import GRB
from collections import deque
from bisect import bisect
from copy import deepcopy


class TimeoutILP(Exception):
    pass


def get_edge(raw_edge):

    parts = raw_edge.split()
    return int(parts[0]), int(parts[1]), float(parts[2])

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


def read_input_graphs(graph_file):

    graphs_raw = open(graph_file, 'r').read().split('#')[1:]
    return [get_graph(raw_g) for raw_g in graphs_raw]

def read_safe_paths(safe_file):
    paths = open(safe_file,'r').read().split('\n')

    listOfGraphs = []
    i = 0

    while(True):
        if i >= len(paths):
            break;
        if "#" in paths[i]:
            
            # newgraph
            i = i + 1
            if i >= len(paths):
                break;
            if "" == paths[i]:
                break;

            # list of paths
            paths_list = []

            while(True):

                line = paths[i].split(" ")
                path = (line[1:len(line)])
                nodes = [eval(node) for node in path]
                edges_list = [[nodes[i], nodes[i + 1]]
                    for i in range(len(nodes) - 1)]
                
                paths_list.append(edges_list)

                i = i + 1
                if i >= len(paths):
                    break;
                if "#" in paths[i]:
                    break;
                if "" == paths[i]:
                    break;

            listOfGraphs.append(paths_list)    
        
    return listOfGraphs

def read_input(graph_file):

    return read_input_graphs(graph_file)


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

def get_ground_truth(raw_graph):

    graph = {
        'n': 0,
        'edges': list(),
        'paths': list(),
        'weights':list ()
    }

    edges_list = list()
    paths_list = list()
    weights_list = list()

    try:
        lines = raw_graph.split('\n')[1:]
        weights = 0
        paths = list()
        nodes = set()
        n = 0

        for i in range(0,len(lines)-1):

            weights = int(lines[i].split(" ")[0])
            paths = [int(i) for i in lines[i].split(" ")[1:-1]]
            edges = list(zip(paths,paths[1:]))

            paths_list.append(paths)
            weights_list.append(weights)
            edges_list.append(edges)
            [nodes.add(v) for v in paths]
            
        graph['n'] = len(nodes)
        graph['weights'] = weights_list
        graph['paths'] = paths_list
        graph['edges'] = edges_list

    finally:
        return graph

def read_graph_solution(ground_truth_file):
    
    graphs_raw = open(ground_truth_file, 'r').read().split('#')[1:]
    
    return [get_ground_truth(raw_g) for raw_g in graphs_raw]

def compareNumberOfPaths(truth_paths,solutions_paths):

    if len(truth_paths) == len(solutions_paths):
        return 1
    else:
        return 0

def comparePath(ground,solution):
    if len(ground) != len(solution):
        return 0
    else:
        for k in range(0,len(ground)):
            if ground[k] != solution[k]:
                return 0
        return 1
            

def compareSequenceOfEdges(truth_edges,solutions_edges):

    if len(truth_edges) != len(solutions_edges):
        return 0
    
    else:
        for ground_path in truth_edges:
            counter = 0
            for solution_path in solutions_edges:
                if comparePath(ground_path,solution_path):
                    counter = 1
                if counter ==1 :
                    break
            if counter == 0:
                return 0 
        return 1
    
def compareWeights(truth_weight,solution_weight):
    if truth_weight == solution_weight:
        return 1
    else:
        return 0
    
def compareSequenceOfEdgesandWeights(ground,solution):
    
    groundEdges = ground['edges']
    groundWeights = ground['weights']
    solutionEdges = solution['edges']
    solutionWeights = solution['weights']

    if (len(groundWeights) != len(solutionWeights)) and (len(groundEdges) != len(solutionEdges)):
        return 0

    else:
        
        for k in range(0,len(groundWeights)):
            counter = 0
            for k1 in range(0,len(solutionWeights)):
                if (comparePath(solutionEdges[k1],groundEdges[k]) and compareWeights(groundWeights[k],solutionWeights[k1])):
                    counter = 1
                if counter == 1:
                    break
            if counter == 0:
                return 0
        return 1

def compareSuperposition(ground,solution):

    groundEdges = ground['edges']
    groundWeights = ground['weights']
    solutionEdges = solution['edges']
    solutionWeights = solution['weights']

    if (len(groundWeights) != len(solutionWeights)) and (len(groundEdges) != len(solutionEdges)):
        return 0

    else:

        # building truth graph using networkx
        truthGraph = nx.DiGraph()
        for i in range(0,len(groundWeights)):
            for (u,v) in groundEdges[i]:
                if truthGraph.has_edge(u,v) == True:
                    truthGraph[u][v]['weight'] += groundWeights[i]
                else:
                    truthGraph.add_edge(u,v,weight=groundWeights[i])

        # building truth graph using networkx
        solutionGraph = nx.DiGraph()
        for i in range(0,len(solutionWeights)):
            for (u,v) in solutionEdges[i]:
                if solutionGraph.has_edge(u,v) == True:
                    solutionGraph[u][v]['weight'] += solutionWeights[i]
                else:
                    solutionGraph.add_edge(u,v,weight=solutionWeights[i])

        # compare metadat from truth and solution
        truthEdgeData = sorted(list(truthGraph.edges.data()))
        solutionEdgeData = sorted(list(solutionGraph.edges.data()))

        for i in range(0,len(truthEdgeData)):
            if truthEdgeData[i] != solutionEdgeData[i]:
                return 0

        return 1

def compare_instances(grounds,solutions,output_file, output_stats=False):

    Mextra = [0]*len(grounds)
    M1 = [0]*len(grounds)
    M2 = [0]*len(grounds)
    M3 = [0]*len(grounds)

    for k in range(0,len(grounds)):
        print("New graph",k)
        base = grounds[k]
        member = solutions[k]  

        # for all metrics: 1: sucess 0: failure

        # extra metrics - number of Paths
        Mextra[k] = compareNumberOfPaths(base['paths'],member['paths'])

        
        # compare M1 = superposition rule
        M1[k] = compareSuperposition(base,member)

        # compare M1 = path rule
        M2[k] = compareSequenceOfEdges(base['edges'],member['edges'])

        # compare M2 = path and weight rule
        M3[k] = compareSequenceOfEdgesandWeights(base,member)

        print(k,Mextra[k],M1[k],M2[k],M3[k])
   
    
    output = open(output_file, 'w+')
    
    metrics = {
        'M1': M1,
        'M2': M2,
        'M3': M3,
        'Mextra': Mextra
    }

    outputMetrics(output,metrics,len(grounds))

    return 0

def outputMetrics(output,metrics,K):

    for k in range(0,K):
        #print(str(metrics['M1'][k]))
        output.write(f'# graph {k}\n')
        M1 = metrics['M1'][k]
        M2 = metrics['M2'][k]
        M3 = metrics['M3'][k]
        output.write(f'{M1} {M2} {M3}')
        output.write('\n')

    return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''
        Compare the flow decomposition outputs from two different formulations.
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
    requiredNamed.add_argument('-i', '--input', type=str, help='Input filename', required=True)
    requiredNamed.add_argument('-o', '--output',type=str, help='Output filename', required=True)
    requiredNamed.add_argument('-p', '--compare',type=str,help='Comparative filename',required=True)
    args = parser.parse_args()

    threads = args.threads
    if threads == 0:
        threads = os.cpu_count()
    print(f'INFO: Using {threads} threads for the Gurobi solver')

    ilp_counter = 0
    ilp_time_budget = args.ilp_time_budget
    time_budget = args.ilp_time_budget
    compare_instances(read_graph_solution(args.input),read_graph_solution(args.compare),args.output, args.output_stats)
    #print(read_graph_solution(args.input))
    #print(read_graph_solution(args.compare))
    #read_comparative(args.compare)

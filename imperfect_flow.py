import os
import sys
import argparse
import networkx as nx
import gurobipy as gp
from gurobipy import GRB
from collections import deque
from bisect import bisect
from copy import deepcopy
import subprocess

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='''
        Computes paths for Minimum Robust Flow Decompositio using different formulations.
        This script uses the Gurobi ILP solver.
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-t', '--threads', type=int, default=0,
                        help='Number of threads to use for the Gurobi solver; use 0 for all threads (default 0).')

    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-ie', '--input', type=str, help='Input filename', required=True)
    requiredNamed.add_argument('-ii', '--input2', type=str, help='Input filename', required=True)

    args = parser.parse_args()

    threads = args.threads
    if threads == 0:
        threads = os.cpu_count()
    print(f'INFO: Using {threads} threads for the Gurobi solver')

    # call bounded
    bounded_command = ''.join(['python ./previous_formulation/imperfect_bounded.py -i ',str(args.input),' -o ./example_outputs/bounded.out'])
    subprocess.call(bounded_command, shell=True)

    # call least squares
    least_squares_command = ''.join(['python ./previous_formulation/imperfect_least_squares.py -i ',str(args.input),' -o ./example_outputs/least_squares.out'])
    subprocess.call(least_squares_command, shell=True)

    # call robust
    robust_command = ''.join(['python ./previous_formulation/imperfect_inexact.py -i ',str(args.input),' -o ./example_outputs/inexact.out'])
    subprocess.call(robust_command, shell=True)
    
    # call inexact
    robust_command = ''.join(['python ./imperfect_path_errors.py -i ',str(args.input2),'  -o ./example_outputs/path_erros.out'])
    subprocess.call(robust_command, shell=True)
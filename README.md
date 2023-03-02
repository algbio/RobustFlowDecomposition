# Robust Flow Decomposition
Flow Decomposition Under Uncertainty

MFD-Robust is a collective tool reporting paths for minimum flow decomposition (MFD) under uncertaint using integer linear programming, using different techniques such as bounded-error, inexact, least-squares and path-error.

It is composed of four different models to address MFD under uncertainty.

- Bounded - Error: given an imperfect flow network, find the minimum set of paths which allows imperfect flow values in each edge bounded by a budget $B$. It is the implementation of the model implemented in .


- Inexact: given an imperfect flow network, find the minimum set of paths considering that for each edge the flow level is limited within a fixed range;

- Least - Squares:  find the minimum flow decomposition based on minimizing the sum of flow errors in each edge;

- Path - Error: given an imperfect flow network, find a minimum flow decomposition that minimizes the error allowed in each path;

The following Figure highlights the different between methods:

<img src="https://github.com/algbio/MFD-ILP/raw/main/fd_cycles.png" width="900" height="550">


It also contains an evaluation module that calculates and compares their outputs with the  of in three metric:

- The superposition of the weighted paths matches the superposition of the ground truth paths (i.e., the original perfect flow);
- The output paths (as sequences of edges) are exactly the same as the ground truth paths;
- The output paths (as sequences of edges) are the same as the ground truth paths, and each path has the same weight as the corresponding ground truth path.


# Run

To run each model individually, simply try:

Bounded-Error: `python ./imperfect_bounded.py -i ./example_inputs/example.graph -o ./example.out`

Least-Squares: `python ./imperfect_least_squares.py -i ./example_inputs/example.graph -o ./example.out`

Path-Errors: `python ./imperfect_path_errors.py -i ./example_inputs/example.graph -o ./example.out`

Inexact: `python ./imperfect_inexact.py -i ./example_inputs/example_inexact.graph -o ./example.out`


To the run all methods together, try:

`python ./imperfect_flow.py -i ./example.graph -o ....`

## Input

- The input is a file containing a sequence of (directed) acyclic flow graphs separated by lines starting with `#`.
- The first line of each flow graph contains the number of vertices of the graph, after this every flow edge from vertex
`u` to  `v` carrying `f` flow is represented in a separated line in the format `u v f`.
- Vertices must be integers following a topological order of the graph.
- An example of such a format can be found in `./example_inputs/example.graph`.

## Output

- The output is a file containing a sequence of paths separated by lines starting with `#` (one per flow
graph in the input).
- Each line contains a path as the corresponding sequence of vertices, starting with their corresponding weight;
- An example of such a format can be found in `./example_output/example.out`.

## Parameters

For each individual formulation:

- `-i <path to input file>`. Mandatory.
- `-o <path to locate output>`. Mandatory.
- `-stats` Output stats to file <output>.stats
- `-t <n>` Use n threads for the Gurobi solver; use 0 for all threads (default 0).
- `-ilptb <n>` Maximum time (in seconds) that the ilp solver is allowed to take when computing safe paths for one flow graph.
If the solver takes more than n seconds, then safe for (all) flow decompositions is reported instead.

For the collective tool:

- `-i <path to input file>`. Mandatory.
- `-be <path to locate bounded error output>`. Mandatory.
- `-ls <path to locate least-squares output>`. Mandatory.
- `-ix <path to locate inexact output>`. Mandatory.
- `-pe <path to locate path error output>`. Mandatory.
- `-stats` Output stats to file <output>.stats
- `-t <n>` Use n threads for the Gurobi solver; use 0 for all threads (default 0).
- `-ilptb <n>` Maximum time (in seconds) that the ilp solver is allowed to take when computing safe paths for one flow graph.
If the solver takes more than n seconds, then safe for (all) flow decompositions is reported instead.


For the evaluation tool:



## Datasets

The datasets can be found in Zenodo at: [https://zenodo.org/record/](https://zenodo.org/record/)

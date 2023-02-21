# Robust
Flow Decomposition Under Uncertainty

MFD-Robust is a collective tool reporting paths for minimum flow decomposition (MFD) under uncertaint using integer linear programming, using different techniques such as
bounded-error, inexact, least-squares and path-error.

It is composed of four different models to address MFD under uncertainty.

- Bounded - Error:

- Inexact:

- Least - Squares:

- Path - Error:

It is contain an evaluation  

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
- `-uef` Uses excess flow to save ILP calls.
- `-uy2v` Use Y2V contraction on the flow graphs to reduce the ILP size.
- `-s/es/rs/ess/esl/rss/rsl {scan, bin_search, exp_search, rep_exp_search}` When running the two-finger algorithm applied
the specified strategy to extend/reduce the current safe interval.
- `-st/est/rst <n>` When running the two-finger algorithm run the `small strategy` when the search space is less than n
and the `large strategy` otherwise.
- `-ugtd/-ugbu` Run a group testing algorithm (top down or bottom up) instead of two-finger.

For the collective tool:


For the evaluation tool:


## Datasets

The datasets can be found in Zenodo at: [https://zenodo.org/record/](https://zenodo.org/record/)

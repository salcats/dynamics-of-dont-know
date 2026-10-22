# The dynamics of 'don't know'

Code behind my MEng thesis (University of Bristol, 2018, supervised by Dr
Jonathan Lawry and Dr Martin Homer). It extends the adaptive voter model — a
standard model of opinion dynamics on a co-evolving network — to include an
explicit uncertain belief state, random state changes representing noise, and
non-updating agents ("zealots") representing individual failure.

## Result

Including an uncertain belief state raises both the fault tolerance and the
noise tolerance of the model, and delays the network's fragmentation into
disconnected components. Analytical predictions agree with agent-based
simulation at N = 1000.

## What's here

**`AdaptiveVoterModel/`** — agent-based simulation. Uses the Doob–Gillespie
stochastic simulation algorithm, extended to handle a network topology that
changes as the simulation runs, which is substantially faster than rejection
sampling for this problem.

- `adaptiveVoterModel.py`, `exclusiveAdaptiveVoterModel.py` — the models
- `adaptiveVoterRunner.py` — command-line entry point
- `dataExtraction.py`, `dataVisualisation.py` — results handling and figures
- `adaptiveVoterExperiment.sh` — the parameter sweeps, run in parallel on the
  university's HPC cluster

**`OdeModels/`** — the analytical side. Moment-closure approximations reduce the
full stochastic process to a low-dimensional system; Markov jump process models
give the consensus time; and bifurcation analysis via Jacobian eigenvalues
locates the fragmentation threshold in parameter space. Binary and ternary
variants are handled separately, with and without mutually exclusive
propositions.

## Running it

```bash
pip install -r requirements.txt
cd AdaptiveVoterModel
python adaptiveVoterRunner.py --help
```

Modes of operation range from a single fixed-parameter run to parameter sweeps
over the interaction threshold, language size and rewiring rate, up to locating
the fragmentation transition. For example:

```bash
python adaptiveVoterRunner.py -m 2 -ag 15 -ll 5 -lu 20 -st 5000 \
    -rl 0.0 -ru 0.0 -or 0.01 -sc 0.0 -tl 0.0 -tu 1 -z 5 -e 1
```

See `adaptiveVoterExperiment.sh` for the sweeps used in the thesis.

## Built with

NumPy, SciPy, networkx, matplotlib.

## Note

This is 2018 code, written for Python 2. It's published as a record of the
thesis work rather than as a maintained package.

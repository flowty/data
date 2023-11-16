# Flowty Data

Data repository for creating and storing instance data for [examples](https://github.com/flowty/examples) the Flowty Network Optimization Solver.

The `data` folder contains instance data converted to DIMACS like formats for various graph problems.

The `src` folder contains the source code to download instance data from original sources and convert it. Install with

```py
pip install https://github.com/flowty/data
```

Usage

```py
flowty_convert --type mcf
```

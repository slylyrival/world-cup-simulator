# WORLD CUP SIMULATOR 5000

# Running the model
Run "run_model.py"

# Under the hood
## teams.py
This file defines the Team class, the 2026 WC teams, and their elos.

## groups.py
This file defines the Group class and a function to initialize the groups for the 2026 WC.

## generate_worlds.py
This file has a bunch of functions for doing game simulation, group stage simulation, and knockout stage simulation. 
It's called "generate_worlds" because at one point it was intended to be used to generate the many possible "worlds" of things that could happen at this world cup.
It is more generally just a "simulate.py" kind of file.

## scoring.py
This file contains a bunch of functions for scoring candidate simulations against the many possible worlds.

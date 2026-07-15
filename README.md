# WORLD CUP SIMULATOR 5000

# Running the model
Run "optimize_entry.py." Numbers of simulations can be adjusted in the first few lines of that module.

# Under the hood
## teams.py
This file defines the Team class, the 2026 WC teams, and their elos.

## groups.py
This file defines the Group class and a function to initialize the groups for the 2026 WC.

## simulation.py
This file has a bunch of functions for doing game simulation, group stage simulation, and knockout stage simulation. 

## scoring.py
This file contains a bunch of functions for scoring candidate simulations against the many possible worlds.

## optimize_entry.py
This file can be run as a script. It contains a bunch of functions for going through the process of making simulations of the 2026 World Cup and evaluating them to find the best entry for the pool.

## third_place_table.txt
This file was copied from Wikipedia and is parsed in order to create a mapping between the third place teams which advance to the knockout stage and their matchups with first place teams.

"""
Runs simulations of the 2026 Fifa World Cup and prints the highest EV entry.

function, command line syntax, environment variables, and files

This script runs simulations of the 2026 FIFA World Cup for Ace Ray's Pool
and prints the entry with the highest expected value against the scoring
criteria. The general procedure for the script is as follows:

    1. Simulate the tournament n number of times.
        These are the possible 'worlds' that could happen in reality.
    2. Evaluate the worlds' group stages to find the most common orders
    3. Set up combinations of group stages results by taking the most common
        group order for each group (1 possible group stage result) and then
        replace results for one group with the second most common (12
        possible group stage results).
    4. Simulate candidate knockout stages from each of the 13 group stage
        results defined in Step 3.
    5. Score each of the candidates in Step 4 against the Worlds from Step 1
        and select the candidate with the highest EV score.
"""

import sys
import pickle
import simulation
import scoring
from teams import make_team
from groups import Group

### GENERATE WORLDS ###
print("Generating possible worlds...")

n = 100000 # number of simulations
cnt = 0
simulated_tournaments = []

while cnt < n:
    entry = simulation.simulate_tournament()
    simulated_tournaments.append(entry)

    percent = round((cnt / n) * 100,2)
    sys.stdout.write(f'\rProgress: |{percent}|%')
    sys.stdout.flush()

    cnt += 1

with open("save_data.pkl", "wb") as file:
    pickle.dump(simulated_tournaments, file)


### GET BEST GROUP ORDERS ###
print("Getting best group orders...")
worlds = simulated_tournaments

best_group_orders = []

for g in range(12):
    best_orders = scoring.get_best_group_orders(g, worlds)[:3]
    best_group_orders.append(best_orders)

with open("best_group_orders.pkl", "wb") as file:
    pickle.dump(best_group_orders, file)



### GENERATE BETTER KNOCKOUT STAGES ###
print("Generating candidate tournaments from best group stages...")

rank_1_group_orders = []
rank_2_group_orders = []
rank_3_group_orders = []
group_orders = [rank_1_group_orders, rank_2_group_orders, rank_3_group_orders]

for group_num, group in enumerate(best_group_orders):
    group_name = "Group " + chr(group_num + 65)

    for rank in range(3):
        teams = []
        ordered_teams = group[rank][1]

        for i, team in enumerate(ordered_teams):
            teams.append(make_team(team))
        group_orders[rank].append(Group(group_name, teams))

group_permutations_to_simulate = []

# add list of best EV groups
group_permutations_to_simulate.append(group_orders[0])

# switch out one best EV group for 2nd best EV group
for i in range(12):
    new_group_list = group_orders[0].copy()
    new_group_list[i] = rank_2_group_orders[i]
    group_permutations_to_simulate.append(new_group_list)

for permutation in group_permutations_to_simulate:
    for group in permutation:
        for team in group.teams:
            team.group = group.name[-1]


n = 1000 # number of knockout stage simulations per group stage permutation

tourney_logs = []

for i, groups in enumerate(group_permutations_to_simulate):
    print("Group permutation ", i, " of ", len(group_permutations_to_simulate), "...")
    third_place_teams = simulation.get_random_third_place_teams(groups)
    cnt = 0
    while cnt < n:
        ko_results = simulation.simulate_knockout(groups, third_place_teams)
        tourney_log = simulation.get_tourney_log(groups, ko_results)
        tourney_logs.append(tourney_log)
        cnt += 1

with open("better_knockout_stages.pkl", "wb") as file:
    pickle.dump(tourney_logs, file)


### EVALUATE CANDIDATES AGAINST WORLDS ###
print("Evaluating candidates against worlds...")

tables = scoring.build_ev_tables(worlds)

best_entry = None
best_ev = 0

for i, candidate in enumerate(tourney_logs):
    ev = scoring.score_candidate_ev(candidate, tables)

    if ev > best_ev:
        best_ev = ev
        best_entry = candidate

    percent = round((i / len(tourney_logs)) * 100,2)
    sys.stdout.write(f'\rProgress: {percent}%')
    sys.stdout.flush()

with open("winning_candidate.pkl", "wb") as file:
    pickle.dump(best_entry, file)


print("\n")
print("EXPECTED SCORE: ", best_ev)
print("WINNING ENTRY: ")

for i, group in enumerate(best_entry[0]):
    print("GROUP", chr(i+65))
    for team in group:
        print(team)
    print("\n")

print("\n")
print("ADVANCING THIRD PLACE TEAMS IN ORDER")
print(best_entry[8])

print("\n")
print("ROUND OF 32 WINNERS")
for team in best_entry[1]:
    print(team)

print("\n")
print("ROUND OF 16 WINNERS")
for team in best_entry[2]:
    print(team)

print("\n")
print("QUARTERFINAL WINNERS")
for team in best_entry[3]:
    print(team)

print("\n")
print("SEMIFINAL WINNERS")
for team in best_entry[4]:
    print(team)

print("\n")
print("THIRD PLACE WINNER")
print(best_entry[5])

print("\n")
print("CHAMPION")
print(best_entry[6])
print("FINAL SCORE")
print(best_entry[7])

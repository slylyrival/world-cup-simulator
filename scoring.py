import pickle
import sys
import itertools
from collections import Counter, defaultdict


### CLANKER WROTE THIS SECTION ###
def build_ev_tables(worlds):
    n = len(worlds)

    group_pos = [[Counter() for _ in range(4)] for _ in range(12)]
    group_exact = [Counter() for _ in range(12)]

    ro32 = [Counter() for _ in range(16)]
    ro16 = [Counter() for _ in range(8)]
    qf = [Counter() for _ in range(4)]
    sf = [Counter() for _ in range(2)]

    third = Counter()
    champ = Counter()

    for world in worlds:
        groups = world[0]

        for g in range(12):
            order = tuple(groups[g])
            group_exact[g][order] += 1

            for pos in range(4):
                group_pos[g][pos][groups[g][pos]] += 1

        for i, team in enumerate(world[1]):
            ro32[i][team] += 1
        for i, team in enumerate(world[2]):
            ro16[i][team] += 1
        for i, team in enumerate(world[3]):
            qf[i][team] += 1
        for i, team in enumerate(world[4]):
            sf[i][team] += 1

        third[world[5]] += 1
        champ[world[6]] += 1

    return {
        "n": n,
        "group_pos": group_pos,
        "group_exact": group_exact,
        "ro32": ro32,
        "ro16": ro16,
        "qf": qf,
        "sf": sf,
        "third": third,
        "champ": champ,
    }

def score_candidate_ev(candidate, tables):
    n = tables["n"]
    ev = 0

    # Groups
    for g, group_order in enumerate(candidate[0]):
        group_order = tuple(group_order)

        for pos, team in enumerate(group_order):
            ev += tables["group_pos"][g][pos][team] / n

        ev += 3 * tables["group_exact"][g][group_order] / n

    # Knockouts
    for i, team in enumerate(candidate[1]):
        ev += 2 * tables["ro32"][i][team] / n

    for i, team in enumerate(candidate[2]):
        ev += 4 * tables["ro16"][i][team] / n

    for i, team in enumerate(candidate[3]):
        ev += 6 * tables["qf"][i][team] / n

    for i, team in enumerate(candidate[4]):
        ev += 8 * tables["sf"][i][team] / n

    ev += 2 * tables["third"][candidate[5]] / n
    ev += 16 * tables["champ"][candidate[6]] / n

    return ev
### END CLANKER WRITTEN SECTION ###


def score_group_stage(candidate, world):

    candidate_groups = candidate[0]
    world_groups = world[0]
    
    score = 0

    for j, candidate_group in enumerate(candidate_groups):
        group_score = 0
        for i in range(4):
            if candidate_group[i] == world_groups[j][i]:
                score += 1
                group_score += 1
        if group_score == 4:
            score +=3

    return score

def score_group(predicted, actual):
    score = 0
    correct_positions = 0

    for i in range(4):
        if predicted[i] == actual[i]:
            score += 1
            correct_positions += 1

    if correct_positions == 4:
        score += 3

    return score

def get_best_group_orders(group_index, worlds):
    actual_orders = [world[0][group_index] for world in worlds]

    teams = actual_orders[0]

    results = []

    for predicted_order in itertools.permutations(teams):
        total = 0

        for actual_order in actual_orders:
            total += score_group(predicted_order, actual_order)

        ev = total / len(actual_orders)
        results.append((ev, predicted_order))

    results.sort(reverse=True, key=lambda x: x[0])
    return results

def score_candidate(candidate, world):

    candidate_groups = candidate[0]
    world_groups = world[0]
    candidate_ro32_winners = candidate[1]
    world_ro32_winners = world[1]
    candidate_ro16_winners = candidate[2]
    world_ro16_winners = world[2]
    candidate_quarters_winners = candidate[3]
    world_quarters_winners = world[3]
    candidate_semi_winners = candidate[4]
    world_semi_winners = world[4]
    candidate_third_place = candidate[5]
    world_third_place = world[5]
    candidate_champion = candidate[6]
    world_champion = world[6]

    score = 0

    # Score group stage
    for j, candidate_group in enumerate(candidate_groups):
        group_score = 0
        for i in range(4):
            if candidate_group[i] == world_groups[j][i]:
                score += 1
                group_score += 1
        if group_score == 4:
            score +=3

    for i in range(16):
        if candidate_ro32_winners[i] == world_ro32_winners[i]:
            score += 2

    for i in range(8):
        if candidate_ro16_winners[i] == world_ro16_winners[i]:
            score += 4
    for i in range(4):
        if candidate_quarters_winners[i] == world_quarters_winners[i]:
            score += 6
    for i in range(2):
        if candidate_semi_winners[i] == world_semi_winners[i]:
            score += 8
    if candidate_third_place == world_third_place:
        score += 2
    if candidate_champion == world_champion:
        score += 16
    return score

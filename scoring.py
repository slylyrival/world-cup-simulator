"""
This module provides functions to evaluate and score world cup simulations.

Classes
-------
None

Functions
---------
build_ev_tables: take all the world simulations and build a table of points
    scored for group stage orders and knockout stage results
score_candidate_ev: get the expected value for the score of a candidate simulation
score_group: return the score of a predicted group against an "actual" group
get_best_group_orders: return the permutations of a groups teams sorted from
    highest ev to lowest ev

Other Objects
-------------
None

"""
import itertools
from collections import Counter

def build_ev_tables(
        worlds: list[list[list[list[str] | str | int]]]
) -> dict[str, list[list[Counter]] | list[Counter] | Counter]:
    """
    This function takes the logs of all the simulated tournament 'worlds' and
    calculates a dictionary of total points for each group stage order or team
    result that a candidate can score in.

    Parameters
    ----------
    worlds (list[list[list[list[str] | str | int]]]): A list of tourney_logs for
        all of the simulated tournaments

    Returns
    -------
    (dict) Total points for a candidate simulation to receive for each point
        scoring opportunity evaluated against all possible worlds
    """
    n = len(worlds)

    group_pos = [[Counter() for _ in range(4)] for _ in range(12)]
    group_exact = [Counter() for _ in range(12)]

    kos = (
            [Counter() for _ in range(16)],
            [Counter() for _ in range(8)],
            [Counter() for _ in range(4)],
            [Counter() for _ in range(2)],
            Counter(),
            Counter()
            )

    for world in worlds:
        groups = world[0]

        for g in range(12):
            order = tuple(groups[g])
            group_exact[g][order] += 1

            for pos in range(4):
                group_pos[g][pos][groups[g][pos]] += 1

        for i, team in enumerate(world[1]):
            kos[0][i][team] += 1
        for i, team in enumerate(world[2]):
            kos[1][i][team] += 1
        for i, team in enumerate(world[3]):
            kos[2][i][team] += 1
        for i, team in enumerate(world[4]):
            kos[3][i][team] += 1

        kos[4][world[5]] += 1
        kos[5][world[6]] += 1

    return {
        "n": n,
        "group_pos": group_pos,
        "group_exact": group_exact,
        "ro32": kos[0],
        "ro16": kos[1],
        "qf": kos[2],
        "sf": kos[3],
        "third": kos[4],
        "champ": kos[5],
    }

def score_candidate_ev(
    candidate: list[list[list[str] | str | int]],
    tables: dict
) -> int:
    """
    This function scores a candidate tournament log against the EV table.

    Parameters
    ----------
    candidate (list[list[list[str] | str | int]]): The tourney_log of the
        candidate tournament.
    
    Returns
    -------
    ev (int): the expected value of the score of the candidate entry.
    """
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

def score_group(predicted: list[str], actual: list[str]) -> int:
    """
    Return the group stage score for a given group order against an 'actual' order.

    Parameters
    ----------
    predicted (list[str]): a list of team names representing a possible permutation
        of group stage results
    actual (list[str]): a list of team names representing the actual results from
        a given simulation

    Returns
    -------
    score (int): the score of the predicted group order evaluated against the
        actual order
    """
    score = 0
    correct_positions = 0

    for i in range(4):
        if predicted[i] == actual[i]:
            score += 1
            correct_positions += 1

    if correct_positions == 4:
        score += 3

    return score

def get_best_group_orders(
    group_index: int,
    worlds: list[list[list[list[str] | str | int]]]
) -> list[tuple[int, list[str]]]:
    """
    Sort the permutations of a group's rankings by highest group stage EV.

    Parameters
    ----------
    group_index (int): an index for which group to evaluate (0=A, 1=B, etc.)
    worlds (list[list[list[list[str] | str | int]]]): a list of tourney logs for
        all simulated worlds

    Returns
    -------
    results (list[tuple[int, list[str]]]): A list of tuples containing the EV
        and a group ranking permutation for a given group, sorted highest EV
        to lowest EV.
    """
    actual_orders = [world[0][group_index] for world in worlds]

    results = []

    for predicted_order in itertools.permutations(actual_orders[0]):
        total = 0

        for actual_order in actual_orders:
            total += score_group(predicted_order, actual_order)

        ev = total / len(actual_orders)
        results.append((ev, predicted_order))

    results.sort(reverse=True, key=lambda x: x[0])

    return results

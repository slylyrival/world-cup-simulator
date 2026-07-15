"""Evaluate and score World Cup simulations."""

from collections import Counter
import itertools
from typing import TypedDict
from simulation import TournamentResults


class EVTable(TypedDict):
    """A table of total points based on evaluating world simulations used to score
    candidate entries.
    """

    n: int
    group_pos: list[list[Counter[str]]]
    group_exact: list[Counter[tuple[str, ...]]]
    ro32: list[Counter[str]]
    ro16: list[Counter[str]]
    qf: list[Counter[str]]
    sf: list[Counter[str]]
    third: Counter[str]
    champ: Counter[str]


def build_ev_tables(worlds: list[TournamentResults]) -> EVTable:
    """Build table of points earned for group rankings and knockout winners.

    This function takes the logs of all the simulated tournament 'worlds' and
    calculates a dictionary of total points for each group stage order or team
    result that a candidate can score in.

    Args:
        worlds: A list of tournament_logs for all of the simulated tournaments

    Returns:
        Total points for a candidate simulation to receive for each point
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
        Counter(),
    )

    for world in worlds:
        groups = world.group_rankings

        for g in range(12):
            order = tuple(groups[g])
            group_exact[g][order] += 1

            for pos in range(4):
                group_pos[g][pos][groups[g][pos]] += 1

        for i, team in enumerate(world.ro32_winners):
            kos[0][i][team] += 1
        for i, team in enumerate(world.ro16_winners):
            kos[1][i][team] += 1
        for i, team in enumerate(world.quarterfinal_winners):
            kos[2][i][team] += 1
        for i, team in enumerate(world.semifinal_winners):
            kos[3][i][team] += 1

        kos[4][world.third_place_winner] += 1
        kos[5][world.champion] += 1

    ev_table: EVTable = {
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

    return ev_table


def score_candidate_ev(candidate: TournamentResults, tables: EVTable) -> float:
    """Score a candidate tournament log against the EV table.

    Args:
        candidate: The log of the candidate tournament.
        tables: The table of expected values against which to score the candidate

    Returns:
        The expected value of the score of the candidate entry.
    """
    n = tables["n"]
    ev = 0

    # Groups

    for g, group_order in enumerate(candidate.group_rankings):
        group_order = tuple(group_order)

        for pos, team in enumerate(group_order):
            ev += tables["group_pos"][g][pos][team] / n

        ev += 3 * tables["group_exact"][g][group_order] / n

    # Knockouts

    for i, team in enumerate(candidate.ro32_winners):
        ev += 2 * tables["ro32"][i][team] / n

    for i, team in enumerate(candidate.ro16_winners):
        ev += 4 * tables["ro16"][i][team] / n

    for i, team in enumerate(candidate.quarterfinal_winners):
        ev += 6 * tables["qf"][i][team] / n

    for i, team in enumerate(candidate.semifinal_winners):
        ev += 8 * tables["sf"][i][team] / n

    ev += 2 * tables["third"][candidate.third_place_winner] / n
    ev += 16 * tables["champ"][candidate.champion] / n

    return ev


def score_group(predicted: tuple[str], actual: tuple[str]) -> int:
    """Return the group stage score for a given group order against an 'actual' order.

    Args:
        predicted: list of team names representing a possible permutation
            of group stage results
        actual: a list of team names representing the actual results from
            a given simulation
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
    group_index: int, worlds: list[TournamentResults]
) -> list[tuple[float, tuple[str]]]:
    """Sort the permutations of a group's rankings by highest group stage EV.

    Args:
        group_index: an index for which group to evaluate (0=A, 1=B, etc.)
        worlds: a list of tournament logs for all simulated worlds

    Returns:
        The EV and a group ranking permutation for a given group, sorted
            highest EV to lowest EV.
    """
    actual_orders = [world.group_rankings[group_index] for world in worlds]

    results = []

    for predicted_order in itertools.permutations(actual_orders[0]):
        total = 0

        for actual_order in actual_orders:
            total += score_group(predicted_order, actual_order)

        ev = total / len(actual_orders)
        results.append((ev, predicted_order))

    results.sort(reverse=True, key=lambda x: x[0])

    return results

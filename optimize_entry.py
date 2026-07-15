"""Generate and evaluate candidate entries for the World Cup prediction pool."""

import pickle
import sys

from groups import Group
import scoring
import simulation
from simulation import TournamentResults
from teams import make_team


NUM_WORLD_SIMULATIONS = 100_000
NUM_KNOCKOUT_SIMULATIONS = 1_000  # per group stage


def main() -> None:
    """
    Run simulations of the 2026 FIFA World Cup and prints the highest EV entry.

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

    worlds = generate_worlds(NUM_WORLD_SIMULATIONS)
    best_group_orders = get_best_group_orders(worlds)
    group_permutations = build_group_permutations(best_group_orders)
    candidates = generate_candidate_logs(
        group_permutations,
        NUM_KNOCKOUT_SIMULATIONS,
    )
    best_entry, best_ev = find_best_candidate(candidates, worlds)
    print_entry(best_entry, best_ev)


def generate_worlds(num_simulations: int) -> list[TournamentResults]:
    """Generate possible tournament outcomes."""

    print("Generating possible worlds...")

    simulation_count = 0
    simulated_tournaments = []

    while simulation_count < NUM_WORLD_SIMULATIONS:
        entry = simulation.simulate_tournament()
        simulated_tournaments.append(entry)

        percent = round(((simulation_count + 1) / NUM_WORLD_SIMULATIONS) * 100, 2)
        sys.stdout.write(f"\rProgress: {percent}%")
        sys.stdout.flush()

        simulation_count += 1

    print("\n")

    with open("save_data.pkl", "wb") as file:
        pickle.dump(simulated_tournaments, file)

    return simulated_tournaments


def get_best_group_orders(worlds: list[TournamentResults]) -> list[...]:
    """Get best group orders."""

    print("Getting best group orders...")

    best_group_orders = []

    for group_index in range(12):
        best_orders = scoring.get_best_group_orders(group_index, worlds)[:3]
        best_group_orders.append(best_orders)

    with open("best_group_orders.pkl", "wb") as file:
        pickle.dump(best_group_orders, file)

    return best_group_orders


def build_group_permutations(best_group_orders: list[...]) -> list[list[Group]]:
    """Build group stage result permutations for better knockout stages."""

    rank_1_group_orders = []
    rank_2_group_orders = []
    rank_3_group_orders = []
    group_orders = [rank_1_group_orders, rank_2_group_orders, rank_3_group_orders]

    for group_index, group in enumerate(best_group_orders):
        group_name = "Group " + chr(group_index + 65)

        for rank in range(3):
            ordered_teams = group[rank][1]
            teams = [make_team(team_name) for team_name in ordered_teams]
            group_orders[rank].append(Group(group_name, teams))

    group_permutations_to_simulate = []

    group_permutations_to_simulate.append(group_orders[0])

    # Switch out one best EV group for 2nd best EV group.
    for group_index in range(12):
        new_group_list = group_orders[0].copy()
        new_group_list[group_index] = rank_2_group_orders[group_index]
        group_permutations_to_simulate.append(new_group_list)

    for permutation in group_permutations_to_simulate:
        for group in permutation:
            for team in group.teams:
                team.group = group.name[-1]

    return group_permutations_to_simulate


def generate_candidate_logs(
    group_permutations: list[list[Group]],
    num_simulations: int,
) -> list[TournamentResults]:
    """Simulate knockout stages and get tournament logs from best group stages."""

    tournament_logs = []

    print("Generating candidate tournaments from best group stages...")

    for i, groups in enumerate(group_permutations):
        print("Group permutation ", i, " of ", len(group_permutations), "...")
        third_place_teams = simulation.get_random_third_place_teams(groups)
        knockout_simulation_count = 0
        while knockout_simulation_count < num_simulations:
            ko_results = simulation.simulate_knockout(groups, third_place_teams)
            tournament_log = simulation.get_tournament_log(groups, ko_results)
            tournament_logs.append(tournament_log)
            knockout_simulation_count += 1

    with open("better_knockout_stages.pkl", "wb") as file:
        pickle.dump(tournament_logs, file)

    return tournament_logs


def find_best_candidate(
    candidates: list[TournamentResults],
    worlds: list[TournamentResults],
) -> tuple[TournamentResults, float]:
    """Evaluate candidates against worlds."""

    print("Evaluating candidates against worlds...")

    tables = scoring.build_ev_tables(worlds)

    if not candidates:
        raise RuntimeError("No candidate tournament logs were generated")

    best_entry = candidates[0]
    best_ev = scoring.score_candidate_ev(best_entry, tables)

    for i, candidate in enumerate(candidates):
        ev = scoring.score_candidate_ev(candidate, tables)

        if ev > best_ev:
            best_ev = ev
            best_entry = candidate

        percent = round((i / len(candidates)) * 100, 2)
        sys.stdout.write(f"\rProgress: {percent}%")
        sys.stdout.flush()

    with open("winning_candidate.pkl", "wb") as file:
        pickle.dump(best_entry, file)

    return tuple([best_entry, best_ev])


def print_entry(entry: TournamentResults, expected_score: float) -> None:
    """Print tournament log of best entry to be used in submission."""

    print("\n")
    print("EXPECTED SCORE: ", expected_score)
    print("WINNING ENTRY: ")

    for i, group in enumerate(entry.group_rankings):
        print("GROUP", chr(i + 65))
        for team in group:
            print(team)
        print("\n")

    print("\n")
    print("ADVANCING THIRD PLACE TEAMS IN ORDER")
    print(entry.third_place_advancers)

    print("\n")
    print("ROUND OF 32 WINNERS")
    for team in entry.ro32_winners:
        print(team)

    print("\n")
    print("ROUND OF 16 WINNERS")
    for team in entry.ro16_winners:
        print(team)

    print("\n")
    print("QUARTERFINAL WINNERS")
    for team in entry.quarterfinal_winners:
        print(team)

    print("\n")
    print("SEMIFINAL WINNERS")
    for team in entry.semifinal_winners:
        print(team)

    print("\n")
    print("THIRD PLACE WINNER")
    print(entry.third_place_winner)

    print("\n")
    print("CHAMPION")
    print(entry.champion)
    print("FINAL SCORE")
    print(entry.final_scoreline)


if __name__ == "__main__":
    main()

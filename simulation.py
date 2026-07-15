"""Simulate World Cup matches, groups, knockout rounds, and tournaments."""

from dataclasses import dataclass
import math
from pathlib import Path
import random

from teams import Team
from groups import Group, initialize_groups


@dataclass
class KnockoutResults:
    """The winners of each match in the knockout stage of the World Cup."""

    ro32_winners: list[Team]
    third_place_teams: list[Team]
    ro16_winners: list[Team]
    quarters_winners: list[Team]
    semi_winners: list[Team]
    third_place: Team
    final_scoreline: tuple[int, int]
    champion: Team


@dataclass
class TournamentResults:
    """The WC group stage results, 3rd place advancers, and knockout stage results."""

    group_rankings: list[list[str]]
    third_place_advancers: list[str]
    ro32_winners: list[str]
    ro16_winners: list[str]
    quarterfinal_winners: list[str]
    semifinal_winners: list[str]
    third_place_winner: str
    champion: str
    final_scoreline: tuple[int, int]


# Expected goals scored by a team given by lambda = MU * e^(K*delta)
# delta: elo difference between teams
# MU: Baseline goals scored per team given equal elo
# K: Sensitivity to elo differences. Bigger K means better team is more dominant
# MU and K are constant across teams and matchups.
MU = 1.35
K = 0.5

THIRD_PLACE_TABLE_PATH = Path(__file__).with_name("third_place_table.txt")

THIRD_PLACE_DICT: dict[frozenset[str], list[str]] = {}
with THIRD_PLACE_TABLE_PATH.open(encoding="utf-8") as f:
    for line in f:
        x = line.split()
        advancing_groups = frozenset(x[1:9])
        ordered_matchups = [g[-1] for g in x[9:17]]
        THIRD_PLACE_DICT[advancing_groups] = ordered_matchups


def simulate_match(teams: list[Team]) -> tuple[int, int]:
    """Simulate a match between two teams.

    Args:
        teams : the two teams in a match.

    Returns:
        The scoreline of the match, e.g. (2, 0).
    """

    delta = (teams[0].elo - teams[1].elo) / 400
    lambdas = (MU * math.exp(K * delta), MU * math.exp(-1 * K * delta))

    p_goals = [[], []]

    # Probabilities of teams scoring up to this many goals are calculated.
    max_goals = 6

    for i in range(max_goals):  # calculate probabilities up to 6 goals
        p_goals[0].append(
            (math.exp(-lambdas[0]) * (lambdas[0] ** i)) / math.factorial(i)
        )
        p_goals[1].append(
            (math.exp(-lambdas[1]) * (lambdas[1] ** i)) / math.factorial(i)
        )

    # Create cumulative density functions for goals scored by each team.

    cdf_goals = [[], []]
    cdf_goals[0] = [sum(p_goals[0][0 : x + 1]) for x in range(6)]
    cdf_goals[1] = [sum(p_goals[1][0 : x + 1]) for x in range(6)]

    cdf_goals_normed = [[], []]
    cdf_goals_normed[0] = [x / sum(p_goals[0]) for x in cdf_goals[0]]
    cdf_goals_normed[1] = [x / sum(p_goals[1]) for x in cdf_goals[1]]

    # Simulated goals scored by each team.
    rand_goals = [random.random(), random.random()]

    scoreline = [None, None]

    for i in range(max_goals):
        if scoreline[0] is None and rand_goals[0] < cdf_goals_normed[0][i]:
            scoreline[0] = i
        if scoreline[1] is None and rand_goals[1] < cdf_goals_normed[1][i]:
            scoreline[1] = i
        if scoreline[0] is not None and scoreline[1] is not None:
            break

    assert scoreline[0] is not None
    assert scoreline[1] is not None

    return tuple(scoreline)


def simulate_group(group: Group) -> Group:
    """Simulate a single group's matches at the World Cup.

    Args:
        group: the initialized group to be simulated.

    Returns:
        The group with final statistics and teams ranked.
    """
    pairings = [
        [group.teams[0], group.teams[1]],
        [group.teams[0], group.teams[2]],
        [group.teams[0], group.teams[3]],
        [group.teams[1], group.teams[2]],
        [group.teams[1], group.teams[3]],
        [group.teams[2], group.teams[3]],
    ]

    for matchup in pairings:
        scoreline = simulate_match(matchup)
        add_group_match_results(matchup[0], matchup[1], scoreline)

    group.sort_group()

    return group


def add_group_match_results(
    team1: Team, team2: Team, scoreline: tuple[int, int]
) -> None:
    """Update the teams' PTS, GF, and GA attributes after a match.

    Args:
        team1: the first team in the matchup
        team2: the second team in the matchup
        scoreline: the result of the match between the two teams, e.g. (2, 0)
    """

    team1.gf += scoreline[0]
    team1.ga += scoreline[1]
    team2.gf += scoreline[1]
    team2.ga += scoreline[0]

    if scoreline[0] > scoreline[1]:
        team1.pts += 3
    elif scoreline[1] > scoreline[0]:
        team2.pts += 3
    else:
        team1.pts += 1
        team2.pts += 1


def print_group_results(group: Group) -> None:
    """Print a group's current standings.

    Args:
        group: the group to be printed
    """
    print(group.name)
    print("\n")
    for team in group.teams:
        print(team.name, ": ", team.pts, " PTS, ", team.gf, " GF, ", team.ga, " GA")
    print("\n")


def get_third_place_teams(groups: list[Group]) -> list[Team]:
    """Determine which third place teams will advance from the group stage to knockout.

    Given the final group stage results, return the list of third-place
    teams that will advance to play the first-place teams in the Round of 32. The list
    of 3rd place teams is ordered by matchup assignment. In order, the teams will play
    the first place team from A, B, D, E, G, I, K, L.

    Args:
        groups: all simulated groups at the end of the group stage, ordered from A-L.

    Returns:
        Third place advancing teams in matchup order playing the first place teams from
            A, B, D, E, G, I, K, L.
    """

    third_place_teams = [group.teams[2] for group in groups]

    # GD, GF, GA, and coinflip are used as tie-breaking criteria.
    # Team conduct is not currently in the model, so it is not used.

    sorted_third_place_teams = sorted(
        third_place_teams,
        key=lambda team: (team.pts, team.gd, team.gf, -team.ga, random.random()),
        reverse=True,
    )

    top_eight = frozenset([team.group for team in sorted_third_place_teams[0:8]])

    # ordered_groups is the group IDs that will play 1A,1B,1D,1E,1G,1I,1K,1L.
    # For example, if EFGHIJKL advance, then it is [E,J,I,F,H,G,L,K].
    # Then, ordered_teams makes the list of appropriate teams.

    ordered_groups = THIRD_PLACE_DICT[top_eight]

    ordered_teams = [third_place_teams[ord(group) - 65] for group in ordered_groups]

    return ordered_teams


def get_random_third_place_teams(groups: list[Group]) -> list[Team]:
    """Return randomly selected third place teams to advance to KO stage.

    Given a list of groups that have been ordered but not actually simulated,
    return a random list of eight third place teams that will advance to play
    the first-place teams from A,B,D,E,G,I,K,L. After the best group stage orders have
    been determined and the knockout stage needs to be simulated, without full points
    and goals data the top eight third place teams cannot be determined. This function
    is used to randomly select eight third place teams to advance and put them in
    matchup assignment order.

    Args:
        groups (list[Group]): the list of all groups ordered from A-L.
    """

    third_place_teams = [group.teams[2] for group in groups]

    sorted_third_place_teams = third_place_teams.copy()
    random.shuffle(sorted_third_place_teams)

    top_eight = frozenset([x.group for x in sorted_third_place_teams[0:8]])

    ordered_groups = THIRD_PLACE_DICT[top_eight]

    ordered_teams = [third_place_teams[ord(group) - 65] for group in ordered_groups]

    return ordered_teams


def get_ro32_teams(groups: list[Group], third_place_teams: list[Team]) -> list[Team]:
    """Return the 32 teams advancing to the round of 32 of the World Cup.

    The list of 32 teams is formed such that 2n and 2n+1 play each other for n=0:16.
    For example, ro32_teams[0] and ro32_teams[1] play each other, ro32_teams[14] and
    ro32_teams[15] play each other, etc.

    Args:
        groups: all simulated groups ordered from A-L.
        third_place_teams: third-place teams in matchup order playing the first
            place teams from A, B, D, E,G, I, K, L.

    Returns:
        The Ro32 teams.
    """

    ro32_teams = [
        # 1E vs A/B/C/D/F3
        groups[4].teams[0],
        third_place_teams[3],
        # 1I vs C/D/F/G/H3
        groups[8].teams[0],
        third_place_teams[5],
        # 2A vs 2B
        groups[0].teams[1],
        groups[1].teams[1],
        # 1F vs 2C
        groups[5].teams[0],
        groups[2].teams[1],
        # 2K vs 2L
        groups[10].teams[1],
        groups[11].teams[1],
        # 1H vs 2J
        groups[7].teams[0],
        groups[9].teams[1],
        # 1D vs B/E/F/I/J3
        groups[3].teams[0],
        third_place_teams[2],
        # 1G vs A/E/H/I/J3
        groups[6].teams[0],
        third_place_teams[4],
        # 1C vs 2F
        groups[2].teams[0],
        groups[5].teams[1],
        # 2E vs 2I
        groups[4].teams[1],
        groups[8].teams[1],
        # 1A vs C/E/F/H/I3
        groups[0].teams[0],
        third_place_teams[0],
        # 1L vs E/H/I/J/K3
        groups[11].teams[0],
        third_place_teams[7],
        # 1J vs 2
        groups[9].teams[0],
        groups[7].teams[1],
        # 2D vs 2G
        groups[3].teams[1],
        groups[6].teams[1],
        # 1B vs E/F/G/I/J3
        groups[1].teams[0],
        third_place_teams[1],
        # 1K vs D/E/I/J/L3
        groups[10].teams[0],
        third_place_teams[6],
    ]

    return ro32_teams


def get_ko_round_winners(teams: list[Team]) -> list[Team]:
    """Simulate fixtures between teams in a knockout round and return winners.

    Args:
        teams: the teams in the knockout round, where 2n and 2n+1 play each other

    Returns:
        The winners in the knockout round, where 2n and 2n+1 play each other in the next
            round
    """

    winners = []

    for n in range(len(teams) // 2):
        matchup = [teams[2 * n], teams[2 * n + 1]]
        score = simulate_match(matchup)
        winners.append(matchup[get_knockout_winner(score)])

    return winners


def get_knockout_winner(score: tuple[int, int]) -> int:
    """From the scoreline of a match, return the index of the winner in the matchup.

    Args:
        score: the scoreline of a fixture, e.g. (2, 0).

    Returns:
        The index of the winner in a matchup, either 0 or 1.
    """

    # If the score is a draw, just coinflip for the winner.
    # No logic for which team is better at penalties is implemented.

    if score[0] == score[1]:
        coinflip = random.random()
        if coinflip < 0.5:
            winner = 0
        else:
            winner = 1
    elif score[0] > score[1]:
        winner = 0
    else:
        winner = 1

    return winner


def simulate_knockout(
    groups: list[Group], third_place_teams: list[Team]
) -> KnockoutResults:
    """Simulate the knockout stage of the World Cup.

    Args:
        groups: all simulated groups ordered from A-L.
        third_place_teams: the third-place teams in order playing the first place
            teams from A,B,D,E,G,I,K,L.

    Returns:
        A log of top-level results of the knockout stage.
    """

    ro32_teams = get_ro32_teams(groups, third_place_teams)
    ro32_winners = get_ko_round_winners(ro32_teams)
    ro16_winners = get_ko_round_winners(ro32_winners)
    quarters_winners = get_ko_round_winners(ro16_winners)
    semi_winners = get_ko_round_winners(quarters_winners)
    semi_losers = [team for team in quarters_winners if team not in semi_winners]
    third_place_scoreline = simulate_match(semi_losers)
    third_place = semi_losers[get_knockout_winner(third_place_scoreline)]
    final_scoreline = simulate_match(semi_winners)
    champion = semi_winners[get_knockout_winner(final_scoreline)]

    knockout_log = KnockoutResults(
        ro32_winners=ro32_winners,
        third_place_teams=third_place_teams,
        ro16_winners=ro16_winners,
        quarters_winners=quarters_winners,
        semi_winners=semi_winners,
        third_place=third_place,
        final_scoreline=final_scoreline,
        champion=champion,
    )

    return knockout_log


def simulate_tournament() -> TournamentResults:
    """Initialize all World Cup groups and simulate the entire tournament.

    Returns:
        A log of the top-level results of the entire tournament.
    """

    groups = [simulate_group(g) for g in initialize_groups()]

    knockout_results = simulate_knockout(groups, get_third_place_teams(groups))

    tournament_log = get_tournament_log(groups, knockout_results)

    return tournament_log


def get_tournament_log(
    groups: list[Group],
    knockout_results: KnockoutResults,
) -> TournamentResults:
    """Construct a log of the group stage and knockout stage results for the
        entire simulated World Cup.

    Args:
        groups: all simulated groups ordered from A-L.
        knockout_results (KnockoutResults): a log of top-level results of the knockout stage

    Returns:
        A log of the relevant results of the entire tournament
    """
    group_rankings = [[team.name for team in group.teams] for group in groups]
    third_place_advancers = [team.name for team in knockout_results.third_place_teams]
    ro32_winners = [team.name for team in knockout_results.ro32_winners]
    ro16_winners = [team.name for team in knockout_results.ro16_winners]
    quarterfinal_winners = [team.name for team in knockout_results.quarters_winners]
    semifinal_winners = [team.name for team in knockout_results.semi_winners]
    third_place_winner = knockout_results.third_place.name
    final_scoreline = knockout_results.final_scoreline
    champion = knockout_results.champion.name

    tournament_log = TournamentResults(
        group_rankings=group_rankings,
        third_place_advancers=third_place_advancers,
        ro32_winners=ro32_winners,
        ro16_winners=ro16_winners,
        quarterfinal_winners=quarterfinal_winners,
        semifinal_winners=semifinal_winners,
        third_place_winner=third_place_winner,
        champion=champion,
        final_scoreline=final_scoreline,
    )

    return tournament_log

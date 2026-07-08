"""
Perform simulations of world cup matches, group stages, and knockout rounds.

Classes
-------
None

Functions
---------
simulate_game: return the scoreline for a game between two teams
simulate_group: simulate all group stage games in a group
add_group_game_results: update teams' attributes after fixture
print_group_results: print a group's current standings
get_third_place_teams: get list of advancing third place teams
get_random_third_place_teams: get random list of advancing third place teams
get_ro32_teams: returns list of the round of 32 teams
get_ko_round_winners: simulate a knockout round and return winners
get_knockout_winner: return either 0 or 1 based on scoreline
simulate_knockout: simulate the knockout stage of the world cup
simulate_tournament: simulate the entire world cup
get_tourney_log: construct a log of the results of the simulated WC


Other Objects
-------------
THIRD_PLACE_DICT (dict): a dictionary with the set of advancing third place
    teams as keys and an ordered list of those teams as values

"""


import math
import time
import random
import pickle

from groups import *

# Expected goals scored by a team given by lambda = MU * e^(K*delta)
# delta: elo difference between teams
# MU: Baseline goals scored per team given equal elo
# K: Sensitivity to elo differences. Bigger K means better team is more dominant
# MU and K are constant across teams and matchups.
MU = 1.35
K = 0.5


THIRD_PLACE_DICT = {}
with open("third_place_table.txt") as f:
    for line in f:
        x = line.split()
        advancing_groups = frozenset(x[1:9])
        ordered_matchups = [g[-1] for g in x[9:17]]
        THIRD_PLACE_DICT[advancing_groups] = ordered_matchups

def simulate_game(teams: list[Team]) -> list[int]:
    """
    Return the scoreline for a simulated game between two teams.

    Parameters
    ----------
    teams (list[Team]): a list of two teams playing a match

    Returns
    -------
    scoreline (list[int]): a list of the teams' scores, e.g. [2,0]

    """

    team_a = teams[0]
    team_b = teams[1]

    delta = (team_a.elo - team_b.elo)/400
    lambda_a = MU * math.exp(K*delta)
    lambda_b = MU * math.exp(-1*K*delta)

    p_goals_a = []
    p_goals_b = []

    # Probabilities of teams scoring up to this many goals are calculated.
    max_goals = 6

    for i in range(max_goals): # calculate probabilities up to 6 goals
        p_goals_a.append((math.exp(-lambda_a) * (lambda_a ** i))/math.factorial(i))
        p_goals_b.append((math.exp(-lambda_b) * (lambda_b ** i))/math.factorial(i))

    # Create cumulative density functions for goals scored by each team.

    cdf_goals_a_unnorm = [sum(p_goals_a[0:x+1]) for x in range(6)]
    cdf_goals_b_unnorm = [sum(p_goals_b[0:x+1]) for x in range(6)]
    cdf_goals_a = [x / sum(p_goals_a) for x in cdf_goals_a_unnorm]
    cdf_goals_b = [x / sum(p_goals_b) for x in cdf_goals_b_unnorm]
    
    # Simulated goals scored by each team.
    rand_goals_a = random.random()
    rand_goals_b = random.random()

    num_goals_a = None
    num_goals_b = None

    for i in range(max_goals):
        if not num_goals_a and rand_goals_a < cdf_goals_a[i]:
            num_goals_a = i
        if not num_goals_b and rand_goals_b < cdf_goals_b[i]:
            num_goals_b = i
        if num_goals_a and num_goals_b:
            break

    scoreline = [num_goals_a, num_goals_b]

    return scoreline

def simulate_group(group: Group) -> Group:
    """
    Return the final group stage results for a group.

    Parameters
    ----------
    group (Group): the initialized group to be simulated

    Returns
    -------
    group (Group): the group with all teams points and tie-breakers simulated
        and sorted
    """
    pts_team1 = 0
    pts_team2 = 0
    pts_team3 = 0
    pts_team4 = 0

    pairings = [[group.team1, group.team2],
                [group.team1, group.team3],
                [group.team1, group.team4],
                [group.team2, group.team3],
                [group.team2, group.team4],
                [group.team3, group.team4]]

    for matchup in pairings:
        scoreline = simulate_game(matchup)
        add_group_game_results(matchup[0], matchup[1], scoreline)

    group.sort_group()

    return group

def add_group_game_results(
    team1: Team,
    team2: Team,
    scoreline: list[int]
) -> None:
    """
    Update the teams' PTS, GF, and GA attributes after a match.

    Parameters
    ----------
    team1 (Team): the first team in the matchup
    team2 (Team): the second team in the matchup
    scoreline (list[int]): the scoreline between the two teams, e.g. [2,0]

    Returns
    -------
    None
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
    """
    Print a group's current standings.

    Parameters
    ----------
    group (Group): the group to be printed

    Returns
    -------
    None

    """
    print(group.name)
    print("\n")
    for team in group.teams:
        print(team.name, ": ",
              team.pts, " PTS, ",
              team.gf, " GF, ",
              team.ga, " GA")
    print("\n")


def get_third_place_teams(groups: list[Group]) -> list[Team]:
    """
    Given the final group stage results, return the ordered list of third-place
    teams that will advance to play the first-place teams from A,B,D,E,G,I,K,L.

    Parameters
    ----------
    groups (list[Group]): the list of all simulated groups after all groups
        have been simulated, ordered from A-L.

    Returns
    -------
    ordered_teams (list[Team]): the list of teams in order playing
        the first place teams from A,B,D,E,G,I,K,L.

    """
    
    third_place_teams = [group.teams[2] for group in groups]

    # GD, GF, GA, and coinflip are used as tie-breaking criteria.
    # Team conduct is not currently in the model, so it is not used.
    third_place_teams = sorted(
            third_place_teams,
            key = lambda t: (t.pts, t.gd, t.gf, -t.ga, random.random()),
            reverse=True
        )

    # frozenset allows top_eight to be used as dict key.
    top_eight = frozenset([x.group for x in third_place_teams[0:8]])

    # ordered_groups is the group IDs that will play 1A,1B,1D,1E,1G,1I,1K,1L.
    # For example, if EFGHIJKL advance, then it is [E,J,I,F,H,G,L,K].
    # Then, ordered_teams makes the list of appropriate teams.
    ordered_groups = THIRD_PLACE_DICT[top_eight]

    ordered_teams = [third_place_teams[ord(g)-65] for g in ordered_groups]

    return ordered_teams

def get_random_third_place_teams(groups: list[Group]) -> list[Team]:
    """
    Given a list of groups that have been ordered but not actually simulated,
    return a random list of eight third place teams that will advance to play
    the first-place teams from A,B,D,E,G,I,K,L.

    Parameters
    ----------
    groups (list[Group]): the list of all groups ordered from A-L.

    Returns
    -------
    ordered_teams (list[Team]): the list of teams in order playing
        the first place teams from A,B,D,E,G,I,K,L.

    """

    third_place_teams = [g.teams[2] for g in groups]

    sorted_third_place_teams = third_place_teams.copy()
    random.shuffle(sorted_third_place_teams)
    
    top_eight = frozenset([x.group for x in sorted_third_place_teams[0:8]])

    ordered_groups = THIRD_PLACE_DICT[top_eight]

    ordered_teams = [third_place_teams[ord(g)-65] for g in ordered_groups]

    return ordered_teams

def get_ro32_teams(
    groups: list[Group],
    third_place_teams: list[Team]
) -> list[Team]:
    """
    Form a list of RO32 teams such that 2n and 2n+1 play each other in the Ro32.

    Parameters
    ----------
    groups (list[Group): the list of all simulated groups ordered from A-L.
    third_place_teams (list[Team]): the list of third-place teams in order
        playing the first place teams from A,B,D,E,G,I,K,L.

    Returns
    -------
    ro32_teams (list[Team]): the list of Ro32 teams.
    """

    ro32_teams = [groups[ 4].teams[0], third_place_teams[3], # 1E vs A/B/C/D/F3
                  groups[ 8].teams[0], third_place_teams[5], # 1I vs C/D/F/G/H3
                  groups[ 0].teams[1], groups[ 1].teams[1] , # 2A vs 2B
                  groups[ 5].teams[0], groups[ 2].teams[1] , # 1F vs 2C
                  groups[10].teams[1], groups[11].teams[1] , # 2K vs 2L
                  groups[ 7].teams[0], groups[ 9].teams[1] , # 1H vs 2J
                  groups[ 3].teams[0], third_place_teams[2], # 1D vs B/E/F/I/J3
                  groups[ 6].teams[0], third_place_teams[4], # 1G vs A/E/H/I/J3
                  groups[ 2].teams[0], groups[ 5].teams[1] , # 1C vs 2F
                  groups[ 4].teams[1], groups[ 8].teams[1] , # 2E vs 2I
                  groups[ 0].teams[0], third_place_teams[0], # 1A vs C/E/F/H/I3
                  groups[11].teams[0], third_place_teams[7], # 1L vs E/H/I/J/K3
                  groups[ 9].teams[0], groups[ 7].teams[1] , # 1J vs 2
                  groups[ 3].teams[1], groups[ 6].teams[1] , # 2D vs 2G
                  groups[ 1].teams[0], third_place_teams[1], # 1B vs E/F/G/I/J3
                  groups[10].teams[0], third_place_teams[6]] # 1K vs D/E/I/J/L3

    return ro32_teams

def get_ko_round_winners(teams: list[Team]) -> list[Team]:
    """
    Simulate fixtures between teams in a knockout round and return winners.

    Parameters
    ----------
    teams (list[Team]): the list of teams in the knockout round, where 2n and
        2n+1 play each other

    Returns
    -------
    winners (list[Team]): the list of winners in the knockout round, where 2n
        and 2n+1 play each other in the next round
    """

    winners = []

    for n in range(len(teams) // 2):
        matchup = [teams[2*n], teams[2*n+1]]
        score = simulate_game(matchup)
        winners.append(matchup[get_knockout_winner(score)])

    return winners

def get_knockout_winner(score: list[int]) -> int:
    """
    From the scoreline of a match, return the index of the winner in the matchup.

    Parameters
    ----------
    score (list[int]): the scoreline of a fixture, e.g. [2,0].

    Returns
    -------
    winner (int): the index of the winner in a matchup, either 0 or 1.
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
    groups: list[Group],
    third_place_teams: list[Team]
)-> list[list[Team | int] | Team]:
    """
    Simulate the knockout stage of the world cup and return results of all
    rounds.

    Parameters
    ----------
    groups (list[Group): the list of all simulated groups ordered from A-L.
    third_place_teams (list[Team]): the list of third-place teams in order
        playing the first place teams from A,B,D,E,G,I,K,L.

    Returns
    -------
    knockout_results (list[list[Team | int] | Team]): a list of lists of the
        winners of each round, the semi-final losers and results
        of the third-place match, and the championship final scoreline.
    """

    ro32_teams = get_ro32_teams(groups, third_place_teams)
    ro32_winners = get_ko_round_winners(ro32_teams)
    ro16_winners = get_ko_round_winners(ro32_winners)
    quarters_winners = get_ko_round_winners(ro16_winners)
    semi_winners = get_ko_round_winners(quarters_winners)
    semi_losers = [team for team in quarters_winners if team not in semi_winners] 
    third_place_scoreline = simulate_game(semi_losers)
    third_place = semi_losers[get_knockout_winner(third_place_scoreline)]
    final_scoreline = simulate_game(semi_winners)
    champion = semi_winners[get_knockout_winner(final_scoreline)]

    knockout_results = [ro32_winners,
                        third_place_teams,
                        ro16_winners,
                        quarters_winners,
                        semi_winners,
                        semi_losers,
                        third_place_scoreline,
                        third_place,
                        final_scoreline,
                        champion
                    ]
    return knockout_results

def simulate_tournament() -> list[list[list[str] | str | int]]:
    """
    Initialize all world cup groups and simulate the entire tournament.

    Parameters
    ----------
    None

    Returns
    -------
    tourney_log (list[list[list[str] | str | int]]): a log of the relevant
        results of the entire tournament
    """

    groups = [simulate_group(g) for g in initialize_groups()]
 
    knockout_results = simulate_knockout(groups, get_third_place_teams(groups))

    tourney_log = get_tourney_log(groups, knockout_results)

    return tourney_log


def get_tourney_log(
    groups: list[Group],
    knockout_results: list[list[list[str] | str | int]]
) -> list[list[list[str] | str | int]]:
    """
    Construct a log of the group stage and knockout stage results for the
    entire simulated world cup.
    
    Parameters
    ----------
    groups (list[Group): the list of all simulated groups ordered from A-L.
    knockout_results (list[list[Team | int] | Team]): a list of lists of the
        winners of each round, the semi-final losers and results
        of the third-place match, and the championship final scoreline.

    Returns
    -------
    tourney_log (list[list[list[str] | str | int]]): a log of the relevant
        results of the entire tournament
    """


    ro32_winners = knockout_results[0]
    third_place_teams = knockout_results[1]
    ro16_winners = knockout_results[2]
    quarters_winners = knockout_results[3]
    semi_winners = knockout_results[4]
    semi_losers = knockout_results[5]
    third_place_scoreline = knockout_results[6]
    third_place = knockout_results[7]
    final_scoreline = knockout_results[8]
    champion = knockout_results[9]

    group_rankings = [[team.name for team in group.teams] for group in groups]

    ro32_winner_names = [team.name for team in ro32_winners]
    ro16_winner_names = [team.name for team in ro16_winners]
    quarters_winner_names = [team.name for team in quarters_winners]
    semi_winner_names = [team.name for team in semi_winners]
    third_place_name = third_place.name
    champ_name = champion.name
    third_place_advancer_names = [team.name for team in third_place_teams]

    tourney_log = [group_rankings,
                   ro32_winner_names,
                   ro16_winner_names,
                   quarters_winner_names,
                   semi_winner_names,
                   third_place_name,
                   champ_name,
                   final_scoreline,
                   third_place_advancer_names]

    return tourney_log

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

def simulate_game(teams) -> list[int]:
    team_a = teams[0]
    team_b = teams[1]

    delta = (team_a.elo - team_b.elo)/400
    lambda_a = MU * math.exp(K*delta)
    lambda_b = MU * math.exp(-1*K*delta)

    p_goals_a = []
    p_goals_b = []

    for i in range(6):
        p_goals_a.append((math.exp(-lambda_a) * (lambda_a ** i))/math.factorial(i))
        p_goals_b.append((math.exp(-lambda_b) * (lambda_b ** i))/math.factorial(i))

    # CREATE CDFS FOR GOALS SCORED
    cdf_goals_a_unnorm = [sum(p_goals_a[0:x+1]) for x in range(6)]
    cdf_goals_b_unnorm = [sum(p_goals_b[0:x+1]) for x in range(6)]
    cdf_goals_a = [x / sum(p_goals_a) for x in cdf_goals_a_unnorm]
    cdf_goals_b = [x / sum(p_goals_b) for x in cdf_goals_b_unnorm]
    
    # SIMULATE GOALS SCORED
    rand_goals_a = random.random()
    rand_goals_b = random.random()

    for i in range(6):
        if rand_goals_a < cdf_goals_a[i]:
            goals_a = i
            break
    for i in range(6):
        if rand_goals_b < cdf_goals_b[i]:
            goals_b = i
            break

    scoreline = [goals_a, goals_b]

    return scoreline

def simulate_group(group) -> Group:
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

def add_group_game_results(team1, team2, scoreline):
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

    # NO RETURN


def print_group_results(group):
    print(group.name)
    print("\n")
    for team in group.teams:
        print(team.name, ": ",
              team.pts, " PTS, ",
              team.gf, " GF, ",
              team.ga, " GA")
    print("\n")


def get_third_place_teams(groups):
    
    all_third_place_teams = []
    for group in groups:
        all_third_place_teams.append(group.teams[2])

    sorted_3rd_place_teams = sorted(
            all_third_place_teams,
            key = lambda t: (t.pts, t.gd, t.gf, -t.ga),
            reverse=True
        )

    best_third_place_teams = frozenset([x.group for x in sorted_3rd_place_teams[0:8]])

    ordered_groups = THIRD_PLACE_DICT[best_third_place_teams]

    ordered_teams = []

    for g in ordered_groups:
        idx = ord(g)-65
        ordered_teams.append(all_third_place_teams[idx])

    return ordered_teams

def get_random_third_place_teams(groups):

    all_third_place_teams = []
    for group in groups:
        all_third_place_teams.append(group.teams[2])

    sorted_third_place_teams = all_third_place_teams.copy()
    random.shuffle(sorted_third_place_teams)
    
    best_third_place_teams = frozenset([x.group for x in sorted_third_place_teams[0:8]])

    ordered_groups = THIRD_PLACE_DICT[best_third_place_teams]

    ordered_teams = []

    for g in ordered_groups:
        idx = ord(g)-65
        ordered_teams.append(all_third_place_teams[idx])

    return ordered_teams

def get_ro32_teams(groups, third_place_teams):

    ro32_teams = [groups[ 4].teams[0], third_place_teams[3], #1E vs A/B/C/D/F3
                  groups[ 8].teams[0], third_place_teams[5], #1I vs C/D/F/G/H3
                  groups[ 0].teams[1], groups[ 1].teams[1] , #2A vs 2B
                  groups[ 5].teams[0], groups[ 2].teams[1] , #1F vs 2C
                  groups[10].teams[1], groups[11].teams[1] , #2K vs 2L
                  groups[ 7].teams[0], groups[ 9].teams[1] , #1H vs 2J
                  groups[ 3].teams[0], third_place_teams[2], #1D vs B/E/F/I/J3
                  groups[ 6].teams[0], third_place_teams[4], #1G vs A/E/H/I/J3
                  groups[ 2].teams[0], groups[ 5].teams[1] , #1C vs 2F
                  groups[ 4].teams[1], groups[ 8].teams[1] , #2E vs 2I
                  groups[ 0].teams[0], third_place_teams[0], #1A vs C/E/F/H/I3
                  groups[11].teams[0], third_place_teams[7], #1L vs E/H/I/J/K3
                  groups[ 9].teams[0], groups[ 7].teams[1] , #1J vs 2
                  groups[ 3].teams[1], groups[ 6].teams[1] , #2D vs 2G
                  groups[ 1].teams[0], third_place_teams[1], #1B vs E/F/G/I/J3
                  groups[10].teams[0], third_place_teams[6]] #1K vs D/E/I/J/L3

    return ro32_teams

def get_ko_round_winners(teams: list[Team]):

    winners = []

    for n in range(len(teams) // 2):
        matchup = [teams[2*n], teams[2*n+1]]
        score = simulate_game(matchup)
        winners.append(matchup[get_knockout_winner(score)])

    return winners

def get_knockout_winner(score):
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

def simulate_knockout(groups, third_place_teams):

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

def simulate_tournament():
    groups = initialize_groups()
    for group in groups:
        group = simulate_group(group)

    third_place_teams = get_third_place_teams(groups)  
    
    knockout_results = simulate_knockout(groups, third_place_teams)

    tourney_log = get_tourney_log(groups, knockout_results)

    return tourney_log


def get_tourney_log(groups, knockout_results):
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

    group_rankings = []
    for group in groups:
        ranking = []
        for team in group.teams:
            ranking.append(team.name)
        group_rankings.append(ranking)

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


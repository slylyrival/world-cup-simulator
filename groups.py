from teams import *

class Group:
    def __init__(self, name, team1, team2, team3, team4):
        self.name = name
        self.team1 = team1
        self.team2 = team2
        self.team3 = team3
        self.team4 = team4
        self.teams = [self.team1,
                      self.team2,
                      self.team3,
                      self.team4]

def initialize_groups():
    groups = [
        Group(
            "Group A",
            make_team("Mexico"),
            make_team("South Africa"),
            make_team("South Korea"),
            make_team("Czechia"),
        ),
        Group(
            "Group B",
            make_team("Canada"),
            make_team("Bosnia and Herzegovina"),
            make_team("Qatar"),
            make_team("Switzerland"),
        ),
        Group(
            "Group C",
            make_team("Brazil"),
            make_team("Morocco"),
            make_team("Haiti"),
            make_team("Scotland"),
        ),
        Group(
            "Group D",
            make_team("United States"),
            make_team("Paraguay"),
            make_team("Australia"),
            make_team("Turkey"),
        ),
        Group(
            "Group E",
            make_team("Germany"),
            make_team("Curacao"),
            make_team("Ivory Coast"),
            make_team("Ecuador"),
        ),
        Group(
            "Group F",
            make_team("Netherlands"),
            make_team("Japan"),
            make_team("Sweden"),
            make_team("Tunisia"),
        ),
        Group(
            "Group G",
            make_team("Belgium"),
            make_team("Egypt"),
            make_team("Iran"),
            make_team("New Zealand"),
        ),
        Group(
            "Group H",
            make_team("Spain"),
            make_team("Cape Verde"),
            make_team("Saudi Arabia"),
            make_team("Uruguay"),
        ),
        Group(
            "Group I",
            make_team("France"),
            make_team("Senegal"),
            make_team("Iraq"),
            make_team("Norway"),
        ),
        Group(
            "Group J",
            make_team("Argentina"),
            make_team("Algeria"),
            make_team("Austria"),
            make_team("Jordan"),
        ),
        Group(
            "Group K",
            make_team("Portugal"),
            make_team("DR Congo"),
            make_team("Uzbekistan"),
            make_team("Colombia"),
        ),
        Group(
            "Group L",
            make_team("England"),
            make_team("Croatia"),
            make_team("Ghana"),
            make_team("Panama"),
        ),
    ]
    for group in groups:
        for team in group.teams:
            team.group = group.name[-1]

    return groups

"""Define Group class and a method for initializing the teams in the 2026 WC.

Class Group contains the group name and the teams in the group.

Function initialize_groups creates and populates new Group instances for the 2026 WC.

"""

import random
from dataclasses import dataclass
from teams import Team, make_team

@dataclass
class Group:
    """A class to represent a World Cup group.

    ...
    Attributes
    ----------
    name: str
        the name of the group (e.g., 'Group A')
    teams: list[Team]
        a list of the four teams in the group

    Methods
    -------
    sort_group():
        Sorts the teams in the group by pts, GD, GF, GA, and cointoss.


    """
    name: str
    teams: list[Team]

    def sort_group(self):
        """
        Modifies the group's teams list in place to sort according to points
        and tie-breaking criteria.

        Parameters
        ----------
        None

        Returns
        -------
        None 

        """

        # I'm just going to pretend tie breaking criteria are GD, GF, GA, and
        # coin toss in that order. This is not what it actually is. It does
        # not matter for this simulation (probably).
        self.teams = sorted(
                self.teams,
                key=lambda g: (g.pts, g.gd, g.gf, -g.ga, random.random()),
                reverse=True
            )

def initialize_groups() -> list[Group]:
    """
    Creates a list of Group objects with initialized Teams for the 2026 WC.

    Parameters
    ----------
    None

    Returns
    -------
    groups (list[Group]): List of 2026 World Cup Groups.

    """
    groups = [
        Group(
            "Group A",
            [make_team("Mexico"),
            make_team("South Africa"),
            make_team("South Korea"),
            make_team("Czechia")],
        ),
        Group(
            "Group B",
            [make_team("Canada"),
            make_team("Bosnia and Herzegovina"),
            make_team("Qatar"),
            make_team("Switzerland")],
        ),
        Group(
            "Group C",
            [make_team("Brazil"),
            make_team("Morocco"),
            make_team("Haiti"),
            make_team("Scotland")],
        ),
        Group(
            "Group D",
            [make_team("United States"),
            make_team("Paraguay"),
            make_team("Australia"),
            make_team("Turkey")],
        ),
        Group(
            "Group E",
            [make_team("Germany"),
            make_team("Curacao"),
            make_team("Ivory Coast"),
            make_team("Ecuador")],
        ),
        Group(
            "Group F",
            [make_team("Netherlands"),
            make_team("Japan"),
            make_team("Sweden"),
            make_team("Tunisia")],
        ),
        Group(
            "Group G",
            [make_team("Belgium"),
            make_team("Egypt"),
            make_team("Iran"),
            make_team("New Zealand")],
        ),
        Group(
            "Group H",
            [make_team("Spain"),
            make_team("Cape Verde"),
            make_team("Saudi Arabia"),
            make_team("Uruguay")],
        ),
        Group(
            "Group I",
            [make_team("France"),
            make_team("Senegal"),
            make_team("Iraq"),
            make_team("Norway")],
        ),
        Group(
            "Group J",
            [make_team("Argentina"),
            make_team("Algeria"),
            make_team("Austria"),
            make_team("Jordan")],
        ),
        Group(
            "Group K",
            [make_team("Portugal"),
            make_team("DR Congo"),
            make_team("Uzbekistan"),
            make_team("Colombia")],
        ),
        Group(
            "Group L",
            [make_team("England"),
            make_team("Croatia"),
            make_team("Ghana"),
            make_team("Panama")],
        ),
    ]

    for group in groups:
        for team in group.teams:
            team.group = group.name[-1]

    return groups

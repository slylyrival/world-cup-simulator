"""Define World Cup teams and construct team instances from rating data.

Class Team contains attributes for a 2026 WC team.
Function make_team makes a Team instance from the TEAM_DATA dictionary.

"""

from dataclasses import dataclass


@dataclass
class Team:
    """A class to represent a World Cup team.

    Attributes
    ----------
    name: str
        the country name of the team
    elo: int
        the elo rating of the team
    gf: int
        the goals scored by the team
    ga: int
        the goals scored against the team
    pts: int
        points scored in the group stage
    group: str
        the letter of the group the team belongs to in the group stage

    Methods
    -------
    gd():
        Returns the current goal differential of the team


    """

    name: str
    elo: int
    gf: int = 0
    ga: int = 0
    pts: int = 0
    group: str = ""

    @property
    def gd(self) -> int:
        """
        Returns goal differntial for the Team.

        Parameters
        ----------
        None

        Returns
        -------
        (int)
        """
        # calculates goal difference from GF - GA
        return self.gf - self.ga


def make_team(team_key: str) -> Team:
    """
    Return a new Team object

    Parameters
    ----------
    team_key (str): the key to TEAM_DATA dictionary identifying the team

    Returns
    -------
    (Team) the new Team

    """
    name, elo = TEAM_DATA[team_key]
    return Team(name, elo)


# This TEAM_DATA dictionary contains names and elo for all the 2026 WC teams.
TEAM_DATA = {
    # Group A
    "Mexico": ("Mexico", 1849),
    "South Africa": ("South Africa", 1674),
    "South Korea": ("South Korea", 1758),
    "Czechia": ("Czechia", 1770),
    # Group B
    "Canada": ("Canada", 1815),
    "Bosnia and Herzegovina": ("Bosnia and Herzegovina", 1703),
    "Qatar": ("Qatar", 1546),
    "Switzerland": ("Switzerland", 1887),
    # Group C
    "Brazil": ("Brazil", 2001),
    "Morocco": ("Morocco", 1857),
    "Haiti": ("Haiti", 1630),
    "Scotland": ("Scotland", 1807),
    # Group D
    "United States": ("United States", 1807),
    "Paraguay": ("Paraguay", 1852),
    "Australia": ("Australia", 1768),
    "Turkey": ("Turkey", 1897),
    # Group E
    "Germany": ("Germany", 1970),
    "Curacao": ("Curacao", 1571),
    "Ivory Coast": ("Ivory Coast", 1772),
    "Ecuador": ("Ecuador", 1923),
    # Group F
    "Netherlands": ("Netherlands", 1956),
    "Japan": ("Japan", 1875),
    "Sweden": ("Sweden", 1793),
    "Tunisia": ("Tunisia", 1701),
    # Group G
    "Belgium": ("Belgium", 1893),
    "Egypt": ("Egypt", 1764),
    "Iran": ("Iran", 1724),
    "New Zealand": ("New Zealand", 1634),
    # Group H
    "Spain": ("Spain", 2089),
    "Cape Verde": ("Cape Verde", 1613),
    "Saudi Arabia": ("Saudi Arabia", 1631),
    "Uruguay": ("Uruguay", 1923),
    # Group I
    "France": ("France", 2028),
    "Senegal": ("Senegal", 1894),
    "Iraq": ("Iraq", 1649),
    "Norway": ("Norway", 1939),
    # Group J
    "Argentina": ("Argentina", 2067),
    "Algeria": ("Algeria", 1794),
    "Austria": ("Austria", 1835),
    "Jordan": ("Jordan", 1659),
    # Group K
    "Portugal": ("Portugal", 1972),
    "DR Congo": ("DR Congo", 1736),
    "Uzbekistan": ("Uzbekistan", 1712),
    "Colombia": ("Colombia", 1947),
    # Group L
    "England": ("England", 2032),
    "Croatia": ("Croatia", 1879),
    "Ghana": ("Ghana", 1673),
    "Panama": ("Panama", 1742),
}

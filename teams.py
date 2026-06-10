class Team:
    def __init__(self, name, elo, gf=0, ga=0, pts=0, group = ''):
        self.name = name
        self.elo = elo
        self.gf = gf
        self.ga = ga
        self.pts = pts
        self.group = group

    @property
    def gd(self):
        # calculates goal difference from GF - GA
        return self.gf - self.ga


team_data = {
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


def make_team(team_key):
    name,elo = team_data[team_key]
    return Team(name, elo)


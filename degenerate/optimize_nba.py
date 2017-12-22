import csv

from ortools.linear_solver import pywraplp


class Player:
    def __init__(self, opts):
        self.name = opts['player']
        self.position = opts['position'].upper()
        self.salary = int(opts['salary'])
        self.projected = float(opts['projection'])
        self.lock = int(opts['lock']) > 0
        self.ban = int(opts['lock']) < 0

    def __repr__(self):
        return "[{0: <2}] {1: <20}(${2}, {3}) {4}".format(self.position, \
                                                          self.name, \
                                                          self.salary,
                                                          self.projected,
                                                          "LOCK" if self.lock else "")


class Roster:
    POSITION_ORDER = {
        "PG": 0,
        "SG": 1,
        "SF": 2,
        "PF": 3,
        "C": 4
    }

    def __init__(self):
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def spent(self):
        return sum(map(lambda x: x.salary, self.players))

    def projected(self):
        return sum(map(lambda x: x.projected, self.players))

    def position_order(self, player):
        return self.POSITION_ORDER[player.position]

    def sorted_players(self):
        return sorted(self.players, key=self.position_order)

    def __repr__(self):
        s = '\n'.join(str(x) for x in self.sorted_players())
        s += "\n\nProjected Score: %s" % self.projected()
        s += "\tCost: $%s" % self.spent()
        return s


SALARY_CAP = 50000

POSITION_LIMITS = [
    ["PG", 1, 3],
    ["SG", 1, 3],
    ["SF", 1, 3],
    ["PF", 1, 3],
    ["C", 1, 2]
]

ROSTER_SIZE = 8


def run():
    solver = pywraplp.Solver('FD', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    all_players = []
    with open('projections/sample-nba.csv', 'r') as csvfile:
        csvdata = csv.DictReader(csvfile, skipinitialspace=True)

        for row in csvdata:
            all_players.append(Player(row))

    variables = []

    for player in all_players:
        if player.lock:
            variables.append(solver.IntVar(1, 1, player.name))
        elif player.ban:
            variables.append(solver.IntVar(0, 0, player.name))
        else:
            variables.append(solver.IntVar(0, 1, player.name))

    objective = solver.Objective()
    objective.SetMaximization()

    for i, player in enumerate(all_players):
        objective.SetCoefficient(variables[i], player.projected)

    salary_cap = solver.Constraint(0, SALARY_CAP)
    for i, player in enumerate(all_players):
        salary_cap.SetCoefficient(variables[i], player.salary)

    for position, min_limit, max_limit in POSITION_LIMITS:
        position_cap = solver.Constraint(min_limit, max_limit)

        for i, player in enumerate(all_players):
            if position == player.position:
                position_cap.SetCoefficient(variables[i], 1)

    size_cap = solver.Constraint(ROSTER_SIZE, ROSTER_SIZE)
    for variable in variables:
        size_cap.SetCoefficient(variable, 1)

    solution = solver.Solve()

    if solution == solver.OPTIMAL:
        roster = Roster()

        for i, player in enumerate(all_players):
            if variables[i].solution_value() == 1:
                roster.add_player(player)

        print("Optimal roster for: $%s\n" % SALARY_CAP)
        print(roster)

    else:
        print("No solution :(")


if __name__ == "__main__":
    run()

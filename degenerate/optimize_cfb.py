from degenerate import Optimizer
from degenerate import PlayerPool
from degenerate import RosterDefinition

NUMBER_OF_LINEUPS = 2
UNIQUE_PLAYERS = 7

if __name__ == "__main__":
    players = PlayerPool().from_csv('projections/cfb_nye_yahoo.csv').all_players()
    roster_definition = RosterDefinition.YAHOO_CFB

    print
    "Optimal CFB rosters for: $%s" % roster_definition['salary_cap']
    print
    "Unique players per roster: %s\n" % UNIQUE_PLAYERS

    rosters = []
    optimizer = Optimizer()

    for i in range(0, NUMBER_OF_LINEUPS):
        roster = optimizer.generate_roster(players, roster_definition, \
                                           rosters, UNIQUE_PLAYERS)

        if roster is None:
            print
            "Couldn't generate enough rosters :("
            break
        else:
            rosters.append(roster)

        print
        "\t\tRoster #%s" % (i + 1)
        print
        roster, '\n'

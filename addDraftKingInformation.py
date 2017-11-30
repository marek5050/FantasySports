import glob


def build_dk_salaries():
    print("build_dk_salaries")
    _vegas = pd.DataFrame()
    found = 0
    notfound = 0
    path = r'data/play'  # use your path
    allFiles = glob.glob(path + "/*.csv")
    print("Number of files: %d" % (len(allFiles)))
    for _file in allFiles:
        try:
            _date = _file.split("/")[1].replace(".csv", "")
            vegas1 = pd.read_csv(_file)
            _vegas = _vegas.append(vegas1)
        except Exception as e:
            print("Error with date: " + _date)
            print(e)
    return _vegas


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="whats the date or * for all", default="2017-18")
    args = parser.parse_args()

    seasons = args.date.split(",")
    created = 0
    # if len(seasons) > 0:
    #     created = buildDatabase.create_player_logs(seasons)
    # else:
    #     print("Did not find a valid season value: %s" % (args.date))
    #
    # print("Finished updating  : %d" % (created))
    salaries = build_dk_salaries()
    # salaries["combo"] = salaries["Name"] + salaries["Position"]
    # salaries = salaries.set_index("Name")
    # salaries["combo"].unique
    from mysql import *

    session = get_session()
    for idx, item in salaries.iterrows():

        try:
            session.add(DKPlayer(**item.to_dict()))
            session.commit()
        except Exception as e:
            # print(e)
            session.rollback()
    session.close()

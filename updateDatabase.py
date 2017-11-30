import buildDatabase

# session = get_session()
# session.query(PlayerLog).delete()


# def get_or_create(session, model, kwargs):
#     instance = session.query(model).filter_by(Game_ID = kwargs["Game_ID"], Player_ID=kwargs["Player_ID"]).first()
#     if instance:
#         return 0, instance
#     else:
#         instance = PlayerLog(**kwargs)
#         session.add(instance)
#         session.commit()
#         return 1, instance

# pl = session.query(Player).all()
# num = 0
# for row in pl:
#     log = player.PlayerGameLogs(row.PERSON_ID).info()
#     for idx, row2 in log.iterrows():
#         row2["GAME_DATE"] = parser.parse(row2["GAME_DATE"]).strftime('%Y%m%d')
#         created, item = get_or_create(session, PlayerLog, row2)
#         num += created
#
# session.commit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="whats the date or * for all", default="2017-18")
    args = parser.parse_args()

    seasons = args.date.split(",")
    print("Season: %s "% (args.date))
    created = 0
    if len(seasons) > 0:
        created = buildDatabase.create_player_logs(seasons,verbose=True)
    else:
        print("Did not find a valid season value: %s" % (args.date))

    print("Finished updating  : %d" % (created))

from mysql import *


session = get_session()

logs = session.execute(select([PlayerLog]).where(PlayerLog.Player_ID=="203518"))
df = pd.DataFrame(data = logs.fetchall(), columns=logs.keys())

print(df.head())
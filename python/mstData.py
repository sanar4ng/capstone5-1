import requests
import pandas as pd
api_key = 'RGAPI-5c385776-a3f1-46d5-8aab-e045125292a0'

master = 'https://kr.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key=' + api_key
r = requests.get(master)
league_df = pd.DataFrame(r.json())

league_df.reset_index(inplace=True)
league_entries_df = pd.DataFrame(dict(league_df['entries'])).T 
league_df = pd.concat([league_df, league_entries_df], axis=1) 

league_df = league_df.drop(['index', 'queue', 'name', 'leagueId', 'entries', 'rank'], axis=1)
league_df.info()
league_df.to_csv('mstData.csv',index=False,encoding = 'cp949')
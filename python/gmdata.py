import requests
import pandas as pd
api_key = 'RGAPI-5c385776-a3f1-46d5-8aab-e045125292a0'

grandmaster = 'https://kr.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key=' + api_key
r = requests.get(grandmaster)
league_df = pd.DataFrame(r.json())

league_df.reset_index(inplace=True)
league_entries_df = pd.DataFrame(dict(league_df['entries'])).T 
league_df = pd.concat([league_df, league_entries_df], axis=1) 

league_df = league_df.drop(['index', 'queue', 'name', 'leagueId', 'entries', 'rank'], axis=1)
league_df.info()


for i in range(len(league_df)):
    try:
        sohwan = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + league_df['summonerName'].iloc[i] + '?api_key=' + api_key 
        r = requests.get(sohwan)
        
        while r.status_code == 429:
            time.sleep(5)
            sohwan = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + league_df['summonerName'].iloc[i] + '?api_key=' + api_key 
            r = requests.get(sohwan)
            
        account_id = r.json()['accountId']
        league_df.iloc[i, -1] = account_id
    
    except:
        pass
league_df.to_csv('gmData.csv',index=False,encoding = 'cp949')
import requests
import pandas as pd
import numpy as np
import time

api_key = 'RGAPI-5c385776-a3f1-46d5-8aab-e045125292a0'
challenger = 'https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=' + api_key
r = requests.get(challenger)
league_df = pd.DataFrame(r.json())

league_df.reset_index(inplace=True)
league_entries_df = pd.DataFrame(dict(league_df['entries'])).T
league_df = pd.concat([league_df, league_entries_df], axis=1) 

league_df = league_df.drop(['index', 'queue', 'name', 'leagueId', 'entries', 'rank'], axis=1)
league_df['account_id']=np.nan

for i in range(len(league_df)):
    try:
        sohwan = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + league_df['summonerName'].iloc[i] + '?api_key=' + api_key 
        r = requests.get(sohwan)
        
        while r.status_code == 429:
            time.sleep(3)
            sohwan = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + league_df['summonerName'].iloc[i] + '?api_key=' + api_key 
            r = requests.get(sohwan)
            while True: # 429error가 끝날 때까지 무한 루프
                if r.status_code == 429:

                    print('try 10 second wait time')
                    time.sleep(10)

                    r = requests.get(api_url)
                    print(r.status_code)

                elif r.status_code == 200: #다시 response 200이면 loop escape
                    print('total wait time : ', time.time() - start_time)
                    print('recovery api cost')
                    break
        
            
        account_id = r.json()['accountId']       
        league_df.iloc[i, -1] = account_id
    
    except:
        pass

league_df.to_csv('challengerData.csv',index=False,encoding = 'cp949')
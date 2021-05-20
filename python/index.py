from flask import Flask
import requests
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from math import pi
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

df_filter=pd.DataFrame()
apikey = 'RGAPI-5c385776-a3f1-46d5-8aab-e045125292a0'

def search(sum_name):
    

    headers = {
        "Origin": "https://developer.riotgames.com",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Riot-Token": apikey,
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }

    url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}".format(sum_name)
    res = requests.get(url=url,headers=headers)
    if not res:
        return redirect(url_for('no_user'))
    encryptedID = res.json()['id'] #id 가져오기
    accountId = res.json()['accountId']
    profileIcon_id = res.json()['profileIconId']

    url_league = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(encryptedID)
    res_league = requests.get(url=url_league,headers=headers)
    league_dicts = res_league.json()

    url_GameID = "https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?queue=420".format(accountId)  #{encryptedAccountId} = account_ID
    #매치를 못찾을 경우
    if not url_GameID:
        return redirect(url_for('no_game'))
    res_GameID = requests.get(url=url_GameID, headers=headers)
    
    Matches = res_GameID.json()['matches'] #gameID가 들어있는 Mathes를 가져옴
    #매치 20개로 자르기
    Matches = Matches[:20]

    Game_IDs = []
    for Matche in Matches:
        Game_IDs.append(Matche['gameId'])
           
    champID=[] #챔프
    Game_DATAs = []
    for Game_ID in Game_IDs:

        Game_DATA = {'game_time':'','b_win':'', 'b_towerKills':'', 'b_inhibitorKills':'', 'b_baronKills':'', 'b_riftHeraldKills':'',
        'r_win':'', 'r_towerKills':'', 'r_inhibitorKills':'', 'r_baronKills':'', 'r_riftHeraldKills':'',
        'b_player':[], 'r_player':[], 'stats':''}

        url_GameData = "https://kr.api.riotgames.com/lol/match/v4/matches/{}".format(Game_ID)
        res_GameData = requests.get(url=url_GameData, headers = headers)
        #플레이시간
        Game_DATA['game_time'] = res_GameData.json()['gameDuration']

        #팀정보
        teams = res_GameData.json()['teams']
        
        blue = teams[0] 
        red = teams[-1]
        if (blue['win']=='Win') :
            Game_DATA['b_win'] = '승리'
            Game_DATA['r_win'] = '패배'
        else :
            Game_DATA['b_win'] = '패배'
            Game_DATA['r_win'] = '승리'
                
        Game_DATA['b_towerKills'] = blue['towerKills'] #포탑
        Game_DATA['b_inhibitorKills'] = blue['inhibitorKills'] #억제기
        Game_DATA['b_baronKills'] = blue['baronKills'] #바론
        Game_DATA['b_riftHeraldKills'] = blue['riftHeraldKills'] #전령

        Game_DATA['r_towerKills'] = red['towerKills'] #포탑
        Game_DATA['r_inhibitorKills'] = red['inhibitorKills'] #억제기
        Game_DATA['r_baronKills'] = red['baronKills'] #바론
        Game_DATA['r_riftHeraldKills'] = red['riftHeraldKills'] #전령

        #최근 20회 데이터
        game_20 = res_GameData.json()['participantIdentities']
        myid_num = 0
        #blue, red 플레이어 이름 
        for i in range(0, 10):
            if accountId == game_20[i].get('player').get('accountId'):
                myid_num = i
            if i < 5:
                Game_DATA['b_player'] += [game_20[i].get('player').get('summonerName')]
            else:
                Game_DATA['r_player'] += [game_20[i].get('player').get('summonerName')]
        
        #개인 통계
        participants = res_GameData.json()['participants'][myid_num]
        champID.append(participants['championId'])
        stats = participants['stats']
        Game_DATA['stats'] = stats
        Game_DATAs.append(Game_DATA)

    static_data_url = 'http://ddragon.leagueoflegends.com/cdn/9.24.2/data/ko_KR/champion.json'
    data = requests.get(static_data_url).json()
    data = data['data']
    my_most_one = []
    my_most = dict()
    for mychamp in champID:
        for key, value in data.items():
            if int(mychamp) == int(value['key']):
                n = value['name']
                en_n = value['id']
                my_most_one.append([en_n, n])
                if (en_n, n) not in my_most:
                    my_most[(en_n, n)] = 1
                else:
                    my_most[(en_n, n)] += 1

    most_num = 0
    most_one = ()
    for key, value in my_most.items():
        if int(value) > most_num:
            most_num = value
            most_one = key
    
    def get_league_info(league_dict):
        res = [
        league_dict.get('queueType'),
        league_dict.get('tier'),
        league_dict.get('rank'),
        league_dict.get('wins'),
        league_dict.get('losses'),
        league_dict.get('leagueName'),
        league_dict.get('leaguePoints')
            ]
        return res
        
    results = []
    for league_dict in league_dicts:
        results.append(get_league_info(league_dict))
    length = len(results)
    df=pd.DataFrame(Game_DATAs)
    return df

def userName_search(user_name):
    match_data=search(user_name)
    
    a_ls = list(match_data['stats'])
    team01_df=match_data.drop(['stats'],axis=1)
    finish=pd.DataFrame()
    team02_df=pd.DataFrame()
    for i in range(len(a_ls)):
        try:  
            team2 = pd.DataFrame(list(a_ls2[i].values()),index = list(a_ls2[i].keys())).T
            team02_df = team02_df.append(team2)
  
        except:
            pass
    team02_df.index = range(len(team02_df))
    final=pd.concat([team02_df,team01_df], axis=1,ignore_index =False,join='inner')
    df_stats_means_sOthers(final,user_name)
    return df_stats_means_sOthers(final,user_name)


def retrun_drop(df):
    df=df.drop('participantId','item0','item1','item2','item3','item4','item5','item6','combatPlayerScore',
                                             'unrealKills','inhibitorKills','killingSprees','largestCriticalStrike',
                                             'largestKillingSpree','largestMultiKill','longestTimeSpentLiving','magicDamageDealt',
                                             'magicDamageDealtToChampions','magicalDamageTaken','objectivePlayerScore','pentaKills',
                                             'perk0Var1','perk0','perk0Var2','perk0Var3','perk1','perk1Var1','perk1Var2','perk1Var3',
                                             'perk2','perk2Var1','perk2Var2','perk2Var3','perk3','perk3Var1','perk3Var2','perk3Var3',
                                             'perk4','perk4Var1','perk4Var2','perk4Var3','perk5','perk5Var1','perk5Var2','perk5Var3',
                                             'perkPrimaryStyle','perkSubStyle','playerScore0','playerScore1','playerScore2','playerScore3',
                                             'playerScore4','playerScore5','playerScore6','playerScore7','playerScore8','playerScore9',
                                             'quadraKills','sightWardsBoughtInGame','statPerk0','statPerk1','statPerk2','totalPlayerScore',
                                             'totalScoreRank','totalUnitsHealed','tripleKills','turretKills','firstBloodAssist',
                                             'firstBloodKill','firstInhibitorAssist','firstInhibitorKill','firstTowerAssist','firstTowerKill',
                                             'doubleKills')
    return df

def df_stats_means_sOthers(searchName,user_name):
    df_filter =searchName
    kda=(df_filter['kills'].mean()+df_filter['assists'].mean())/df_filter['deaths'].mean()
    dpg=df_filter['totalDamageDealtToChampions'].mean()/df_filter['goldEarned'].mean()
    totgold=df_filter['goldEarned'].mean()/1000
    wardsPlaced=df_filter['wardsPlaced'].mean()
    champLevel=df_filter['champLevel'].mean()
    totdmg=df_filter['totalDamageDealtToChampions'].mean()/1000
    totmk=df_filter['totalMinionsKilled'].mean()
    timeCCingOthers=df_filter['timeCCingOthers'].mean()
    df = pd.DataFrame(data=np.array([[user_name,kda,dpg, totgold, wardsPlaced,champLevel,totdmg,timeCCingOthers]]), 
                      columns=['username','kda', 'dpg', 'totgold','wardsPlaced','champLevel','totdmg','timeCCingOthers'])

    return kda

def userName_to_account(str):
    user_name=str
    userName = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+user_name+'?api_key=' + api_key
    r = requests.get(userName)
    accountId=r.json()['accountId']
    return accountId

def account_to_gameId(str):
    accountId=str
    match = 'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountId  +'?season='+ '&endIndex=20'+ '&api_key=' + api_key
    r = requests.get(match)
    gameId=pd.DataFrame(r.json()['matches'])
    return gameId

def account_to_matches(str1):
    match1 = pd.DataFrame()
    for i in range(len(str1)):
        gameId=str1[i]
        api_url='https://kr.api.riotgames.com/lol/match/v4/matches/' + str(gameId) + '?api_key=' + api_key
        r = requests.get(api_url)
        accountId=r.json()
        mat = pd.DataFrame(list(accountId.values()), index=list(accountId.keys())).T
        match1 = match1.append(mat)
    
    return match1

def normalization_0(list1,i):
    team01_df = pd.DataFrame()
    a_ls=list1
    for i in range(i, i+1):
        try:
            for j in range(0,10):
                a_ls[i][j].pop('bans',None)
                team1 = pd.DataFrame(list(a_ls[i][j].values()),index = list(a_ls[i][j].keys())).T
                team01_df = team01_df.append(team1)


        except:
            pass

    
    team01_df.index = range(len(team01_df))
    return team01_df['stats']

def normalization_1(list1):
    a_ls1=list1
    team02_df = pd.DataFrame()
    for i in range(len(a_ls1)):
        try:
            a_ls1[i].pop('bans',None)
            team1 = pd.DataFrame(list(a_ls1[i].values()),index = list(a_ls1[i].keys())).T
            team02_df = team02_df.append(team1)


        except:
            pass


    team02_df.index = range(len(team02_df))
    return team02_df

def normalization_2(list1,i):
    a_ls2=list1
    team03_df= pd.DataFrame()
    for i in range(i,i+1):
        try:
            for j in range(0,10):
                a_ls2[i][j].pop('bans',None)
                team1 = pd.DataFrame(list(a_ls2[i][j].values()),index = list(a_ls2[i][j].keys())).T
                team03_df = team03_df.append(team1)


        except:
            pass


    team03_df.index = range(len(team03_df))
    return team03_df['player']

def normalization_3(list1):
    a_ls3=list1
    team04_df = pd.DataFrame()
    for i in range(len(a_ls3)):
        try:

            team3 = pd.DataFrame(list(a_ls3[i].values()),index = list(a_ls3[i].keys())).T
            team04_df = team04_df.append(team3)


        except:
            pass

    team04_df.index = range(len(team04_df))
    return team04_df

def return_participantId(str1, df):
    id1=str1
    for i in range(0,10):
        if df.at[i,'summonerName']==id1:
            return i+1
            
def return_stat(int,a_ls1):
    team05_df=pd.DataFrame()
    
    for i in range(0,10):
        
        if normalization_1(a_ls1).at[i,'participantId']==int:
            team05_df=normalization_1(a_ls1)[(normalization_1(a_ls1)['participantId']==int)]
            return team05_df



app = Flask(__name__)
@app.route('/')
@app.route('/home')
def home():
    return 'Hello, World!'
@app.route('/user/<user_name>')
def user(user_name):
    searchName=userName_search(user_name)
    return searchName

if __name__ == '__main__':
    app.run(debug=True)
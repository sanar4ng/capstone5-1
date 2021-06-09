from flask import Flask,render_template,request, url_for, session, redirect, flash
import requests
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from math import pi
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import PIL.Image as pilimg
import os

user = os.path.join('static', 'images/user')
df_filter=pd.DataFrame()

apikey = 'RGAPI-5c385776-a3f1-46d5-8aab-e045125292a0'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = user
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')
@app.route('/user')
def search():
    if request.method == 'POST':
        sum_name = request.form['sum_name']
    elif request.method=='GET':
        sum_name = request.args.get('sum_name')

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
    encryptedID = res.json()['id']
    accountId = res.json()['accountId']
    profileIcon_id = res.json()['profileIconId']

    url_league = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(encryptedID)
    res_league = requests.get(url=url_league,headers=headers)
    league_dicts = res_league.json()

    url_GameID = "https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?queue=420".format(accountId)  #{encryptedAccountId} = account_ID
    
    if not url_GameID:
        return redirect(url_for('no_game'))
    res_GameID = requests.get(url=url_GameID, headers=headers)
    
    Matches = res_GameID.json()['matches']
    
    Matches = Matches[:20]

    Game_IDs = []
    for Matche in Matches:
        Game_IDs.append(Matche['gameId'])
           
    champID=[]
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
    
    def stats_means_sOthers(str0, str1):
        df_filter = pd.read_csv('pythonJN/match{0}Data{1}.csv'.format(str0,str1))
        kda=(df_filter['kills'].mean()+df_filter['assists'].mean())/df_filter['deaths'].mean()
        dpg=df_filter['totalDamageDealtToChampions'].mean()/df_filter['goldEarned'].mean()
        totgold=df_filter['goldEarned'].mean()/1000
        wardsPlaced=df_filter['wardsPlaced'].mean()
        champLevel=df_filter['champLevel'].mean()
        totdmg=df_filter['totalDamageDealtToChampions'].mean()/1000
        totmk=df_filter['totalMinionsKilled'].mean()
        timeCCingOthers=df_filter['timeCCingOthers'].mean()

        lskk=[round(kda, 1),round(dpg, 1),round(totgold, 1),round(wardsPlaced, 1),round(champLevel, 1), round(totdmg, 1)
        , round(totmk, 1), round(timeCCingOthers, 1)]
        return lskk

    def proheat(Game_DATAs):
        df=pd.DataFrame()
        kda=[]
        dpg = []
        goldEarned = []
        wardsPlaced = []
        champLevel = []
        totalDamageDealtToChampions = []
        totalMinionsKilled = []
        timeCCingOthers = []
        for Game_DATA in Game_DATAs:
            if Game_DATA['stats']['deaths']==0:
                death=1
            else:
                death=Game_DATA['stats']['deaths']
        
            kda.append(round((Game_DATA['stats']['kills']+Game_DATA['stats']['assists'])/death,2))
            dpg.append(round((Game_DATA['stats']['totalDamageDealtToChampions']+Game_DATA['stats']['goldEarned'])/1000,2))
            goldEarned.append(round(Game_DATA['stats']['goldEarned']/1000))
            wardsPlaced.append(Game_DATA['stats']['wardsPlaced'])
            champLevel.append(Game_DATA['stats']['champLevel'])
            totalDamageDealtToChampions.append(round(Game_DATA['stats']['totalDamageDealtToChampions']/1000))
            totalMinionsKilled.append(Game_DATA['stats']['totalMinionsKilled']/ 10)
            timeCCingOthers.append(Game_DATA['stats']['timeCCingOthers'])

        df['kda']=[round(sum(kda)/len(kda),2)]
        df['dpg']=round(sum(dpg)/len(dpg),2)
        df['goldEarned']=round(sum(goldEarned)/len(goldEarned),2)
        df['wardsPlaced']=round(sum(wardsPlaced)/len(wardsPlaced),2)
        df['champLevel']=round(sum(champLevel)/len(champLevel),2)
        df['totalDamageDealtToChampions']=round(sum(totalDamageDealtToChampions)/len(totalDamageDealtToChampions),2)
        df['totalMinionsKilled']=round(sum(totalMinionsKilled)/len(totalMinionsKilled),2)
        df['timeCCingOthers']=round(sum(timeCCingOthers)/len(timeCCingOthers),2)

        plt.pcolor(df)
        plt.xticks(np.arange(0.5))
        plt.yticks(np.arange(1))
        plt.savefig('./static/images/user/user.png')
        
        

    df1= pd.read_csv('proheat/allpro.csv')
    list_from_df = df1.values.tolist()
    listcoll =[stats_means_sOthers('Win','T'),stats_means_sOthers('Lose','T'),stats_means_sOthers('Win','J'),stats_means_sOthers('Lose','J')
      ,stats_means_sOthers('Win','M'),stats_means_sOthers('Lose','M'),stats_means_sOthers('Win','B'),stats_means_sOthers('Lose','B')
      ,stats_means_sOthers('Win','S'),stats_means_sOthers('Lose','S')]
    
    results = []
    for league_dict in league_dicts:
        results.append(get_league_info(league_dict))
    length = len(results)
    proheat(Game_DATAs)
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'user.png')
    #df=pd.DataFrame(Game_DATAs)
    return render_template('search.html',sum_name=sum_name,results=results, length=length, 
    profileIcon=profileIcon_id, my_most_one=my_most_one, most_one=most_one, most_num=most_num,
    Game_DATAs=Game_DATAs, zip=zip,listcoll=listcoll, img_file=full_filename, list_from_df= list_from_df)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000)

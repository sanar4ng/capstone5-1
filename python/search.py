import requests

user_name = 'Wilder 아데산야'
api_key = 'RGAPI-5c385776-a3f1-46d5-8aab-e045125292a0'
summoner = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + user_name + '?api_key=' + api_key
r = requests.get(summoner)
print(r.json()['id'])

tier_url = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/" + r.json()['id'] +'?api_key=' + api_key
r2  = requests.get(tier_url)
print(r2.json())

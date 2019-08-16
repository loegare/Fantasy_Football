

import requests
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
games=['2019081552']

import statid
# gid=2018120900
def single_game_fps(games):
    df_g=[]
    drives=[]
    for gid in games:
        print (gid)
        url2='http://www.nfl.com/liveupdate/game-center/{}/{}_gtd.json'.format(gid,gid)

        d=requests.get(url2).json()

        df_d=[]
        for key,val in d[str(gid)]['drives'].items():

            if key =='crntdrv':
                continue
            df=pd.DataFrame(val)[['start','end']].dropna()

            df2=pd.DataFrame([0])
            counter=0
            for i in df.columns:
                counter=0
                for j in df[i]:
                    df2[i+' '+df[i].index[counter]]=j
                    counter+=1
            df2=df2.drop([0,'start team','end team','end qtr'],axis=1)



            df=pd.DataFrame(val).drop(['plays','start','end'],axis=1).drop_duplicates()
            try:
                df=df.drop('redzone',axis=1)
            except:
                pass

            df=df.reset_index().drop('index',axis=1).reset_index()

            df2=df2.reset_index()

            df=pd.merge(df,df2,on='index').drop('index',axis=1)
            df['driveid']=key
            df_d.append(df)

            for key2,val2 in val['plays'].items():
                for key3,val3 in val2['players'].items():
                    df=(pd.DataFrame(val3))
                    df['playerid']=key3
                    df['play']=key2
                    df['drive']=key
                    df['description']=val2['desc']
                    df['gid']=gid
                    df['posteam']=val2['posteam']
                    df_g.append(df)


        df=pd.concat(df_d).fillna(0)

        df['posteam']=df['posteam'].str.pad(3,'right')
        df['start yrdln']=np.where(df['start yrdln']=='',df['posteam']+' 0',df['start yrdln'])
        df['start yrdln']=np.where(df['start yrdln']=='50',df['posteam']+' 50',df['start yrdln'])
        df['start yrdln']=df['start yrdln'].str.replace('  ',' ')

        df['start yrdln']=np.where(df['posteam']==df['start yrdln'].str[:3].str.strip(),
                                   df['start yrdln'].str.split(' ').str[1],
                                   (50-df['start yrdln'].str.split(' ').str[1].astype(np.int64))+50)

        df['end yrdln']=df['start yrdln'].astype(np.int64)+df['penyds'].astype(np.int64)+df['ydsgained'].astype(np.int64)
        df['gid']=gid



        dteam={d[str(gid)]['home']['abbr']:d[str(gid)]['away']['abbr'],
               d[str(gid)]['away']['abbr']:d[str(gid)]['home']['abbr'],
              '':''}

        df['defteam']=df['posteam'].str.strip().apply(lambda x: dteam[x])

        df['points']=0

        df['points']=np.where(df['fds']>0,df['points']-(.2*df['fds']),df['points'])

        df['points']=np.where(df['result']=='Touchdown',
                              np.where(df['start yrdln'].astype(np.int64)<50,
                                       df['points']-3,
                                       df['points']-1),df['points'])

        df['points']=np.where(df['result']=='Field Goal',
                              np.where(df['start yrdln'].astype(np.int64)<50,
                                       df['points']-1,
                                       df['points']-0),df['points'])

        df['points']=np.where((df['fds']==0)&((df['result']=='Punt')|
                                             (df['result']=='Fumble')|
                                             (df['result']=='Interception')),
                              df['points']+1,
                              df['points'])
        df['points']=np.where((df['result']=='Downs'),
                              df['points']+1,
                              df['points'])


        drives.append(df.copy())
    df=pd.concat(df_g)
    statdfs=[]
    for key,val in statid.idmap.items():
        tdf=pd.DataFrame(val)
        tdf['statId']=key
        statdfs.append(tdf)

    st=pd.concat(statdfs)

    df2=pd.merge(df,st,on='statId',how='left')

    # df3=pd.merge(df2,pd.read_excel('points.xlsx'),
    #          left_on=['cat','fields'],
    #          right_on=['cat2','field']).\
    # drop({'cat_x','fields','cat2'},axis=1).\
    #     rename({'cat_y':'cat'},axis=1)

    df3=pd.merge(df2,pd.read_excel('points.xlsx'),
             left_on=['fields'],
             right_on=['field']).\
    drop({'cat_x','fields','cat2'},axis=1).\
        rename({'cat_y':'cat'},axis=1)

    df3['points']=np.where(df3['cat']=='yds',df3['points']*df3['yards'],df3['points'])
    df3['playerName']=df3['playerName'].fillna(1)
    df3['playerName']=np.where(df3['clubcode']==df3['posteam'],df3['playerName'],df3['clubcode'])
    df3['playerName']=np.where(df3['playerName']==1,
                               np.where(df3['cat']=='defense',
                                        df3['posteam'].str.strip().apply(lambda x: dteam[x]),
                                        df3['clubcode']),
                              df3['playerName'])
    plays=df3.copy()
    drives=pd.concat(drives)

    play_piv=plays.pivot_table(index=['clubcode', 'playerName', 'statId', 'yards',
           'play', 'drive', 'description', 'gid', 'posteam', 'cat',
           'field'],aggfunc={'playerid':lambda x: ','.join(x),
                                                   'points':np.mean}).reset_index()

    pp2=play_piv.pivot_table(index=['playerName','clubcode','gid'],values='points',aggfunc=sum).reset_index()

    dpiv=drives.pivot_table(index=['defteam','gid'],values='points',aggfunc=sum).reset_index()

    dpiv['clubcode']=dpiv['defteam']
    dpiv=dpiv[['defteam','clubcode','gid','points']]

    dpiv.columns=pp2.columns

    fullpiv=pd.concat([pp2,dpiv]).pivot_table(index=['playerName','clubcode','gid'],values='points',aggfunc=sum).reset_index()

    return (fullpiv)

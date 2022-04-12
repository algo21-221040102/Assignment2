#In[]

#Data is based on JoinQuant
from weakref import ref
from jqdata import *
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

#In[]
#Delete new stocks
def delnew(df):
    for i in df.index:
        security = df.loc[i, 'code']
        pub_date = df.loc[i, 'pub_date']
        pub_date = dt.datetime.strptime(str(pub_date),'%Y-%m-%d').date()
        try:
            list_date = get_security_info(security).start_date
        except:
            continue
        if pub_date-list_date < dt.timedelta(365):
            df.loc[i,'code'] = np.nan
    df = df.dropna()
    return df

#In[]
#Find the reference index of different stocks
def index(stock):
    if stock[0:3] == '000':
        ref = '399001.XSHE'
    elif stock[0:3] == '002':
        ref = '399005.XSHE'
    elif stock[0:3] == '300':
        ref = '399006.XSHE'
    elif stock[0] == '6':
        ref = '000001.XSHG'
    else:
        ref = '000300.XSHG'
    return ref

#In[]
def later(date, n=8):
    start = dt.datetime.strptime(str(date),'%Y-%m-%d')
    end = start+dt.datetime(n+14)
    days = get_trade_days(start, end)
    return days[n-1]

#In[]
def delta(start_date,end_date):
    days = get_trade_days(start_date,end_date)
    return len(days)

#In[]
year_list = [2014, 2015, 2016, 2017, 2018]
n=8                                         #The period after announcement
#p1, p2: Rising rate before/after announcement
#a1, a2: Abs of average rising rate
#r1, r2: Relative rising rate
#l1, l2: Average time between highest price and announcement
#insider: Inside trading proportion
#range: Announcement first day average high open range
#strategy: Strategic average annualized return
table = pd.DataFrame(np.zeros([5,13]), index = year_list
                    columns= ['p1', 'p2','a1','a2','r1','r2','l1','l2','h1','h2','insider','range','strategy'])

#In[]
for year in year_list:
    date1 = date1 = dt.date(year,1,1)
    date2 = dt.date(year+1,1,1)
    #Get annual performance forecast type of "performance significantly increased" data
    q = query(finance.STK_FIN_FORCAST).filter(finance.STK_FIN_FORCAST.type=='业绩大幅上升',
                                          finance.STK_FIN_FORCAST.pub_date>date1,
                                          finance.STK_FIN_FORCAST.pub_date<date2,)
    forcast = finance.run_query(q)[['code','pub_date','type']]
    forcast = delnew(forcast)
    forcast['reference'] = forcast['code'].map(index)
    print('Year:'+str(year))
    print(forcast.tail())
    for i in forcast.index:
        stock = forcast.loc[i,'code']
        reference = forcast.loc[i,'reference']
        date = forcast.loc[i,'pub_date']
        end = later(date)
        try:
            prices = get_price([stock,reference],count=2*n+1,end_date=end,fields=['open','close','high'])
        except:
            continue
        # Calculate 'p1', 'p2','a1','a2','r1','r2','l1','l2','h1','h2','insider','range','return'
        highest1 = prices['high'][stock][1:n+1].max()

        highest2 = prices['high'][stock][n+1:].max()

        date_high1 = prices['high'][stock][1:n+1].idxmax()

        date_high2 = prices['high'][stock][n:].idxmax()

        forcast.loc[i,'abs1'] = highest1/prices['close'][stock][0]-1

        forcast.loc[i,'abs2'] = highest2/prices['close'][stock][n]-1

        ind_ret1 = prices['high'].loc[date_high1,reference]/prices['close'][reference][0]-1

        ind_ret2 = prices['high'].loc[date_high2,reference]/prices['close'][reference][n]-1

        forcast.loc[i,'rel1'] = forcast.loc[i,'abs1']-ind_ret1

        forcast.loc[i,'rel2'] = forcast.loc[i,'abs2']-ind_ret2

        forcast.loc[i,'len1'] = delta(date_high1,date)-1

        forcast.loc[i,'len2'] = delta(date,date_high2)

        forcast.loc[i,'high1'] = highest1/prices['close'][stock][n]

        forcast.loc[i,'high2'] = highest2/prices['close'][stock][n]
        
        open_price = prices['open'][stock][n+1]

        close_price = prices['open'][stock][n+4]

        forcast.loc[i,'range'] = open_price/prices['close'][stock][n]-1

        forcast.loc[i,'strategy'] = close_price/open_price-1
    
    forcast = forcast.dropna()

    table.loc[year,'p1'] = round(len(forcast[forcast.abs1>0])/len(forcast)*100,1)

    table.loc[year,'p2'] = round(len(forcast[forcast.abs2>0])/len(forcast)*100,1)

    table.loc[year,'a1'] = round(forcast['abs1'].mean()*100,1)

    table.loc[year,'a2'] = round(forcast['abs2'].mean()*100,1)

    table.loc[year,'r1'] = round(forcast['rel1'].mean()*100,1)

    table.loc[year,'r2'] = round(forcast['rel2'].mean()*100,1)

    table.loc[year,'l1'] = round(forcast['len1'].mean(),1)

    table.loc[year,'l2'] = round(forcast['len2'].mean(),1)

    table.loc[year,'h1'] = round(forcast['high1'].mean(),2)

    table.loc[year,'h2'] = round(forcast['high2'].mean(),2)

    condition = (forcast.rel1>0)&(forcast.rel2<0)

    table.loc[year,'insider'] = round(len(forcast[condition])/len(forcast)*100,1)

    table.loc[year,'range'] = round(forcast['range'].mean()*100,1)

    table.loc[year,'strategy'] = round(forcast['strategy'].mean()*100*240/3,1)

#In[]
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
#Setting figure parameters
fig = plt.figure(figsize=(7,4))
w = 0.35
t = table.index
p1 = table.p1
p2 = table.p2
plt.bar(t,p1,color='c',label='Rise probability before announcement',width=w,alpha=0.7)
plt.bar(t+w,p2,color='m',label='Rise probability after announcement',width=w,alpha=0.7)

plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)

plt.xticks(fontsize=14)
plt.yticks(np.arange(0,110,20),fontsize=14)

plt.xlabel('year',fontsize=14)
plt.ylabel('probability %',fontsize=14)

for a,b in zip(t,p1):
    plt.text(a,b+1,b,ha='center', va= 'bottom',fontsize=12,color='c')
for a,b in zip(t,p2):
    plt.text(a+w,b+1,b,ha='center', va= 'bottom',fontsize=12,color='m')

plt.legend(bbox_to_anchor=(1.02, 1),fontsize=14)
plt.title('Rising probability',fontsize=15)
plt.show()

#In[]

a1 = table.a1
a2 = table.a2
fig = plt.figure(figsize=(7,10))
plt.subplot(2,1,1)
plt.bar(t,a1,color='blue',label='The highest average increase before the announcement',width=w,alpha=0.7)
plt.bar(t+w,a2,color='orange',label='The highest average increase after the announcement',width=w,alpha=0.7)
plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)
plt.xticks(fontsize=14)
plt.yticks(np.arange(0,15,2),fontsize=14)
plt.xlabel('Year',fontsize=14)
plt.ylabel('Rising rate%',fontsize=14)
for a,b in zip(t,a1):
    plt.text(a,b+0.1,b,ha='center', va= 'bottom',fontsize=12,color='blue')
for a,b in zip(t,a2):
    plt.text(a+w,b+0.1,b,ha='center', va= 'bottom',fontsize=12,color='orangered')
plt.legend(fontsize=13)
plt.title('Stock prices rose by an average of eight days',fontsize=15)

plt.show()


r1 = table.r1
r2 = table.r2
fig = plt.figure(figsize=(7,10))
plt.subplot(2,1,2)
plt.bar(t,r1,color='blue',label='Average before the announcement of the highest relative rise',width=w,alpha=0.7)
plt.bar(t+w,r2,color='chocolate',label='Average after the announcement of the highest relative rise',width=w,alpha=0.7)
plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)
plt.xticks(fontsize=14)
plt.yticks(np.arange(0,11,2),fontsize=14)
plt.xlabel('Year',fontsize=14)
plt.ylabel('Rising rate%',fontsize=14)
for a,b in zip(t,r1):
    plt.text(a,b+0.1,b,ha='center', va= 'bottom',fontsize=12,color='deepskyblue')
for a,b in zip(t,r2):
    plt.text(a+w,b+0.1,b,ha='center', va= 'bottom',fontsize=12,color='chocolate')
plt.legend(fontsize=13)
plt.title('The highest relative gain in an 8-day average',fontsize=15)

plt.show()

#In[]

r = table.range

fig = plt.figure(figsize=(7,4))

plt.bar(t,r,color='red',label='Announcement first day average high open range',width=0.5,alpha=0.7)

plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)

plt.xticks(fontsize=14)
plt.yticks(np.arange(0,2.1,0.5),fontsize=14)

plt.xlabel('Year',fontsize=14)
plt.ylabel('Rising rate%',fontsize=14)

for a,b in zip(t,r):
    plt.text(a,b+0.1,b,ha='center', va= 'bottom',fontsize=13,color='red')

plt.legend(fontsize=14)
plt.title('Announcement first day average high open range',fontsize=15)
plt.show()

#In[]

l1 = table.l1
l2 = table.l2

fig = plt.figure(figsize=(7,4))

plt.bar(t,l1,color='olive',label='Average response time before announcement',width=w,alpha=0.7)
plt.bar(t+w,l2,color='pink',label='Average response time after announcement',width=w,alpha=0.7)

plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)

plt.xticks(fontsize=14)
plt.yticks(np.arange(0,7,1),fontsize=14)

plt.xlabel('Year',fontsize=14)
plt.ylabel('Days',fontsize=14)

for a,b in zip(t,l1):
    plt.text(a,b+0.1,b,ha='center', va= 'bottom',fontsize=12,color='olive')
for a,b in zip(t,l2):
    plt.text(a+w,b+0.1,b,ha='center', va= 'bottom',fontsize=12,color='deeppink')
 
plt.legend(bbox_to_anchor=(1.02, 1),fontsize=14)
plt.title('average response time',fontsize=15)
plt.show()

#In[]

h1 = table.h1
h2 = table.h2

fig = plt.figure(figsize=(7,4))

plt.bar(t,h1,color='teal',label='Average high price multiple before the announcement',width=w,alpha=0.7)

plt.bar(t+w,h2,color='orange',label='Average high price multiple after the announcement',width=w,alpha=0.7)

plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)

plt.xticks(fontsize=14)
plt.yticks(np.arange(0,1.5,0.2),fontsize=14)

plt.xlabel('Year',fontsize=14)
plt.ylabel('multiple',fontsize=14)

for a,b in zip(t,h1):
    plt.text(a,b+0.03,b,ha='center', va= 'bottom',fontsize=12,color='teal')
for a,b in zip(t,h2):
    plt.text(a+w,b+0.03,b,ha='center', va= 'bottom',fontsize=12,color='darkorange')
 
plt.legend(bbox_to_anchor=(1.02, 1),fontsize=14)
plt.title('Average multiple of the highest price',fontsize=15)
plt.show()

#In[]

insider = table.insider

fig = plt.figure(figsize=(7,4))

plt.bar(t,insider,color='dimgrey',label='Insider trading ratio',width=0.5,alpha=0.7)

plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)

plt.xticks(fontsize=14)
plt.yticks(np.arange(0,35,5),fontsize=14)

plt.xlabel('Year',fontsize=14)
plt.ylabel('ratio%',fontsize=14)

for a,b in zip(t,insider):
    plt.text(a,b+0.5,b,ha='center', va= 'bottom',fontsize=14,color='dimgrey')
 
plt.legend(fontsize=14)
plt.title('Insider trading ratio',fontsize=15)
plt.show()

#In[]

s = table.strategy

fig = plt.figure(figsize=(7,4))

plt.bar(t,s,color='orange',label='Average annualized return',width=0.5,alpha=0.7)

plt.grid(linestyle='-',linewidth=1,axis='y',alpha=0.5)

plt.xticks(fontsize=14)
plt.yticks(np.arange(-60,155,30),fontsize=14)

plt.xlabel('Year',fontsize=14)
plt.ylabel('yield%',fontsize=14)

for a,b in zip(t,s):
    if b>=0:
        plt.text(a,b+5,b,ha='center', va= 'bottom',fontsize=14,color='darkorange')
    else:
        plt.text(a,b-15,b,ha='center', va= 'bottom',fontsize=14,color='darkorange')

plt.legend(fontsize=14)
plt.title('Average annualized return',fontsize=15)
plt.show()
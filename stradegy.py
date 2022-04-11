#In[]
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
#p1, p2: Rising 
table = pd.DataFrame(np.zeros([5,13]), index = year_list
                    columns= ['p1', 'p2','a1','a2','r1','r2','l1','l2','h1','h2','insider','range','strategy'])
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
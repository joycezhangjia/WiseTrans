#from sklearn import preprocessing
#from sklearn.linear_model import LinearRegression
#import statsmodels.api as sm
#import sklearn.metrics
#from sklearn.model_selection import train_test_split
#from sklearn.model_selection import KFold

import xgboost as xgb
import numpy as np
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

#from sklearn.model_selection import cross_val_score
#from sklearn.datasets import make_blobs
#from sklearn.ensemble import RandomForestClassifier
#from sklearn.ensemble import ExtraTreesClassifier
#from sklearn.tree import DecisionTreeClassifier
#import matplotlib.pyplot as plt
#from sklearn.model_selection import train_test_split
#from sklearn.model_selection import train_test_split
#from sklearn.datasets import load_breast_cancer
#from sklearn.model_selection import GridSearchCV

#import pydotplus
#from sklearn import tree
#from sklearn.preprocessing import LabelEncoder
#from io import BytesIO as StringIO

#from collections import Counter

from time import time

import m2cgen as m2c

# from imblearn.over_sampling import RandomOverSampler

def min_max_norm(x):
    x = np.array(x)
    x_norm = (x - np.min(x)) / (np.max(x) - np.min(x))
    return x_norm, np.min(x), np.max(x)


def test_min_max_norm(x, min, max):
    x = np.array(x)
    x_norm = (x - min) / (max - min)
    return x_norm


def train_feature_matrix(values):

    minmax = []
    value, min, max = min_max_norm(values['Judge_Perf'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Perf'] = pd.Series(value, index=values['Judge_Perf'].index)
    value, min, max = min_max_norm(values['Judge_Thp'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Thp'] = pd.Series(value, index=values['Judge_Thp'].index)
    value, min, max = min_max_norm(values['Judge_Rtt_recent'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Rtt_recent'] = pd.Series(value, index=values['Judge_Rtt_recent'].index)
    value, min, max = min_max_norm(values['Judge_Rtt_9'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Rtt_9'] = pd.Series(value, index=values['Judge_Rtt_9'].index)
    value, min, max = min_max_norm(values['Judge_Rtt_3'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Rtt_3'] = pd.Series(value, index=values['Judge_Rtt_3'].index)
    value, min, max = min_max_norm(values['Judge_Rtt_rate'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Rtt_rate'] = pd.Series(value, index=values['Judge_Rtt_rate'].index)
    value, min, max = min_max_norm(values['Judge_Ttfb'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Ttfb'] = pd.Series(value, index=values['Judge_Ttfb'].index)
    value, min, max  = min_max_norm(values['Judge_Ttfb_9'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Ttfb_9'] = pd.Series(value, index=values['Judge_Ttfb_9'].index)
    value, min, max = min_max_norm(values['Judge_Ttfb_3'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Ttfb_3'] = pd.Series(value, index=values['Judge_Ttfb_3'].index)
    value, min, max = min_max_norm(values['Judge_Ttfb_rate'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Ttfb_rate'] = pd.Series(value, index=values['Judge_Ttfb_rate'].index)
    value, min, max = min_max_norm(values['Judge_Retran_short'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Retran_short'] = pd.Series(value, index=values['Judge_Retran_short'].index)
    value, min, max = min_max_norm(values['Judge_Retran_long'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Retran_long'] = pd.Series(value, index=values['Judge_Retran_long'].index)

    feature = values
    return feature, minmax

def test_feature_matrix(values, minmax):

    value = test_min_max_norm(values['Judge_Perf'].values, minmax[0], minmax[1])
    values['Judge_Perf'] = pd.Series(value, index=values['Judge_Perf'].index)
    value = test_min_max_norm(values['Judge_Thp'].values, minmax[2], minmax[3])
    values['Judge_Thp'] = pd.Series(value, index=values['Judge_Thp'].index)
    value = test_min_max_norm(values['Judge_Rtt_recent'].values, minmax[4], minmax[5])
    values['Judge_Rtt_recent'] = pd.Series(value, index=values['Judge_Rtt_recent'].index)
    value = test_min_max_norm(values['Judge_Rtt_9'].values, minmax[6], minmax[7])
    values['Judge_Rtt_9'] = pd.Series(value, index=values['Judge_Rtt_9'].index)
    value = test_min_max_norm(values['Judge_Rtt_3'].values, minmax[8], minmax[9])
    values['Judge_Rtt_3'] = pd.Series(value, index=values['Judge_Rtt_3'].index)
    value = test_min_max_norm(values['Judge_Rtt_rate'].values, minmax[10], minmax[11])
    values['Judge_Rtt_rate'] = pd.Series(value, index=values['Judge_Rtt_rate'].index)
    value = test_min_max_norm(values['Judge_Ttfb'].values, minmax[12], minmax[13])
    values['Judge_Ttfb'] = pd.Series(value, index=values['Judge_Ttfb'].index)
    value = test_min_max_norm(values['Judge_Ttfb_9'].values, minmax[14], minmax[15])
    values['Judge_Ttfb_9'] = pd.Series(value, index=values['Judge_Ttfb_9'].index)
    value = test_min_max_norm(values['Judge_Ttfb_3'].values, minmax[16], minmax[17])
    values['Judge_Ttfb_3'] = pd.Series(value, index=values['Judge_Ttfb_3'].index)
    value = test_min_max_norm(values['Judge_Ttfb_rate'].values, minmax[18], minmax[19])
    values['Judge_Ttfb_rate'] = pd.Series(value, index=values['Judge_Ttfb_rate'].index)
    value = test_min_max_norm(values['Judge_Retran_short'].values, minmax[20], minmax[21])
    values['Judge_Retran_short'] = pd.Series(value, index=values['Judge_Retran_short'].index)
    value = test_min_max_norm(values['Judge_Retran_long'].values, minmax[22], minmax[23])
    values['Judge_Retran_long'] = pd.Series(value, index=values['Judge_Retran_long'].index)
    feature = values
    return feature


def train_tcp(df1):

    df1, minmax = train_feature_matrix(
        df1.drop(['BW', 'Loss', 'Delay', 'TCP-Mean', 'QUIC-Mean', 'TCP-SucR', 'QUIC-SucR'], axis=1))


    train_feature = df1[['Judge_Retran_long', 'Judge_Ttfb_9', 'Judge_Thp', 'Judge_Rtt_9', 'Judge_Ttfb_rate',
                   'Judge_Ttfb', 'Judge_Perf']]
    train_label = df1['Best']

    gbm = xgb.XGBClassifier(learning_rate=0.3, n_estimators=100, max_depth=7, min_child_weight=1, seed=27,
                            subsample=0.9, colsample_bytree=0.8, gamma=0.2, reg_alpha=0, reg_lambda=1, n_jobs=44,
                            eval_metric='merror', objective='binary:logistic')

    print("Begin to fit TCP")
    t0 = time()
    gbm.fit(train_feature, train_label)
    print("Done Fiting in %0.3fs" % (time() - t0))
    jia = gbm.feature_importances_
    print(jia)
    print(gbm.feature_importances_)
    gbm.save_model('TCP.model')
    code = m2c.export_to_c(gbm)
    return code, minmax


def train_quic(df1):
    df1, minmax = train_feature_matrix(
        df1.drop(['BW', 'Loss', 'Delay', 'TCP-Mean', 'QUIC-Mean', 'TCP-SucR', 'QUIC-SucR'], axis=1))
    #df1 = df1.reindex(np.random.permutation(df1.index))

    train_feature = df1[['Judge_Retran_long', 'Judge_Ttfb_9', 'Judge_Ttfb_rate', 'Judge_Rtt_9', 'Judge_Thp']]
    train_label = df1['Best']

    gbm = xgb.XGBClassifier(learning_rate=0.3, n_estimators=200, max_depth=7, min_child_weight=1, seed=27,
                            subsample=0.9, colsample_bytree=0.8, gamma=0.3, reg_alpha=0, reg_lambda=1, n_jobs=44,
                            eval_metric='merror', objective='binary:logistic')
    print("Begin to fit QUIC")
    t0 = time()
    gbm.fit(train_feature, train_label)
    print("Done Fiting in %0.3fs" % (time() - t0))
    print(gbm.feature_importances_)
    gbm.save_model('QUIC.model')
    code = m2c.export_to_c(gbm)
    return code, minmax


def train(filename1):
    df1 = pd.read_csv(filename1, index_col=None)
    df1 = df1.reindex(np.random.permutation(df1.index))


    df1_tcp = df1.loc[df1.Protocol == 0, ["BW", "Loss", "Delay", "Window", "Timestamp", "Wise", "Method", "NetType", "OsType", "Status", "Quic_alter_race",
         "Is_zero_rtt", "Received_bytes", "Sent_bytes", "Protocol", "Weak", "Duration", "Ttfb", "Ttfb_avg", "Judge_Ttfb",
         "Judge_Ttfb_9", "Judge_Ttfb_3", "Ttfb_rate", "Judge_Ttfb_rate", "Rtt", "Judge_Rtt_recent", "Judge_Rtt_9",
         "Judge_Rtt_3", "Judge_Rtt_rate", "Retran", "Judge_Retran_short", "Judge_Retran_long", "Throughput", "Performance",
         "Judge_Thp", "Judge_Perf", "Sends", "InitCon", "Udp", "Body_recv", "Connection Time", "Transfer Time", "Dns",
         "Redirect", "Pending", "Head_recv", "Ssl", "SinChange", "TcpCon", "SinEnStart", "TCP-Mean", "QUIC-Mean",
         "TCP-Med", "QUIC-Med", "TCP-SucR", "QUIC-SucR", "Best"]]#0:57]
    df1_quic = df1.loc[df1.Protocol == 1, ["BW", "Loss", "Delay", "Window", "Timestamp", "Wise", "Method", "NetType", "OsType", "Status", "Quic_alter_race",
         "Is_zero_rtt", "Received_bytes", "Sent_bytes", "Protocol", "Weak", "Duration", "Ttfb", "Ttfb_avg", "Judge_Ttfb",
         "Judge_Ttfb_9", "Judge_Ttfb_3", "Ttfb_rate", "Judge_Ttfb_rate", "Rtt", "Judge_Rtt_recent", "Judge_Rtt_9",
         "Judge_Rtt_3", "Judge_Rtt_rate", "Retran", "Judge_Retran_short", "Judge_Retran_long", "Throughput", "Performance",
         "Judge_Thp", "Judge_Perf", "Sends", "InitCon", "Udp", "Body_recv", "Connection Time", "Transfer Time", "Dns",
         "Redirect", "Pending", "Head_recv", "Ssl", "SinChange", "TcpCon", "SinEnStart", "TCP-Mean", "QUIC-Mean",
         "TCP-Med", "QUIC-Med", "TCP-SucR", "QUIC-SucR", "Best"]]#0:57]

    t_code, t_minmax = train_tcp(df1_tcp)
    q_code, q_minmax = train_quic(df1_quic)

    ft = open('tcp_minmax.txt','w')
    print(t_minmax)
    for t in t_minmax:
        ft.write(str(t)+', ')
    ft.write('\n')
    ft.close()
    ft = open('tcp_code_all.txt', 'w')
    ft.write(t_code)
    ft.close()
    fq = open('quic_minmax.txt','w')
    for q in q_minmax:
        fq.write(str(q)+', ')
    fq.write('\n')
    fq = open('quic_code_all.txt', 'w')
    fq.write(q_code)
    fq.close()

if __name__ == '__main__':
    train("Train_data.csv")




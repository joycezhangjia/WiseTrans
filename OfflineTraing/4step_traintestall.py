import sklearn.metrics
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

import xgboost as xgb
import numpy as np
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.model_selection import cross_val_score
from time import time
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
    value, min, max = min_max_norm(values['Judge_Ttfb_9'].values)
    print(values['Judge_Ttfb_9'].values)
    minmax.append(min)
    minmax.append(max)
    values['Judge_Ttfb_9'] = pd.Series(value, index=values['Judge_Ttfb_9'].index)
    print(value)
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


def train_tcp(df1, df2):

    df1, minmax = train_feature_matrix(
        df1.drop(['BW', 'Loss', 'Delay', 'TCP-Mean', 'QUIC-Mean', 'TCP-SucR', 'QUIC-SucR'], axis=1))
    #print(df1[['Judge_Perf']])
    train_feature = df1[['Judge_Retran_long', 'Judge_Ttfb_9', 'Judge_Thp', 'Judge_Rtt_9', 'Judge_Ttfb_rate', 'Judge_Ttfb', 'Judge_Perf']]
    train_label = df1['Best']

    df2 = test_feature_matrix(
        df2.drop(['BW', 'Loss', 'Delay', 'TCP-Mean', 'QUIC-Mean', 'TCP-SucR', 'QUIC-SucR'], axis=1), minmax)

    test_feature = df2[['Judge_Retran_long', 'Judge_Ttfb_9', 'Judge_Thp', 'Judge_Rtt_9', 'Judge_Ttfb_rate', 'Judge_Ttfb', 'Judge_Perf']]
    test_label = df2['Best']

    gbm = xgb.XGBClassifier(learning_rate=0.3, n_estimators=100, max_depth=7, min_child_weight=1, seed=27,
                            subsample=0.9, colsample_bytree=0.8, gamma=0.2, reg_alpha=0, reg_lambda=1, n_jobs=44,
                            eval_metric='merror', objective='binary:logistic')
    print("Begin to fit TCP")
    t0 = time()
    gbm.fit(train_feature, train_label)
    y_score = gbm.predict(test_feature)
    print("Done Fiting in %0.3fs" % (time() - t0))
    fi = gbm.feature_importances_
    print(fi)
    y_ret = y_score
    ret = pd.Series(y_ret, index=df2.index)

    confusion_matrix = sklearn.metrics.confusion_matrix(test_label, ret.values)
    print('confusion_matrix:\n', confusion_matrix)

    precision, recall, fscore, support = sklearn.metrics.precision_recall_fscore_support(
        test_label, ret.values)
    print(precision, recall, fscore, support)
    precision_macro, recall_macro, fscore_macro, support_macro = sklearn.metrics.precision_recall_fscore_support(
        test_label, ret.values, beta=1, average='macro')
    fscore_macro = float(2 * precision_macro * recall_macro / (precision_macro + recall_macro))
    print('macro:', precision_macro, recall_macro, fscore_macro, support_macro)

    return len(y_score), precision_macro, recall_macro, fscore_macro, minmax


def train_quic(df1, df2):
    df1, minmax = train_feature_matrix(
        df1.drop(['BW', 'Loss', 'Delay', 'TCP-Mean', 'QUIC-Mean', 'TCP-SucR', 'QUIC-SucR'], axis=1))

    train_feature = df1[['Judge_Retran_long', 'Judge_Ttfb_9', 'Judge_Ttfb_rate', 'Judge_Rtt_9', 'Judge_Thp']]
    train_label = df1['Best']

    df2 = test_feature_matrix(
        df2.drop(['BW', 'Loss', 'Delay', 'TCP-Mean', 'QUIC-Mean', 'TCP-SucR', 'QUIC-SucR'], axis=1), minmax)

    test_feature = df2[['Judge_Retran_long', 'Judge_Ttfb_9', 'Judge_Ttfb_rate', 'Judge_Rtt_9', 'Judge_Thp']]
    test_label = df2['Best']

    # gbm = xgb.XGBClassifier(learning_rate=0.3, n_estimators=400, n_jobs=44, eval_metric='merror',
    #                        objective='binary:logistic')

    gbm = xgb.XGBClassifier(learning_rate=0.3, n_estimators=200, max_depth=7, min_child_weight=1, seed=27,
                            subsample=0.9, colsample_bytree=0.8, gamma=0.3, reg_alpha=0, reg_lambda=1, n_jobs=44,
                            eval_metric='merror', objective='binary:logistic')
    print("Begin to fit QUIC")
    t0 = time()
    gbm.fit(train_feature, train_label)
    y_score = gbm.predict(test_feature)
    print("Done Fiting in %0.3fs" % (time() - t0))
    fi = gbm.feature_importances_
    print(fi)
    y_ret = y_score
    ret = pd.Series(y_ret, index=df2.index)
    # ret = ret.reindex(test_data.index)
    confusion_matrix = sklearn.metrics.confusion_matrix(test_label, ret.values)
    print('confusion_matrix:\n', confusion_matrix)

    precision, recall, fscore, support = sklearn.metrics.precision_recall_fscore_support(
        test_label, ret.values)
    print(precision, recall, fscore, support)
    precision_macro, recall_macro, fscore_macro, support_macro = sklearn.metrics.precision_recall_fscore_support(
        test_label, ret.values, beta=1, average='macro')
    fscore_macro = float(2 * precision_macro * recall_macro / (precision_macro + recall_macro))
    print('macro:', precision_macro, recall_macro, fscore_macro, support_macro)
    return len(y_score), precision_macro, recall_macro, fscore_macro, minmax

def train(filename1):
    df1 = pd.read_csv(filename1, index_col=None)
    df1 = df1.reindex(np.random.permutation(df1.index))
    df12, df3 = train_test_split(df1, test_size=0.333, random_state=0)
    df1 = df12
    df2 = df3

    feature_name = ["BW", "Loss", "Delay", "Window", "Timestamp", "Wise", "Method", "NetType", "OsType", "Status", "Quic_alter_race",
         "Is_zero_rtt", "Received_bytes", "Sent_bytes", "Protocol", "Weak", "Duration", "Ttfb", "Ttfb_avg", "Judge_Ttfb",
         "Judge_Ttfb_9", "Judge_Ttfb_3", "Ttfb_rate", "Judge_Ttfb_rate", "Rtt", "Judge_Rtt_recent", "Judge_Rtt_9",
         "Judge_Rtt_3", "Judge_Rtt_rate", "Retran", "Judge_Retran_short", "Judge_Retran_long", "Throughput", "Performance",
         "Judge_Thp", "Judge_Perf", "Sends", "InitCon", "Udp", "Body_recv", "Connection Time", "Transfer Time", "Dns",
         "Redirect", "Pending", "Head_recv", "Ssl", "SinChange", "TcpCon", "SinEnStart", "TCP-Mean", "QUIC-Mean",
         "TCP-Med", "QUIC-Med", "TCP-SucR", "QUIC-SucR", "Best"]
    df1_tcp = df1.loc[df1.Protocol == 0, feature_name]
    df1_quic = df1.loc[df1.Protocol == 1, feature_name]

    df2_tcp = df2.loc[df2.Protocol == 0, feature_name]
    df2_quic = df2.loc[df2.Protocol == 1, feature_name]

    tcplen, t_p, t_r, t_f, t_minmax = train_tcp(df1_tcp, df2_tcp)
    quiclen, q_p, q_r, q_f, q_minmax = train_quic(df1_quic, df2_quic)

    print("******************ALL************")
    precision_macro = (t_p * tcplen + q_p *quiclen ) / (tcplen + quiclen)
    recall_macro = (t_r * tcplen + q_r *quiclen ) / (tcplen + quiclen)
    fscore_macro = float(2 * precision_macro * recall_macro / (precision_macro + recall_macro))
    print('macro:', precision_macro, recall_macro, fscore_macro)


if __name__ == '__main__':
    train("Train_data.csv")





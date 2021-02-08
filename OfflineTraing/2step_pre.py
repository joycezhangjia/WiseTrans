import json
import numpy as np
import pandas as pd
import csv



def process(filename):

    bws = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1, 1.5, 2, 10, 40, 80]
    losss = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 20, 25, 30, 35, 40]
    delays = [0, 15, 30, 45, 60, 80, 100, 200, 300, 400, 600, 800, 1000, 1250, 1500]


    windows = [30]

    df = pd.read_csv(filename, index_col=None)
    for bw in bws:
        for loss in losss:
            for delay in delays:
                for window in windows:
                    data = df.loc[
                        (df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), ['Protocol', 'Status', 'Duration']]


                    data_t_s = data.loc[data.Protocol == 0, ['Status', 'Duration']]
                    data_q_s = data.loc[data.Protocol == 1, ['Status', 'Duration']]
                    if float(data_q_s.shape[0]) == 0:
                        continue
                    print(bw, loss, delay)
                    data_t = data_t_s.loc[data_t_s.Status == 0, 'Duration']
                    data_q = data_q_s.loc[data_q_s.Status == 0, 'Duration']

                    suc_t = float(data_t.shape[0]) / float(data_t_s.shape[0])
                    suc_q = float(data_q.shape[0]) / float(data_q_s.shape[0])

                    tcp_dur = data_t.values.tolist()
                    quic_dur = data_q.values.tolist()
                    tcp_mean = np.mean(tcp_dur)
                    quic_mean = np.mean(quic_dur)
                    tcp_med = np.median(tcp_dur)
                    quic_med = np.median(quic_dur)
                    if float(tcp_mean) / float(quic_mean) > 1.4 and tcp_med > quic_med:
                        best = 1
                    elif tcp_med < quic_med and float(tcp_mean) / float(quic_mean) > 1.5:
                        best = 1
                    else:
                        best = 0

                    df.loc[
                        (df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), ['TCP-Mean']] = tcp_mean

                    df.loc[
                        (df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), [
                            'TCP-Mean']] = tcp_mean
                    df.loc[(df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), ['TCP-Med']] = tcp_med
                    df.loc[
                        (df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), [
                            'QUIC-Mean']] = quic_mean
                    df.loc[
                        (df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), [
                            'QUIC-Med']] = quic_med
                    df.loc[(df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), ['TCP-SucR']] = suc_t
                    df.loc[(df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), ['QUIC-SucR']] = suc_q
                    df.loc[(df['BW'] == bw) & (df['Loss'] == loss) & (df['Delay'] == delay) & (df['Window'] == window), ['Best']] = best

    data = df.loc[(df['Judge_Perf'] >= 0) & (df['Judge_Thp'] >= 0) & (df['Judge_Rtt_9'] >= 0) & (df['Judge_Ttfb'] >= 0) & (df['Judge_Ttfb_9'] >= 0) & (df['Judge_Ttfb_rate'] >= 0) & (df['Judge_Retran_long'] >= 0), ["BW", "Loss", "Delay", "Window", "Timestamp", "Wise", "Method", "NetType", "OsType", "Status", "Quic_alter_race", "Is_zero_rtt", "Received_bytes", "Sent_bytes", "Protocol", "Weak", "Duration", "Ttfb", "Ttfb_avg", "Judge_Ttfb", "Judge_Ttfb_9", "Judge_Ttfb_3", "Ttfb_rate", "Judge_Ttfb_rate", "Rtt", "Judge_Rtt_recent", "Judge_Rtt_9", "Judge_Rtt_3", "Judge_Rtt_rate", "Retran", "Judge_Retran_short", "Judge_Retran_long", "Throughput", "Performance",
         "Judge_Thp", "Judge_Perf", "Sends", "InitCon", "Udp", "Body_recv", "Connection Time", "Transfer Time", "Dns",
         "Redirect", "Pending", "Head_recv", "Ssl", "SinChange", "TcpCon", "SinEnStart", "TCP-Mean", "QUIC-Mean",
         "TCP-Med", "QUIC-Med", "TCP-SucR", "QUIC-SucR", "Best"]]#0:57]

    data = data.loc[((df['Delay'] == 15) & (df['Judge_Rtt_9'] >= 15)) | ((df['Delay'] == 45) & (df['Judge_Rtt_9'] >= 45)) | ((df['Delay'] == 80) & (df['Judge_Rtt_9'] >= 80)) | ((df['Delay'] == 200) & (df['Judge_Rtt_9'] >= 200)), ["BW", "Loss", "Delay", "Window", "Timestamp", "Wise", "Method", "NetType", "OsType", "Status", "Quic_alter_race", "Is_zero_rtt", "Received_bytes", "Sent_bytes", "Protocol", "Weak", "Duration", "Ttfb", "Ttfb_avg", "Judge_Ttfb", "Judge_Ttfb_9", "Judge_Ttfb_3", "Ttfb_rate", "Judge_Ttfb_rate", "Rtt", "Judge_Rtt_recent", "Judge_Rtt_9", "Judge_Rtt_3", "Judge_Rtt_rate", "Retran", "Judge_Retran_short", "Judge_Retran_long", "Throughput", "Performance", "Judge_Thp", "Judge_Perf", "Sends", "InitCon", "Udp", "Body_recv", "Connection Time", "Transfer Time", "Dns",
         "Redirect", "Pending", "Head_recv", "Ssl", "SinChange", "TcpCon", "SinEnStart", "TCP-Mean", "QUIC-Mean",
         "TCP-Med", "QUIC-Med", "TCP-SucR", "QUIC-SucR", "Best"]]# 0:57]

    data.to_csv('Train_data.csv', index=False)


if __name__ == '__main__':
    process("data.csv")

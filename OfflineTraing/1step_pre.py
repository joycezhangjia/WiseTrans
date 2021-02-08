import json
import numpy as np
import csv

def process(log):
    time = []
    try:
        pos = 0
        for i in range(0, 3):
            if log[pos] != '[':
                raise Exception()
            pos += 1
            lo = pos
            while log[pos] != ']':
                pos += 1
            hi = pos
            pos += 1
            time.append(log[lo:hi])

        #
        msg = log[pos + 1:]
        i = len(msg) - 1
        while msg[i] != ']':
            i -= 1
        msg = msg[:i]
        if '[127.0.0.1][INFO]' in msg:
            raise Exception()
        else:
            info = json.loads(msg)
            # (msg)
            info['timestamp'] = time[0]
            if "https://quic.baidu.com" in info['base']['url']:# and int(info['base']['status']) == 0:
                return info
            else:
                pass
            # return info
    except:
        pass


def process_stats(data):
    try:
        info = json.loads(data)
        return info
    except:
        pass

def dowithr(weak_net_reason):

    reason = weak_net_reason.split("**CNT: ")

    weak_reason = []
    for x in reason:
        if "t_rate" in x:
            weak_reason.append(x)
    flag = len(weak_reason)
    return weak_reason, flag


def main():

    bws = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1, 1.5, 2, 10, 40, 80]
    losss = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 20]
    delays = [0, 15, 30, 45, 60, 80, 100, 200, 300, 400, 600, 800, 1000, 1250, 1500]

    windows = [30]

    files = []

    for bw in bws:
        for loss in losss:
            for delay in delays:
                for window in windows:
                    files.append("Test1220_" + str(bw) + "_" + str(loss) + "_" + str(delay) + "_" + str(window))

    f = open('data.csv', 'w')
    csv_writer = csv.writer(f)
    csv_writer.writerow(
        ["BW", "Loss", "Delay", "Window", "Timestamp", "Wise", "Method", "NetType", "OsType", "Status", "Quic_alter_race",
         "Is_zero_rtt", "Received_bytes", "Sent_bytes", "Protocol", "Weak", "Duration", "Ttfb", "Ttfb_avg", "Judge_Ttfb",
         "Judge_Ttfb_9", "Judge_Ttfb_3", "Ttfb_rate", "Judge_Ttfb_rate", "Rtt", "Judge_Rtt_recent", "Judge_Rtt_9",
         "Judge_Rtt_3", "Judge_Rtt_rate", "Retran", "Judge_Retran_short", "Judge_Retran_long", "Throughput", "Performance",
         "Judge_Thp", "Judge_Perf", "Sends", "InitCon", "Udp", "Body_recv", "Connection Time", "Transfer Time", "Dns",
         "Redirect", "Pending", "Head_recv", "Ssl", "SinChange", "TcpCon", "SinEnStart", "TCP-Mean", "QUIC-Mean",
         "TCP-Med", "QUIC-Med", "TCP-SucR", "QUIC-SucR", "Best"])
    logs = []
    cnt = 0
    wri = 0

    for file in files:
        try:
            f1 = open("log/" + file, 'r')
        except:
            continue

        print(file)
        stats = file.split('_')
        for line in f1:
            log = process(line)
            if log:
                log['BW'] = float(stats[1])
                log['Loss'] = float(stats[2])
                log['Delay'] = float(stats[3])
                log['Window'] = float(stats[4])
                logs.append(log)
                cnt += 1


        f1.close()

    flag = 0
    num = 0
    temp_reason = []
    leng = len(logs)
    tcp_mean = 0
    quic_mean = 0
    tcp_med = 0
    quic_med = 0
    tcp_suc = 0
    quic_suc = 0
    best = 3
    for i in range(leng):
        num += 1
        log = logs[leng-i-1]
        bw = float(log['BW'])
        loss = float(log['Loss'])
        delay = float(log['Delay'])
        window = float(log['Window'])
        time = str(log['timestamp'])
        appname = str(log['base']['app_name'])
        wise = 0
        method = str(log['base']['method'])
        nettype = int(log['base']['nettype'])
        ostype = int(log['base']['os_type'])
        status = str(log['base']['status'])
        quic_alter_race = int(log['quic']['alter_race_info'])
        protocol = int(log['response']['connection_info'])
        if protocol == 5:
            is_zero_rtt = str(log['quic']['is_zero_rtt'])
            pro = 1
        else:
            is_zero_rtt = "false"
            pro = 0
        received_bytes = int(log['response']['received_bytes'])
        sent_bytes = int(log['response']['sent_bytes'])
        timing_body_recv = int(log['timing']['body_recv'])
        timing_connect = int(log['timing']['tcp'])
        timing_dns = int(log['timing']['dns'])
        timing_duration_time = int(log['timing']['duration'])
        timing_head_recv = int(log['timing']['head_recv'])
        timing_init_connect = int(log['timing']['init_connect'])
        timing_pending_wait_time = int(log['timing']['pending_wait_time'])
        timing_redirect = int(log['timing']['redirect'])
        timing_send = int(log['timing']['send'])
        timing_since_engine_start = int(log['timing']['since_engine_start'])
        timing_since_last_network_change = int(log['timing']['since_last_network_change'])
        timing_ssl = int(log['timing']['ssl'])
        timing_ttfb = int(log['timing']['ttfb'])
        try:
            temp = str(log['secondary']['network_quality_records_stats'])
            llog = process_stats(temp)
        except:
            pass

        tcp_retrans_cnt = int(llog['tcp_retrans_cnt'])
        tcp_total_send_cnt = int(llog['tcp_total_send_cnt'])
        tcp_rtt_ms_avg = int(llog['tcp_rtt_ms_avg'])
        http_ttfb_ms_avg = int(llog['http_ttfb_ms_avg'])
        udp_rtt_ms_avg = int(llog['udp_rtt_ms_avg'])
        weak_net_reason_ = str(log['secondary']['weak_net_reason'])
        # timing_retran
        if tcp_retrans_cnt >= 0 and tcp_total_send_cnt > 0:
            timing_retran = float(format(
                float(tcp_retrans_cnt) / float(tcp_total_send_cnt)/ 1460.0,
                '.2f'))
        else:
            timing_retran = -1.0

        # timing_ttfb_rate
        if timing_ttfb >= 0 and http_ttfb_ms_avg > 0:
            timing_ttfb_rate = format(float(timing_ttfb) / float(http_ttfb_ms_avg) / 1000.0, '.2f')
        else:
            timing_ttfb_rate = -1.0

        # timing_performance
        if received_bytes >= 0 and timing_duration_time > 0:
            timing_performance = float(format((float(received_bytes)) / float(timing_duration_time) * 1000.0, '.2f'))
        else:
            timing_performance = -1.0

        # timing_performance
        if received_bytes >= 0 and timing_body_recv > 0:
            timing_throughput = float(
                format((float(received_bytes)) / float(timing_body_recv) * 1000.0, '.2f'))
        else:
            timing_throughput = -1.0

        connection_time = timing_duration_time - timing_body_recv - timing_head_recv - timing_ttfb - timing_send
        transfer_time = timing_duration_time - connection_time
        weak = ""
        judge_ttfb_9 = float(http_ttfb_ms_avg)
        judge_ttfb_3 = float(http_ttfb_ms_avg)
        judge_rtt_9 = float(tcp_rtt_ms_avg)
        judge_rtt_3 = float(tcp_rtt_ms_avg)
        judge_rtt_r = float(tcp_rtt_ms_avg)
        judge_retran_s = timing_retran
        judge_retran_l = timing_retran
        judge_ttfb_rate = timing_ttfb_rate
        judge_ttfb = timing_ttfb/1000.0
        judge_perf = timing_performance
        judge_thp = timing_throughput
        judge_rtt_rate = 1.0
        wri += 1
        csv_writer.writerow(
            [bw, loss, delay, window, time, wise, method, nettype, ostype, status, quic_alter_race, is_zero_rtt,
             received_bytes, sent_bytes, pro, weak, timing_duration_time, timing_ttfb, http_ttfb_ms_avg,
             judge_ttfb, judge_ttfb_9, judge_ttfb_3, timing_ttfb_rate, judge_ttfb_rate, tcp_rtt_ms_avg,
             judge_rtt_r, judge_rtt_9, judge_rtt_3, judge_rtt_rate, timing_retran, judge_retran_s, judge_retran_l,
             timing_throughput, timing_performance, judge_thp, judge_perf, timing_send, timing_init_connect,
             udp_rtt_ms_avg, timing_body_recv, connection_time, transfer_time, timing_dns, timing_redirect,
             timing_pending_wait_time, timing_head_recv, timing_ssl, timing_since_last_network_change,
             timing_connect,
             timing_since_engine_start, tcp_mean, quic_mean, tcp_med, quic_med, tcp_suc, quic_suc, best])



    f.close()
    print("cnt: " + str(cnt))
    print("wri: " + str(wri))
    print("num: " + str(num))


if __name__ == '__main__':
    main()

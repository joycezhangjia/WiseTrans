
#include "protocol_selection.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <utility>
#include <vector>


namespace {

const uint32_t kObservativeLargeWindow = 30;
const uint32_t kObservativeMediumWindow = 15;
const uint32_t kObservativeSmallWindow = 8;

const uint32_t kObservativeWindows[] = {
        kObservativeLargeWindow,
        kObservativeMediumWindow,
        kObservativeSmallWindow
};

}  // namespace

namespace net {

    int Duration = 0;
    int Ttfb = 0;
    int Rtt = 0;
    int Retran_cnt = 0;
    int Total_send_cnt = 0;
    int Sends = 0;
    int Initcon = 0;
    int Ttfb_avg = 0;
    int Received_byte = 0;
    int Udp = 0;
    int Body_recv = 0;
    int Protocol = -1;
    int Retran_cnt_re = 0;
    int Total_send_cnt_re = 0;
    int Rtt_re = 0;
    int Ttfb_avg_re = 0;
    int Udp_re = 0;

    int var=0;

    
    bool SenseNetworkQuality(
            NetworkQualitySnapshotMap& snapshots) {
        static_assert(arraysize(kObservativeWindows) == 3,
                      "Size of kObservativeWindows must be equals to 3.");

        const auto& large_window_it = snapshots.find(kObservativeLargeWindow);
        const auto& medium_window_it = snapshots.find(kObservativeMediumWindow);
        const auto& small_window_it = snapshots.find(kObservativeSmallWindow);
        if (large_window_it == snapshots.end() ||
            medium_window_it == snapshots.end() ||
            small_window_it == snapshots.end())
            return false;

        const auto& large_window = large_window_it->second;
        const auto& medium_window = medium_window_it->second;
        const auto& small_window = small_window_it->second;

        bool connect_happened_in_large_window = false;
        uint32_t socket_begin_count_in_large_window =
                large_window.socket_conn_begin_end_succeed +
                large_window.socket_conn_begin_end_failed +
                large_window.socket_conn_begin_pending +
                large_window.url_request_out_of_interval;
        uint32_t socket_begin_count_in_medium_window =
                medium_window.socket_conn_begin_end_succeed +
                medium_window.socket_conn_begin_end_failed +
                medium_window.socket_conn_begin_pending;
        if (socket_begin_count_in_large_window >
            socket_begin_count_in_medium_window) {
            connect_happened_in_large_window = true;
        }

        bool no_data_writed = false;
        if (small_window.socket_write_ok_count == 0 &&
            medium_window.socket_write_ok_count == 0)
            no_data_writed = true;

        bool no_data_read = false;
        if (small_window.socket_read_ok_count == 0 &&
            medium_window.socket_read_ok_count == 0)
            no_data_read = true;

#if !defined(NDEBUG) && defined(ENABLE_NQE_DEBUG_LOG)
        bool has_socket_connection_pending = false;
  if (small_window.socket_conn_begin_pending > 0 ||
      small_window.socket_conn_out_of_interval > 0 ||
      medium_window.socket_conn_begin_pending > 0 ||
      medium_window.socket_conn_out_of_interval > 0 ||
      large_window.socket_conn_begin_pending > 0 ||
      large_window.socket_conn_out_of_interval > 0) {
    has_socket_connection_pending = true;
  }
#endif

        bool has_url_request_pending = false;
        if (small_window.url_request_begin_pending > 0 ||
            small_window.url_request_out_of_interval > 0 ||
            medium_window.url_request_begin_pending > 0 ||
            medium_window.url_request_out_of_interval > 0 ||
            large_window.url_request_begin_pending > 0 ||
            large_window.url_request_out_of_interval > 0) {
            has_url_request_pending = true;
        }

        // 1, try probing
        if (connect_happened_in_large_window == true &&
            no_data_writed == true &&
            no_data_read == true &&
            has_url_request_pending == true &&
            probe_enabled_ == true) {
            // Calling to start a ProbeJob to confirm if it is "Offline".
            MaybeStartProbeJob();
        }

        // 2, judge by records data
        if (current_network_quality_index_ != NETWORK_QUALITY_PROBING) {
            if (JudgeWeakNet()) {
                current_network_quality_index_ = NETWORK_QUALITY_BAD;
                DVLOG(1) << "NQE judge weak net, reason: " << weak_net_reason_;
            } else if (no_data_read == false) {
                current_network_quality_index_ = NETWORK_QUALITY_CONNECTED;
            } else {
                if (current_network_quality_index_ != NETWORK_QUALITY_OFFLINE &&
                    current_network_quality_index_ != NETWORK_QUALITY_APP_NOT_CONNECTED) {
                    current_network_quality_index_ = NETWORK_QUALITY_UNKNOWN;
                }
            }
        }

        // 3, try to notify new quality index
        MaybeNotifyObserversOfNetworkQualityIndex();

        return true;
    }

    bool JudgeWeakNet() {
        const baidu::BdConfigReader* reader = baidu::BdConfigReader::Get();
        if (!reader) {
            return false;
        }
        const baidu::BdConfig* config = reader->GetBdConfigPtr();

        int weak_window_sec = -1;
        if (config->nq.weak_window_sec > 0 || config->nq.weak_window_sec == -1)
            weak_window_sec = config->nq.weak_window_sec;

        int weak_min_cnt = 0;
        if (config->nq.weak_min_cnt >= 0)
            weak_min_cnt = config->nq.weak_min_cnt;
#if defined(OS_IOS)

#elif defined(OS_ANDROID)
        if (JudgeWeakNetByXGB(weak_window_sec, weak_min_cnt)){
            return true;
        }
#endif

        weak_net_reason_ = "";
        return false;
    }

    
    bool JudgeWeakNetBySocketRecordsForData(int window, int min_cnt) {
        const baidu::BdConfigReader* reader = baidu::BdConfigReader::Get();
        if (!reader) {
            return false;
        }
        const baidu::BdConfig* config = reader->GetBdConfigPtr();

        if (!config->nq.weak_policy_tcp_retrans_enable &&
            !config->nq.weak_policy_tcp_recv_len_enable &&
            !config->nq.weak_policy_tcp_rtt_enable) {
            return false;
        }

        int tcp_rtt_threshold = kDefaultWeakPolicyTcpRttThresholdMs;
        if (config->nq.weak_policy_tcp_rtt_threshold_ms > 0)
            tcp_rtt_threshold = config->nq.weak_policy_tcp_rtt_threshold_ms;

        base::TimeTicks now_tick = tick_clock_->NowTicks();
        base::TimeTicks anchor = base::TimeTicks();
        if (window != -1) {
            base::TimeDelta delta = base::TimeDelta::FromSeconds(window);
            anchor = now_tick - delta;
        }


#if defined(OS_IOS)
        int total_send_bytes = 0;
        int retrans_bytes = 0;
#elif defined(OS_ANDROID)
        int total_send_cnt = 0;
        int retrans_cnt = 0;
#endif


        int total_recv_cnt = 0;
        int recv_mss_len_cnt = 0;

        int total_tcp_rtt_cnt = 0;
        int tcp_rtt_weak_cnt = 0;
        int total_tcp_rtt_sum = 0;
        int total_tcp_rtt_avg = 0;

        for (const auto& record : socket_records_) {
            if (!record.second->end_time_.is_null() &&
                record.second->end_time_ < anchor) {
                continue;
            }

            int rcv_mss = kDefaultMss;
#if defined(OS_IOS)
            int cur_txretransmitbytes_first = 0;
            int cur_txretransmitbytes_last = 0;
#elif defined(OS_ANDROID)
            int snd_mss = kDefaultMss;
            int cur_retrans_first = 0;
            int cur_retrans_last = 0;
#endif


            int snd_mss = kDefaultMss;
            int cur_retrans_first = 0;
            int cur_retrans_last = 0;


            // traverse tcp_info_list: get mss, get retrans count, get tcp_rtt count
            std::vector<struct SocketTcpInfo> &tcp_info_list = record.second->tcp_info_list_;
            int tcp_info_list_len = tcp_info_list.size();
            for (int i = tcp_info_list_len - 1; i >= 0; i--) {
                // judge timetick to anchor, timeck is ordered in the list
                if (tcp_info_list[i].timetick_ < anchor) {
                    // the initial retrans count should from the first evicted tcp_info
                    if (i != tcp_info_list_len - 1) {
#if defined(OS_IOS)
                        cur_txretransmitbytes_first =
              tcp_info_list[i].tcp_info_.tcpi_txretransmitbytes;
#elif defined(OS_ANDROID)
                        cur_retrans_first = tcp_info_list[i].tcp_info_.tcpi_total_retrans;
#endif
                    }

                    break;
                }

                if (i == tcp_info_list_len - 1) {
// judge mss by the last tcp_info
#if defined(OS_IOS)
                    if (tcp_info_list[i].tcp_info_.tcpi_maxseg > 0) {
          rcv_mss = tcp_info_list[i].tcp_info_.tcpi_maxseg;
        }
#elif defined(OS_ANDROID)
                    if (tcp_info_list[i].tcp_info_.tcpi_snd_mss > 0) {
          snd_mss = tcp_info_list[i].tcp_info_.tcpi_snd_mss;
        }
        if (tcp_info_list[i].tcp_info_.tcpi_rcv_mss > 0) {
          rcv_mss = tcp_info_list[i].tcp_info_.tcpi_rcv_mss;
        }
#endif

                    // record the last retrans
#if defined(OS_IOS)
                    cur_txretransmitbytes_last =
            tcp_info_list[i].tcp_info_.tcpi_txretransmitbytes;
#elif defined(OS_ANDROID)
                    cur_retrans_last = tcp_info_list[i].tcp_info_.tcpi_total_retrans;
#endif
                }

                // if no tcp_rtt or tcp_retrans policy, do not traverse the tcp_info list
                if (!config->nq.weak_policy_tcp_rtt_enable &&
                    !config->nq.weak_policy_tcp_retrans_enable) {
                    break;
                }

                // accumulate tcp rtt
                if (config->nq.weak_policy_tcp_rtt_enable) {
                    if (tcp_info_list[i].tcp_info_.tcpi_rttcur != 0) {
                        total_tcp_rtt_cnt++;
                        total_tcp_rtt_sum = total_tcp_rtt_sum + tcp_info_list[i].tcp_info_.tcpi_rttcur;
                        if (tcp_info_list[i].tcp_info_.tcpi_rttcur > tcp_rtt_threshold)
                            tcp_rtt_weak_cnt++;
                    }
                }
            }

            // accumulate retrans_cnt
#if defined(OS_IOS)
            retrans_bytes += cur_txretransmitbytes_last - cur_txretransmitbytes_first;
#elif defined(OS_ANDROID)
            retrans_cnt += cur_retrans_last - cur_retrans_first;
#endif

            // traverse event_list: judge recv length, write count
            std::vector<struct SocketEvent>& event_list = record.second->event_list_;
            int event_list_len = event_list.size();
            for (int i = event_list_len - 1; i >= 0; i--) {
                // judge timetick to anchor, timeck is ordered in the list
                if (event_list[i].timetick_ < anchor) {
                    break;
                }

                // if no tcp_recv_len or tcp_retrans policy, do not traverse the event list
                if (!config->nq.weak_policy_tcp_recv_len_enable &&
                    !config->nq.weak_policy_tcp_retrans_enable) {
                    break;
                }

                if (config->nq.weak_policy_tcp_recv_len_enable) {
                    if (event_list[i].state_ == SocketPerformanceWatcher::STATE_READ_OK) {
                        total_recv_cnt++;
                        if (event_list[i].rv_ == rcv_mss)
                            recv_mss_len_cnt++;
                    }
                }

                if (config->nq.weak_policy_tcp_retrans_enable) {
                    if ((event_list[i].state_ ==
                         SocketPerformanceWatcher::STATE_START_WRITE) &&
                        (event_list[i].rv_ > 0)) {
#if defined(OS_IOS)
                        total_send_bytes += event_list[i].rv_;
#elif defined(OS_ANDROID)
                        total_send_cnt += event_list[i].rv_ / snd_mss + 1;
#endif
                    }
                }
            }
        }

#if defined(OS_ANDROID)
        Retran_cnt = retrans_cnt;
        Total_send_cnt = total_send_cnt;
        Rtt = total_tcp_rtt_cnt > 0 ? (total_tcp_rtt_sum / total_tcp_rtt_cnt) : 0;

#elif defined(OS_IOS)

        // judge by tcp_retrans policy

        if (config->nq.weak_policy_tcp_retrans_enable) {
            do {
                // if total_send_cnt is 0, since connect may also cause retrans, set
                // total_send_cnt to 1
                if (total_send_bytes == 0)
        total_send_bytes = 1;

      if (retrans_bytes == 0 || total_send_bytes < min_cnt)
        break;

      int tcp_retrans_percentage = kDefaultWeakPolicyTcpRetransPercentage;
      if (config->nq.weak_policy_tcp_retrans_percentage >= 0)
        tcp_retrans_percentage = config->nq.weak_policy_tcp_retrans_percentage;

      if (retrans_bytes * 100 / total_send_bytes >= tcp_retrans_percentage) {

        std::stringstream ss;
        ss << "retrans_bytes: " << retrans_bytes
           << ", total_send_bytes: " << total_send_bytes
           << ", tcp_retrans_percentage: " << tcp_retrans_percentage;
        weak_net_reason_ = ss.str();
        return true;
      }
            } while(0);
        }

        // judge by tcp_recv_len policy
        if (config->nq.weak_policy_tcp_recv_len_enable) {
            do {
                if (recv_mss_len_cnt == 0 || total_recv_cnt == 0 ||
                    total_recv_cnt < min_cnt)
                    break;

                int tcp_recv_len_percentage = kDefaultWeakPolicyTcpRecvLenPercentage;
                if (config->nq.weak_policy_tcp_recv_len_percentage >= 0)
                    tcp_recv_len_percentage =
                            config->nq.weak_policy_tcp_recv_len_percentage;
                if (recv_mss_len_cnt * 100 / total_recv_cnt >= tcp_recv_len_percentage) {
                    std::stringstream ss;
                    ss << "recv_mss_len_cnt: " << recv_mss_len_cnt
                       << ", total_recv_cnt: " << total_recv_cnt
                       << ", tcp_recv_len_percentage: " << tcp_recv_len_percentage;
                    weak_net_reason_ = ss.str();
                    return true;
                }
            } while(0);
        }

        // judge by tcp_rtt policy
        if (config->nq.weak_policy_tcp_rtt_enable) {
            do {
                if (tcp_rtt_weak_cnt == 0 || total_tcp_rtt_cnt == 0 || total_tcp_rtt_cnt < min_cnt)
                    break;

                int tcp_rtt_percentage = kDefaultWeakPolicyTcpRttPercentage;
                if (config->nq.weak_policy_tcp_rtt_percentage >= 0)
                    tcp_rtt_percentage = config->nq.weak_policy_tcp_rtt_percentage;
                if (tcp_rtt_weak_cnt * 100 / total_tcp_rtt_cnt >= tcp_rtt_percentage) {
                    std::stringstream ss;
                    ss << "tcp_rtt_weak_cnt: " << tcp_rtt_weak_cnt
                       << ", total_tcp_rtt_cnt: " << total_tcp_rtt_cnt
                       << ", tcp_rtt_percentage: " << tcp_rtt_percentage;
                    weak_net_reason_ = ss.str();
                    return true;
                }
            } while(0);
        }
#endif
        return false;
    }

    bool JudgeWeakNetByUrlRequestRecordsForData(int window, int min_cnt) {
        const baidu::BdConfigReader* reader = baidu::BdConfigReader::Get();
        if (!reader) {
            return false;
        }
        const baidu::BdConfig* config = reader->GetBdConfigPtr();

        if (!config->nq.weak_policy_http_ttfb_enable) {
            return false;
        }

        base::TimeTicks now_tick = tick_clock_->NowTicks();
        base::TimeTicks anchor = base::TimeTicks();
        if (window != -1) {
            base::TimeDelta delta = base::TimeDelta::FromSeconds(window);
            anchor = now_tick - delta;
        }

        int http_ttfb_threshold = kDefaultWeakPolicyHttpTtfbThresholdMs;
        if (config->nq.weak_policy_http_ttfb_threshold_ms > 0)
            http_ttfb_threshold = config->nq.weak_policy_http_ttfb_threshold_ms;

        int total_http_ttfb_cnt = 0;
        int http_ttfb_weak_cnt = 0;
        int total_http_ttfb_sum = 0;

        for (auto& it : url_request_records_) {
            if (it.second->begin < anchor)
                continue;

            if (it.second->ttfb.ToInternalValue() == 0)
                continue;

            total_http_ttfb_cnt++;
            total_http_ttfb_sum = total_http_ttfb_sum + it.second->ttfb.InMilliseconds();
            if (it.second->ttfb.InMilliseconds() > http_ttfb_threshold) {
                http_ttfb_weak_cnt++;
            }
        }
#if defined(OS_ANDROID)
        Ttfb_avg = total_http_ttfb_cnt > 0 ? (total_http_ttfb_sum / total_http_ttfb_cnt) : 0;
        Udp = rtt_observations_.GetQuicAvgRttInWindow(anchor);     //zhangjia0515


#elif defined(OS_IOS)
        // judge by http_ttfb policy
        if (http_ttfb_weak_cnt == 0 ||
            total_http_ttfb_cnt == 0 ||
            total_http_ttfb_cnt < min_cnt) {
            return false;
        }

        int http_ttfb_percentage = kDefaultWeakPolicyHttpTtfbPercentage;
        if (config->nq.weak_policy_http_ttfb_percentage >= 0)
            http_ttfb_percentage = config->nq.weak_policy_http_ttfb_percentage;

        if (http_ttfb_weak_cnt * 100 / total_http_ttfb_cnt >= http_ttfb_percentage) {
            std::stringstream ss;
            ss << "http_ttfb_weak_cnt: " << http_ttfb_weak_cnt
               << ", total_http_ttfb_cnt: " << total_http_ttfb_cnt
               << ", http_ttfb_percentage: " << http_ttfb_percentage;
            weak_net_reason_ = ss.str();
            return true;
        }
#endif
        return false;
    }

    bool JudgeWeakNetByXGB(int window, int min_cnt) {
        const baidu::BdConfigReader* reader = baidu::BdConfigReader::Get();
        if (!reader) {
            return false;
        }
        const baidu::BdConfig* config = reader->GetBdConfigPtr();
#if defined(OS_ANDROID)
        JudgeWeakNetBySocketRecordsForData(window, min_cnt);
        JudgeWeakNetByUrlRequestRecordsForData(window, min_cnt);
        int duration = Duration;
        int ttfb = Ttfb;
        int rtt = Rtt;
        int retran_cnt = Retran_cnt;
        int total_send_cnt = Total_send_cnt;
        int sends = Sends;
        int initcon = Initcon;
        int ttfb_avg = Ttfb_avg;
        int received_byte = Received_byte;
        int udp = Udp;
        int body_recv = Body_recv;
        int protocol = Protocol;
        bool weak = false;
        Retran_cnt_re = Retran_cnt;
        Total_send_cnt_re = Total_send_cnt;
        Rtt_re = Rtt;
        Ttfb_avg_re = Ttfb_avg;
        Udp_re = Udp;
        if (config->nq.weak_policy_http_ttfb_enable){
            //quic
#if defined(ENABLE_NQE_DEBUG_LOG)
#endif
            if (protocol == 5){
                do{
                    if (ttfb <= 0 || ttfb_avg <= 0 || duration <= 0 || udp < 0 || rtt < 0 || total_send_cnt <= 0 || sends <= 0 || body_recv <= 0 || received_byte <= 0){
                        break;
                    }
                    weak = JudgeQuic(udp, float(ttfb/ttfb_avg), duration, ttfb, rtt, float(retran_cnt/total_send_cnt), sends, body_recv, ttfb_avg, float(received_byte/duration));
                }while(0);
                            }
            //tcp
            else {
                do{
                    if (ttfb <= 0 || ttfb_avg <= 0 || duration <= 0 || udp < 0 || rtt < 0 || total_send_cnt <= 0 || sends <= 0 || body_recv <= 0 || received_byte <= 0){
                        break;
                    }
                    weak = JudgeTcp(duration, ttfb, rtt, float(retran_cnt/total_send_cnt), sends, initcon, ttfb_avg, float(received_byte/duration));

                }while(0);
            }
            if (weak){
                std::stringstream ss;
                ss << "xgboost judged";
                weak_net_reason_ = ss.str();
            }
        }
        return weak;

#endif
    }
    bool JudgeQuic(int Udp, float Ttfb_rate, int Duration, int Ttfb, int Rtt, float Retran, int Sends, int Body_recv, int Ttfb_avg, float Performance){
        double quic_input[10] = {double(Udp), double(Ttfb_rate), double(Duration), double(Ttfb), double(Rtt), double(Retran), double(Sends), double(Body_recv), double(Ttfb_avg), double(Performance)};
        double result[2] = {0.0 , 0.0};
        predict_quic(quic_input, result);
        if (result[1] > result[0]){
            return true;
        }
        else {
            return false;
        }
    }
    bool JudgeTcp(int Duration, int Ttfb, int Rtt, float Retran, int Sends, int Initcon, int Ttfb_avg, float Performance){
        double tcp_input[8] = {double(Duration), double(Ttfb), double(Rtt), double(Retran), double(Sends), double(Initcon), double(Ttfb_avg), double(Performance)};
        double result[2] = {0.0 , 0.0};
        predict_tcp(tcp_input, result);
        if (result[1] > result[0]){
            return true;
        }
        else {
            return false;
        }
    }

}  // namespace net

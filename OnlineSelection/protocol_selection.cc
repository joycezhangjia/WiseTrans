
#include "protocol_selection.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <utility>
#include <vector>


namespace {
    //...
    //...
    //...
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

    
    bool SenseNetworkQuality(NetworkQualitySnapshotMap& snapshots) {
        //...
        //...
        //...
                             
        // 1, try probing
        if (connect_happened_in_large_window == true &&
            no_data_writed == true &&
            no_data_read == true &&
            has_url_request_pending == true &&
            probe_enabled_ == true) {
            // Calling to start a ProbeJob to confirm if it is "Offline".
            MaybeStartProbeJob();
        }

        // 2, select by records data
        if (current_network_quality_index_ != NETWORK_QUALITY_PROBING) {
            if (SelectProtocol()) {
                current_network_quality_index_ = NETWORK_QUALITY_BAD;
                DVLOG(1) << "WiseTrans selects QUIC, reason: " << quic_selection_reason_;
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
    
    void MaybeStartProbeJob() {
        if (is_probing_)
            return;

        // Avoid frequent probe, which may result in loss of flow and attack on the
        // probe target.
        if (!last_probe_time_.is_null()) {
            base::TimeDelta duration = base::TimeTicks::Now() - last_probe_time_;
            if (duration <
                base::TimeDelta::FromSeconds(kDefaultMinProbeIntervalInSecond))
                return;
        }

        current_network_quality_index_ = NETWORK_QUALITY_PROBING;

        DVLOG(2) << "start probe job";
        probe_record_.reset(new ProbeRecord());
        probe_request_.reset(
                new ProbeRequest(probe_record_, ProbeRequest::CUSTOMIZED_PROBE_HTTP,
                                 base::Bind(&NetworkQualityEstimator::ProbeJobDone,
                                            weak_ptr_factory_.GetWeakPtr())));
        probe_request_->StartProbe();

        is_probing_ = true;
        last_probe_time_ = base::TimeTicks::Now();
    }


    bool SelectProtocol() {
        //...
        //...
        //...

        int weak_window_sec = -1;
        if (config->nq.weak_window_sec > 0 || config->nq.weak_window_sec == -1)
            weak_window_sec = config->nq.weak_window_sec;

        int weak_min_cnt = 0;
        if (config->nq.weak_min_cnt >= 0)
            weak_min_cnt = config->nq.weak_min_cnt;
#if defined(OS_IOS)
        //...
        //...
        //...
#elif defined(OS_ANDROID)
        if (SelectProtocolByXGB(weak_window_sec, weak_min_cnt)){
            return true;
        }
#endif

        quic_selection_reason_ = "";
        return false;
    }

    
    bool SelectProtocolBySocketRecordsForData(int window, int min_cnt) {
        //...
        //...
        //...

        if (!config->nq.weak_policy_tcp_retrans_enable &&
            !config->nq.weak_policy_tcp_rtt_enable) {
            return false;
        }


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

        int total_tcp_rtt_cnt = 0;
        int total_tcp_rtt_sum = 0;
        int total_tcp_rtt_avg = 0;

        for (const auto& record : socket_records_) {
            if (!record.second->end_time_.is_null() &&
                record.second->end_time_ < anchor) {
                continue;
            }

#if defined(OS_IOS)
            int cur_txretransmitbytes_first = 0;
            int cur_txretransmitbytes_last = 0;
#elif defined(OS_ANDROID)
            int snd_mss = kDefaultMss;
            int cur_retrans_first = 0;
            int cur_retrans_last = 0;
#endif


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

                // if no tcp_retrans policy, do not traverse the event list
                if (!config->nq.weak_policy_tcp_retrans_enable) {
                    break;
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
        //...
        //...
        //...
        
#endif
        return false;
    }

    bool SelectProtocolByUrlRequestRecordsForData(int window, int min_cnt) {
        //...
        //...
        //...
        
        if (!config->nq.weak_policy_http_ttfb_enable) {
            return false;
        }

        base::TimeTicks now_tick = tick_clock_->NowTicks();
        base::TimeTicks anchor = base::TimeTicks();
        if (window != -1) {
            base::TimeDelta delta = base::TimeDelta::FromSeconds(window);
            anchor = now_tick - delta;
        }


        int total_http_ttfb_cnt = 0;
        int total_http_ttfb_sum = 0;

        for (auto& it : url_request_records_) {
            if (it.second->begin < anchor)
                continue;

            if (it.second->ttfb.ToInternalValue() == 0)
                continue;

            total_http_ttfb_cnt++;
            total_http_ttfb_sum = total_http_ttfb_sum + it.second->ttfb.InMilliseconds();
        }
#if defined(OS_ANDROID)
        Ttfb_avg = total_http_ttfb_cnt > 0 ? (total_http_ttfb_sum / total_http_ttfb_cnt) : 0;
        Udp = rtt_observations_.GetQuicAvgRttInWindow(anchor);     //zhangjia0515


#elif defined(OS_IOS)
        //...
        //...
        //...
        
#endif
        return false;
    }

    bool SelectProtocolByXGB(int window, int min_cnt) {
        //...
        //...
        //...
                             
#if defined(OS_ANDROID)
        SelectProtocolBySocketRecordsForData(window, min_cnt);
        SelectProtocolByUrlRequestRecordsForData(window, min_cnt);
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
            if (protocol == 5){
                do{
                    if (ttfb <= 0 || ttfb_avg <= 0 || duration <= 0 || udp < 0 || rtt < 0 || total_send_cnt <= 0 || sends <= 0 || body_recv <= 0 || received_byte <= 0){
                        break;
                    }
                    selection = JudgeQuic(udp, float(ttfb/ttfb_avg), duration, ttfb, rtt, float(retran_cnt/total_send_cnt), sends, body_recv, ttfb_avg, float(received_byte/duration));
                }while(0);
                            }
            //tcp
            else {
                do{
                    if (ttfb <= 0 || ttfb_avg <= 0 || duration <= 0 || udp < 0 || rtt < 0 || total_send_cnt <= 0 || sends <= 0 || body_recv <= 0 || received_byte <= 0){
                        break;
                    }
                    selection = JudgeTcp(duration, ttfb, rtt, float(retran_cnt/total_send_cnt), sends, initcon, ttfb_avg, float(received_byte/duration));

                }while(0);
            }
            if (selection){
                std::stringstream ss;
                ss << "xgboost selected";
                quic_selection_reason_ = ss.str();
            }
        }
        return selection;
#elif defined(OS_IOS)
        //...
        //...
        //...
                   
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
    
    void MaybeNotifyObserversOfNetworkQualityIndex() {
        DCHECK(thread_checker_.CalledOnValidThread());

        // do not notify unknown
        if (current_network_quality_index_ == NETWORK_QUALITY_UNKNOWN) {
            return;
        }

        // notify changed index
        if (current_network_quality_index_ == last_notified_network_quality_index_) {
            return;
        }

        if (current_network_quality_index_ == NETWORK_QUALITY_BAD ||
            current_network_quality_index_ == NETWORK_QUALITY_PROBING)
            ever_notified_weak_net_ = true;

        FOR_EACH_OBSERVER(
                NetworkQualityIndexObserver,
                network_quality_index_observer_list_,
                OnNetworkQualityIndexChanged(current_network_quality_index_));
        last_notified_network_quality_index_ = current_network_quality_index_;
    }

}  // namespace net

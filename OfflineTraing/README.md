# Offline Training
WiseTrans collects log on testbed with various network conditions for offline training. Readers can reproduce the training process using the logs and the scripts.

## Training 
To train the classification model, run    
`python 1step_pre.py`, which extracts all information from logs in `data.csv`.  

`python 2step_pre.py`, which does calculation for each <RTT, BtlBw, LossRate> and labels each feature in `Train_data.csv`.  

`python 3step_trainall.py`, which trains models using XGBoost for TCP and QUIC, shown in `TCP.model` and `QUIC.model`. The models translated into C code can be seen in `tcp_code_all.txt` and `quic_code_all.txt`. The parameters used in normalization are stored in `tcp_minmix.txt` and `quic_minmax.txt`.
  
`python 4step_traintestall.py`, which splits the dataset into train set and test set, and evaluates the performance of classifiers. 

## Trace logs
The description of the keywords in the logs is listed below.

Field Name | Data Type | Description
------|------|---------
response/connection\_info  | int32 | UNKNOWN=0, HTTP1\_1=1,DEPRECATED\_SPDY2=2, SPDY3=3, HTTP2=4, QUIC=5
response/received\_bytes | int32 | Received bytes
response/sent | int32 | Sent bytes
timing/duration | int32 | The time interval between the client sending request and receiving the whole response body
timing/head\_recv | int32 | The duration of receiving the response header
timing/ttfb | int32 | The time interval from the client sending the request to the client receiving the first byte
timing/send | int32 | The duration of sending the request (after connection establishment)
timing/body\_recv | int32 | The duration of receiving the response body
secondary/network\_quality\_records\_stats/tcp\_retrans\_cnt | int32 |
secondary/network\_quality\_records\_stats/tcp\_rtt\_ms\_avg | int32 | Average RTT in time window
secondary/network\_quality\_records\_stats/http\_ttfb\_ms\_avg | int32 | Average TTFB in time window

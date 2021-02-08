# Offline Training
WiseTrans collects log on testbed with various network conditions for offline training. Readers can reproduce the training process using the logs and the scripts.

## Training 
To train the classification model, run    
<center>`python 1step_pre.py`</center>  
which extracts all information from logs in `data.csv`.  
<center>`python 2step_pre.py`</center>  
which does calculation for each <RTT, BtlBw, LossRate> and labels each feature in `Train_data.csv`.  
<center>`python 3step_trainall.py`</center>  
which trains models using XGBoost for TCP and QUIC, shown in `TCP.model` and `QUIC.model`. The models translated into C code can be seen in `tcp_code_all.txt` and `quic_code_all.txt`. The parameters used in normalization are stored in `tcp_minmix.txt` and `quic_minmax.txt`.  
<center>`python 4step_traintestall.py`</center>  
which splits the dataset into train set and test set, and evaluates the performance of classifiers.    

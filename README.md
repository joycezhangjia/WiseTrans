# WiseTrans
WiseTrans is an adaptive transport protocol selection for mobile web service. See the paper for more details.

## Offline Training
WiseTrans collects logs on testbed with various network conditions for offline training.  
The traces and running scripts for training could be found in `<OfflineTraining>`.

## Online Selection
WiseTrans selects and switches transport protocols at the request level to reach both high performance and acceptable overhead.  
WiseTrans is implemented in Baidu's network library. We only provide sample scripts (for Android) to show the process how WiseTrans extracts features and selects protocol in `<OnlineSelection>`.

## Measurements of one popular mobile web service in the wild
We conduct large-scale passive measurements of one popular mobile app of Baidu. Users can access the short video mobile web service of Baidu with this app. We collect and sample feed refresh request data from the users, which is sent by the app when a user wants to refresh the current list of recommended videos.  
The request logs could be found in `<Measurements>`.  
It is worth mentioning that the analysis of user's location and ISP in our paper is based on user's IP addresses. For ethical and privacy considerations, we have hidden the ip address as well as other private imformation in the logs. Therefore, readers may not be able to obtain these two information. Information related to the status of the network and the transport process of the request is still available.

For any questions, please post an issue or send an email to [joycezhangjia@gmail.com]

# WiseTrans
WiseTrans is an adaptive transport protocol selection for mobile web service. See the paper for more details.

## Offline Training
WiseTrans collects logs on testbed with various network conditions for offline training.  

The traces and running scripts for training could be found in `<OfflineTraining>`.

## Online Selection
WiseTrans selects and switches transport protocols at the request level to reach both high performance and acceptable overhead.  

WiseTrans is implemented in Baidu's network library. We only provide sample scripts (for Android) to show the process how WiseTrans extracts features and selects protocol in `<OnlineSelection>`.


For any questions, please post an issue or send an email to [joycezhangjia@gmail.com](mailto:joycezhangjia@gmail.com)

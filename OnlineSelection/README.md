# Online Selection
WiseTrans is implemented in Baidu's network library, containing about 4000 lines of C code. 

We only provide sample scripts (for Android) to show the main process. The specific details of the function implementation and the iOS part are not presented.

`protocol_selection_quic.cc` and `protocol_selection_tcp.cc` are the models trained offline.

`protocol_selection.cc` presents the process of feature calculation and protocol selection.  

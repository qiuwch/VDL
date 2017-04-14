The result reported in this page is one server <-> one client.

packet_size: 1000, packet_count: 1000
```
[wqiu7@yuille-fb-head speed_test]$ sh run_speed_test.sh
[wqiu7@yuille-fb-head speed_test]$ Counter: Network Throughput, Sum: 8000000.00
Timer: Communication, total time: 0.021127, count: 1000
Speed: 378662.63KB/s
Done
```
```
[wqiu7@yuille-fb-head speed_test]$ sh run_fb_speed.sh
[wqiu7@yuille-fb-head speed_test]$ Done
Counter: Network Throughput, Sum: 8000000.00
Timer: Communication, total time: 0.035649, count: 1000
Speed: 224411.34KB/s
```
---
packet_size: 100000, packet_count: 1000
```
[wqiu7@yuille-fb-head speed_test]$ sh run_speed_test.sh
[wqiu7@yuille-fb-head speed_test]$ Counter: Network Throughput, Sum: 800000000.00
Timer: Communication, total time: 0.245775, count: 1000
Speed: 3255003.56KB/s
Done
```
```
[wqiu7@yuille-fb-head speed_test]$ sh run_fb_speed.sh
[wqiu7@yuille-fb-head speed_test]$ Done
Counter: Network Throughput, Sum: 800000000.00
Timer: Communication, total time: 3.153588, count: 1000
Speed: 253679.28KB/s
```

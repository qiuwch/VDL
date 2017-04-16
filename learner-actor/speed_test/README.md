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
---
One server <-> two clients. The speed is for per client.
```
Counter: Network Throughput, Sum: 800000000.00
Timer: Communication, total time: 11.381395, count: 1000
Speed: 70290.15KB/s
Done
Counter: Network Throughput, Sum: 800000000.00
Timer: Communication, total time: 12.255185, count: 1000
Speed: 65278.49KB/s
```
---
One server <-> three clients

```
Timer: Communication, total time: 19.186336, count: 1000
Speed: 41696.34KB/s
Done
Done
Counter: Network Throughput, Sum: 800000000.00
Timer: Communication, total time: 19.811284, count: 1000
Speed: 40381.03KB/s
Done
Counter: Network Throughput, Sum: 800000000.00
Timer: Communication, total time: 18.688811, count: 1000
Speed: 42806.36KB/s
```

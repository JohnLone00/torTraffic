
# 去官网下载源码
``` shell
cd /home
mkdir tor
cd tor
wget https://dist.torproject.org/tor-0.4.7.13.tar.gz
tar -zxvf tor-0.4.7.13.tar.gz
cd tor-0.4.7.13
```
# 编译
```
sudo apt update
sudo apt upgrade
sudo apt-get install make
sudo apt-get install build-essential
sudo apt-get install libevent-dev -y
sudo apt-get install libssl-dev -y
sudo apt-get install zlib1g-dev -y
./configure
make && make install
```

# python脚本环境
``` shell
sudo apt-get install firefox
sudo apt-get install tcpdump
sudo apt-get install python3-pip
sudo apt-get install git
pip3 install selenium
pip3 install psutil
cd /home
git clone https://github.com/JohnLone00/torTraffic.git
cd traffic
cd torTaffic
chmod 777 geckodriver
```

# 运行脚本
```shell
sudo apt-get install ethtool
ethtool -K eth0 gro off
python3 main.py -w awf200.txt -b 1 -e 50
```

import time
import redis
import requests
import socket
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
import psutil
import signal
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

itertimes = 30
serverIP = "localhost"
serverTorPort = 9050
serverTcpdumpPath = r"./torPCAP-Pure/"
serverInforPath = r"./torInfor/"
badPcapLog = r"./torTrafficLog/badPcapLog.txt"
websitesFile = ''
executable_path=r'./torTraffic/geckodriver'  # selenium启动firefox需要的驱动
keeptime = 120


def initDriver():
    #  配置浏览器代理

    firefox_profile = FirefoxProfile()
    # set socks proxy
    firefox_profile.set_preference("network.proxy.type", 1)
    firefox_profile.set_preference("network.proxy.socks_version", 5)
    firefox_profile.set_preference("network.proxy.socks", serverIP)
    firefox_profile.set_preference("network.proxy.socks_port", serverTorPort)
    # firefox_profile.set_preference("network.proxy.socks_remote_dns", True)
    firefox_profile.set_preference("browser.download.folderList", 2)
    # 禁用缓存
    firefox_profile.set_preference("browser.cache.disk.enable", False)
    firefox_profile.set_preference("browser.cache.memory.enable", False)
    firefox_profile.set_preference("browser.cache.offline.enable", False)
    firefox_profile.set_preference("network.http.use-cache", False)
    firefox_profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0")

    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--disable-gpu')



    d = DesiredCapabilities.FIREFOX
    d["goog:loggingPrefs"] = {"performance": "ALL"}
    
    driver = webdriver.Firefox(desired_capabilities=d,executable_path=executable_path,
                               firefox_profile=firefox_profile,
                               options=firefox_options)
    return driver

def startTcpdump(filename):
    #cmd = "tcpdump tcp port \(8443 or 9001 or 443 or 8140 or 8080 or 80 or 9030 or 9040 or 9050 or 9051 or 9150 or 9003 or 500\) -w " + filename
    # cmd = "tcpdump tcp port \(8443 or 9001 or 443 or 500 or 9003\) -w " + filename
    # cmd  = "tcpdump tcp and \(\(src host 192.210.190.98 and src port 17602\) or \(dst host 192.210.190.98 and dst port 17602\)\) -w " + filename
    cmd = "tcpdump tcp and not port \(9050 or 22 or 21 or 6010 or 6011\) -w " + filename
    os.popen(cmd)

def closeTcpdump():
    time.sleep(2)
    try:
        os.popen('ps -ef | grep tcpdump | grep -v grep | cut -c 10-18 | xargs kill')
    except:
        print('have not closed!!')

def openTor():
    # 启动进程
    process = subprocess.Popen(["/home/tor/tor-0.4.7.13/src/app/tor"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, universal_newlines=True)

    # 设置等待的特定输出
    desired_output = "100%"
    timeout_seconds = 10
    start_time = time.time()
    while True:
        # 读取标准输出
        output = process.stdout.readline()
        print(output, end="")  # 打印标准输出，如果需要的话
        if desired_output in output:
            print("Tor bulit! OK!")
            return True

        if time.time() - start_time > timeout_seconds:
            print("Tor error!")
            return False

def closeTor():
    result = subprocess.run("pkill tor", shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

def simulation(driver,url):

    try:
        driver.get(url)
        time.sleep(20)
    except exceptions.TimeoutException as e:  # 若页面长时间没有加载完成 则执行js脚本 停止加载
        driver.execute_script("window.stop()")
        print('Time out!!!!')
        return True

    except BaseException as e2:
        print(e2)
        print('Error!!!!')
        # with open(badPcapLog,'a') as f:
        #     r.rpush('supply', str(times) + ' ' + url)
        return False

    try:
        print(driver.title)
        if "ERROR" in driver.title:
            return False
        if "403 Forbidden" in driver.title:
            return False
        if "Just a moment..." in driver.title:
            return False
        if "wrong" in driver.title:
            return False
        if "Access Denied" in driver.title:
            return False
        if "Error" in driver.title:
            return False
        if "403" in driver.title:
            return False
        if "406" in driver.title:
            return False
    except BaseException as e3:
        print('Title miss!!!!')
        return False

    return True



def main(num):
    with open(websitesFile, 'r') as f:
        for line in f.readlines():
            flag = openTor()
            if not flag:
                while True:
                    closeTor()
                    time.sleep(1)
                    flag = openTor()
                    if flag:
                        break

            driver = initDriver()
            # 设置页面加载 超时时间
            driver.set_page_load_timeout(keeptime)
            driver.set_script_timeout(keeptime)
            driver.delete_all_cookies()
            url = line.strip()
            if not os.path.exists(serverTcpdumpPath + str(num)):
                os.makedirs(serverTcpdumpPath + str(num))
            u = url
            filepath = serverTcpdumpPath + str(num) + '/'+ u.replace('https://','') +'.pcap'
            print(filepath)
            startTcpdump(filepath)
            flag = simulation(driver, url)
            closeTcpdump()
            driver.delete_all_cookies()
            driver.quit()
            if not flag:
                os.remove(filepath)
                print("Delete："+filepath)
            closeTor()
            time.sleep(2)






def supply():
    while r.llen('supply') != 0:
        # flag = openTor()
        # if flag == False:
        #     closeTor()
        #     continue
        driver = initDriver()
        driver.set_page_load_timeout(keeptime)
        driver.set_script_timeout(keeptime)
        driver.delete_all_cookies()
        e = r.lindex('supply', 0)
        times,url = e.split(' ')
        if not os.path.exists(serverTcpdumpPath + str(times)):
            os.makedirs(serverTcpdumpPath + str(times))
        u = url
        filepath = serverTcpdumpPath + str(times) + '/' + u.replace('https://', '') + '.pcap'
        print(filepath)
        startTcpdump(filepath)
        simulation(driver, url)
        closeTcpdump()
        r.lpop('supply')
        driver.quit()
        time.sleep(2)
        # closeTor()



def traffic(website,begin,end):
    global websitesFile
    websitesFile = "./torTraffic/"+website
    for num in range(begin,end+1):
         main(num)
    # supply()
    # r.delete('supply')


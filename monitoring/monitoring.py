import wmi
import time
import datetime
import schedule
import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import locale
import csv

locale.setlocale(locale.LC_CTYPE, "Japanese_Japan.932")
path = './monitoring'
if not os.path.exists(path):
    os.mkdir(path) 

w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")

tmp = defaultdict(list)
n = 1
def job():
    global n
    print("job {}回目 実行".format(n))
    n += 1
    
    now = datetime.datetime.now()
    tmp["Date Time"].append(now.strftime("%m月%d日 %H時"))
    temperature_infos = w.Sensor()

    for sensor in temperature_infos:
        if sensor.SensorType==u'Temperature':
            if sensor.Name == 'CPU Package':
                tmp[sensor.Name].append(sensor.Value)

def view1():
    print("本ゼミ")
    global tmp
    df = pd.DataFrame.from_dict(tmp, orient='index').T
    
    if not os.path.exists("./monitoring/monitoring.csv"):
        df.to_csv("./monitoring/monitoring.csv")
        df.to_csv("./monitoring/再起動用monitoring.csv")
    else:
        df.to_csv("./monitoring/monitoring.csv", mode='a', header=False)
        df.to_csv("./monitoring/再起動用monitoring.csv", mode='a', header=False)
        time.sleep(1)
        df = pd.read_csv("./monitoring/monitoring.csv")
        df = df.drop_duplicates()

    df = df.set_index('Date Time')
    print(df)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(df.index, df['CPU Package'], color='#b22222',marker='o', label='CPU')
    plt.legend()

    s = df.index
    #↓横軸の間隔
    ticks = 5
    plt.xticks(range(0,len(s),ticks),rotation=70)
    
    plt.title('Monitoring')
    plt.xlabel('DateTime')
    plt.ylabel('Temperature')

    now = datetime.datetime.now()
    fig.savefig("./monitoring/{}_本ゼミ.png".format(now.strftime("%m月%d日")), dpi=200, bbox_inches="tight")  

def view2():
    print("自主ゼミ")
    global tmp
    df = pd.DataFrame.from_dict(tmp, orient='index').T

    if not os.path.exists("./monitoring/monitoring.csv"):
        df.to_csv("./monitoring/monitoring.csv")
        df.to_csv("./monitoring/再起動用monitoring.csv")
    else:
        df.to_csv("./monitoring/monitoring.csv", mode='a', header=False)
        df.to_csv("./monitoring/再起動用monitoring.csv", mode='a', header=False)
        df = pd.read_csv("./monitoring/monitoring.csv")
        df = df.drop_duplicates()

    df = df.set_index('Date Time')
    print(df)

    fig = plt.figure(figsize=(6, 4))
    plt.plot(df.index, df['CPU Package'], color='#b22222',marker='o', label='CPU')
    plt.legend()

    s = df.index
    #↓横軸の間隔
    ticks = 5
    plt.xticks(range(0,len(s),ticks),rotation=70)
    
    plt.title('Monitoring')
    plt.xlabel('DateTime')
    plt.ylabel('Temperature')

    now = datetime.datetime.now()
    fig.savefig("./monitoring/{}_自主ゼミ.png".format(now.strftime("%m月%d日")), dpi=200, bbox_inches="tight")

def remove1():
    print("リセット")
    os.remove("./monitoring/monitoring.csv")
    tmp = defaultdict(list)

def remove2():
    print("再起動用csv削除")
    os.remove("./monitoring/再起動用monitoring.csv")

def main():
    #schedule.every(0.1).minutes.do(job)
    schedule.every(2).hours.do(job)
    #本ゼミ用↓
    #schedule.every(2).minutes.do(view1)
    schedule.every().monday.at("10:00").do(view1)
    #リセット用↓
    schedule.every().monday.at("12:00").do(remove1)
    #自主ゼミ用↓
    #schedule.every(1).minutes.do(view2)
    schedule.every().thursday.at("10:00").do(view2)
    #再起動用csv削除用↓
    schedule.every().thursday.at("12:00").do(remove2)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
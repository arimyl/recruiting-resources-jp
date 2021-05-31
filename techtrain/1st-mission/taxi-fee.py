#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import re
import datetime

## config
# 正規表現
time_c=re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3}')
dist_c=re.compile(r'\d+\.\d')
## module
# str to time
def str_to_time(str):
    ts=re.split('[:.]',str)
    return datetime.timedelta(hours=int(ts[0]),minutes=int(ts[1]),seconds=int(ts[2]),milliseconds=int(ts[3]))

# 運賃計算
# 現在基準運賃、合計距離、前回記録時間、今回記録時間、今回距離、低速累積時間
def calculate_fee(base_fee,sum_d,time_p,time,dist,low_sp_t):
    # str to time
    check_t=str_to_time(time) # 今回記録時間
    check_t2=str_to_time(time_p) # 前回記録時間
    # speed fee
    if ((float(dist)/1000)/((check_t-check_t2).total_seconds()/360)) <= 10:
        low_sp_t+=(check_t-check_t2).total_seconds()
    else:
        base_fee+=int(low_sp_t//90.0)*80
        low_sp_t=0
    # check time
    # 深夜割増(`00:00:00.000` 〜 `04:59:59.999`、`22:00:00.000` 〜 `23:59.59.999`)
    w=1.0 # 割増係数
    while check_t > str_to_time("24:00:00.000"):
        check_t-=str_to_time("24:00:00.000")
    if (str_to_time("00:00:00.000")<=check_t and check_t<=str_to_time("04:59:59.999")) | (str_to_time("22:00:00.000")<=check_t and check_t<=str_to_time("23:59:59.999")):
        w=1.25
    # sum distance
    sum_d += float(dist)*w
    # distance fee
    if sum_d <= 1052.0:
        fee=int(base_fee)
    else:
        fee=int(base_fee-(1052.0-sum_d)//237*80)
    return fee, base_fee, sum_d, low_sp_t

## input data
if __name__ == "__main__":
    drive_logs = []
    base_fee=int(410)
    sum_d=float(0)
    low_sp_t=0
    for line in sys.stdin:
        log_str=line.split()
        ## reset logs
        if len(log_str)==0:
            # 終了コード`0`
            sys.exit()
        # confirm data
        if time_c.search(log_str[0])==None:
            # 終了コード`1` 以上終了
            sys.exit(1)
        if dist_c.search(log_str[1])==None:
            # 終了コード`1` 以上終了
            sys.exit(1)
        drive_logs.append(log_str)
        ## calculate
        if len(drive_logs) > 1:
            (fee,base_fee,sum_d,low_sp_t)=calculate_fee(base_fee,sum_d,drive_logs[-2][0],drive_logs[-1][0],drive_logs[-2][1],low_sp_t)

            ## summary
            print(fee)
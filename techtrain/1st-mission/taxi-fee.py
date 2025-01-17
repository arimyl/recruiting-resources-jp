import datetime
import dataclasses
import re
import sys
from typing import List

## config
# 正規表現
time_c = re.compile(r'\d{1,2}:\d{1,2}:\d{1,2}\.\d{1,3}')
dist_c = re.compile(r'\d{1,2}\.\d{1}')

@dataclasses.dataclass
class DriveRecord:
    base_fee: int
    sum_distance: float
    low_speed_time: float

## module
# str to time
def str_to_time(item: str) -> datetime.timedelta:
    """時間文字列をdatetimeに変換
    """
    ts = list(map(int, re.split('[:.]', item)))
    return datetime.timedelta(hours = ts[0], minutes = ts[1], seconds = ts[2], milliseconds = ts[3])

def calculate_fee(drive_record: DriveRecord, time_p: str, time: str, dist: str) -> None:
    """運賃計算
    結果を drive_record に記録
    """
    # str to time
    check_t = str_to_time(time) # 今回記録時間
    check_t2 = str_to_time(time_p) # 前回記録時間
    # speed fee
    if ((float(dist) / 1000) / ((check_t-check_t2).total_seconds() / 360)) <= 10:
        drive_record.low_speed_time += (check_t - check_t2).total_seconds()
    else:
        drive_record.base_fee += int(drive_record.low_speed_time // 90.0) * 80
        drive_record.low_speed_time = 0
    # check time
    # 深夜割増(`00:00:00.000` 〜 `04:59:59.999`、`22:00:00.000` 〜 `23:59.59.999`)
    w = 1.0 # 割増係数
    while check_t > str_to_time("24:00:00.000"):
        check_t -= str_to_time("24:00:00.000")
    if (str_to_time("00:00:00.000") <= check_t and check_t <= str_to_time("04:59:59.999")) | (str_to_time("22:00:00.000") <= check_t \
        and check_t <= str_to_time("23:59:59.999")):
        w = 1.25
    # sum distance
    drive_record.sum_distance += float(dist) * w

def drive_fee(drive_logs: List[str]) -> int:
    """運転記録から計算した運賃を返す
    """
    time_p = ''
    # (base_fee, sum_distance, low_speed_time)
    drive_record = DriveRecord(410, 0, 0)
    fee = 0
    try:
        # input
        for drive_log in drive_logs:
            # confirm data
            if time_c.search(drive_log[0]) is None:
                # 終了コード`1` 異常終了
                sys.exit(1)
            if dist_c.search(drive_log[1]) is None:
                # 終了コード`1` 異常終了
                sys.exit(1)
            ## calculate
            if drive_log[1] != '0.0':
                calculate_fee(drive_record, time_p, drive_log[0], drive_log[1])

            time_p = drive_log[0]

        ## summary
        # speed fee
        if drive_record.low_speed_time > 0:
            drive_record.base_fee += int(drive_record.low_speed_time // 90.0) * 80
        # distance fee
        if drive_record.sum_distance <= 1052.0:
            fee = drive_record.base_fee
        else:
            fee = int(drive_record.base_fee + (drive_record.sum_distance - 1052.0) // 237 * 80)
        
        return fee

    except Exception:
        sys.exit(1) # 異常終了

if __name__ == "__main__":
    drive_logs = []

    # input
    lines = sys.stdin.readlines()
    for line in lines:
        drive_log = line.split()
        if len(drive_log) == 0:
            break
        elif len(drive_log) == 2: 
            drive_logs.append(drive_log)
        else:
            sys.exit(1) # 異常終了
    # output
    fee = drive_fee(drive_logs)
    print(fee)
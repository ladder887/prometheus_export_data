import csv
import requests
import sys
import re
from datetime import datetime
from os import mkdir
from jproperties import Properties
from collections import OrderedDict


# 모든 메트릭 수집후 하나의 CSV에 저장 - irate를 사용한 초당 메트릭을 수집


#설정
prometheus_url = "http://192.168.1.159:9090"
start_time = "2023-10-08T13:00:51Z"  #GMT기준
end_time = "2023-10-08T13:10:50Z"
Label = "Attack_data"

#파일 이름설정
title = prometheus_url.replace("http://", "").replace(".", "_").replace(":9090", "")
title = title + "_" + Label

new_folder = 'csv/metrics'
csv_file_name = new_folder + '/' + title + '.csv'


def get_metrics_name():
    metrics_file = 'metrics.txt'
    if len(sys.argv) > 4:
        metrics_file = sys.argv[4]

    with open('C:/Users/Cysec/Desktop/test/config/' + metrics_file) as input_metrics:
        lines = input_metrics.read().splitlines()
    new_names = list(OrderedDict.fromkeys(lines))
    return new_names


metric_names = get_metrics_name()

with open(csv_file_name, 'w', newline="") as file:
    writer = csv.writer(file)
    index_name = ['timestamp']
    metric_list = []
    
    #데이터 요청
    for metric_name in metric_names:
        response = requests.get('{0}/api/v1/query_range'.format(prometheus_url), params={
            'query': metric_name, 'start': start_time, 'end': end_time, 'step': '1s'}, verify=False)
        results = response.json()['data']['result']
        metric_list.append(results)

    #메트릭 이름 추출
        for result in results:
            num = metric_name + "_"
            for key, value in result['metric'].items():
                if key not in ["__name__", "instance", "job"]:
                    num += value + '_'
            index_name.append(num)
    writer.writerow(index_name)
    for i in range(0, len(metric_list[0][0]["values"])):
        subl = []
        ts_value = metric_list[0][1]["values"][i][0]
        t = datetime.utcfromtimestamp(float(ts_value))
        subl.append(t.strftime("%d/%m/%Y %H:%M:%S"))
        for results in metric_list:
            for result in results:
                subl.append(result["values"][i][1])
        writer.writerow(subl)

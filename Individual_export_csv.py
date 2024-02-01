import csv
import requests
import sys
import re
from datetime import datetime
from os import mkdir
from jproperties import Properties

results = temp.temp

# 개별 저장 csv 코드 - 메트릭별로 csv가 따로 저장됨

def get_metrics_name():
    metrics_file = 'metrics.txt'
    if len(sys.argv) > 4:
        metrics_file = sys.argv[4]

    with open('C:/Users/Cysec/Desktop/test/config/' + metrics_file) as input_metrics:
        lines = input_metrics.read().splitlines()
    new_names = list(set(lines))
    return new_names


def load_settings():
    configs = Properties()
    with open('c:/Users/Cysec/Desktop/test/config/settings.properties', 'rb') as config_file:
        configs.load(config_file)
    return configs

def check_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url)


if len(sys.argv) < 4:
    print('Invalid number of arguments, a minimum of 3 arguments: <prometheus_url> <start_date> <end_date>')
    sys.exit(1)

# validate prometheus url
prometheus_url = sys.argv[1]
if check_url(prometheus_url) is None:
    print('Error passing argument <prometheus_url>: Invalid url format')
    sys.exit(1)

metric_names = get_metrics_name()
# TODO usage of configs in settings.properties
configs = load_settings()
write_header = True
# create performance directory with timestamp
new_folder = 'csv/metrics' #+ ts_title
#mkdir(new_folder)

for metric_name in metric_names:
    print('exported metric name:' + metric_name)
    response = requests.get('{0}/api/v1/query_range'.format(prometheus_url), params={
        'query': metric_name, 'start': sys.argv[2], 'end': sys.argv[3], 'step': '1s'}, verify=False)
    print(response)
    results = response.json()['data']['result']
    print(results)

    title = metric_name
    csv_file_name = new_folder + '/' + title + '.csv'

    with open(csv_file_name, 'w') as file:
        writer = csv.writer(file)
        index_name = ['timestamp']
        #인덱스 이름 추출
        for result in results:
            num = ""
            for key, value in result['metric'].items():
                if key not in ["instance", "job", "__name__"]:
                    num += value
                if num == "":
                    num = 'value'
            index_name.append(num)
        writer.writerow(index_name)


        for i in range(0, len(results[0]["values"])):
            subl = []
            ts_value = result["values"][i][0]
            t = datetime.utcfromtimestamp(float(ts_value))
            subl.append(t.strftime("%d/%m/%Y %H:%M:%S"))
            for result in results:
                subl.append(result["values"][i][1])
            writer.writerow(subl)



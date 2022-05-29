from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import WriteOptions
import logging


class Config:
    conf_name = 'Heisenbug'
    pacing_sec = 0.1
    api_host = 'http://localhost:9090'
    kafka_hosts = ['localhost:29092']
    influx_bucket = 'demo_bucket'
    influx_org = 'demo_org'
    influx_client = InfluxDBClient(url="http://localhost:8086",
                                   token='demo_token',
                                   org=influx_org, )
    influxdb = influx_client.write_api(write_options=WriteOptions(batch_size=10,
                                                                  flush_interval=10_000,
                                                                  jitter_interval=2_000,
                                                                  retry_interval=5_000, ))
    products = [
        {"Code": 111, "Name": "Молоко 1 л.", "Price": 150},
        {"Code": 123, "Name": "Кефир 1 л.", "Price": 100},
        {"Code": 124, "Name": "Сметана 100 г.", "Price": 80},
        {"Code": 125, "Name": "Творог 100 г.", "Price": 120},
        {"Code": 126, "Name": "Сгущёнка", "Price": 170},
    ]


class LogConfig():
    logger = logging.getLogger('demo_logger')
    logger.setLevel('DEBUG')
    file = logging.FileHandler(filename='test_logs.log')
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(file)
    logger.propagate = False


logger = LogConfig().logger
cfg = Config()

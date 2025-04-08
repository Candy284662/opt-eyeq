import time
import random
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(url="http://influxdb:8086", token="3390EqIj-DvP7r3rmXOEi02OEkH78SOmvT6S2mTr5lMOLFNJgxEzzFnCgVp8rVuenLQGIF0RyZdgygwaFdVwbw==", org="itsolutions")
write_api = client.write_api(write_options=SYNCHRONOUS)
BUCKET = " eyqdb"

def generate_test_data():
    hosts = ["test_host1", "test_host2", "test_host3"]
    for _ in range(10):
        for host in hosts:
            point = (
                Point("system_metrics")
                .tag("host", host)
 Ascending() .field("disk_usage", random.uniform(50, 95))
                .field("memory_usage", random.uniform(40, 90))
                .field("process_count", random.randint(100, 250))
                .time(int(time.time()))
            )
            write_api.write(bucket=BUCKET, record=point)
        print(f"Test data written for {hosts}")
        time.sleep(5)

if __name__ == "__main__":
    generate_test_data()

from locust import events, HttpUser, constant_pacing, task, LoadTestShape
import assertion
import time
import random
import kafka_sender
from config import cfg, logger
from functools import wraps
import os


def proceed_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_start_time = time.time()
        transaction = func(*args, **kwargs)
        processing_time = int((time.time() - request_start_time) * 1000)

        if func.__name__ == "send_payment":
            events.request.fire(
                request_type="KAFKA",
                name=func.__name__,
                response_time=processing_time,
                response_length=0,
                context=None,
                exception=None,
            )
        else:
            processing_time = int(transaction.elapsed.total_seconds() * 1000)

        cfg.influxdb.write(
            cfg.influx_bucket,
            cfg.influx_org,
            [{
                "measurement": f"{cfg.conf_name}_db",
                "tags": {"transaction_name": func.__name__},
                "time": time.time_ns(),
                "fields": {"response_time": processing_time},
            }],
        )

        logger.debug(
            f"""{func.__name__} status: {transaction.status_code 
            if func.__name__ != 'send_payment'
            else 'message delivered'}"""
        )

    return wrapper


class GlobalUser(HttpUser):
    wait_time = constant_pacing(cfg.pacing_sec)
    host = cfg.api_host

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        os.remove("test_logs.log")
        logger.info("TEST STARTED")

    def on_start(self):
        self.login()
        self.kfk = kafka_sender.KafkaSender()

    @task(5)
    @proceed_request
    def add_to_cart(self) -> None:
        transaction = self.add_to_cart.__name__
        headers = {
            "accept": "text/html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "token": self.token_id,
        }
        product = random.choice(cfg.products)
        body = {
            "Product": product["Name"],
            "Prod_code": product["Code"],
        }
        with self.client.post("/cart/add", headers=headers, json=body, catch_response=True, name=transaction) as request:
            assertion.check_http_response(transaction, request)
        return request

    @task(5)
    @proceed_request
    def send_payment(self):
        self.kfk.send()
        return None

    @proceed_request
    def login(self) -> None:
        with self.client.get(f"/login/demo-user", catch_response=True, name='login') as request:
            assertion.check_http_response('login', request)
        self.token_id = request.text
        return request


class StagesShape(LoadTestShape):
    stages = [
        {"duration": 20, "users": 2, "spawn_rate": 1},
        {"duration": 40, "users": 4, "spawn_rate": 1},
        {"duration": 60, "users": 8, "spawn_rate": 1},
        {"duration": 80, "users": 16, "spawn_rate": 1},
        {"duration": 100, "users": 20, "spawn_rate": 1},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None

#!/usr/bin/env python
# coding: utf-8
# developer : Nikolai Maksimov (X5 Group)
# date: 30.05.2022

import locust
import assertion
import os
import time
from kafka_sender import kfk
from config import cfg, logger
from functools import wraps


master_users_counter = 0
worker_users_counter = 0


def master_listener(environment, msg, **kwargs):
    global master_users_counter
    master_users_counter += 1
    environment.runner.send_message("increase_worker_users", master_users_counter)


def worker_listener(environment, msg, **kwargs):
    global worker_users_counter
    worker_users_counter = msg.data


def proceed_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_start_time = time.time()
        transaction = func(*args, **kwargs)
        processing_time = int((time.time() - request_start_time) * 1000)

        if func.__name__ == "send_kafka":
            locust.events.request.fire(
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

        logger.debug(f"{func.__name__} status: {transaction.status_code if func.__name__ != 'send_kafka' else 'message delivered'}")

    return wrapper


class DemoUser(locust.HttpUser):
    wait_time = locust.constant_pacing(cfg.pacing_sec)
    host = cfg.api_host

    @locust.events.init.add_listener
    def on_locust_init(environment, **_kwargs):
        if isinstance(environment.runner, locust.runners.MasterRunner):
            environment.runner.register_message("users", master_listener)
        if isinstance(environment.runner, locust.runners.WorkerRunner):
            environment.runner.register_message("increase_worker_users", worker_listener)

    @locust.events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        os.remove("test_logs.log")
        logger.info("TEST STARTED")

    def on_start(self):
        if isinstance(self.environment.runner, locust.runners.WorkerRunner):
            self.environment.runner.send_message("users")
        time.sleep(0.1)
        self.user_id = worker_users_counter
        self.login()

    @locust.task(7)
    @proceed_request
    def send_http(self):
        transaction = self.send_http.__name__
        headers = {
            "accept": "text/html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "token": self.token_id,
        }
        with self.client.get("/demo_http", headers=headers, catch_response=True, name=transaction) as request:
            assertion.check_http_response(transaction, request)
        return request

    @locust.task(3)
    @proceed_request
    def send_kafka(self):
        kfk.send()
        return None

    @proceed_request
    def login(self):
        transaction = self.login.__name__
        with self.client.get(f"/login/user{self.user_id}", catch_response=True, name=transaction) as request:
            assertion.check_http_response(transaction, request)
        logger.debug(f"user {self.user_id} logged in")
        self.token_id = request.text
        return request

    def on_stop(self):
        logger.debug(f"user {self.user_id} stopped")

    @locust.events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        logger.info("TEST STOPPED")


class StagesShape(locust.LoadTestShape):
    stages = [
        {"duration": 20, "users": 1, "spawn_rate": 1},
        {"duration": 40, "users": 5, "spawn_rate": 1},
        {"duration": 60, "users": 3, "spawn_rate": 1},
        {"duration": 80, "users": 10, "spawn_rate": 1},
        {"duration": 100, "users": 1, "spawn_rate": 1},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None

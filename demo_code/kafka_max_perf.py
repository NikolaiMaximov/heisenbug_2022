from locust import events, task, constant_pacing, User, LoadTestShape
import time
import os
from config import cfg, logger
import kafka_sender


class KafkaUser(User):
    wait_time = constant_pacing(cfg.pacing_sec)

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        os.remove("test_logs.log")
        logger.info("TEST STARTED")

    def on_start(self):
        self.kfk = kafka_sender.KafkaSender()

    @task
    def send_payment(self):
        request_start_time = time.time()
        self.kfk.send()
        processing_time = int((time.time() - request_start_time) * 1000)
        events.request.fire(
            request_type="KAFKA",
            name='send_payment',
            response_time=processing_time,
            response_length=0,
            context=None,
            exception=None,
        )

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        logger.info("TEST STOPPED")


class StagesShape(LoadTestShape):
    stages = [
        {"duration": 20, "users": 1, "spawn_rate": 1},
        {"duration": 40, "users": 2, "spawn_rate": 1},
        {"duration": 60, "users": 4, "spawn_rate": 1},
        {"duration": 80, "users": 8, "spawn_rate": 1},
        {"duration": 100, "users": 10, "spawn_rate": 1},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None
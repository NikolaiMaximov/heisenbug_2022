from locust import task, constant_pacing, HttpUser, LoadTestShape
import random
import assertion
from config import cfg, logger


class CartUser(HttpUser):
    wait_time = constant_pacing(cfg.pacing_sec)
    host = cfg.api_host

    def on_start(self):
        self.login()

    @task
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

    def login(self) -> None:
        with self.client.get(f"/login/demo-user", catch_response=True, name='login') as request:
            assertion.check_http_response('login', request)
        self.token_id = request.text

    def on_stop(self):
        logger.debug(f"user stopped")


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
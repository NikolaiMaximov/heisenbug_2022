#!/usr/bin/env python
# coding: utf-8
# Rebuild docker -> docker-compose up -d --no-deps --build mock


from fastapi import FastAPI, Request
import base64
import random
import time
import json


app = FastAPI()


@app.post("/cart/add")
async def add_to_cart(request: Request):
    product = json.loads(await request.body())
    prod_name = product['Product']
    prod_code = product['Prod_code']
    answers = [
        f"Товар #{prod_code} - '{prod_name}' добавлен в корзину",
        "Ошибка добавления товара",
        ]
    return random.choice(answers)


@app.get("/login/{username}")
def token(username: str):
    return f"Token {base64.standard_b64encode(username.encode('utf-8'))}"

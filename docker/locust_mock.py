#!/usr/bin/env python
# coding: utf-8

# developer : Nikolai Maksimov (X5 Group)
# date: 17.11.2021

from fastapi import FastAPI
import base64
import random
import time

app = FastAPI()


@app.get("/demo_http")
def demo_http():
    time.sleep(random.randrange(1, 3))
    return random.choice([f'Response is {True}',
                          f'Response is {False}', ])


@app.get("/login/{username}")
def token(username: str):
    return f"Token {base64.standard_b64encode(username.encode('utf-8'))}"

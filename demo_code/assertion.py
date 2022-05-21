#!/usr/bin/env python
# coding: utf-8

# developer : Nikolai Maksimov (X5 Group)
# date: 17.11.2021


def check_http_response(transaction, response):
    response_body = str(response.content)
    if transaction == 'login':
        if 'Token' not in response_body:
            response.failure('Login failed')

    if transaction == 'send_http':
        if 'False' in response_body:
            response.failure('Bad response')



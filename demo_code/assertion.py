def check_http_response(transaction, response):
    response_body = response.text
    if transaction == 'login':
        if 'Token' not in response_body:
            response.failure('Login failed')

    if transaction == 'add_to_cart':
        if 'добавлен в корзину' not in response_body:
            response.failure(response_body)

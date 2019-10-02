import logging
from requests import Response


def response_to_curl(response: Response) -> None:
    """ Логгирует выполненный запрос в CURL формат
    """
    req = response.request
    command = "curl"
    command += " -X " + req.method
    body = req.body
    if body:
        if isinstance(body, bytes):
            body = body.decode()
        command += " -d '{}'".format(body)
    command += " '{}', {:.3f}ms".format(req.url, response.elapsed.total_seconds() * 1000)
    logging.debug(f'REQUEST: {command}')
    logging.debug(f'RESPONSE CODE: {response.status_code}')
    logging.debug(f'RESPONSE: \n{response.text} \n')

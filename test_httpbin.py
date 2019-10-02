import pytest
from requests import Session
from tools import response_to_curl
from requests.status_codes import _codes
from requests import Response
import logging

HTTPBIN_URL = 'https://httpbin.org'


class ApiClient(Session):
    def request(self, method, url, **kwargs) -> Response:
        url = f'{HTTPBIN_URL}{url}'
        response = super().request(method, url, **kwargs)
        response_to_curl(response)
        return response


api = ApiClient()


@pytest.fixture(autouse=True)
def init(request):
    """ Просто для удобного логгирования, что бы понимать в логах какой тест запустился
    """
    logging.info(f'Start of the: {request.node.name}')
    yield
    logging.info(f'End of the: {request.node.name}')


def test_headers():
    current_headers = api.get('/headers').json()
    # Тут нас интресуют только заголовки Accept и Host, так как они не должны изменяться
    assert current_headers['headers']['Accept'] == '*/*'
    assert current_headers['headers']['Host'] == 'httpbin.org'

    # Сохраним структуру предыдущего ответа и дополним его header'ом, который мы отправим
    expected_headers = current_headers
    headers = {'Key': 'Value'}
    expected_headers['headers'].update(headers)

    current_headers = api.get('/headers', headers=headers).json()
    assert current_headers == expected_headers


codes = [c for c in _codes.keys() if c >= 200]


@pytest.mark.parametrize('code', codes)
@pytest.mark.parametrize('method', ['GET', 'PATCH', 'POST', 'PUT', 'DELETE'])
def test_status(code, method):
    """ Тут проверим все коды ошибок
        FIXME: httpbin иногда может тупить и тесты могут быть нестабильными
    """
    response = api.request(method, f'/status/{code}')
    if code in (301, 302, 303, 307):
        # Тут нам надо проверить только коды редиректов
        redirect_codes = [r.status_code for r in response.history]
        assert code in redirect_codes
    else:
        assert response.status_code == code


def test_redirect():
    """ Проверим количество редиректов

    """
    expected_redirects = 3
    response = api.get(f'/redirect/{expected_redirects}')
    redirects = [r.status_code for r in response.history]

    # Количество кодов - это количество редиректов
    assert len(redirects) == expected_redirects

    # Все редиректы должны быть с 302 кодом
    assert all(302 == c for c in redirects)

    expected_redirects = 0
    response = api.get(f'/redirect/{expected_redirects}')
    redirects = [r.status_code for r in response.history]
    assert len(redirects) == expected_redirects

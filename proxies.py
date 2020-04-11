import re
import requests
import urllib3


# tipos de proxy
PROXY_LAYER_TRANSPARENT = 0 # insecure
PROXY_LAYER_ANONYMOUS = 1   # safe
PROXY_LAYER_ELITE = 2       # very safe


def get_real_addr():
    response = requests.get('https://api.ipify.org')
    if response.status_code != 200:
        return False
    return response.text


def check_proxy_layer(html: str, proxy_addr: str, real_addr: str) -> int:

    regex = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    addrs = re.findall(regex, html)

    if len(addrs):
        if real_addr in addrs:
            return PROXY_LAYER_TRANSPARENT

        # o proxy envia o proprio ip
        elif proxy_addr in addrs:
            return PROXY_LAYER_ANONYMOUS

        # ip diferente do proxy (random)
        else:
            return PROXY_LAYER_ANONYMOUS

    # não é possivel identificar que a conexão possui um proxy (muito seguro)
    return PROXY_LAYER_ELITE


def check_target_access(html):
    check_list = [
        '<TITLE>Access Denied<\/TITLE>',
        '<title>403 Forbidden<\/title>'
    ]

    regex = re.compile('|'.join(check_list))
    if re.search(regex, html):
        return False
    else:
        return True


def check_proxy(proxy_host: str, proxy_port: str, real_addr: str, url_layer: str, domain: str, callback):

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'close',
    }

    proxy = '{}:{}'.format(proxy_host, proxy_port)
    proxies = {
        'http': 'http://{}'.format(proxy),
        'https': 'https://{}'.format(proxy)
    }

    try:

        response = requests.get(
            url_layer,
            headers=headers,
            proxies=proxies, 
            timeout=10,
            verify=False)

        if response.status_code != 200:
            callback(True, {
                'msg': 'verificacao de layer retornou um http status != 200'
            })
        proxy_layer = check_proxy_layer(response.text, proxy_host, real_addr)

        response = requests.get(
            domain, 
            headers=headers, 
            proxies=proxies, 
            timeout=10)
        if response.status_code != 200:
            callback(True, {
                'msg': 'verificacao do alvo retornou um http status != 200'
            })

        if check_target_access(response.text):
            open('./output/{}_{}.html'.format(proxy_host, proxy_port), 'w').write(response.text)

        callback(False, {
            'layer': proxy_layer,
            'host': proxy_host,
            'port': proxy_port,
            'ping': response.elapsed.total_seconds()
        })

    except (requests.exceptions.ReadTimeout, 
            requests.exceptions.ProxyError,
            requests.exceptions.ConnectionError,
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.ChunkedEncodingError,
            urllib3.exceptions.ProtocolError,
            requests.exceptions.ConnectTimeout) as exception:

        callback(True, {
            'msg': '{}'.format(type(exception).__name__)
        })

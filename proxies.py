import re
import requests
import urllib3


# tipos de proxy
PROXY_LAYER_TRANSPARENT = 0 # insecure
PROXY_LAYER_ANONYMOUS = 1   # insecure
PROXY_LAYER_ELITE = 2       # secure


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

    # não é possivel identificar que a conexão possui um proxy (seguro)
    return PROXY_LAYER_ELITE


def check_proxy(proxy_host: str, proxy_port: str, url_layer: str, domain: str, callback):

    proxy = '{}:{}'.format(proxy_host, proxy_port)
    proxies = {
        'http': 'http://{}'.format(proxy),
        'https': 'https://{}'.format(proxy)
    }
    
    
    try:
        response = requests.get(
            url_layer, 
            proxies=proxies, 
            timeout=10,
            verify=False)

        if response.status_code != 200:
            callback(True, {
                'msg': 'verificacao de layer retornou um http status != 200'
            })

        proxy_layer = check_proxy_layer(response.text, proxy_host, '127.0.0.1')
        callback(False, {
            'layer': proxy_layer
        })
    
    except (requests.exceptions.ReadTimeout, 
            requests.exceptions.ProxyError,
            requests.exceptions.ConnectionError,
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.ConnectTimeout) as exception:

        callback(True, {
            'msg': '{}'.format(type(exception).__name__)
        })

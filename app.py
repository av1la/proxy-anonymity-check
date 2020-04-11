from proxies import check_proxy
from queue_manager import Queue

def main():

    proxies = open('./input/proxies.txt', 'r').read()
    
    routines = []
    for proxy in proxies.splitlines():

        host, port = proxy.split(':')

        routines.append({
            'function': check_proxy,
            'args': {
                'proxy_host': host, 
                'proxy_port': port, 
                'url_layer': 'http://presscomp.com.br/test/php/test.php', 
                'domain': 'https://google.com.br/',
                'callback': on_proxy_check_finish
            }
        })

    queue = Queue(routines)
    queue.start()


def on_proxy_check_finish(err: bool, result: dict) -> bool:
    print(err, result)
    return True


main()
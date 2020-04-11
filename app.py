from proxies import check_proxy
from proxies import get_real_addr
from queue_manager import Queue


def main():

    real_addr = get_real_addr()
    if not real_addr:
        print('não foi possivel obter o ip real do utilizador.')
        exit()

    proxies = open('./input/proxies2.txt', 'r').read()

    routines = []
    for proxy in proxies.splitlines():

        host, port = proxy.split(':')

        routines.append({
            'function': check_proxy,
            'args': {
                'proxy_host': host, 
                'proxy_port': port,
                'real_addr': real_addr,
                'url_layer': 'http://presscomp.com.br/test/php/test.php', 
                'domain': 'https://www.netflix.com/',
                'callback': on_proxy_check_finish
            }
        })

    queue = Queue(routines, max_threads=300)
    queue.start()


def on_proxy_check_finish(err: bool, result: dict):
    print(err, result)


main()
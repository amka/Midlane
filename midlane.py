# coding: utf-8
import socket
import sys
from thread import start_new_thread

__author__ = 'Andrey Maksimov <meamka@ya.ru>'
__date__ = '09.03.16'

BUFFER_SIZE = 8192
MAX_CONNECTIONS = 100


def proxy_server(host, port, conn, addr, data):
    s = socket.socket()
    try:
        s.connect((host, port))
        s.send(data)

        while True:
            reply = s.recv(BUFFER_SIZE)

            if len(reply) > 0:
                conn.send(reply)

                dar = '%.3s KB' % (float(len(reply)) / 1024,)
                print '[*] Request Done: %s => %s <=' % (addr[0], dar)
            else:
                break

    except Exception as e:
        print e

    finally:
        s.close()
        conn.close()
        sys.exit()


def conn_string(conn, data, addr):
    """

    :param conn:
    :param data:
    :type data: str
    :param addr:
    :return:
    """
    try:
        request = data.splitlines()
        method, url, protocol_version = request[0].split()

        http_pos = url.find('://')
        if http_pos == -1:
            temp = url
        else:
            temp = url[http_pos + 3:]

        port_pos = temp.find(':')
        host_pos = temp.find('/')
        if host_pos == -1:
            host_pos = len(temp)

        if port_pos == -1 or host_pos < port_pos:
            port = 80
            host = temp[:host_pos]
        else:
            port = int(temp[port_pos + 1:host_pos])
            host = temp[:port_pos]

        print 'METHOD:   %s' % method
        print 'PROTOCOL: %s' % url[:http_pos]
        print 'HOST:     %s' % host
        print 'PORT:     %s' % port

        proxy_server(host, port, conn, addr, data)

    except Exception as e:
        sys.stderr.write(e.msg + '\n')
        pass


def main(hostname, port, max_connects=MAX_CONNECTIONS):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((hostname, port))
    sock.listen(max_connects)
    sys.stdout.write('Midlane listen %s on port %s…\n' % (hostname, port))
    while True:
        try:
            conn, addr = sock.accept()
            data = conn.recv(BUFFER_SIZE)
            print 'Received data: %s' % data

            start_new_thread(conn_string, (conn, data, addr))
        except KeyboardInterrupt:
            sock.close()
            sys.stdout.write('Midlane stopped by keyboard. Bye…\n')
            sys.exit(0)


if __name__ == '__main__':
    main('', 9091)

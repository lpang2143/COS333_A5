#-----------------------------------------------------------------------
# regserver.py
# Author: Hervé Ishimwe, Louis Pang
#-----------------------------------------------------------------------

from os import name
from sys import exit, stderr
from socket import socket, SOL_SOCKET, SO_REUSEADDR
import argparse
from multiprocessing import Process, cpu_count
from pickle import dump, load
from time import process_time
from reg_details import get_detail
from reg_overview import get_overviews

#-----------------------------------------------------------------------

def consume_cpu_time(delay):

    i = 0
    initial_time = process_time()
    while(process_time() - initial_time) < delay:
        i += 1

#-----------------------------------------------------------------------

def handle_client(sock, delay):
    successful = False
    in_flo = sock.makefile(mode='rb')
    raw_input = load(in_flo)

    input_type = int(raw_input[0])
    input_tuple = raw_input[1]
    print("input type: ", input_type)
    print("input tuple: ", input_tuple)

    consume_cpu_time(delay)

    if input_type != 0 | input_type != 1:
        print('Improper Input Type')
        return

    if input_type == 0:
        print('Received command: get_overviews')
        to_send = get_overviews(input_tuple)
    elif input_type == 1:
        print('Received command: get_detail')
        to_send = get_detail(input_tuple)

    if to_send is not None:
        successful = True

    out_list = [successful, to_send]

    out_flo = sock.makefile(mode='wb')
    dump(out_list, out_flo)
    out_flo.flush()

#-----------------------------------------------------------------------

def create_parser():
    parser = argparse.ArgumentParser(
        description='Server for the registrar application',
        allow_abbrev=False)
    parser.add_argument('port', type=int,
        help='the port at which the server should listen')
    parser.add_argument('delay', type=int,
        help=('the artificial number of seconds'
              'the server will wait after a query'))
    return parser

#-----------------------------------------------------------------------

def main():
    parser = create_parser()
    input_args = parser.parse_args()

    print('CPU count:', cpu_count)

    try:
        port = input_args.port
        delay = input_args.delay

        server_sock = socket()
        print('Opened server socket')
        if name != 'nt':
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind(('', port))
        # print(result)
        # if(result != True):
        #     print('Address is already in use')
        #     exit(1)
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')

        while True:
            try:
                sock, client_addr = server_sock.accept()
                with sock:
                    print('Accepted connection, opened socket')
                    print('Server IP addr and port:',sock.getsockname())
                    print('Client IP addr and port:',client_addr)
                    process = Process(target=handle_client,
                        args=[sock, delay])
                    process.start()

            except Exception as ex:
                print(ex, file=stderr)

    except IOError as i_o:
        print(i_o, file=stderr)
        exit(1)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()

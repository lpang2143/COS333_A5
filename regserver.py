#-----------------------------------------------------------------------
# regserver.py
# Author: Hervé Ishimwe, Louis Pang
#-----------------------------------------------------------------------

from os import name
from sys import exit, stderr
from socket import socket, SOL_SOCKET, SO_REUSEADDR
import argparse
from pickle import dump, load
from reg_details import get_detail
from reg_overview import get_overviews

#-----------------------------------------------------------------------

def handle_client(sock):
    successful = False
    in_flo = sock.makefile(mode='rb')
    raw_input = load(in_flo)
    input_type = int(raw_input[0])
    input_tuple = raw_input[1]
    print("input type: ", input_type)
    print("input tuple: ", input_tuple)
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
    return parser

#-----------------------------------------------------------------------

def main():
    parser = create_parser()
    input_args = parser.parse_args()

    try:
        port = input_args.port

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
                    handle_client(sock)
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

from sys import exit, argv, stderr
from socket import socket
from pickle import dump, load

def main():
    try:
        host = 'localhost'
        port = int(54321)

        test = (('AMS',None,None,None))
        input = ('1', 9112)

        with socket() as sock:
            sock.connect((host, port))
            out_flo = sock.makefile(mode='wb')
            dump(input, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode='rb')
            check, data = load(in_flo)
            print(check == True)
            print(data)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)



if __name__ == '__main__':
    main()
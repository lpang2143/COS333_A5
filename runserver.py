#-----------------------------------------------------------------------
# regserver.py
# Author: Hervé Ishimwe & Louis Pang
#-----------------------------------------------------------------------

import argparse
from sys import exit, stderr
from regapp import app

#-----------------------------------------------------------------------
# returns an argparse object after checking the command-line args
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
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()

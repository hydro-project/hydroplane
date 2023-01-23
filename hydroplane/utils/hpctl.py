import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests


def handle_error(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as request_error:
        try:
            print(json.dumps(response.json(), indent=2))
        except requests.exceptions.JSONDecodeError as decode_error:
            print(response.text)

        raise request_error


def start_process(process_spec_path: str, server: str):
    process_file = Path(process_spec_path)
    if not process_file.exists():
        raise ValueError(f"Can't find file {process_file}")

    with process_file.open() as fp:
        process_spec = json.load(fp)

    response = requests.post(f'http://{server}/process', json=process_spec)
    handle_error(response)


def stop_process_or_group(process_or_group_name: str, group: bool, server: str):
    if group:
        stop_group(process_or_group_name, server)
    else:
        stop_process(process_or_group_name, server)


def stop_process(process_name: str, server: str):
    response = requests.delete(f'http://{server}/process/{process_name}')
    handle_error(response)


def stop_group(group_name: str, server: str):
    response = requests.delete(f'http://{server}/group/{group_name}')
    handle_error(response)


def list_processes(group_name: Optional[str], server: str):
    if group_name is not None:
        request_uri = f'http://{server}/group/{group_name}'
    else:
        request_uri = f'http://{server}/process'

    response = requests.get(request_uri)
    handle_error(response)

    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A convenience script for controlling '
                                     'a Hydroplane server.')

    parser.add_argument('-d', '--debug', default=False, action='store_true',
                        help='print stack traces for any exceptions raised by the script')

    subparsers = parser.add_subparsers(required=True)

    start_parser = subparsers.add_parser('start', help='start a process')
    start_parser.add_argument('process_spec_path', help='path to a file containing a '
                              'process specification')
    start_parser.set_defaults(cmd=start_process)

    stop_parser = subparsers.add_parser('stop', help='stop a process')
    stop_parser.add_argument('process_or_group_name', help='the name of process or group to stop')
    stop_parser.add_argument(
        '-g', '--group', default=False, action='store_true',
        help='if specified, stops a group with the given name; otherwise, stops a process '
        'with the given name'
    )
    stop_parser.set_defaults(cmd=stop_process_or_group)

    list_parser = subparsers.add_parser('list', help='list a process or group')
    list_parser.add_argument('-g', '--group_name', help='the name of the group to list. '
                             'If unspecified, this command lists all processes')
    list_parser.set_defaults(cmd=list_processes)

    for subparser in (start_parser, stop_parser, list_parser):
        server_source = (" - read from HYDROPLANE_SERVER environment variable"
                         if os.getenv('HYDROPLANE_SERVER') is not None
                         else '')

        subparser.add_argument(
            '-s', '--server',
            help=f"the server's address (default: %(default)s{server_source})",
            default=os.getenv('HYDROPLANE_SERVER', 'localhost:8000')
        )

    args = parser.parse_args()

    cmd = args.cmd
    debug = args.debug

    args_dict = vars(args)
    del args_dict['cmd']
    del args_dict['debug']

    try:
        cmd(**args_dict)
    except Exception as e:
        if debug:
            raise e
        else:
            print(f'ERROR: {e}')
            sys.exit(1)

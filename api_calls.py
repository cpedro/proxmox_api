#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: api_calls.py
Description: Makes various Proxmox VE API calls.

usage: api_calls.py [-h] -H HOST -u USERNAME [-p PASSWORD] [-r] [-v] [-n] [-s]
                    [-g]

Proxmox API Test Program

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Proxmox Host to connect to.
  -u USERNAME, --username USERNAME
                        Username to use to authenticate.
  -p PASSWORD, --password PASSWORD
                        Password, leave blank to be prompted to enter your
                        password
  -r, --show-raw        Show raw output as JSON instead of formatted output.
  -v, --list-vms        List all virtual machines and their disks.
  -n, --list-nodes      List all nodes.
  -s, --list-storage    List all storage.
  -g, --list-ha-groups  List HA groups.
"""

__author__ = 'Chris Pedro'
__copyright__ = '(c) Chris Pedro 2020'
__licence__ = 'MIT'


import argparse
import getpass
import json
import sys

from pve import API
from signal import signal, SIGINT


def list_ha_groups(api, **kwargs):
    groups = api.get_ha_groups()

    if kwargs['show_raw']:
        print(groups)
        return
    if kwargs['show_json']:
        print(json.dumps(groups))
        return

    g_out = """{}:
    comment: {}
    nodes: {}
    resources:"""
    r_out = """        {}:
            type: {}
            state: {}"""

    for group in groups:
        print(g_out.format(
            group['group'], group['comment'], group['nodes']))
        for res in group['resources']:
            print(r_out.format(res['sid'], res['type'], res['state']))


def list_storages(api, **kwargs):
    storage = api.get_storages()

    if kwargs['show_raw']:
        print(storage)
        return
    if kwargs['show_json']:
        print(json.dumps(storage))
        return

    output = """{}:
    type: {}
    content: {}
    shared: {}
    size: {}
    used: {:.1%}"""

    for ds in storage:
        print(output.format(
            ds['storage'], ds['type'], ds['content'], ds['shared'],
            ds['total'], ds['used_fraction']))


def list_nodes(api, **kwargs):
    nodes = api.get_nodes()

    if kwargs['show_raw']:
        print(nodes)
        return
    if kwargs['show_json']:
        print(json.dumps(nodes))
        return

    n_out = """{}:
    status: {}
    cpu: {:.1%}
    memory: {:.1%}"""
    net_out = """        {}:
            comments: {}"""
    ip_out = """            ip: {}"""

    for node in nodes:
        print(n_out.format(
            node['node'], node['status'], node['cpu'],
            node['mem'] / node['maxmem']))
        for net in node['network']:
            print(net_out.format(net['iface'], net['comments'].rstrip()))
            if 'cidr' in net:
                print(ip_out.format(net['cidr']))


def list_vms(api, **kwargs):
    vms = api.get_vms()

    if kwargs['show_raw']:
        print(vms)
        return
    if kwargs['show_json']:
        print(json.dumps(vms))
        return

    v_out = """{}:
    name: {}
    status: {}
    cpu: {}
    memory: {}
    disks:"""
    d_out = """        {}:
            size: {}"""

    for vm in vms:
        print(v_out.format(
            vm['vmid'], vm['name'], vm['status'], vm['cpus'], vm['maxmem']))
        for disk in vm['disks']:
            print(d_out.format(disk['volid'], disk['size']))


def parse_args(args):
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='CLI Proxmox API Program')
    parser.add_argument(
        '-H', '--host', required=True, help='Proxmox Host to connect to.')
    parser.add_argument(
        '-u', '--username', required=True,
        help='Username to use to authenticate.')
    parser.add_argument(
        '-p', '--password', default='',
        help='Password, leave blank to be prompted to enter your password')
    parser.add_argument(
        '-r', '--show-raw', action='store_true',
        help='Show raw output instead of formatted output.')
    parser.add_argument(
        '-j', '--show-json', action='store_true',
        help='Show output as JSON instead of formatted output.')
    parser.add_argument(
        '-v', '--list-vms', action='store_true',
        help='List all virtual machines and their disks.')
    parser.add_argument(
        '-n', '--list-nodes', action='store_true', help='List all nodes.')
    parser.add_argument(
        '-s', '--list-storages', action='store_true', help='List all storage.')
    parser.add_argument(
        '-g', '--list-ha-groups', action='store_true', help='List HA groups.')
    return parser.parse_args(args)


def handler(signal_received, frame):
    """Signal handler.
    """
    sys.exit(0)


def main(args):
    """Main method.
    """
    args = parse_args(args)

    if sys.stdin.isatty() and len(args.password) == 0:
        try:
            password = getpass.getpass('Enter Password: ')
        # Catch Ctrl-D
        except EOFError:
            return 0
    else:
        password = args.password

    f_kwargs = {'show_raw': args.show_raw, 'show_json': args.show_json}

    api = API(
        args.host, user=args.username, password=password, verify_ssl=False)

    if args.list_vms:
        list_vms(api, **f_kwargs)
    if args.list_nodes:
        list_nodes(api, **f_kwargs)
    if args.list_storages:
        list_storages(api, **f_kwargs)
    if args.list_ha_groups:
        list_ha_groups(api, **f_kwargs)


if __name__ == '__main__':
    signal(SIGINT, handler)
    sys.exit(main(sys.argv[1:]))


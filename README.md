# Proxmox API Scripts

Collection of Python programs and libraries to admin Proxmox VE via web API.
Uses [proxmoxer](https://pypi.org/project/proxmoxer/).

## Requirements
To make sure you have all requirements:

```bash
$ pip3 install -r requirements.txt
```

## pve_api_calls.py
Main script that can be used to call the underlying functions defined in pve.

```
usage: pve_api_calls.py [-h] -H HOST -u USERNAME [-p PASSWORD] [-r] [-j] [-v]
                        [-n] [-s] [-g] [-f]

CLI Proxmox API Program

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Proxmox Host to connect to.
  -u USERNAME, --username USERNAME
                        Username to use to authenticate.
  -p PASSWORD, --password PASSWORD
                        Password, leave blank to be prompted to enter your
                        password
  -r, --show-raw        Show raw output instead of formatted output.
  -j, --show-json       Show output as JSON instead of formatted output.
  -v, --list-vms        List all virtual machines and their disks.
  -n, --list-nodes      List all nodes.
  -s, --list-storages   List all storage.
  -g, --list-ha-groups  List HA groups.
  -f, --fstrim          Run fstrim on all VMs.
```

When using the `-j`, you can pipe through `jq` for 'cleaner' output.  It can
also be used to filter output.
```bash
$ ./pve_api_calls.py -H HOST -u USER -p PASS -s -j | jq
[
  {
    "total": 35401613312,
    "type": "dir",
    "used_fraction": 0.119363802173604,
    "enabled": 1,
    "content": "backup",
    "active": 1,
    "storage": "local",
    "avail": 29347225600,
    "shared": 0,
    "used": 4225671168
  },
  {
    "used_fraction": 0,
    "type": "lvmthin",
    "enabled": 1,
    "total": 81302388736,
    "shared": 0,
    "used": 0,
    "avail": 81302388736,
    "storage": "local-lvm",
    "content": "rootdir,images",
    "active": 1
  }
]
```

## TODO
* Added extra methods to PVEAPI.
* Write unit tests.


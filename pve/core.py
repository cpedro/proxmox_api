# -*- coding: utf-8 -*-
"""
File: pve_api/core.py
Description: Core of Proxmox API.  Defines the class and methods.
"""

__author__ = 'Chris Pedro'
__copyright__ = '(c) Chris Pedro 2020'
__licence__ = 'MIT'


from proxmoxer import ProxmoxAPI


def dedup(dict, id):
    """Quick and dirty function to dedup the lists of dictionaries based on an
    id to determine whether or not an item has been 'seen'
    """
    seen = set()
    dedup = []

    for d in dict:
        if d[id] not in seen:
            seen.add(d[id])
            dedup.append(d)

    return dedup


class API(object):
    """Proxmox VE API class.  Does common tasks, wrapping up what is in
    proxmoxer.
    """
    def __init__(self, host, **kwargs):
        api = ProxmoxAPI(host, **kwargs)
        self.api = api

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, api):
        self._api = api

    def create_vm(self, node, vm, *args, **kwargs):
        """Creates and sets up a VM on the PVE cluster.
        """
        self.api.nodes(node).qemu.create(**vm)
        return

    def get_ha_groups(self, *args, **kwargs):
        """Get and returns all HA groups on the PVE cluster, along with resources.
        """
        groups = self.api.cluster.ha.groups.get()
        resources = self.api.cluster.ha.resources.get()

        for group in groups:
            group_resources = []
            for resource in resources:
                if resource['group'] == group['group']:
                    group_resources.append(resource)
            group['resources'] = group_resources

        return groups

    def get_nodes(self, *args, **kwargs):
        """Get and returns a list of all nodes on the PVE cluster.
        """
        nodes = self.api.nodes.get()
        # Add to this list to get more info on node.
        properties = ['network', 'services']

        for node in nodes:
            for p in properties:
                node[p] = self.api.nodes(node['node']).get(p)

        return nodes

    def get_storages(self, *args, **kwargs):
        """Get and returns a list of all storage active on the PVE cluster.
        """
        storage = []
        seen = set()

        for node in self.api.nodes.get():
            for ds in self.api.nodes(node['node']).get('storage'):
                if ds['shared'] != 1:
                    ds['node'] = node['node']
                elif ds['storage'] in seen:
                    continue
                else:
                    seen.add(ds['storage'])

                ds['contents'] = self.api.nodes(
                    node['node']).storage(ds['storage']).get('content')
                storage.append(ds)

        return storage

    def get_vms(self, *args, **kwargs):
        """Get and returns a list of all VMs and disks on the PVE cluster.
        """
        vms = []
        all_disks = []

        for node in self.api.nodes.get():
            vms.extend(self.api.nodes(node['node']).get('qemu', full=1))
            # Loop through storage with content = images only.
            storage = self.api.nodes(node['node']).get(
                'storage', content='images')
            for ds in storage:
                all_disks.extend(
                    self.api.nodes(
                        node['node']).storage(ds['storage']).get('content'))
        all_disks = dedup(all_disks, 'volid')

        for vm in vms:
            vmdisks = []
            for disk in all_disks:
                if int(disk['vmid']) == int(vm['vmid']):
                    vmdisks.append(disk)
            vm['disks'] = vmdisks

        return vms


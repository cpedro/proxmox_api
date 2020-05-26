# -*- coding: utf-8 -*-
"""
File: pve_api/core.py
Description: Core of Proxmox API.  Defines the class and methods.
"""

__author__ = 'Chris Pedro'
__copyright__ = '(c) Chris Pedro 2020'
__licence__ = 'MIT'


from proxmoxer import ProxmoxAPI


def dedup(dict, to_match):
    """Quick and dirty function to deduplicate the lists of dictionaries based
    on an id to determine whether or not an item has been 'seen'
    """
    seen = set()
    dlist = []

    for d in dict:
        if d[to_match] not in seen:
            seen.add(d[to_match])
            dlist.append(d)

    return dlist


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

    def create_vm(self, node, vmid, **kwargs):
        """Creates and sets up a VM on the PVE cluster.
        """
        self.api.nodes(node).qemu.create(vmid=vmid, **kwargs)
        return

    def delete_vm(self, node, vmid, **kwargs):
        """Deletes a VM from a node.
        Can use **kwargs to specify additional options, such as purge=1 to
        purge disks and backups.
        """
        self.api.nodes(node).qemu(vmid).delete(**kwargs)
        return

    def start_vm(self, node, vmid, **kwargs):
        """Starts a VM on a node.
        """
        self.api.nodes(node).qemu(vmid).status.start.post(**kwargs)
        return

    def stop_vm(self, node, vmid, **kwargs):
        """Stops a VM on a node.
        """
        self.api.nodes(node).qemu(vmid).status.stop.post(**kwargs)
        return

    def ha_add_vm(self, vmid, **kwargs):
        """Adds VM as a HA resource.
        Can use **kwargs to specify additional options, such as group='<group>'
        to specify group to be added to, or state='started'
        """
        self.api.cluster.ha.resources.create(sid='vm:' + str(vmid), **kwargs)
        return

    def ha_remove_vm(self, vmid):
        """Removes a VM from HA.
        """
        self.api.cluster.ha.resources('vm:' + str(vmid)).delete()
        return

    def get_ha_groups(self):
        """Get and returns all HA groups on the PVE cluster, along with
        resources.
        """
        groups = self.api.cluster.ha.groups.get()
        resources = self.api.cluster.ha.resources.get()

        for group in groups:
            group_resources = []
            for resource in resources:
                group_resources.append(resource)
            group['resources'] = group_resources

        return groups

    def get_nodes(self):
        """Get and returns a list of all nodes on the PVE cluster.
        """
        nodes = self.api.nodes.get()
        # Add to this list to get more info on node.
        properties = ['network', 'services']

        for node in nodes:
            for p in properties:
                node[p] = self.api.nodes(node['node']).get(p)

        return nodes

    def get_storages(self):
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

    def get_vms(self):
        """Get and returns a list of all VMs and disks on the PVE cluster.
        """
        vms = []
        all_disks = []

        for node in self.api.nodes.get():
            # Before adding VM to list, add the node as well.
            for vm in self.api.nodes(node['node']).get('qemu', full=1):
                vm['node'] = node['node']
                vms.append(vm)
            # Loop through storage with content = images only.
            storage = self.api.nodes(node['node']).get(
                'storage', content='images')
            for ds in storage:
                all_disks.extend(
                    self.api.nodes(
                        node['node']).storage(ds['storage']).get('content'))
        all_disks = dedup(all_disks, 'volid')

        for vm in vms:
            vmdisks = list(
                disk for disk in all_disks
                if int(disk['vmid']) == int(vm['vmid']))
            vm['disks'] = vmdisks

        return vms

    def fstim_vm(self, node, vmid):
        """Perform an fstrim on a VM.
        """
        try:
            return self.api.nodes(node).qemu(vmid).agent.post('fstrim')
        except Exception as e:
            return {'result': {'exception': str(e)}}


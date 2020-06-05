#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ipaddress
from ciscoconfparse import CiscoConfParse

# 定数
l3sw_conf_file = 'config/190702_tvl3-inside01.log'
wanfw_conf_file = 'config/200410_tvfw-wan-dc01.log'
inetfw_conf_file = 'config/200526_tvfw-outside01.xml'


# Class
class NetworkObject():
    def __init__(self, name, parent):
        self.name = name
        for child in parent.children:
            ary = child.text.strip().split()
            if ary[0] == 'host':
                self.network = ipaddress.ip_address(ary[1])
            elif ary[0] == 'subnet':
                self.network = ipaddress.ip_network(f'{ary[1]}/{ary[2]}')
            elif ary[0] == 'range':
                pass
            elif ary[0] == 'fqdn':
                pass
            else:
                pass

    def __str__(self):
        return str(self.network)


class ServiceObject():
    def __init__(self, name, parent):
        self.name = name
        self.source_port = ''
        self.destination_port = ''
        for child in parent.children:
            ary = child.text.strip().split()
            if ary[0] == 'description':
                continue
            if ary[0] != 'service':
                raise
            if ary[1] == 'ip':
                self.svc = 'any'
            elif ary[1] in ('icmp', 'icmp6'):
                if len(ary) > 2:
                    icmp_type = ary[2]
                if len(svc) > 3:
                    icmp_code = ary[3]
                self.svc = f'icmp({icmp_type}:{icmp_code})'
            elif ary[1] in('tcp', 'udp', 'sctp'):
                detail = ary[2:]
                while detail:
                    ent = detail.pop(0)
                    ope = detail.pop(0)
                    if ope == 'eq':
                        port = detail.pop(0)
                    elif ope == 'lt':
                        port = '<' + detail.pop(0)
                    elif ope == 'gt':
                        port = '>' + detail.pop(0)
                    elif ope == 'neq':
                        port = '!' + detail.pop(0)
                    elif ope == 'range':
                        port = detail.pop(0) + ' - ' + detail.pop(0)
                    if ent == 'source':
                        self.source_port = port
                    elif ent == 'destination':
                        self.destination_port = port
            else:
                raise

    def __str__(self):
        return f'src:{self.source_port}; dst:{self.destination_port}'


class ObjectGroup():
    def __init__(self, name):
        super(ObjectGroup, self).__init__()
        self.name = name
        self.og = []

    def add_object(self, o):
        self.og.append(o)

    def get_object(self, name):
        return ','.join([str(o) for o in self.og])


obj_dict = {}
wan_conf = CiscoConfParse(wanfw_conf_file, syntax='asa')
for o in wan_conf.find_objects(r'^object\s'):
    stmt = o.text.strip().split()
    obj_type = stmt[1]
    obj_name = stmt[2]
    if obj_type == 'network':
        obj = NetworkObject(obj_name, o)
    elif obj_type == 'service':
        obj = ServiceObject(obj_name, o)
    obj_dict[obj_name] = obj

for og in wan_conf.find_objects(r'^object-group'):
    stmt = og.text.strip().split()
    og_type = stmt[1]
    og_name = stmt[2]
    if og_type == 'network':
        pass
    if og_type == 'service':
        pass

for k, v in obj_dict.items():
    print(f'{k}:{v}')

# obj_dic = {}
# wan_conf = CiscoConfParse(wanfw_conf_file, syntax='asa')
# for o in wan_conf.find_objects(r'^object\s'):
#     ary = o.text.split()
#     obj_type = ary[1]
#     name = ary[2]
#     for entity in o.children:
#         ent = entity.text.split()
#         ent_type = ent[0]
#         if ent_type == 'host':
#             obj_dic[name] = NetworkObject(name, f'{ent[1]}/32')
#         elif ent_type == 'subnet':
#             obj_dic[name] = NetworkObject(name, f'{ent[1]}/{ent[2]}')
#         elif ent_type == 'service':
#             obj_dic[name] = ServiceObject(name, ent[1:])
#         else:
#             pass
#     print(o.text)

# print(f'action    src         dest       proto')
# for acl in wan_conf.find_objects(r'^ip access-list'):
#     for a in acl.re_search_children(r'^\s*\d+'):
#         stmt = a.text.strip().split()
#         action = stmt[1]
#         src = stmt[3]
#         dest = stmt[4]
#         proto = stmt[2]
#         print(f'{action} {src} > {dest} {proto}')

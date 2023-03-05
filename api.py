#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 23:26:06 2019

@author: roy
"""
from typing import List

import requests
from base64 import b64encode
import re

from model import WeekSchedule, DaySchedule, HourSchedule, Target, GroupedTarget, Rule, Host, IpTarget
from utils import check


# var ACT_GET = 1;
# var ACT_SET = 2;
# var ACT_ADD = 3;
# var ACT_DEL = 4;
# var ACT_GL = 5;
# var ACT_GS = 6;
# var ACT_OP = 7;
# var ACT_CGI = 8;

class Router(object):

    def __init__(self, host, username='admin', password='admin'):
        self.host = host
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.referer = 'http://' + self.host
        self.session.headers['Cookie'] = self.get_auth_cookie(username, password)
        self.session.headers['Referer'] = self.referer

        self.main_referer = self.referer + '/mainFrame.htm'

        # Stop the requests after a specific time
        self.timeout = 1.5
        self.post_timeout = 3

    def update_login_credentials(self, new_username, new_password):
        self.username = new_username
        self.password = new_password
        self.session.headers['Cookie'] = self.get_auth_cookie(new_username, new_password)

    @classmethod
    def get_auth_cookie(cls, username, password):
        user_pass_str = username + ':' + password
        user_pass_encode = b64encode(user_pass_str.encode()).decode('ascii')
        authentication = 'Basic ' + user_pass_encode
        return 'Authorization=' + authentication

    def login(self):
        print("Invoking login")
        response = self.session.get(self.referer, timeout=self.timeout)
        is_login_success = re.search('(?i)username or password is incorrect', response.text)
        if is_login_success == None:
            return True

    def post_data(self, referer, post_url, payload):
        self.session.headers['Referer'] = referer
        print("-" * 10)
        print(f"{post_url} {self.session.headers}\n{payload}")
        response = self.session.post(post_url, data=payload, timeout=self.post_timeout)
        print(response.status_code)
        print(response.text)
        print("-" * 10)
        return response

    def get_wan_details(self):
        print("Invoking get_wan_details")
        referer = self.main_referer
        post_url = self.referer + '/cgi?1&1'
        payload = '[WAN_ETH_INTF#1,0,0,0,0,0#0,0,0,0,0,0]0,2\r\nenable\r\nX_TP_lastUsedIntf\r\n[WAN_IP_CONN#1,1,1,0,0,0#0,0,0,0,0,0]1,0\r\n'
        response = self.post_data(referer, post_url, payload).text

        addressingType = r'(?:addressingType=)(.*)'
        ipAddress = r'(?:externalIPAddress=)(.*)'
        subnetMask = r'(?:subnetMask=)(.*)'
        defaultGateway = r'(?:defaultGateway=)(.*)'
        dnsServers = r'(?:DNSServers=)(.*)'

        wan_details = [addressingType, ipAddress, subnetMask, defaultGateway, dnsServers]
        for c in range(len(wan_details)):
            search = re.search(wan_details[c], response)
            wan_details[c] = search.group(search.lastindex)
        return wan_details

    def configure_wan(self, ipAddress, subnetMask, defaultGateway, dnsServers, dnsServers2):
        print("Invoking configure_wan")
        referer = self.main_referer
        post_url = self.referer + '/cgi?2&2'
        payload = '[WAN_ETH_INTF#1,0,0,0,0,0#0,0,0,0,0,0]0,2\r\nX_TP_lastUsedIntf=ipoe_eth3_s\r\nX_TP_lastUsedName=ewan_ipoe_s\r\n[WAN_IP_CONN#1,1,1,0,0,0#0,0,0,0,0,0]1,18\r\nexternalIPAddress={}\r\nsubnetMask={}\r\ndefaultGateway={}\r\nNATEnabled=1\r\nX_TP_FullconeNATEnabled=0\r\nX_TP_FirewallEnabled=1\r\nmaxMTUSize=1500\r\nDNSOverrideAllowed=1\r\nDNSServers={},{}\r\nX_TP_IPv4Enabled=1\r\nX_TP_IPv6Enabled=0\r\nX_TP_IPv6AddressingType=Static\r\nX_TP_ExternalIPv6Address=::\r\nX_TP_PrefixLength=64\r\nX_TP_DefaultIPv6Gateway=::\r\nX_TP_IPv6DNSOverrideAllowed=0\r\nX_TP_IPv6DNSServers=::,::\r\nenable=1\r\n'.format(
            ipAddress, subnetMask, defaultGateway, dnsServers, dnsServers2)

        response = self.post_data(referer, post_url, payload).text
        if response == '[error]0':
            return True

    def reboot(self):
        print("Invoking reboot")
        referer = self.main_referer
        post_url = self.referer + '/cgi?7'
        payload = '[ACT_REBOOT#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n'
        response = self.post_data(referer, post_url, payload).text
        if response == '[error]0':
            return True

    def enable_access_control(self, enable: bool = False):
        print("Invoking enable_access_control")
        check(enable, bool, "enable")
        payload = f"[FIREWALL#0,0,0,0,0,0#0,0,0,0,0,0]0,2\r\nenable={int(enable)}\r\ndefaultAction=0\r\n"
        post_url = self.referer + '/cgi?2'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    # requires already existing shcedule at least one
    # if schedule configuration(not name) already exists, then error
    def add_schedule(self, name: str, schedule: WeekSchedule):
        print("Invoking add_schedule")
        check(name, str, "name")
        check(schedule, WeekSchedule, "schedule")
        formatted_schedule = Router.format_schedule(schedule)
        print(schedule)
        print(formatted_schedule)
        payload = f"[TASK_SCHEDULE#0,0,0,0,0,0#0,0,0,0,0,0]0,15\r\nentryName={name}\r\n{formatted_schedule}"
        post_url = self.referer + '/cgi?3'  # if first schedule - change to ?2,and also replace first '0' -> '2' in payload after TASK_SCHEDULE after '#'(either first or second)
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True
        if response.text == '[error]4712':
            print(
                "Error: Such configuration already exists. Not the name, the configuration of the schedule exactly the same as in one of the existing ones")
            return False
        if response.text == '[error]1001':
            print(f"Error: Such schedule for name {name} already exists")
            return False

    def get_schedules(self, include_parent: bool = False):
        print("Invoking get_schedules")
        payload = "[TASK_SCHEDULE#0,0,0,0,0,0#0,0,0,0,0,0]0,2\r\nentryName\r\nisParentCtrl\r\n"
        post_url = self.referer + '/cgi?5'
        response = self.post_data(self.main_referer, post_url, payload)
        if '[error]0' in response.text:
            return [(id, schedule) for id, schedule in Router.parse_schedules(response.text) if
                    "childSchedule" not in schedule or include_parent]

    @staticmethod
    def parse_schedules(sch_str: str):
        sch_id_name = []
        schedules = sch_str.split("[")
        for sch in schedules[1:-1]:
            lines = re.split("\r?\n", sch)
            id = int(lines[0].split(",")[0])
            name = lines[1].split('=')[1]
            sch_id_name.append((id, name))
        return sch_id_name

    def delete_schedule(self, id):
        print("Invoking delete_schedule")
        check(id, int, "id")
        payload = f"[TASK_SCHEDULE#{id},0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        post_url = self.referer + '/cgi?4'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    def delete_target(self, id):
        print("Invoking delete_target")
        check(id, int, "id")
        payload = f"[EXTERNAL_HOST#{id},0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        post_url = self.referer + '/cgi?4'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    def delete_host(self, id):
        print("Invoking delete_host")
        check(id, int, "id")
        payload = f"[INTERNAL_HOST#{id},0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        post_url = self.referer + '/cgi?4'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    # allow 0, deny - 1
    def add_rule(self, rule: Rule):
        print("Invoking add_rule")
        payload = f"[RULE#0,0,0,0,0,0#0,0,0,0,0,0]0,8\r\nruleName={rule.name}\r\ninternalHostRef={rule.host}\r\nexternalHostRef={rule.target}\r\nscheduleRef={rule.schedule}\r\naction={int(rule.deny)}\r\nenable={int(rule.enable)}\r\ndirection=1\r\nprotocol=0\r\n"
        post_url = self.referer + '/cgi?3'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    def enable_rule(self, id: int, enable: bool = False):
        print("Invoking enable_rule")
        check(id, int, "id")
        check(enable, bool, "enable")
        payload = f"[RULE#{id},0,0,0,0,0#0,0,0,0,0,0]0,1\r\nenable={int(enable)}\r\n"
        post_url = self.referer + '/cgi?2'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    def delete_rule(self, id: int):
        print("Invoking delete_rule")
        check(id, int, "id")
        payload = f"[RULE#{id},0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        post_url = self.referer + '/cgi?4'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    def get_rules(self, include_parent: bool = False):
        print("Invoking get_rules")
        payload = "[RULE#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n[FIREWALL#0,0,0,0,0,0#0,0,0,0,0,0]1,2\r\nenable\r\ndefaultAction\r\n"
        post_url = self.referer + '/cgi?5&1'
        response = self.post_data(self.main_referer, post_url, payload)
        if '[error]0' in response.text:
            return [rule for rule in Router.parse_rules(response.text) if not rule.parent_ctrl or include_parent]

    @staticmethod
    def parse_rules(rules_str: str):
        rules_repr = rules_str.split("[")
        rules = []

        for rule in rules_repr[1:-2]:
            lines = re.split("\r?\n", rule)
            id = int(lines[0].split(",")[0])

            def get_value(num):
                return lines[num].split("=")[1]

            enable = bool(int(get_value(1)))
            deny = bool(int(get_value(2)))
            name = str(get_value(3))
            parent = bool(int(get_value(4)))
            # skip 5, 6, 7
            host = str(get_value(8))
            target = str(get_value(9))
            schedule = str(get_value(10))
            rules.append(Rule(name, host, target, schedule, deny, enable, id, parent))
        return rules

    def add_host(self, host: Host):
        print("Invoking add_host")
        payload = f"[INTERNAL_HOST#0,0,0,0,0,0#0,0,0,0,0,0]0,3\r\ntype=1\r\nentryName={host.name}\r\nmac={host.mac}\r\n"
        post_url = self.referer + '/cgi?3'
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True
        if response.text == '[error]1001':
            print(f"Error: Host with name: {host.name} already exists")
            return False
        if response.text == '[error]4710':
            print(f"Error: Host with mac address: {host.mac} already exists")
            return False

    def get_hosts(self, include_parent: bool = False):
        print("Invoking get_hosts")
        payload = "[INTERNAL_HOST#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        post_url = self.referer + '/cgi?5'
        response = self.post_data(self.main_referer, post_url, payload)
        if '[error]0' in response.text:
            return [(id, host) for id, host in Router.parse_hosts(response.text) if
                    "childMac" not in host or include_parent]

    @staticmethod
    def parse_hosts(sch_str: str):
        host_id_name = []
        schedules = sch_str.split("[")
        for sch in schedules[1:-1]:
            lines = re.split("\r?\n", sch)
            id = int(lines[0].split(",")[0])
            name = lines[3].split('=')[1]
            host_id_name.append((id, name))
        return host_id_name

    def add_ip_target(self, target: IpTarget):
        print("Invoking add_ip_target")
        payload = f"[EXTERNAL_HOST#0,0,0,0,0,0#0,0,0,0,0,0]0,6\r\nentryName={target.name}\r\ntype=0\r\nIPStart={target.intStart()}\r\nIPEnd={target.intEnd()}\r\nportStart={target.portStart}\r\nportEnd={target.portEnd}\r\n"
        post_url = self.referer + '/cgi?3'
        response = self.post_data(self.main_referer, post_url, payload)
        if '[error]0' in response.text:
            return True

    def add_target(self, target: GroupedTarget):
        print("Invoking add_target")
        # /cgi?3 adds with first entry -> returns id
        # /cgi?2 updates entry with id and adds new entries
        id = self._set_target(target.first())
        if not id: return False
        res = self._add_targets(target.targets_omit_first(), id)
        if res:
            return id

    def get_targets(self, include_parent: bool = False):
        print("Invoking get_targets")
        payload = "[EXTERNAL_HOST#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        post_url = self.referer + '/cgi?5'
        response = self.post_data(self.main_referer, post_url, payload)
        if '[error]0' in response.text:
            return [(id, target) for id, target in Router.parse_targets(response.text) if
                    "childUrl" not in target or include_parent]

    @staticmethod
    def parse_targets(targets_str: str):
        target_id_name = []
        schedules = targets_str.split("[")
        for sch in schedules[1:-1]:
            lines = re.split("\r?\n", sch)
            id = int(lines[0].split(",")[0])
            name = lines[3].split('=')[1]
            target_id_name.append((id, name))
        return target_id_name

    def _get_target_id(self, response):
        print("Invoking _get_target_id")
        return int(response[1:].split(",")[0])

    def _set_target(self, target: Target):
        print("Invoking _set_target")
        payload = Router.format_target(target, 0, 0)
        post_url = self.referer + '/cgi?3'
        response = self.post_data(self.main_referer, post_url, payload)
        if '[error]0' in response.text:
            return self._get_target_id(response.text)
        if '[error]1001' in response.text:
            print(f"Error: Target with name: {target.name} already exists")
            return None

    def _add_targets(self, targets: List[Target], id: int):
        print("Invoking _add_targets")
        payload = ""
        post_url = self.referer + '/cgi?'
        for i, target in enumerate(targets):
            post_url += "2&"
            payload += Router.format_target(target, id, i)
        post_url = post_url[:-1]
        response = self.post_data(self.main_referer, post_url, payload)
        if response.text == '[error]0':
            return True

    def change_pass(self, new_username, new_password):
        print("Invoking change_pass")
        check(new_username, str, "new_username")
        check(new_password, str, "new_password")
        payload = f"[/cgi/auth#0,0,0,0,0,0#0,0,0,0,0,0]0,3\r\noldPwd={self.password}\r\nname={new_username}\r\npwd={new_password}\r\n"
        post_url = self.referer + '/cgi?8'
        response = self.post_data(self.main_referer, post_url, payload)
        if '[error]0' in response.text:
            self.update_login_credentials(new_username, new_password)
            return True

    def change_wifi_pass(self, new_password):
        print("Invoking change_wifi_pass")
        payload = f"[LAN_WLAN#1,1,0,0,0,0#0,0,0,0,0,0]0,5\r\nBeaconType=11i\r\nIEEE11iAuthenticationMode=PSKAuthentication\r\nIEEE11iEncryptionModes=AESEncryption\r\nX_TP_PreSharedKey={new_password}\r\nX_TP_GroupKeyUpdateInterval=0\r\n"
        post_url = self.referer + '/cgi?2'
        try:
            response = self.post_data(self.main_referer, post_url, payload)
            if '[error]0' in response.text: return True
        except Exception as e:
            print(f"It's okay, connection refused because no internet: {e}")
            # won't get the response back, because no connection to the router

    @staticmethod
    def format_target(target: Target, id: int, index: int):
        return f"[EXTERNAL_HOST#{id},0,0,0,0,0#0,0,0,0,0,0]{index},4\r\nentryName={target.name}\r\ntype=2\r\naddUrl=1\r\ntmpUrl={target.url}\r\n"

    @staticmethod
    def format_schedule(schedule: WeekSchedule):
        return Router.format_days(schedule.days_starting_sunday())

    @staticmethod
    def format_days(days):
        res = ""
        for schedule, day in days:
            value_0, value_1 = Router.compute_day_value(schedule)
            res += f"{day}Am={value_0}\r\n"
            res += f"{day}Pm={value_1}\r\n"
        return res

    @staticmethod
    def compute_day_value(day_schedule: DaySchedule):
        hours = list(map(lambda x: x.occupied, sorted(day_schedule.full)))
        values = []

        def unique_pos(idx):
            return 2 ** idx

        for index, hour in enumerate(hours):
            half_index = (index * 2) % 24
            if hour & HourSchedule.FIRST_HALF:
                values.append(unique_pos(half_index))
            else:
                values.append(0)

            if hour & HourSchedule.SECOND_HALF:
                values.append(unique_pos(half_index + 1))
            else:
                values.append(0)
        am = values[:24]
        pm = values[24:48]
        return sum(am), sum(pm)


sched = WeekSchedule.parse(""
                           "2,2,2,2, 2,2,2,2, 2,2,2,2,     2,2,2,2, 2,2,2,2, 2,2,2,2\n"  # mon
                           "1,1,1,1, 1,1,1,1, 1,1,1,1,     1,1,1,1, 1,1,1,1, 1,1,1,1\n"  # tue
                           "2,2,2,2, 2,2,2,2, 2,2,2,2,     2,2,2,2, 2,2,2,2, 2,2,2,2\n"  # wed
                           "0,1,2,3, 0,1,2,3, 0,1,2,3,     0,1,2,3, 0,1,2,3, 0,1,2,3\n"  # thu
                           "0,0,0,0, 0,0,0,0, 0,0,0,0,     0,0,0,0, 0,0,0,0, 0,0,0,0\n"  # fri
                           "0,0,0,0, 3,3,3,3, 3,3,3,3,     0,0,0,0, 0,0,0,0, 0,0,0,0\n"  # sat
                           "0,0,0,0, 0,0,1,1, 0,1,1,1,     0,0,0,0, 0,0,0,0, 0,0,0,0\n")  # sun

router = Router("192.168.0.1", "admin", "admin")
# print(router.add_rule("new", "xiaomi", "Youtube", "S3", True, True))
# print(router.add_schedule("S15", sched))
# print(router.enable_access_control(True))
# router.add_host("new3", "10:6F:D9:A0:1C:D2")
# router.add_target(GroupedTarget("cgg", ["a", "b", "c", "d", "e", "f", "g", "i"]))
# router.change_pass("admin", "admin")
# print(router.get_rules())
# print(router.change_wifi_pass("*********"))
# router.enable_rule(11, True)
# router.delete_rule(11)
# print(router.get_schedules())
# print(router.get_hosts())

# print(router.get_targets())
# print(router.add_ip_target(IpTarget("tel","149.154.160.1", "149.154.175.1",1, 65534)))

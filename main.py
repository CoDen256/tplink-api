import os

from api import Router
from model import *

router_ip = "192.168.0.1"
username = "admin"
password = "admin"


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "r") as f:
        return "".join(f.readlines())


def delete_all_rules(router: Router):
    print("DELETING EVERYTHING FOR RULES")
    for rule in router.get_rules(False):
        print(f"Deleting rule {rule}")
        router.delete_rule(rule.id)

    for host_id, host in router.get_hosts(False):
        print(f"Deleting host {host} for {host_id}")
        router.delete_host(host_id)

    for (target_id, target) in router.get_targets(False):
        print(f"Deleting target {target} for {target_id}")
        router.delete_target(target_id)

    for (schedule_id, schedule) in router.get_schedules(False):
        print(f"Deleting schedule {schedule} for {schedule_id}")
        router.delete_schedule(schedule_id)


def load_all_rules(router: Router, config):
    print("LOADING CONFIG")
    hosts = Host.parse_hosts(read(f"{config}/hosts.txt"))
    rules = Rule.parse_rules(read(f"{config}/rules.txt"))
    schedules = WeekSchedule.parse_weeks(read(f"{config}/schedules.txt"))
    targets = GroupedTarget.parse_targets(read(f"{config}/targets.txt"))

    for host in hosts:
        print(f"Adding host {host}")
        router.add_host(host)

    for name, schedule in schedules:
        print(f"Adding schedule: {name}: {schedule}")
        router.add_schedule(name, schedule)

    for target in targets:
        print(f"Adding target {target}")
        router.add_target(target)

    for rule in rules:
        print(f"Adding rule {rule}")
        router.add_rule(rule)


def main():
    router = Router(router_ip, username, password)
    router.enable_access_control(True)
    # delete_all_rules(router)
    load_all_rules(router, "resources")

if __name__ == '__main__':
    main()

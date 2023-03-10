import re
from typing import List

from utils import check, iptonum, partition


class WeekSchedule:
    WEEK = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def __init__(self, days):
        if (len(days) != 7):
            raise AttributeError(f"Days should be 7 in a week, not {len(days)}")

        self.days = days

    def __repr__(self):
        return f"{self.days}"

    def __str__(self):
        return self.__repr__()

    def days_with_names(self):
        return [(x, WeekSchedule.WEEK[i]) for (i, x) in enumerate(self.days)]

    def days_starting_sunday(self):
        return self.days_with_names()[-1:] + self.days_with_names()[:-1]

    def replace(self, index, day_schedule):
        days = self.days[:]
        days[index] = day_schedule
        return WeekSchedule(days)

    def shift_half_hours(self, count, fill_occupied=0):
        return WeekSchedule([
            day.shift_half_hours(count, fill_occupied) for day in self.days
        ])

    @classmethod
    def parse(cls, string: str):
        days = []
        days_str = list(filter(lambda x: bool(x), string.split("\n")))
        for day in days_str:
            days.append(DaySchedule.parse(day))
        return WeekSchedule(days)

    @classmethod
    def parse_weeks(cls, string: str):
        if not string: return []
        weeks_names = []
        str = string.split("---")
        for s in str[1:]:
            split = s.split("\n", maxsplit=1)
            name = split[0]
            weeks_names.append((name, WeekSchedule.parse(split[1])))
        return weeks_names

    def __eq__(self, other):
        if isinstance(other, WeekSchedule):
            return self.days == other.days
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class DaySchedule:
    def __init__(self, hours):
        if (len(hours) > 24):
            raise AttributeError("Hours should be not more than 24")
        self.full: List[HourSchedule] = list(sorted(self.compute_full_day(hours)))

    def shift_half_hours(self, count, fill_rest_occupied=0):
        if (fill_rest_occupied > count): raise AttributeError("Fill rest count should be less than count")
        result = []
        half_hours = [(bool(h.occupied & h.FIRST_HALF), bool(h.occupied & h.SECOND_HALF)) for h in self.full]
        flat_hours = [hour for pair in half_hours for hour in pair]
        shifted = ([True] * fill_rest_occupied + [False] * (count - fill_rest_occupied) + flat_hours)[:48]
        for i, pair in enumerate(partition(shifted, 2)):
            (first, second) = pair
            result.append(HourSchedule(i, first + (second << 1)))
        return DaySchedule(result)

    @staticmethod
    def compute_full_day(hours):
        full: List[HourSchedule] = hours[:]
        hours_known = set(map(lambda x: x.hour_of_day, full))
        if (len(hours_known) < len(full)):
            raise AttributeError("Hours should not repeat")
        for hour in range(24):
            if hour not in hours_known:
                full.append(HourSchedule(hour, HourSchedule.EMPTY))
        return full
    def replace(self, hour_schedule):
        hours = self.full[:]
        for i, hour in enumerate(hours):
            if hour.hour_of_day == hour_schedule.hour_of_day:
                hours[i] = hour_schedule
        return DaySchedule(hours)
    def __eq__(self, other):
        if isinstance(other, DaySchedule):
            return self.full == other.full
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    # "0,1,2,3, 0,1,2,3, 0,1,2,3,     0,1,2,3, 0,1,2,3, 0,1,2,3"
    @classmethod
    def parse(cls, string: str):
        split = re.split("\D*,\D*", string)
        res = []
        for i in range(24):
            res.append(HourSchedule(i, int(split[i])))
        return DaySchedule(res)

    def __repr__(self):
        return f"{list(filter(lambda x: x.occupied != 0, self.full))}"

    def __str__(self):
        return self.__repr__()


class HourSchedule:
    EMPTY = 0
    FIRST_HALF = 1
    SECOND_HALF = 2
    FULL = 3

    def __repr__(self):
        return f"{self.hour_of_day}:00({self.occupied})"

    def __str__(self):
        return self.__repr__()

    def __init__(self, hour_of_day, occupied=3):
        if hour_of_day >= 24 or hour_of_day < 0:
            raise AttributeError("Hour should be between 0 and 23")
        if occupied >= 4 or occupied < 0:
            raise AttributeError("Occupied should be between 0 and 3")
        self.hour_of_day = hour_of_day
        self.occupied = occupied

    def __lt__(self, other):
        return self.hour_of_day < other.hour_of_day

    def __gt__(self, other):
        return not self.__lt__(other)

    def __eq__(self, other):
        if isinstance(other, HourSchedule):
            return self.hour_of_day == other.hour_of_day and \
                self.occupied == other.occupied
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class Host:
    def __init__(self, name, mac):
        self.name = check(name, str, "name")
        self.mac = check(mac, str, "mac")
        if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
            print(f"Invalid mac address: {mac}")

    def __eq__(self, other):
        if isinstance(other, Host):
            return self.name == other.name and \
                self.mac == other.mac
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    @classmethod
    def parse_host(cls, str):
        name, mac = tuple(list(str.split("=")))
        return Host(name, mac)

    @classmethod
    def parse_hosts(cls, str):
        if not str: return []

        hosts = re.split("\r?\n", str)
        return [Host.parse_host(s) for s in hosts]


class IpTarget:
    def __init__(self, name, ipStart, ipEnd, portStart, portEnd):
        self.name = check(name, str, "name")
        self.ipStart = check(ipStart, str, "ipStart")
        self.ipEnd = check(ipEnd, str, "ipEnd")
        self.portStart = check(portStart, int, "portStart")
        self.portEnd = check(portEnd, int, "portEnd")
        if (portStart <= 0 or portStart > 65534 or portEnd <= 0 or portEnd > 65534):
            raise AttributeError(f"port should be between 1 and 65534, but was :{portStart}-{portEnd}")
        if (portStart > portEnd):
            raise AttributeError(f"Port start should be less than port end, but was: {portStart} - {portEnd}")

    def __str__(self):
        return f"{self.name}[{self.ipStart} {self.ipEnd}][{self.portStart}-{self.portEnd}]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, IpTarget):
            return self.name == other.name and \
                self.ipStart == other.ipStart and \
                self.ipEnd == other.ipEnd and \
                self.portEnd == other.portEnd and \
                self.portStart == other.portStart
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    @classmethod
    def parse_target(cls, str):
        name, rest = tuple(list(str.split("=")))
        start, end, port_start, port_end = tuple(list(rest.split(",")))
        return IpTarget(name, start, end, int(port_start), int(port_end))

    @classmethod
    def parse_targets(cls, str):
        if not str: return []

        targets = re.split("\r?\n", str)
        return [IpTarget.parse_target(s) for s in targets]

    def intStart(self):
        return iptonum(self.ipStart)

    def intEnd(self):
        return iptonum(self.ipEnd)


class GroupedTarget:
    def __init__(self, name, urls):
        if not urls: raise AttributeError("GroupedTarget.urls must not be empty")
        self.urls = urls
        self.name = name

    def targets(self):
        return [Target(self.name, url) for url in self.urls]

    def first(self):
        return Target(self.name, self.urls[0])

    def targets_omit_first(self):
        return self.targets()[1:]

    def __str__(self):
        return f"{self.name}{self.urls}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, GroupedTarget):
            return self.name == other.name and \
                self.urls == other.urls
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    @classmethod
    def parse_target(cls, str):
        name, urls = tuple(list(str.split("=")))
        return GroupedTarget(name, urls.split(","))

    @classmethod
    def parse_targets(cls, str):
        if not str: return []

        targets = re.split("\r?\n", str)
        return [GroupedTarget.parse_target(s) for s in targets]


class Target:
    def __init__(self, name, url):
        if not url: raise AttributeError("Target.url must not be empty")
        self.url = url
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Target):
            return self.name == other.name and \
                self.url == other.url
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class Rule:
    def __init__(self, name: str, host: str, target: str, schedule: str, deny: bool, enable: bool, id: int = 0,
                 parent_ctrl: bool = False):
        self.name = check(name, str, "name")
        self.host = check(host, str, "host")
        self.target = check(target, str, "schedule")
        self.schedule = check(schedule, str, "schedule")
        self.deny = check(deny, bool, "deny")
        self.enable = check(enable, bool, "enable")
        self.id = check(id, int, "id")
        self.parent_ctrl = check(parent_ctrl, bool, "parent_ctrl")

    def __str__(self):
        return f"{self.name}({self.id})({self.host} -> {self.target}|{self.schedule}) [{self.deny}, {self.enable}, {self.parent_ctrl}]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Rule):
            return self.name == other.name and \
                self.host == other.host and \
                self.target == other.target and \
                self.schedule == other.schedule and \
                self.deny == other.deny and \
                self.enable == other.enable and \
                self.id == other.id and \
                self.parent_ctrl == other.parent_ctrl
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    @classmethod
    def parse_rule(cls, str):
        name, params = tuple(list(str.split("=")))
        (host, target, schedule, deny, enable) = tuple(list(params.split(",")))
        deny = bool(int(deny))
        enable = bool(int(enable))
        return Rule(name, host, target, schedule, deny, enable)

    @classmethod
    def parse_rules(cls, str):
        if not str: return []
        targets = re.split("\r?\n", str)
        return [Rule.parse_rule(s) for s in targets]

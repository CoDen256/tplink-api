import re
from typing import List


class WeekSchedule:
    WEEK = ["mon","tue","wed","thu","fri","sat", "sun"]
    def __init__(self, days):
        if (len(days) != 7):
            raise AttributeError(f"Days should be 7 in a week, not {len(days)}")

        self.days = days

    def days_with_names(self):
        return [(x, WeekSchedule.WEEK[i]) for (i, x) in enumerate(self.days)]

    def days_starting_sunday(self):
        return self.days_with_names()[-1:] + self.days_with_names()[:-1]

    @classmethod
    def parse(cls, string: str):
        days = []
        days_str = list(filter(lambda x: bool(x), string.split("\n")))
        for day in days_str:
            days.append(DaySchedule.parse(day))
        return WeekSchedule(days)

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

    @staticmethod
    def compute_full_day(hours):
        full: List[HourSchedule] = hours[:]
        hours_known = set(map(lambda x: x.hour_of_day, full))
        if (len(hours_known) < len(full)):
            raise AttributeError("Hours should not repeat itself")
        for hour in range(24):
            if hour not in hours_known:
                full.append(HourSchedule(hour, HourSchedule.EMPTY))
        return full

    def __eq__(self, other):
        if isinstance(other, DaySchedule):
            return self.full == other.full
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    "0,1,2,3, 0,1,2,3, 0,1,2,3,     0,1,2,3, 0,1,2,3, 0,1,2,3"
    @classmethod
    def parse(cls, string: str):
        split = re.split("\D*,\D*", string)
        res = []
        for i in range(24):
            res.append(HourSchedule(i, int(split[i])))
        return DaySchedule(res)
    def __repr__(self):
        return f"{list(filter(lambda x: x.occupied != 0, self.full))}"

    def __str__(self):return self.__repr__()
class HourSchedule:
    EMPTY = 0
    FIRST_HALF = 1
    SECOND_HALF = 2
    FULL = 3

    def __repr__(self):
        return f"{self.hour_of_day}:00({self.occupied})"

    def __str__(self):return self.__repr__()

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

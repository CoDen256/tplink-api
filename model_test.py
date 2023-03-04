import unittest
from model import *


def inc(schedule: List[HourSchedule], factor=1, start=0):
    res = []
    for (i, s) in enumerate(schedule):
        res.append(HourSchedule(start + i * factor, s.occupied))
    return res


class MyTestCase(unittest.TestCase):

    def test_week(self):
        sched = WeekSchedule.parse(""
                                   "2,2,2,2, 2,2,2,2, 2,2,2,2,     2,2,2,2, 2,2,2,2, 2,2,2,2\n"
                                   "1,1,1,1, 1,1,1,1, 1,1,1,1,     1,1,1,1, 1,1,1,1, 1,1,1,1\n"
                                   "2,2,2,2, 2,2,2,2, 2,2,2,2,     2,2,2,2, 2,2,2,2, 2,2,2,2\n"
                                   "0,1,2,3, 0,1,2,3, 0,1,2,3,     0,1,2,3, 0,1,2,3, 0,1,2,3\n"
                                   "0,0,0,0, 0,0,0,0, 0,0,0,0,     0,0,0,0, 0,0,0,0, 0,0,0,0\n"
                                   "0,0,0,0, 3,3,3,3, 3,3,3,3,     0,0,0,0, 0,0,0,0, 0,0,0,0\n"
                                   "0,0,0,0, 0,0,0,0, 0,0,0,0,     0,0,0,0, 0,0,0,0, 0,0,0,0\n")
        self.assertEquals(sched, WeekSchedule(
            [DaySchedule(inc([HourSchedule(0, 2)] * 24)),
             DaySchedule(inc([HourSchedule(0, 1)] * 24)),
             DaySchedule(inc([HourSchedule(0, 2)] * 24)),
             DaySchedule(
                 inc([HourSchedule(0, 0)] * 6, 4, 0) +
                 inc([HourSchedule(0, 1)] * 6, 4, 1) +
                 inc([HourSchedule(0, 2)] * 6, 4, 2) +
                 inc([HourSchedule(0, 3)] * 6, 4, 3)),
             DaySchedule([]),
             DaySchedule(inc([HourSchedule(0, 3)] * 8, start=4)),
             DaySchedule([])
             ]
        ))

    def test_parse_day(self):
        self.assertEquals(DaySchedule.parse("0,1,2,3, 0,1,2,3, 0,1,2,3,     0,1,2,3, 0,1,2,3, 0,1,2,3"),
                          DaySchedule(
                              inc([HourSchedule(0, 0)] * 6, 4, 0) +
                              inc([HourSchedule(0, 1)] * 6, 4, 1) +
                              inc([HourSchedule(0, 2)] * 6, 4, 2) +
                              inc([HourSchedule(0, 3)] * 6, 4, 3))
                          )

    def test_neq_weeks(self):
        self.assertNotEquals(WeekSchedule([
            DaySchedule([HourSchedule(1)]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
            DaySchedule([]),
        ]), WeekSchedule([
            DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
        ])
        )

        self.assertNotEquals(WeekSchedule([
            DaySchedule([HourSchedule(1)]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
            DaySchedule([]),
        ]), WeekSchedule([
            DaySchedule([]), DaySchedule([]), DaySchedule([HourSchedule(1)]), DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
            DaySchedule([]),
        ])
        )

    def test_eq_weeks(self):
        self.assertEquals(WeekSchedule([
            DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
        ]), WeekSchedule([
            DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
        ])
        )

        self.assertEquals(WeekSchedule([
            DaySchedule([HourSchedule(0, 0)]), DaySchedule([HourSchedule(2, 3)]), DaySchedule([]), DaySchedule([]),
            DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
        ]), WeekSchedule([
            DaySchedule([]), DaySchedule([HourSchedule(2)]), DaySchedule([HourSchedule(0, 0)]), DaySchedule([]),
            DaySchedule([]), DaySchedule([]),
            DaySchedule([]),
        ])
        )

    def test_day_to_much(self):
        with self.assertRaises(AttributeError):
            DaySchedule([HourSchedule(0)] * 25)

    def test_day_repeated(self):
        with self.assertRaises(AttributeError):
            DaySchedule([HourSchedule(0), HourSchedule(0)])

    def test_full_days(self):
        self.assertEquals(DaySchedule([
            HourSchedule(0), HourSchedule(1), HourSchedule(23),
            HourSchedule(2, 0), HourSchedule(22, 0), HourSchedule(21, 0)
        ]), DaySchedule([
            HourSchedule(0), HourSchedule(1), HourSchedule(23)
        ]))

    def test_day(self):
        self.assertEquals(DaySchedule([
            HourSchedule(0), HourSchedule(1), HourSchedule(23)
        ]), DaySchedule([
            HourSchedule(0), HourSchedule(1), HourSchedule(23)
        ]))

    def test_day_ne(self):
        self.assertNotEquals(DaySchedule([
            HourSchedule(0), HourSchedule(1), HourSchedule(23)
        ]), DaySchedule([
            HourSchedule(0), HourSchedule(1), HourSchedule(23, 2)
        ]))

    def test_hour_equal(self):
        self.assertEquals(HourSchedule(0), HourSchedule(0))

    def test_hour_notequal(self):
        self.assertNotEquals(HourSchedule(0), HourSchedule(1))

    def test_hour_error(self):
        with self.assertRaises(AttributeError):
            HourSchedule(24)
        with self.assertRaises(AttributeError):
            HourSchedule(23, 4)
        with self.assertRaises(AttributeError):
            HourSchedule(23, -1)
        with self.assertRaises(AttributeError):
            HourSchedule(-1, 0)
        with self.assertRaises(AttributeError):
            HourSchedule(25, 2)


if __name__ == '__main__':
    unittest.main()

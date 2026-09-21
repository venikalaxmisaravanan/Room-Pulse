"""Hand-written prototype data for RoomPulse.

Everything in this file is written by hand and deterministic: seeding twice
produces exactly the same database. No randomness, no generated bulk data.

The catalogue holds 9 rooms across 3 buildings with clearly different types,
capacities (20-120 seats) and 29 timetable slots spread over Monday-Saturday.

The *gaps* matter as much as the bookings, because later stages need something
to demonstrate:

- Rooms with free windows (for example EN-101 is only used Monday morning and
  Friday midday) so AVAILABLE can appear next to IN_CLASS.
- Overlapping sessions in different rooms at the same time, and rooms that stay
  free all day (BS-104 has nothing on Tuesday or Thursday).
- A Saturday workshop, plus an evening seminar, so occupancy and timetable
  sources can visibly disagree once the engine exists.

Nothing here decides availability: the timetable is only one input.
"""


def slot(day: str, start: str, end: str, course: str) -> dict[str, str]:
    """Small helper so the dataset below stays readable and consistent."""
    return {
        "day_of_week": day,
        "start_time": start,
        "end_time": end,
        "course_name": course,
    }


ROOMS: list[dict] = [
    # ------------------------------------------------- Engineering Block -----
    {
        "code": "EN-101",
        "name": "Lecture Hall EN-101",
        "building": "Engineering Block",
        "room_type": "Classroom",
        "capacity": 80,
        "timetable": [
            slot("Monday", "08:00", "09:30", "Discrete Mathematics (MATH201)"),
            slot("Wednesday", "08:00", "09:30", "Discrete Mathematics (MATH201)"),
            slot("Friday", "11:30", "13:00", "Engineering Physics (PHY110)"),
        ],
    },
    {
        "code": "EN-102",
        "name": "Tutorial Room EN-102",
        "building": "Engineering Block",
        "room_type": "Classroom",
        "capacity": 40,
        "timetable": [
            slot("Tuesday", "09:45", "11:15", "Linear Algebra (MATH204)"),
            slot("Thursday", "09:45", "11:15", "Linear Algebra (MATH204)"),
            slot("Friday", "14:00", "15:30", "Technical Writing (ENG105)"),
        ],
    },
    {
        "code": "EN-L1",
        "name": "Computer Laboratory L1",
        "building": "Engineering Block",
        "room_type": "Computer Laboratory",
        "capacity": 35,
        "timetable": [
            slot("Monday", "09:45", "11:15", "Programming Fundamentals (CS101)"),
            slot("Tuesday", "14:00", "15:30", "Programming Lab (CS101L)"),
            slot("Thursday", "11:30", "13:00", "Databases Lab (CS210L)"),
            slot("Saturday", "10:00", "12:00", "Weekend Coding Workshop (CS-OPEN)"),
        ],
    },
    # ----------------------------------------------------- Science Block -----
    {
        "code": "SC-115",
        "name": "Lecture Hall SC-115",
        "building": "Science Block",
        "room_type": "Classroom",
        "capacity": 90,
        "timetable": [
            slot("Monday", "14:00", "15:30", "Organic Chemistry (CHEM201)"),
            slot("Wednesday", "11:30", "13:00", "Organic Chemistry (CHEM201)"),
            slot("Thursday", "08:00", "09:30", "Cell Biology (BIO120)"),
        ],
    },
    {
        "code": "SC-210",
        "name": "Seminar Room SC-210",
        "building": "Science Block",
        "room_type": "Seminar Room",
        "capacity": 25,
        "timetable": [
            slot("Monday", "11:00", "13:00", "Research Methods Seminar (SCI300)"),
            slot("Wednesday", "14:00", "15:30", "Research Methods Seminar (SCI300)"),
            slot("Friday", "09:45", "11:15", "Academic Skills (SCI101)"),
        ],
    },
    {
        "code": "SC-L2",
        "name": "Electronics Laboratory L2",
        "building": "Science Block",
        "room_type": "Electronics Laboratory",
        "capacity": 30,
        "timetable": [
            slot("Tuesday", "11:30", "13:00", "Digital Electronics Lab (ECE220L)"),
            slot("Thursday", "14:00", "15:30", "Microcontrollers Lab (ECE230L)"),
            slot("Friday", "08:00", "09:30", "Circuit Analysis Lab (ECE110L)"),
        ],
    },
    # ---------------------------------------------------- Business Block -----
    {
        "code": "BS-104",
        "name": "Lecture Hall BS-104",
        "building": "Business Block",
        "room_type": "Classroom",
        "capacity": 120,
        "timetable": [
            slot("Monday", "11:30", "13:00", "Introduction to Economics (ECO101)"),
            slot("Wednesday", "08:00", "09:30", "Introduction to Economics (ECO101)"),
            slot("Friday", "15:45", "17:15", "Business Statistics (BUS130)"),
        ],
    },
    {
        "code": "BS-301",
        "name": "Case Study Room BS-301",
        "building": "Business Block",
        "room_type": "Seminar Room",
        "capacity": 20,
        "timetable": [
            slot("Tuesday", "08:00", "09:30", "Marketing Strategy (BUS220)"),
            slot("Wednesday", "09:45", "11:15", "Organisational Behaviour (BUS215)"),
            slot("Thursday", "15:45", "17:15", "Entrepreneurship Seminar (BUS330)"),
            slot("Thursday", "18:00", "19:30", "Evening Case Clinic (BUS-OPEN)"),
        ],
    },
    {
        "code": "BS-L3",
        "name": "Computer Laboratory L3",
        "building": "Business Block",
        "room_type": "Computer Laboratory",
        "capacity": 45,
        "timetable": [
            slot("Monday", "15:45", "17:15", "Data Analytics Lab (BUS340L)"),
            slot("Tuesday", "09:45", "11:15", "Data Analytics Lab (BUS340L)"),
            slot("Wednesday", "15:45", "17:15", "Financial Modelling Lab (FIN310L)"),
        ],
    },
]
# people.py

# All instructors, deduped, role = DI

# To make someone inactive for a period
#         "inactive_periods": [
#            ("2026-02-01", "2026-03-30")
#       ]

PEOPLE = {
#
# Instructors
#
    "A MARVIN": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Instructor", "Lead Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-05-27", "2026-05-27"),
            ("2026-06-03", "2026-06-03")
        ]
    },

    "J KARRAN": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False
    },

    "K BATTY": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Instructor", "Tug Pilot", "Lead Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-04-01", "2026-05-05"),
            ("2026-06-17", "2026-06-18"),
            ("2026-06-27", "2026-06-28")
        ]
    },

    "D PYE": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Instructor", "Lead Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False
    },

    "G ALEXANDER": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Instructor", "Lead Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-04-19", "2026-04-20"),
            ("2026-05-31", "2026-06-01"),
            ("2026-06-14", "2026-06-15"),
            ("2026-06-28", "2026-06-29"),
            ("2026-07-05", "2026-07-06"),
            ("2026-07-12", "2026-07-13")
# not available 16th & 23rd August
        ]
    },

    "D BRADBROOK": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False
    },

    "M OAKEY": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
            "inactive_periods": [
            ("2026-03-13", "2026-03-22")
        ]
    },

    "A PEACOCK": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": True,
        "inactive_periods": [
            ("2026-04-04", "2026-04-04"),
            ("2026-04-05", "2026-04-05"),
            ("2026-04-11", "2026-04-11"),
            ("2026-04-12", "2026-04-12"),
            ("2026-04-18", "2026-04-18"),
            ("2026-04-26", "2026-04-26"),
            ("2026-05-02", "2026-05-02"),
            ("2026-05-09", "2026-05-09"),
            ("2026-05-10", "2026-05-10"),
            ("2026-05-17", "2026-05-17"),
            ("2026-05-24", "2026-05-24"),
            ("2026-05-31", "2026-05-31"),
            ("2026-06-06", "2026-06-06"),
            ("2026-06-07", "2026-06-07"),
            ("2026-06-14", "2026-06-14"),
            ("2026-06-20", "2026-06-20"),
            ("2026-06-21", "2026-06-21"),
            ("2026-06-27", "2026-06-27"),
            ("2026-06-28", "2026-06-28")
        ]
    },

    "C STURDY": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
    },

    "P TOUGH": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-04-04", "2026-04-05"),
            ("2026-04-11", "2026-04-12"),
            ("2026-04-15", "2026-04-16"),
            ("2026-04-22", "2026-04-23"),
            ("2026-04-29", "2026-04-30"),
            ("2026-05-03", "2026-05-04"),
            ("2026-05-09", "2026-05-10"),
            ("2026-05-16", "2026-05-17"),
            ("2026-05-27", "2026-05-28"),
            ("2026-06-03", "2026-06-04"),
            ("2026-06-10", "2026-06-11"),
            ("2026-06-14", "2026-06-15"),
            ("2026-06-17", "2026-06-18"),
            ("2026-06-20", "2026-06-21"),
            ("2026-06-27", "2026-06-28")
        ]
    },

    # "A HOLLINGS": {
    #     "allowed_days": {"Sat", "Sun", "Wed"},
    #     "allowed_roles": {"Instructor"},
    #     "max_shifts_per_week": 1,
    #     "requires_snr_di": True,
    #     "inactive_periods": [
    #         ("2026-02-04", "2026-03-07"),
    #         ("2026-02-12", "2026-03-15"),
    #         ("2026-02-20", "2026-03-23"),
    #         ("2026-02-28", "2026-03-03"),
    #         ("2026-03-08", "2026-03-11"),
    #         ("2026-03-16", "2026-03-19"),
    #         ("2026-03-24", "2026-03-27"),
    #     ]
    # },

    "R KALIN": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Instructor", "Tug Pilot", "Lead Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-05-23", "2026-05-31"),
            ("2026-06-20", "2026-06-28"),
            ("2026-07-18", "2026-07-26")
        ]
    },

    "P NAYERI": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Instructor", "Tug Pilot", "Leed Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-02-01", "2026-03-17")
        ]
    },

#
# Tug Pilots
#
    "M BOND": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1
    },

    "D JOHNSTON": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-02-01", "2026-02-09")
        ]
    },

    "R HAMBLY": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-03-01", "2026-03-18"),
            ("2026-03-21", "2026-04-18"),
            ("2026-05-23", "2026-06-19"),
            ("2026-06-24", "2026-07-18"),
            ("2026-09-19", "2026-12-31")
        ]
    },

    "R BECK": {
        "allowed_days": {"Wed", "Sat"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-04-04", "2026-04-14"),
            ("2026-04-18", "2026-04-24"),
            ("2026-05-20", "2026-05-20"),
            ("2026-05-27", "2026-06-09")
        ]
    },

    "H MCDERMOTT-ROW": {
        "allowed_days": {"Wed", "Sat"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-04-19", "2026-04-23"),
            ("2026-05-17", "2026-05-23"),
            ("2026-06-04", "2026-06-06"),
            ("2026-06-15", "2026-06-19")
        ]
    },

    "R NUZA": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1
    },

    "K PROCTOR": {
        "allowed_days": {"Wed", "Sat"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1
    },

#
# BI/IFPs
#
    "M BLADES": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"BI/IFP"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-03-13", "2026-03-16"),
            ("2026-03-27", "2026-03-29"),
            ("2026-05-23", "2026-05-23")
        ]
    },

       "J FELAKOWSKI": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"BI/IFP"},
        "max_shifts_per_week": 1
    },

       "R WADDINGTON": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"BI/IFP"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-06-21", "2026-06-21"),
            ("2026-06-28", "2026-06-28"),
            ("2026-07-19", "2026-07-19"),
            ("2026-08-09", "2026-08-09"),
            ("2026-08-16", "2026-08-16")
        ]
    },

       "T PAVIS": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"BI/IFP", "Tug Pilot"},
        "max_shifts_per_week": 1
    },
#
# LPSs
#
    "P HUBER": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-05-30", "2026-05-31"),
            ("2026-06-06", "2026-06-07"),
            ("2026-06-13", "2026-06-14"),
            ("2026-06-20", "2026-06-21"),
            ("2026-06-27", "2026-06-28")
        ]
#  not avail 18/19 July
    },
    
    "A SPRAY": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "R WALSH": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "R STEMBROWICZ": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "M PERRIER": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "A CARDEN": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Duty Pilot", "LPS"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-04-04", "2026-04-05")
        ]
    },

    "H SOUTHWORTH": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "P ARTHUR": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS", "Duty Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-06-26", "2026-07-05"),
            ("2026-07-19", "2026-07-19")
        ]
    },

    "A HANKIN": {
        "allowed_days": {"Wed", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "S HAWKIN": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "M LENCH": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "D HAWKINS": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "R ROWNTREE": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
          ("2026-04-01", "2026-04-01"),
          ("2026-05-20", "2026-05-20"),
          ("2026-05-27", "2026-05-27"),
          ("2026-06-03", "2026-06-03"),
          ("2026-06-10", "2026-06-10")
        ]
    },

    "K MALONE": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-07-01", "2026-07-31")
        ]
    },

    "C THRUSH": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },
#
# Duty Pilots
#
    "M DOWLING": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-04-13", "2026-05-31")
        ]
    },

    "J DAY": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "J EMSLEY": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "S CAREY": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "E CAREY": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "R CARTER": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "T CHEN": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "A FREESTONE": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "R BAMFORD": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    # "R DONNELLY": {
    #     "allowed_days": {"Wed"},
    #     "allowed_roles": {"Duty Pilot"},
    #     "max_shifts_per_week": 1
    # },

    "P TOMLINSON": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-05-24", "2026-05-25"),
            ("2026-05-31", "2026-06-01"),
            ("2026-06-21", "2026-06-22"),
            ("2026-06-28", "2026-06-29"),
            ("2026-07-19", "2026-07-20")
        ]
    },

    "J DAY": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "B DOUGLAS": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "C BALL": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "E ROBINSON": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "C LEPARD": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "J MASHEDER": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-05-09", "2026-05-16")
        ]
    },

    "C WHITE": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "A STOCKS": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-04-01", "2026-04-25"),
            ("2026-05-10", "2026-05-11"),
            ("2026-05-16", "2026-05-17")
        ]
    },

    "G DUNN": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },
}

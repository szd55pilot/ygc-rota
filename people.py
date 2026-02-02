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
        "requires_snr_di": False
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
            ("2026-02-17", "2026-05-03")
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
            ("2026-02-01", "2026-02-02"),
            ("2026-02-22", "2026-02-23"),
            ("2026-03-08", "2026-03-09")
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
        "requires_snr_di": True
    },

    "C STURDY": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-02-17", "2026-02-19")
        ]
    },

    "P TOUGH": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False
    },

    "A HOLLINGS": {
        "allowed_days": {"Sat", "Sun", "Wed"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": True,
        "inactive_periods": [
            ("2026-02-04", "2026-03-07"),
            ("2026-02-12", "2026-03-15"),
            ("2026-02-20", "2026-03-23"),
            ("2026-02-28", "2026-03-03"),
            ("2026-03-08", "2026-03-11"),
            ("2026-03-16", "2026-03-19"),
            ("2026-03-24", "2026-03-27"),
        ]
    },

    "R KALIN": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Instructor", "Tug Pilot", "Lead Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-02-01", "2026-03-17")
        ]
    },

        "P NAYERI": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Instructor", "Tug Pilot"},
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
        "allowed_days": {"Wed", "Sat", "Sun"},
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
            ("2026-03-01", "2026-03-18")
        ]
    },

    "R BECK": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1
    },

    "H MCDERMOTT-ROW": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Tug Pilot"},
        "max_shifts_per_week": 1
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
            ("2026-03-27", "2026-03-29")
        ]
    },

       "J FELAKOWSKI": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"BI/IFP"},
        "max_shifts_per_week": 1
    },

       "R WADDINGTON": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"BI/IFP"},
        "max_shifts_per_week": 1
    },

       "T PAVIS": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"BI/IFP"},
        "max_shifts_per_week": 1
    },
#
# LPSs
#
    "P HUBER": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },
    
    "A SPRAY": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-02-01", "2026-02-27")
        ] 
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
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-02-06", "2026-02-15")
        ]
    },

    "H SOUTHWORTH": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

    "P ARTHUR": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
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
          ("2026-02-17", "2026-02-19")
        ]
    },

    "K MALONE": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"LPS"},
        "max_shifts_per_week": 1
    },

#
# Duty Pilots
#
    "M DOWLING": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
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

    "C THRUSH": {
        "allowed_days": {"Wed", "Sat", "Sun"},
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

    "R DONNELLY": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "P TOMLINSON": {
        "allowed_days": {"Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1,
        "inactive_periods": [
            ("2026-02-21", "2026-02-23")
        ]
    },

    "MAX SIU": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
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
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "J MASHEDER": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "C WHITE": {
        "allowed_days": {"Sat"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "A STOCKS": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

    "G DUNN": {
        "allowed_days": {"Sat", "Sun"},
        "allowed_roles": {"Duty Pilot"},
        "max_shifts_per_week": 1
    },

}

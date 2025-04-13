from datetime import datetime, timedelta
import pandas as pd
from subject import subjects_info

# Date range
start_date = pd.to_datetime("2025-01-01")
end_date = pd.to_datetime("2026-03-31")

# Holidays
national_holidays = [
    ("2025-05-01", "Labor Day"),
    ("2025-06-15", "Republic Day")
]

state_holidays = [
    ("2025-05-27", "State Foundation Day")
]

school_holidays = [
    ("2025-06-10", "School Sports Day"),
    ("2025-06-11", "Staff Meeting")
]

# Events
school_events = [
    ("2025-05-25", "Annual Day"),
    ("2025-06-05", "Parent-Teacher Meeting")
]

# Summer vacation
midyear_vacation_start = pd.to_datetime("2025-10-31")
midyear_vacation_end = pd.to_datetime("2025-11-15")

# Assessments
unit_tests_1_start = pd.to_datetime("2025-07-20")
exams_1_start = pd.to_datetime("2025-10-20")
unit_tests_2_start = pd.to_datetime("2026-01-20")
exams_2_start = pd.to_datetime("2026-03-20")

subject_count = len(subjects_info.items())
unit_tests_1_end = unit_tests_1_start + timedelta(days=subject_count - 1)
unit_tests_2_end = unit_tests_2_start + timedelta(days=subject_count - 1)
exams_1_end = exams_1_start + timedelta(days=subject_count - 1)
exams_2_end = exams_2_start + timedelta(days=subject_count - 1)

unit_tests_1 = pd.date_range(start=unit_tests_1_start.normalize(), end=unit_tests_1_end.normalize(), freq='D')
unit_tests_2 = pd.date_range(start=unit_tests_2_start.normalize(), end=unit_tests_2_end.normalize(), freq='D')
exams_1 = pd.date_range(start=exams_1_start.normalize(), end=exams_1_end.normalize(), freq='D')
exams_2 = pd.date_range(start=exams_2_start.normalize(), end=exams_2_end.normalize(), freq='D')




# schedule_generator.py

import pandas as pd
import math
from datetime import datetime, timedelta
from schedule_config import *
from subject import subjects_info

class ScheduleGenerator:
    def __init__(self):
        self.vacation_dates = pd.date_range(start=midyear_vacation_start, end=midyear_vacation_end)
        self.unavailable_dates = self._get_unavailable_dates()
        self.valid_dates = self._get_valid_dates()
        self.sections = self._split_schedule_sections()
        self.schedule_df = self._create_schedule_dataframe()
        self._schedule_subjects()
        
    def _get_unavailable_dates(self):
        all_holidays = national_holidays + state_holidays + school_holidays + school_events
        holiday_dates = {pd.to_datetime(date) for date, _ in all_holidays}

        unit_tests_dates = {pd.to_datetime(date) for date in unit_tests_1.tolist() + unit_tests_2.tolist()}
        exams_dates = {pd.to_datetime(date) for date in exams_1.tolist() + exams_2.tolist()}

        return holiday_dates.union(unit_tests_dates).union(exams_dates).union(set(self.vacation_dates))
    
    def _get_valid_dates(self, week_days=6):
        full_range = pd.date_range(start=start_date, end=end_date, freq='D')
        allowed_weekdays = set(range(0, week_days))  # 0=Monday, ..., 6=Sunday
        return [
            date for date in full_range
            if date not in self.unavailable_dates and date.weekday() in allowed_weekdays
        ]

    def _split_schedule_sections(self):
        return {
            'section_1': [d for d in self.valid_dates if d < unit_tests_1_start],
            'section_2': [d for d in self.valid_dates if unit_tests_1_end < d < exams_1_start],
            'section_3': [d for d in self.valid_dates if self.vacation_dates[-1] < d < unit_tests_2_start],
            'section_4': [d for d in self.valid_dates if unit_tests_2_end < d < exams_2_start]
        }
    
    def _create_schedule_dataframe(self):
        schedule_df = pd.DataFrame(
            index=self.valid_dates,
            columns=[i for i in range(1, 8)]
        )
        schedule_df[:] = ''
        
        # Add assessments
        unit_tests_1_df = pd.DataFrame(
            index=pd.to_datetime([date for date in unit_tests_1]),
            columns=[i for i in range(1, 8)]
        )
        exams_1_df = pd.DataFrame(
            index=pd.to_datetime([date for date in exams_1]),
            columns=[i for i in range(1, 8)]
        )
        unit_tests_2_df = pd.DataFrame(
            index=pd.to_datetime([date for date in unit_tests_2]),
            columns=[i for i in range(1, 8)]
        )
        exams_2_df = pd.DataFrame(
            index=pd.to_datetime([date for date in exams_2]),
            columns=[i for i in range(1, 8)]
        )
        for i, (subject, _) in enumerate(subjects_info.items()):
            unit_tests_1_df.iloc[i, :] = 'unit_tests_1: ' + subject
            unit_tests_2_df.iloc[i, :] = 'unit_tests_2: ' + subject
            exams_1_df.iloc[i, :] = 'exams_1: ' + subject
            exams_2_df.iloc[i, :] = 'exams_2: ' + subject

        
        # Add events
        event_df = pd.DataFrame(
            index=pd.to_datetime([date for date, _ in school_events]),
            columns=[i for i in range(1, 8)]
        )
        event_df[:] = 'Event'
        
        # Add vacation
        vacation_df = pd.DataFrame(
            index=self.vacation_dates,
            columns=[i for i in range(1, 8)]
        )
        vacation_df[:] = 'Vacation'
        
        return pd.concat([schedule_df, event_df, vacation_df, unit_tests_1_df, exams_1_df, unit_tests_2_df, exams_2_df]).sort_index()
    
    def _schedule_subjects(self):
        for subject, sections_data in subjects_info.items():
            for section_name, section_dates in self.sections.items():
                if section_name in sections_data:
                    section_info = sections_data[section_name]
                    self._distribute_lessons(subject, section_dates, section_info)
    
    def _distribute_lessons(self, subject, section_dates, section_info):
        # Skip if no dates in this section
        if not section_dates:
            return
            
        # Collect all items to schedule
        items = []
        for lesson, periods in section_info['lessons']:
            items.extend([f"{subject}.{lesson} (Lesson)"] * math.ceil(periods))
        for practical, periods in section_info['practicals']:
            items.extend([f"{subject}.{practical} (Practical)"] * math.ceil(periods))
        for assignment, periods in section_info['assignments']:
            items.extend([f"{subject}.{assignment} (Assignment)"] * math.ceil(periods))
        
        # Skip if nothing to schedule
        if not items:
            return
        
        # Create all available slots (date + period)
        slots = []
        for date in section_dates:
            #for period in range(1, 8):
            period = 1
            slots.append((date, period))
        
        # Calculate spacing between items
        spacing = max(1, len(slots) // len(items))
        
        # Schedule items with equal spacing
        for i, item in enumerate(items):
            # Find next available slot starting from ideal position
            ideal_pos = i * spacing
            for pos in range(ideal_pos, len(slots)):
                date, period = slots[pos]
                date, period = self._get_available_slot(date, period)
                self.schedule_df.at[date, period] = item
                break
            else:
                print ('Could not got available slot')

    def _get_available_slot(self, date, period):
        dates = self.schedule_df.index[self.schedule_df.index.get_loc(date):]
        date_idx = 0

        while date_idx < len(dates):
            while period <= 7:
                if pd.isna(self.schedule_df.at[dates[date_idx], period]) or self.schedule_df.at[dates[date_idx], period] == '':
                    return (dates[date_idx], period)
                period += 1
            date_idx += 1
            period = 1  # Reset period for next date

        print('No available slot found')
        return (date, period)  # fallback, though it may be invalid
    
    def generate_schedule(self):
        return self.schedule_df

if __name__ == "__main__":
    generator = ScheduleGenerator()
    schedule = generator.generate_schedule()
    schedule.to_csv('detailed_schedule.csv')
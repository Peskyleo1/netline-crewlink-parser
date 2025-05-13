import re
import pandas as pd
from collections import defaultdict

def parse_schedule_from_txt(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().strip().splitlines()

    day_pattern = re.compile(r'^[A-Z][a-z]{2}\d{2}')
    daily_blocks = defaultdict(list)

    current_day = None
    for line in lines:
        if day_pattern.match(line):
            current_day = line.strip()
        if current_day:
            daily_blocks[current_day].append(line.strip())

    updated_data = []

    for day, lines in daily_blocks.items():
        first_line = lines[0]
        match = re.match(r'^([A-Z][a-z]{2})(\d{2})(?:\s+([A-Z/]+)(?:\s+([A-Z]{3}))?)?', first_line)
        if match:
            weekday, day_num, duty_type, duty_location = match.groups()
            date_str = f"{weekday}{day_num}"
        else:
            date_str, duty_type, duty_location = None, None, None

        check_in_time = None
        check_out_time = None
        check_in_airport = None
        check_out_airport = None
        hotel = None
        flight_time = duty_time = rest_time = None
        meals = []
        duty_flights = []

        for line in lines:
            if "C/I" in line:
                match = re.search(r'C/I\s+([A-Z]{3})\s+(\d{4})', line)
                if match:
                    check_in_airport, check_in_time = match.groups()
                    duty_type = "C/I"
            elif "C/O" in line:
                match = re.search(r'C/O\s+!?(\d{4})\s+([A-Z]{3})', line)
                if match:
                    check_out_time, check_out_airport = match.groups()
            elif re.match(r'^H\d+\s+[A-Z]{3}$', line):
                hotel = line
            elif line.startswith("[FT"):
                flight_time = re.search(r'\[FT\s+([\d:]+)\]', line).group(1)
            elif line.startswith("[DT"):
                duty_time = re.search(r'\[DT\s+([\d:]+)\]', line).group(1)
            elif line.startswith("[RT"):
                rest_time = re.search(r'\[RT\s+([\d:]+)\]', line).group(1)
            elif "meal" in line.lower():
                meals.append(line)
            elif line.startswith("AZ"):
                flight_match = re.match(
                    r'(AZ \d+)(?:\s+R)?\s+([A-Z]{3})\s+(\d{4})\s+!?(\d{4}(?:\+\d)?)\s+([A-Z]{3})\s+(\w+)',
                    line
                )
                if flight_match:
                    flight_number, dep_airport, dep_time, arr_time, arr_airport, aircraft = flight_match.groups()
                    duty_flights.append({
                        "Flight Number": flight_number,
                        "Departure Airport": dep_airport,
                        "Departure Time": dep_time,
                        "Arrival Time": arr_time,
                        "Arrival Airport": arr_airport,
                        "Aircraft": aircraft,
                        "Requested": "R" in line
                    })

        if not duty_flights:
            updated_data.append({
                "Date": date_str,
                "Weekday": weekday,
                "Day Number": day_num,
                "Duty Type": duty_type,
                "Duty Location": duty_location,
                "Check-In Airport": check_in_airport,
                "Check-In Time": check_in_time,
                "Check-Out Time": check_out_time,
                "Hotel": hotel,
                "Flight Number": None,
                "Departure Airport": None,
                "Departure Time": None,
                "Arrival Time": None,
                "Arrival Airport": None,
                "Aircraft": None,
                "Requested": None,
                "Flight Time": flight_time,
                "Duty Time": duty_time,
                "Rest Time": rest_time,
                "Meals": ", ".join(meals)
            })
        else:
            for flight in duty_flights:
                updated_data.append({
                    "Date": date_str,
                    "Weekday": weekday,
                    "Day Number": day_num,
                    "Duty Type": duty_type,
                    "Duty Location": duty_location,
                    "Check-In Airport": check_in_airport,
                    "Check-In Time": check_in_time,
                    "Check-Out Time": check_out_time,
                    "Hotel": hotel,
                    "Flight Number": flight["Flight Number"],
                    "Departure Airport": flight["Departure Airport"],
                    "Departure Time": flight["Departure Time"],
                    "Arrival Time": flight["Arrival Time"],
                    "Arrival Airport": flight["Arrival Airport"],
                    "Aircraft": flight["Aircraft"],
                    "Requested": flight["Requested"],
                    "Flight Time": flight_time,
                    "Duty Time": duty_time,
                    "Rest Time": rest_time,
                    "Meals": ", ".join(meals)
                })

    df = pd.DataFrame(updated_data)
    return df

if __name__ == "__main__":
    input_path = "combined_cleaned_roster.txt"  # Replace with your file path
    output_path = "parsed_schedule.csv"

    df = parse_schedule_from_txt(input_path)
    df.to_csv(output_path, index=False)
    print(f"CSV saved to {output_path}")

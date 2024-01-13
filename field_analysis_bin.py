import gtfs_realtime_pb2
import json
import os


def list_all_fields(vehicle_positions):
    all_fields = set()

    for vehicle in vehicle_positions:
        # Using reflection to get all field names
        for field in vehicle.DESCRIPTOR.fields:
            try:
                # For fields that support presence checking
                if vehicle.HasField(field.name):
                    all_fields.add(field.name)
            except ValueError:
                # For fields that do not support presence checking, like repeated fields or message fields
                if getattr(vehicle, field.name):
                    all_fields.add(field.name)

        # Checking nested fields in 'trip'
        if vehicle.HasField('trip'):
            for field in vehicle.trip.DESCRIPTOR.fields:
                try:
                    if vehicle.trip.HasField(field.name):
                        all_fields.add(f"trip.{field.name}")
                except ValueError:
                    if getattr(vehicle.trip, field.name):
                        all_fields.add(f"trip.{field.name}")

    return all_fields
def analyze_vehicle_positions(vehicle_positions, fields_to_analyze, enum_fields, exclude_unique_count):
    summary = {field: {"present": 0, "absent": 0, "unique_values": {}} for field in fields_to_analyze}

    for vehicle in vehicle_positions:
        for field in fields_to_analyze:
            is_nested = '.' in field
            field_parts = field.split('.') if is_nested else [field]
            field_obj = vehicle

            # Access nested fields
            for part in field_parts:
                field_obj = getattr(field_obj, part, None)
                if field_obj is None:
                    break

            # Check field presence and count unique values (if applicable)
            if field_obj is not None and not (isinstance(field_obj, str) and field_obj == ""):
                summary[field]["present"] += 1
                if field not in exclude_unique_count and isinstance(field_obj, int):  # For enumerated types
                    enum_value = field_obj
                    if field in enum_fields:
                        enum_value = enum_fields[field].Name(field_obj)
                    summary[field]["unique_values"][enum_value] = summary[field]["unique_values"].get(enum_value, 0) + 1
            else:
                summary[field]["absent"] += 1

    return summary

# Fields to analyze - will be dynamically populated
fields_to_analyze = []
enum_fields = {
    'current_status': gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus,
    'occupancy_status': gtfs_realtime_pb2.VehiclePosition.OccupancyStatus,
    'trip.schedule_relationship': gtfs_realtime_pb2.TripDescriptor.ScheduleRelationship
}
exclude_unique_count = ['current_stop_sequence', 'timestamp']

# Define the file path in a variable
file_path = 'gtfs_files/gtfsrt.bin'

# Load and parse GTFS Real-Time data
feed = gtfs_realtime_pb2.FeedMessage()
with open(file_path, 'rb') as f:
    feed.ParseFromString(f.read())

# Extract vehicle positions
vehicle_positions = [entity.vehicle for entity in feed.entity if entity.HasField('vehicle')]

# List all fields used in vehicle positions
fields_used = list_all_fields(vehicle_positions)
fields_to_analyze = list(fields_used)

# Output the fields used
print("Fields used in Vehicle Positions:")
for field in sorted(fields_used):
    print(f"  - {field}")

# Analyze the vehicle positions
analysis_results = analyze_vehicle_positions(vehicle_positions, fields_to_analyze, enum_fields, exclude_unique_count)

# Output the results
for field, data in analysis_results.items():
    print(f"Field: {field}")
    print(f"  Present: {data['present']}")
    print(f"  Absent: {data['absent']}")
    if data["unique_values"] and field not in exclude_unique_count:
        print(f"  Unique Values: {data['unique_values']}")
    print()

# File path for the title
title = file_path.replace('/', ' > ')  # Example: 'gtfs_files > gtfsrt.bin'

# Prepare data for charts
chart_data = {}
for field, data in analysis_results.items():
    if field in enum_fields and data["unique_values"]:
        # Enumerated field: use unique values for the pie chart
        chart_data[field] = {
            "labels": list(data["unique_values"].keys()),
            "data": list(data["unique_values"].values()),
            "counts": data["unique_values"]
        }
    else:
        # Non-enumerated field: use present and absent counts
        chart_data[field] = {
            "labels": ["Present", "Absent"],
            "data": [data["present"], data["absent"]],
            "counts": {"Present": data["present"], "Absent": data["absent"]}
        }

# Generate HTML content
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .chart-container {{
            display: inline-block;
            width: 300px; /* Adjust the width as needed */
        }}
        .chart-title {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>GTFS Analysis Report: {title}</h1>
    <h2>Fields Present</h2>
    <ul>
        {''.join([f'<li>{field}</li>' for field in fields_used])}
    </ul>
    <h2>Field Analysis</h2>
    <div style="display: flex; flex-wrap: wrap;">
        {''.join([f'<div class="chart-container"><h3 class="chart-title">{field} ({", ".join([f"{k}: {v}" for k, v in chart_data[field]["counts"].items()])})</h3><canvas id="{field}_chart"></canvas></div>' for field in chart_data.keys()])}
    </div>
    <script>
        const chartData = {json.dumps(chart_data)};
        window.onload = function() {{
            for (const [field, data] of Object.entries(chartData)) {{
                const ctx = document.getElementById(field + '_chart').getContext('2d');
                new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: data.labels,
                        datasets: [{{
                            data: data.data,
                            backgroundColor: ['green', 'red', 'blue', 'yellow', 'purple', 'orange'] // Add more colors if needed
                        }}]
                    }}
                }});
            }}
        }};
    </script>
</body>
</html>
"""

# Write the HTML file
with open("gtfs_analysis_report.html", "w") as file:
    file.write(html_content)

print("Report generated: gtfs_analysis_report.html")
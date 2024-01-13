import os
import requests
import gtfs_realtime_pb2
import datetime
import time
import json

def list_all_fields(vehicle_positions):
    all_fields = set()
    for vehicle in vehicle_positions:
        for field in vehicle.DESCRIPTOR.fields:
            try:
                if vehicle.HasField(field.name):
                    all_fields.add(field.name)
            except ValueError:
                if getattr(vehicle, field.name):
                    all_fields.add(field.name)
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
            for part in field_parts:
                field_obj = getattr(field_obj, part, None)
                if field_obj is None:
                    break
            if field_obj is not None and not (isinstance(field_obj, str) and field_obj == ""):
                summary[field]["present"] += 1
                if field not in exclude_unique_count and isinstance(field_obj, int):
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

def get_unix_timestamp_one_hour_ago():
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    return int(time.mktime(one_hour_ago.timetuple()))

api_key = os.environ.get('GTFS_API_KEY')
if not api_key:
    raise ValueError("API key not found. Set the GTFS_API_KEY environment variable.")

url = "https://data.bus-data.dft.gov.uk/api/v1/gtfsrtdatafeed/"
params = {
    'startTimeAfter': get_unix_timestamp_one_hour_ago(),
    'api_key': api_key
}

response = requests.get(url, params=params)

if response.status_code == 200:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    vehicle_positions = [entity.vehicle for entity in feed.entity if entity.HasField('vehicle')]
    fields_used = list_all_fields(vehicle_positions)
    fields_to_analyze = list(fields_used)
    analysis_results = analyze_vehicle_positions(vehicle_positions, fields_to_analyze, enum_fields, exclude_unique_count)

    # Use the URL as the title
    title = url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    # Include a timestamp in the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_analysis_report_{timestamp}.html"
    chart_data = {}
    for field, data in analysis_results.items():
        if field in enum_fields and data["unique_values"]:
            chart_data[field] = {
                "labels": list(data["unique_values"].keys()),
                "data": list(data["unique_values"].values()),
                "counts": data["unique_values"]
            }
        else:
            chart_data[field] = {
                "labels": ["Present", "Absent"],
                "data": [data["present"], data["absent"]],
                "counts": {"Present": data["present"], "Absent": data["absent"]}
            }

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .chart-container {{
                display: inline-block;
                width: 300px;
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
                                backgroundColor: ['green', 'red', 'blue', 'yellow', 'purple', 'orange']
                            }}]
                        }}
                    }});
                }}
            }};
        </script>
    </body>
    </html>
    """

    with open(filename, "w") as file:
        file.write(html_content)
    print(f"Report generated: {filename}")
else:
    print("Failed to fetch data:", response.status_code)

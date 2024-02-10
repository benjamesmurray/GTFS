import os
import requests
import gtfs_realtime_pb2
import datetime
import time
import pandas as pd
import json
from datetime import datetime, timedelta

def list_all_fields(message, prefix=''):
    all_fields = set()
    for field in message.DESCRIPTOR.fields:
        field_name = f"{prefix}.{field.name}" if prefix else field.name
        try:
            if message.HasField(field.name):
                if field.type == field.TYPE_MESSAGE and not field.label == field.LABEL_REPEATED:
                    sub_message = getattr(message, field.name)
                    sub_fields = list_all_fields(sub_message, field_name)
                    all_fields.update(sub_fields)
                else:
                    all_fields.add(field_name)
        except ValueError:
            if getattr(message, field.name) is not None:
                all_fields.add(field_name)
    return all_fields

def get_unix_timestamp_one_minute_ago():
    one_minute_ago = datetime.now() - timedelta(minutes=1)
    return int(time.mktime(one_minute_ago.timetuple()))
def get_unix_timestamp_one_hour_ago():
    one_hour_ago = datetime.now() - timedelta(hours=1)
    return int(time.mktime(one_hour_ago.timetuple()))

def get_unix_timestamp_one_week_ago():
    one_week_ago = datetime.now() - timedelta(days=7)
    return int(time.mktime(one_week_ago.timetuple()))


# Get API Key from Environment Variable
api_key = os.environ.get('GTFS_API_KEY')
if not api_key:
    raise ValueError("API key not found. Set the GTFS_API_KEY environment variable.")

# API Request
url = "https://data.bus-data.dft.gov.uk/api/v1/gtfsrtdatafeed/"
params = {
#    'startTimeAfter': get_unix_timestamp_one_hour_ago(),
#   'startTimeAfter' = get_unix_timestamp_one_minute_ago()
    'startTimeAfter': get_unix_timestamp_one_week_ago(),
    'api_key': api_key
}

response = requests.get(url, params=params)

# Check if response is OK
if response.status_code == 200:
    # Parse the response using the protobuf schema
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    all_vehicle_fields = set()
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vehicle_fields = list_all_fields(entity.vehicle)
            all_vehicle_fields.update(vehicle_fields)

    print("All possible fields:", all_vehicle_fields)
    # Prepare data for different formats
    vehicles_data = []

    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vehicle_info = {}


            # Function to recursively extract fields and their values
            def extract_fields(message, prefix=''):
                for field in message.DESCRIPTOR.fields:
                    field_name = f"{prefix}{field.name}" if prefix else field.name
                    # Check if field is a message and not repeated
                    if field.type == field.TYPE_MESSAGE and not field.label == field.LABEL_REPEATED:
                        sub_message = getattr(message, field.name)
                        extract_fields(sub_message, prefix=field_name + '_')
                    elif field.label == field.LABEL_REPEATED:
                        # Handle repeated fields by joining their string representations
                        repeated_values = getattr(message, field.name)
                        vehicle_info[field_name] = ', '.join([str(v) for v in repeated_values])
                    else:
                        # Directly assign non-message and non-repeated field values
                        vehicle_info[field_name] = getattr(message, field.name, None)


            # Extract fields from the vehicle message
            extract_fields(entity.vehicle)

            vehicles_data.append(vehicle_info)

    # Proceed with creating a DataFrame and saving to CSV as before
    df = pd.DataFrame(vehicles_data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save to CSV with timestamp in filename
    csv_filename = f'vehicle_positions_{timestamp}.csv'
    df.to_csv(csv_filename, index=False)
    print(f"Vehicle positions saved to '{csv_filename}'")


else:
    print("Failed to fetch data:", response.status_code)

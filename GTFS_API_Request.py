import os
import requests
import gtfs_realtime_pb2
import datetime
import time

def get_unix_timestamp_one_hour_ago():
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    return int(time.mktime(one_hour_ago.timetuple()))

# Get API Key from Environment Variable
api_key = os.environ.get('GTFS_API_KEY')
if not api_key:
    raise ValueError("API key not found. Set the GTFS_API_KEY environment variable.")

# API Request
url = "https://data.bus-data.dft.gov.uk/api/v1/gtfsrtdatafeed/"
params = {
    'startTimeAfter': get_unix_timestamp_one_hour_ago(),
    'api_key': api_key
}

response = requests.get(url, params=params)

# Check if response is OK
if response.status_code == 200:
    # Parse the response using the protobuf schema
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    # Save vehicle positions to a file
    with open('vehicle_positions.txt', 'w') as file:
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                file.write(str(entity.vehicle) + '\n')
    print("Vehicle positions saved to 'vehicle_positions.txt'")
else:
    print("Failed to fetch data:", response.status_code)

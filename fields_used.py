import gtfs_realtime_pb2

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

# Load and parse the GTFS Real-Time data
feed = gtfs_realtime_pb2.FeedMessage()
with open('gtfsrt.bin', 'rb') as f:
    feed.ParseFromString(f.read())

# Extract vehicle positions
vehicle_positions = [entity.vehicle for entity in feed.entity if entity.HasField('vehicle')]

# List all fields used in vehicle positions
fields_used = list_all_fields(vehicle_positions)

# Output the results
print("Fields used in Vehicle Positions:")
for field in sorted(fields_used):
    print(f"  - {field}")

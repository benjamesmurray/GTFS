import gtfs_realtime_pb2

def analyze_vehicle_positions(vehicle_positions):
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

# Fields to analyze
fields_to_analyze = [
    'current_status', 'current_stop_sequence', 'occupancy_status', 'position',
    'timestamp', 'trip', 'trip.route_id', 'trip.schedule_relationship',
    'trip.start_date', 'trip.start_time', 'trip.trip_id', 'vehicle'
]

# Enum fields and their types
enum_fields = {
    'current_status': gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus,
    'occupancy_status': gtfs_realtime_pb2.VehiclePosition.OccupancyStatus,
    'trip.schedule_relationship': gtfs_realtime_pb2.TripDescriptor.ScheduleRelationship
}

# Fields to exclude from unique value counting
exclude_unique_count = ['current_stop_sequence', 'timestamp']

# Load and parse GTFS Real-Time data
feed = gtfs_realtime_pb2.FeedMessage()
with open('gtfs_files/gtfsrt.bin', 'rb') as f:
    feed.ParseFromString(f.read())

# Extract vehicle positions and analyze
vehicle_positions = [entity.vehicle for entity in feed.entity if entity.HasField('vehicle')]
analysis_results = analyze_vehicle_positions(vehicle_positions)

# Output the results
for field, data in analysis_results.items():
    print(f"Field: {field}")
    print(f"  Present: {data['present']}")
    print(f"  Absent: {data['absent']}")
    if data["unique_values"] and field not in exclude_unique_count:
        print(f"  Unique Values: {data['unique_values']}")
    print()

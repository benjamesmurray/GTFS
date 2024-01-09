import gtfs_realtime_pb2

def print_entity_details(entity):
    for field in entity.DESCRIPTOR.fields:
        try:
            if entity.HasField(field.name):
                print(f"  {field.name}: {getattr(entity, field.name)}")
            elif field.label == field.LABEL_REPEATED:  # For repeated fields
                repeated_field = getattr(entity, field.name)
                if repeated_field:
                    print(f"  {field.name}: {repeated_field}")
        except ValueError:
            # For fields that do not support presence checking
            value = getattr(entity, field.name)
            if value is not None:
                print(f"  {field.name}: {value}")

# Function to print top 3 entities of a given type
def print_top_three(entities, entity_type):
    print(f"Top 3 {entity_type}:")
    for entity in entities[:3]:
        print_entity_details(entity)
        print()  # Add a new line for better readability

# Load and parse the GTFS Real-Time data
feed = gtfs_realtime_pb2.FeedMessage()
with open('gtfsrt.bin', 'rb') as f:
    feed.ParseFromString(f.read())

# Separating different types of data
trip_updates = [entity.trip_update for entity in feed.entity if entity.HasField('trip_update')]
vehicle_positions = [entity.vehicle for entity in feed.entity if entity.HasField('vehicle')]
service_alerts = [entity.alert for entity in feed.entity if entity.HasField('alert')]

# Count and print the results
print(f"Total Trip Updates: {len(trip_updates)}")
print(f"Total Vehicle Positions: {len(vehicle_positions)}")
print(f"Total Service Alerts: {len(service_alerts)}")

# Print the top 3 of each type
print_top_three(trip_updates, "Trip Updates")
print_top_three(vehicle_positions, "Vehicle Positions")
print_top_three(service_alerts, "Service Alerts")

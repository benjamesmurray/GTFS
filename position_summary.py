import gtfs_realtime_pb2

def count_vehicle_positions(vehicle_positions):
    total_count = len(vehicle_positions)
    both_count = 0
    only_trip_id_count = 0
    only_route_id_count = 0
    neither_count = 0

    for vehicle in vehicle_positions:
        has_trip_id = vehicle.trip.trip_id != ""
        has_route_id = vehicle.trip.route_id != ""

        if has_trip_id and has_route_id:
            both_count += 1
        elif has_trip_id and not has_route_id:
            only_trip_id_count += 1
        elif not has_trip_id and has_route_id:
            only_route_id_count += 1
        else:
            neither_count += 1

    return total_count, both_count, only_trip_id_count, only_route_id_count, neither_count

# Load and parse the GTFS Real-Time data
feed = gtfs_realtime_pb2.FeedMessage()
with open('gtfsrt.bin', 'rb') as f:
    feed.ParseFromString(f.read())

# Extract vehicle positions
vehicle_positions = [entity.vehicle for entity in feed.entity if entity.HasField('vehicle')]

# Count vehicle positions
total, both, only_trip, only_route, neither = count_vehicle_positions(vehicle_positions)

# Output the results
print(f"Total vehicle positions: {total}")
print(f"Vehicle positions with both a trip_id and route_id: {both}")
print(f"Vehicle positions with only a trip_id and no route_id: {only_trip}")
print(f"Vehicle positions with only a route_id and no trip_id: {only_route}")
print(f"Vehicle positions without either a trip_id or route_id: {neither}")

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import zipfile
import os


def create_db_and_tables(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Table creation statements
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agency (
        agency_id TEXT PRIMARY KEY,
        agency_name TEXT,
        agency_url TEXT,
        agency_timezone TEXT,
        agency_lang TEXT,
        agency_phone TEXT,
        agency_fare_url TEXT,
        agency_noc TEXT);
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stops (
        stop_id TEXT PRIMARY KEY,
        stop_code TEXT,
        stop_name TEXT,
        stop_desc TEXT,
        stop_lat TEXT,
        stop_lon TEXT,
        zone_id TEXT,
        stop_url TEXT,
        location_type INTEGER,
        parent_station TEXT,
        stop_timezone TEXT,
        wheelchair_boarding INTEGER,
        platform_code TEXT);
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS routes (
        route_id TEXT PRIMARY KEY,
        agency_id TEXT,
        route_short_name TEXT,
        route_long_name TEXT,
        route_desc TEXT,
        route_type INTEGER,
        route_url TEXT,
        route_color TEXT,
        route_text_color TEXT,
        FOREIGN KEY (agency_id) REFERENCES agency (agency_id));
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trips (
        route_id TEXT,
        service_id TEXT,
        trip_id TEXT PRIMARY KEY,
        trip_headsign TEXT,
        trip_short_name TEXT,
        direction_id INTEGER,
        block_id TEXT,
        shape_id TEXT,
        wheelchair_accessible INTEGER,
        bikes_allowed INTEGER,
        vehicle_journey_code TEXT, 
        FOREIGN KEY (route_id) REFERENCES routes (route_id));
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stop_times (
        trip_id TEXT,
        arrival_time TEXT,
        departure_time TEXT,
        stop_id TEXT,
        stop_sequence INTEGER,
        stop_headsign TEXT,
        pickup_type INTEGER,
        drop_off_type INTEGER,
        shape_dist_traveled REAL,
        timepoint INTEGER,  -- Added column for timepoint
        FOREIGN KEY (trip_id) REFERENCES trips (trip_id),
        FOREIGN KEY (stop_id) REFERENCES stops (stop_id));
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS calendar (
        service_id TEXT PRIMARY KEY,
        monday INTEGER,
        tuesday INTEGER,
        wednesday INTEGER,
        thursday INTEGER,
        friday INTEGER,
        saturday INTEGER,
        sunday INTEGER,
        start_date TEXT,
        end_date TEXT);
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS calendar_dates (
        service_id TEXT,
        date TEXT,
        exception_type INTEGER,
        FOREIGN KEY (service_id) REFERENCES calendar (service_id));
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shapes (
        shape_id TEXT,
        shape_pt_lat TEXT,
        shape_pt_lon TEXT,
        shape_pt_sequence INTEGER,
        shape_dist_traveled TEXT);
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feed_info (
        feed_publisher_name TEXT,
        feed_publisher_url TEXT,
        feed_lang TEXT,
        feed_start_date TEXT,
        feed_end_date TEXT,
        feed_version TEXT);
    ''')

    # Commit changes
    conn.commit()
    return conn


def load_gtfs_data(conn, zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("gtfs_data")

    base_path = "gtfs_data/"
    files = [
        ("agency.txt", "agency"),
        ("stops.txt", "stops"),
        ("routes.txt", "routes"),
        ("trips.txt", "trips"),
        ("stop_times.txt", "stop_times"),
        ("calendar.txt", "calendar"),
        ("calendar_dates.txt", "calendar_dates"),
        ("shapes.txt", "shapes"),
        ("feed_info.txt", "feed_info")
    ]

    for file_name, table_name in files:
        df = pd.read_csv(base_path + file_name)
        df.to_sql(table_name, conn, if_exists='append', index=False)

    # Clean up extracted files
    for root, dirs, files in os.walk(base_path):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(base_path)


from datetime import datetime, timedelta
import sqlite3

def populate_temp_dates(conn):
    cursor = conn.cursor()
    # Change from TEMP TABLE to a regular table
    cursor.execute("DROP TABLE IF EXISTS temp_dates;")
    cursor.execute("CREATE TABLE IF NOT EXISTS temp_dates (date TEXT);")

    for i in range(43):  # Today plus 42 days
        date = (datetime.now() + timedelta(days=i)).strftime('%Y%m%d')  # Matches the GTFS date format
        cursor.execute("INSERT INTO temp_dates (date) VALUES (?);", (date,))

    conn.commit()

    # Diagnostic: Check the count of dates inserted
    cursor.execute("SELECT COUNT(*) FROM temp_dates;")
    count = cursor.fetchone()[0]
    print(f"Inserted {count} rows into temp_dates.")

    # Diagnostic: Sample some dates inserted into temp_dates
    cursor.execute("SELECT date FROM temp_dates LIMIT 5;")
    sample_dates = cursor.fetchall()
    print("Sample dates in temp_dates:", sample_dates)


def create_day_specific_views(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT date FROM temp_dates;")
    dates = cursor.fetchall()

    for date_tuple in dates:
        date = date_tuple[0]
        view_name = f"upcoming_trips_view_{date}"

        cursor.execute(f'''
        CREATE VIEW IF NOT EXISTS {view_name} AS
        SELECT 
            '{date}' AS service_date,
            a.agency_id,
            r.route_id,
            t.trip_id
        FROM 
            calendar c
        JOIN 
            trips t ON c.service_id = t.service_id
        JOIN 
            routes r ON t.route_id = r.route_id
        JOIN 
            agency a ON r.agency_id = a.agency_id
        WHERE
            ('{date}' BETWEEN c.start_date AND c.end_date)
            AND CASE strftime('%w', date(substr('{date}', 1, 4) || '-' || substr('{date}', 5, 2) || '-' || substr('{date}', 7, 2)))
                WHEN '0' THEN c.sunday
                WHEN '1' THEN c.monday
                WHEN '2' THEN c.tuesday
                WHEN '3' THEN c.wednesday
                WHEN '4' THEN c.thursday
                WHEN '5' THEN c.friday
                WHEN '6' THEN c.saturday
            END = 1
        AND NOT EXISTS (
            SELECT 1 FROM calendar_dates cd WHERE cd.service_id = c.service_id AND cd.date = '{date}' AND cd.exception_type = 2
        )
        UNION
        SELECT 
            '{date}' AS service_date,
            a.agency_id,
            r.route_id,
            t.trip_id
        FROM 
            calendar_dates cd
        JOIN 
            trips t ON cd.service_id = t.service_id
        JOIN 
            routes r ON t.route_id = r.route_id
        JOIN 
            agency a ON r.agency_id = a.agency_id
        WHERE 
            cd.exception_type = 1 AND
            cd.date = '{date}';
        ''')
        print(f"Created view: {view_name}")

        # Diagnostic check for each view
        cursor.execute(f"SELECT COUNT(*) FROM {view_name};")
        view_count = cursor.fetchone()[0]
        print(f"{view_name} has {view_count} rows.")

    conn.commit()


def generate_db_schema_json(conn, db_name, sample_size=5):
    cursor = conn.cursor()
    cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view');")
    db_objects = cursor.fetchall()

    schema = {}

    for obj_name, obj_type in db_objects:
        cursor.execute(f"PRAGMA table_info({obj_name});")
        columns_info = cursor.fetchall()

        columns = [{"name": col[1], "type": col[2]} for col in columns_info]

        cursor.execute(f"SELECT * FROM {obj_name} LIMIT {sample_size};")
        sample_data = cursor.fetchall()

        schema[obj_name] = {
            "type": obj_type,
            "columns": columns,
            "sample_data": sample_data
        }

    with open(f'{db_name}_schema.json', 'w') as f:
        json.dump(schema, f, indent=4)

    print("Database schema JSON has been generated.")


def main(zip_path):
    db_name = f"gtfs_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    conn = create_db_and_tables(db_name)
    load_gtfs_data(conn, zip_path)
    populate_temp_dates(conn)  # Populate temporary table with the next 42 days
    create_day_specific_views(conn)  # Create the view considering both regular schedules and exceptions

    # Generate the JSON schema file
    generate_db_schema_json(conn, db_name)

    conn.close()
    print(f"Database {db_name} created successfully with GTFS data and specialized view and schema JSON.")


if __name__ == "__main__":
    zip_path = 'gtfs_files/itm_east_anglia_gtfs.zip'
    main(zip_path)
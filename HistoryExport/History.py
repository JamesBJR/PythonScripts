import os
import sqlite3
import shutil
import datetime

def export_edge_history(output_file="edge_history.txt"):
    # Define the path for the Edge history database
    user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
    history_path = os.path.join(user_profile, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "History")

    # Make a copy of the database because it might be locked by Edge
    temp_history_path = "temp_history"
    shutil.copy2(history_path, temp_history_path)

    # Connect to the copied database
    connection = sqlite3.connect(temp_history_path)
    cursor = connection.cursor()

    # Query to get URLs and visit times
    cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC")

    # Convert Edge's timestamp to a readable date
    def convert_time(edge_timestamp):
        epoch_start = datetime.datetime(1601, 1, 1)
        return epoch_start + datetime.timedelta(microseconds=edge_timestamp)

    # Open the output file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("URL, Title, Visit Count, Last Visit Time\n")
        for row in cursor.fetchall():
            url, title, visit_count, last_visit_time = row
            last_visit_time = convert_time(last_visit_time)
            file.write(f"{url}, {title}, {visit_count}, {last_visit_time}\n")

    # Close the database connection
    connection.close()
    os.remove(temp_history_path)
    print(f"History exported to {output_file}")

# Run the function
export_edge_history()

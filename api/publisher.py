# In: api/publisher.py

import zmq
import duckdb
import os
import pandas as pd
import json
import time

# --- Configuration ---
# Use the absolute path to ensure the db is found
PROJECT_ROOT = "/Users/joshuaveasy/O and L/jv-quant-research"
DB_FILE = os.path.join(PROJECT_ROOT, "asset_universe.duckdb")
ZMQ_PORT = "5556"
TOPIC = "UNIVERSE_TODAY"

def get_latest_candidates_as_json():
    """Connects to the database and returns the latest candidates as a JSON string."""
    try:
        con = duckdb.connect(database=DB_FILE, read_only=True)
        df = con.execute("SELECT * FROM candidates ORDER BY fit_score DESC").fetchdf()
        con.close()
        # Convert DataFrame to a list of dictionaries, then to a JSON string
        return df.to_json(orient='records')
    except Exception as e:
        print(f"Publisher Error: Could not read from database. {e}")
        return None

def run_publisher():
    """
    Initializes a ZMQ publisher and periodically broadcasts the latest
    asset universe on a specific topic.
    """
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{ZMQ_PORT}")
    print(f"ZMQ Publisher started. Broadcasting on tcp://*:{ZMQ_PORT}")
    print(f"Broadcasting topic: '{TOPIC}'")

    try:
        while True:
            # 1. Fetch the latest data
            candidates_json = get_latest_candidates_as_json()

            if candidates_json:
                # 2. Broadcast the data as a multipart message:
                #    - Frame 1: The topic (so subscribers can filter)
                #    - Frame 2: The actual JSON data payload
                print(f"Broadcasting update for topic '{TOPIC}'...")
                socket.send_string(TOPIC, zmq.SNDMORE)
                socket.send_json(candidates_json)
            else:
                print("No data to broadcast. Will try again in 60 seconds.")

            # 3. Wait before broadcasting again
            # In a real system, this would be triggered by the pipeline finishing
            time.sleep(60)

    except KeyboardInterrupt:
        print("\nPublisher shutting down.")
    finally:
        socket.close()
        context.term()

# --- To run this publisher directly ---
if __name__ == '__main__':
    run_publisher()

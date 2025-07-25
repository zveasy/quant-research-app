# In: api/publisher.py

import zmq
import duckdb
import os
import time

# --- Configuration ---
# Read database path from the environment with a fallback
DB_FILE = os.getenv("DB_PATH", "./asset_universe.duckdb")
ZMQ_PORT = "5556"
TOPIC = "UNIVERSE_TODAY"


def get_latest_candidates_as_json():
    """Connects to the database and returns the latest candidates as a JSON string."""
    try:
        con = duckdb.connect(database=DB_FILE, read_only=True)
        df = con.execute("SELECT * FROM candidates ORDER BY fit_score DESC").fetchdf()
        con.close()
        # Convert DataFrame to a list of dictionaries, then to a JSON string
        return df.to_json(orient="records")
    except Exception as e:
        print(f"Publisher Error: Could not read from database. {e}")
        return None


def run_publisher(stop_event=None, run_once: bool = False):
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
            # Sub-millisecond interval (0.5 ms)
            if run_once:
                break
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.0005)

    except KeyboardInterrupt:
        print("\nPublisher shutting down.")
    finally:
        socket.close()
        context.term()


# --- To run this publisher directly ---
if __name__ == "__main__":
    run_publisher()


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import zmq
import threading
import time
import json
from api import publisher

ZMQ_PORT = "5556"
TOPIC = "UNIVERSE_TODAY"

# Helper: Run the publisher in a thread so we can subscribe to it
class PublisherThread(threading.Thread):
    def __init__(self, stop_event):
        super().__init__()
        self.stop_event = stop_event

    def run(self):
        publisher.run_publisher(stop_event=self.stop_event)

# Test ZMQ subscriber
def test_zmq_publisher_broadcast(monkeypatch):
    # Patch get_latest_candidates_as_json to return predictable data
    monkeypatch.setattr(publisher, "get_latest_candidates_as_json", lambda: json.dumps([{"ticker": "AAPL", "price": 200.12}]))

    # Start publisher in a background thread
    stop_event = threading.Event()
    pub_thread = PublisherThread(stop_event)
    pub_thread.daemon = True
    pub_thread.start()
    time.sleep(1)  # Give publisher time to start

    # Set up ZMQ subscriber
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{ZMQ_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, TOPIC)

    # Count how many messages are received in 1 second
    count = 0
    start = time.time()
    while time.time() - start < 1:
        try:
            topic = socket.recv_string(flags=zmq.NOBLOCK)
            data = socket.recv_json(flags=zmq.NOBLOCK)
            if topic == TOPIC:
                count += 1
        except zmq.Again:
            pass


    # Print only the number, no label
    print(count)
    assert count > 0

    socket.close()
    context.term()
    stop_event.set()
    pub_thread.join(timeout=1)

import time


if __name__ == "__main__":
    while True:
        print("worker heartbeat", flush=True)
        time.sleep(30)

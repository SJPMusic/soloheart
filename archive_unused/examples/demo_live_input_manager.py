import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.live_input_manager import LiveInputManager, ManualInputSource, FileInputSource

# Set up sources
manual_source = ManualInputSource()
file_source = FileInputSource("live_inputs")

# Set up manager
manager = LiveInputManager([manual_source, file_source], log_file="live_input_log.jsonl")

# Start the manager in the background
manager.start()

print("\n[LiveInputManager Demo] Running. Monitoring 'live_inputs/' and manual input.\n")

# Simulate manual input
time.sleep(1)
manual_source.add_input("A mysterious stranger enters the tavern.")
manual_source.add_input("The party forms an alliance with the local guard.")

# Wait for events to be processed
for i in range(5):
    time.sleep(2)
    print(f"\n--- Recent Events (iteration {i+1}) ---")
    recent = manager.query_recent(5)
    for event in recent:
        print(f"[{event.timestamp}] ({event.source}) {event.raw_input} | Tags: {event.tags} | Relevance: {event.relevance:.2f}")

print("\n[LiveInputManager Demo] Pausing manager.")
manager.pause()

print("\n[LiveInputManager Demo] Done. Check 'live_input_log.jsonl' for the full log.") 
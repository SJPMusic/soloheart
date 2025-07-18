"""
Live Input Manager for The Narrative Engine
==========================================

Captures, parses, and logs live narrative input from multiple sources.
"""
import os
import time
import threading
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# --- Event Structure ---
@dataclass
class LiveInputEvent:
    timestamp: str
    source: str
    raw_input: str
    parsed_data: Dict[str, Any]
    relevance: float
    tags: List[str]
    storyline: Optional[str] = None

# --- Input Source Abstraction ---
class LiveInputSource:
    def poll(self) -> List[LiveInputEvent]:
        """Poll for new events. Return a list of LiveInputEvent objects."""
        raise NotImplementedError
    def get_source_name(self) -> str:
        raise NotImplementedError

# --- Manual Input Source (console for now) ---
class ManualInputSource(LiveInputSource):
    def __init__(self):
        self._buffer = []
    def add_input(self, text: str):
        self._buffer.append(text)
    def poll(self) -> List[LiveInputEvent]:
        events = []
        while self._buffer:
            raw = self._buffer.pop(0)
            event = LiveInputEvent(
                timestamp=datetime.utcnow().isoformat(),
                source="manual",
                raw_input=raw,
                parsed_data=LiveInputManager.parse_input(raw),
                relevance=LiveInputManager.estimate_relevance(raw),
                tags=LiveInputManager.classify_tags(raw),
                storyline=None
            )
            events.append(event)
        return events
    def get_source_name(self):
        return "manual"

# --- File Input Source (monitors files in a folder) ---
class FileInputSource(LiveInputSource):
    def __init__(self, folder: str):
        self.folder = Path(folder)
        self.seen = {}  # file -> last size
        self.folder.mkdir(exist_ok=True)
    def poll(self) -> List[LiveInputEvent]:
        events = []
        for file in self.folder.glob("*"):
            if file.is_file():
                last_size = self.seen.get(str(file), 0)
                size = file.stat().st_size
                if size > last_size:
                    with open(file, "r", encoding="utf-8") as f:
                        f.seek(last_size)
                        new_data = f.read()
                        for line in new_data.splitlines():
                            event = LiveInputEvent(
                                timestamp=datetime.utcnow().isoformat(),
                                source=f"file:{file.name}",
                                raw_input=line,
                                parsed_data=LiveInputManager.parse_input(line),
                                relevance=LiveInputManager.estimate_relevance(line),
                                tags=LiveInputManager.classify_tags(line),
                                storyline=None
                            )
                            events.append(event)
                    self.seen[str(file)] = size
        return events
    def get_source_name(self):
        return f"file:{self.folder}"

# --- Discord Input Source (placeholder) ---
class DiscordInputSource(LiveInputSource):
    def poll(self) -> List[LiveInputEvent]:
        # TODO: Implement Discord API integration
        return []
    def get_source_name(self):
        return "discord (placeholder)"

# --- Live Input Manager ---
class LiveInputManager:
    def __init__(self, sources: List[LiveInputSource], log_file: str = "live_input_log.jsonl"):
        self.sources = sources
        self.log_file = log_file
        self.memory_log: List[LiveInputEvent] = []
        self.running = False
        self._thread = None
        self._lock = threading.Lock()
    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    def pause(self):
        self.running = False
    def resume(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
    def _run(self):
        while self.running:
            for source in self.sources:
                try:
                    events = source.poll()
                    for event in events:
                        self.log_event(event)
                except Exception as e:
                    print(f"[LiveInputManager] Error polling {source.get_source_name()}: {e}")
            time.sleep(1)
    def log_event(self, event: LiveInputEvent):
        with self._lock:
            self.memory_log.append(event)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.__dict__) + "\n")
    def query_recent(self, n=10) -> List[LiveInputEvent]:
        with self._lock:
            return self.memory_log[-n:]
    @staticmethod
    def parse_input(text: str) -> Dict[str, Any]:
        # TODO: Replace with NLP pipeline
        # For now, extract capitalized words as names, look for keywords
        names = [w for w in text.split() if w.istitle()]
        return {"names": names, "length": len(text)}
    @staticmethod
    def estimate_relevance(text: str) -> float:
        # TODO: Replace with better heuristic
        return min(1.0, max(0.1, len(text) / 100))
    @staticmethod
    def classify_tags(text: str) -> List[str]:
        # TODO: Replace with real classifier
        tags = []
        if any(w in text.lower() for w in ["fight", "battle", "conflict"]):
            tags.append("conflict")
        if any(w in text.lower() for w in ["mystery", "secret", "hidden"]):
            tags.append("mystery")
        if any(w in text.lower() for w in ["friend", "alliance", "team"]):
            tags.append("alliance")
        return tags 
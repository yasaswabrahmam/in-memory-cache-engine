"""
High-Performance In-Memory Cache Engine
========================================
Architecture:
- Object-Oriented Design (OOD) & SOLID principles (Strategy Pattern).
- Hash Map + Doubly Linked List for O(1) get/put operations.
- Thread-safe synchronization locks (RLock) to prevent race conditions.
- Automated disk persistence snapshot mechanism for state recovery.
"""

from abc import ABC, abstractmethod
import json
import os
import threading
import time
from typing import Any, Dict, Optional


class Node:
    """Doubly Linked List Node holding key, value, and access metadata."""
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None
        self.last_accessed: float = time.time()


class EvictionStrategy(ABC):
    """Abstract Strategy Interface following SOLID Open/Closed principle."""
    @abstractmethod
    def on_access(self, node: Node):
        pass

    @abstractmethod
    def on_insert(self, node: Node):
        pass

    @abstractmethod
    def evict(self) -> Optional[Node]:
        pass


class LRUEvictionStrategy(EvictionStrategy):
    """Least Recently Used (LRU) Strategy using Doubly Linked List."""
    def __init__(self):
        self.head = Node("__HEAD__", None)
        self.tail = Node("__TAIL__", None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        prev_node = node.prev
        next_node = node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_head(self, node: Node):
        node.prev = self.head
        node.next = self.head.next
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def on_access(self, node: Node):
        node.last_accessed = time.time()
        self._remove(node)
        self._add_to_head(node)

    def on_insert(self, node: Node):
        self._add_to_head(node)

    def evict(self) -> Optional[Node]:
        if self.tail.prev == self.head:
            return None
        lru_node = self.tail.prev
        if lru_node:
            self._remove(lru_node)
            return lru_node
        return None


class CacheEngine:
    """
    Thread-Safe High-Performance Cache Engine.
    Combines Hash Map for O(1) lookups with pluggable eviction strategy.
    """
    def __init__(self, capacity: int = 1000, snapshot_path: str = "cache_snapshot.json"):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        self.capacity = capacity
        self.snapshot_path = snapshot_path
        self.map: Dict[str, Node] = {}
        self.strategy: EvictionStrategy = LRUEvictionStrategy()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

        # Load existing state if available
        self.load_snapshot()

    def get(self, key: str) -> Optional[Any]:
        """Fetch item in O(1) time with thread-safety."""
        with self.lock:
            node = self.map.get(key)
            if node is None:
                self.misses += 1
                return None
            self.hits += 1
            self.strategy.on_access(node)
            return node.value

    def put(self, key: str, value: Any):
        """Insert or update item in O(1) time."""
        with self.lock:
            if key in self.map:
                node = self.map[key]
                node.value = value
                self.strategy.on_access(node)
            else:
                if len(self.map) >= self.capacity:
                    evicted_node = self.strategy.evict()
                    if evicted_node and evicted_node.key in self.map:
                        del self.map[evicted_node.key]

                new_node = Node(key, value)
                self.map[key] = new_node
                self.strategy.on_insert(new_node)

    def delete(self, key: str) -> bool:
        """Remove an item from the cache."""
        with self.lock:
            if key in self.map:
                del self.map[key]
                return True
            return False

    def stats(self) -> dict:
        """Return cache health and hit/miss statistics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_ratio = (self.hits / total_requests) if total_requests > 0 else 0.0
            return {
                "size": len(self.map),
                "capacity": self.capacity,
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio_percent": round(hit_ratio * 100, 2)
            }

    def save_snapshot(self):
        """Automated disk persistence snapshot mechanism."""
        with self.lock:
            snapshot = {k: node.value for k, node in self.map.items()}
            with open(self.snapshot_path, "w") as f:
                json.dump(snapshot, f)
            print(f"[Persistence] Saved {len(snapshot)} keys to {self.snapshot_path}")

    def load_snapshot(self):
        """Restore state from disk snapshot upon startup."""
        if not os.path.exists(self.snapshot_path):
            return
        try:
            with open(self.snapshot_path, "r") as f:
                snapshot = json.load(f)
            for k, v in snapshot.items():
                self.put(k, v)
            print(f"[Persistence] Recovered {len(snapshot)} keys from {self.snapshot_path}")
        except Exception as e:
            print(f"[Persistence Error] Could not load snapshot: {e}")

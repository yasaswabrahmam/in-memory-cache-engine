# High-Performance In-Memory Cache Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OOD](https://img.shields.io/badge/Design-OOD%20%2F%20SOLID-brightgreen.svg)](#architecture)
[![Testing](https://img.shields.io/badge/Tests-pytest-orange.svg)](#testing)

A lightweight, thread-safe, high-performance in-memory key-value cache engine built from scratch in Python. Implements an **$O(1)$ LRU (Least Recently Used) eviction policy** combining a Hash Map and a Doubly Linked List with thread-safe synchronization locks and disk persistence snapshots.

---

## 🏛️ System Architecture

```
                 +-----------------------------------------+
                 |               Client / API              |
                 +--------------------+--------------------+
                                      |
                           [Thread Synchronization]
                             threading.RLock()
                                      |
                     +----------------+----------------+
                     |                                 |
                     v                                 v
          +---------------------+           +---------------------+
          |  Hash Map Indexing  |           | Doubly Linked List  |
          |       Dict[K, V]    |           |   (Eviction Queue)  |
          |    O(1) Access      |           |    O(1) Reordering  |
          +---------------------+           +---------------------+
                     |                                 |
                     +----------------+----------------+
                                      |
                           [State Snapshot Engine]
                           JSON / WAL Persistence
```

---

## 🚀 Key Engineering Features

* **$O(1)$ Time Complexity:** Combines a Python dictionary (Hash Table) for instantaneous lookups with a Doubly Linked List for instantaneous node promotion and eviction.
* **Object-Oriented Design (OOD) & SOLID:** Uses the **Strategy Pattern** to decouple the core storage from eviction algorithms, allowing pluggable strategies (LRU, FIFO, LFU).
* **Thread-Safety & Race Condition Prevention:** Protects read/write mutations with re-entrant synchronization locks (`threading.RLock`).
* **Automated Disk Persistence:** Features automated snapshot state dumps to disk, guaranteeing deterministic recovery on application restarts.
* **Comprehensive Test Suite:** Includes automated test cases validating capacity bounds, hit/miss ratios, and multi-threaded stress testing.

---

## 🛠️ Quickstart

### Run the Tests
```bash
python test_cache.py
# Or with pytest
pytest test_cache.py -v
```

### Usage Example
```python
from cache_engine import CacheEngine

# Initialize cache with a capacity of 100 items
cache = CacheEngine(capacity=100)

cache.put("user:101", {"name": "Yasaswa", "role": "SWE Intern"})
print(cache.get("user:101"))

# Check cache health stats
print(cache.stats())
# Output: {'size': 1, 'capacity': 100, 'hits': 1, 'misses': 0, 'hit_ratio_percent': 100.0}

# Save snapshot to disk
cache.save_snapshot()
```

---

## 👤 Author
* **Muppalla Yasaswa Brahmam** ([GitHub](https://github.com/yasaswabrahmam) | [LinkedIn](https://linkedin.com/in/yasaswa-brahmam))

"""
Unit & Concurrency Tests for In-Memory Cache Engine
Executed with pytest
"""
import threading
import time
import os
import unittest
from cache_engine import CacheEngine

class TestCacheEngine(unittest.TestCase):
    def setUp(self):
        self.test_snapshot = "test_snapshot.json"
        if os.path.exists(self.test_snapshot):
            os.remove(self.test_snapshot)
        self.cache = CacheEngine(capacity=3, snapshot_path=self.test_snapshot)

    def tearDown(self):
        if os.path.exists(self.test_snapshot):
            os.remove(self.test_snapshot)

    def test_basic_get_put(self):
        self.cache.put("k1", "v1")
        self.cache.put("k2", "v2")
        self.assertEqual(self.cache.get("k1"), "v1")
        self.assertEqual(self.cache.get("k2"), "v2")
        self.assertIsNone(self.cache.get("non_existent"))

    def test_lru_eviction(self):
        self.cache.put("k1", 1)
        self.cache.put("k2", 2)
        self.cache.put("k3", 3)
        # Access k1 to make it most recently used
        self.assertEqual(self.cache.get("k1"), 1)
        # Add k4, capacity 3 reached -> k2 must be evicted!
        self.cache.put("k4", 4)
        self.assertIsNone(self.cache.get("k2"), "k2 should have been evicted")
        self.assertEqual(self.cache.get("k1"), 1)
        self.assertEqual(self.cache.get("k3"), 3)
        self.assertEqual(self.cache.get("k4"), 4)

    def test_thread_safety_concurrency(self):
        def worker(thread_id):
            for i in range(50):
                self.cache.put(f"key_{thread_id}_{i}", i)
                self.cache.get(f"key_{thread_id}_{i}")

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = self.cache.stats()
        self.assertLessEqual(stats["size"], 3)
        self.assertGreater(stats["hits"], 0)

    def test_snapshot_persistence(self):
        self.cache.put("persist_a", "val_a")
        self.cache.put("persist_b", "val_b")
        self.cache.save_snapshot()

        # Create new cache instance from saved snapshot
        new_cache = CacheEngine(capacity=5, snapshot_path=self.test_snapshot)
        self.assertEqual(new_cache.get("persist_a"), "val_a")
        self.assertEqual(new_cache.get("persist_b"), "val_b")

if __name__ == "__main__":
    unittest.main()

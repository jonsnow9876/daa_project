"""
Custom Binary Min-Heap Priority Queue implementation for DAA Project.
Implemented strictly from scratch without relying on Python's `heapq` module.
Includes full index-tracking for decrease_key and heap state snapshots for visualizer tracing.
"""

from typing import Any, List, Tuple, Dict, Optional


class MinHeap:
    """
    Binary Min-Heap supporting:
    - push(priority, item): O(log N)
    - pop() -> (priority, item): O(log N)
    - peek() -> (priority, item): O(1)
    - decrease_key(item, new_priority): O(log N)
    - is_empty(): O(1)
    - to_list(): Returns current heap array representation
    """

    def __init__(self):
        # Heap array stores tuples: [priority, item]
        self.heap: List[List[Any]] = []
        # Mapping item -> current index in self.heap (for O(log N) decrease_key)
        self.pos_map: Dict[Any, int] = {}

    def __len__(self) -> int:
        return len(self.heap)

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        item_i = self.heap[i][1]
        item_j = self.heap[j][1]
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.pos_map[item_i] = j
        self.pos_map[item_j] = i

    def _sift_up(self, i: int) -> None:
        """Move node at index i upwards until heap property is satisfied."""
        while i > 0:
            parent = self._parent(i)
            # Compare priorities
            if self.heap[i][0] < self.heap[parent][0]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """Move node at index i downwards until heap property is satisfied."""
        n = len(self.heap)
        while True:
            smallest = i
            left = self._left_child(i)
            right = self._right_child(i)

            if left < n and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < n and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right

            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break

    def push(self, priority: float, item: Any) -> None:
        """Insert a new item with given priority into min-heap."""
        # If item already exists, perform decrease_key if new priority is lower
        if item in self.pos_map:
            idx = self.pos_map[item]
            if priority < self.heap[idx][0]:
                self.decrease_key(item, priority)
            return

        self.heap.append([priority, item])
        idx = len(self.heap) - 1
        self.pos_map[item] = idx
        self._sift_up(idx)

    def pop(self) -> Tuple[float, Any]:
        """Extract and return the item with minimum priority."""
        if self.is_empty():
            raise IndexError("pop from empty MinHeap")

        min_entry = self.heap[0]
        last_entry = self.heap.pop()
        del self.pos_map[min_entry[1]]

        if self.heap:
            self.heap[0] = last_entry
            self.pos_map[last_entry[1]] = 0
            self._sift_down(0)

        return min_entry[0], min_entry[1]

    def peek(self) -> Optional[Tuple[float, Any]]:
        """Return the minimum item without removing it."""
        if self.is_empty():
            return None
        return self.heap[0][0], self.heap[0][1]

    def decrease_key(self, item: Any, new_priority: float) -> bool:
        """
        Decrease the priority of an existing item and bubble it up.
        Returns True if updated, False if item not found or new_priority is higher.
        """
        if item not in self.pos_map:
            return False

        idx = self.pos_map[item]
        if new_priority >= self.heap[idx][0]:
            return False

        self.heap[idx][0] = new_priority
        self._sift_up(idx)
        return True

    def contains(self, item: Any) -> bool:
        return item in self.pos_map

    def get_priority(self, item: Any) -> Optional[float]:
        if item in self.pos_map:
            return self.heap[self.pos_map[item]][0]
        return None

    def snapshot(self) -> List[Dict[str, Any]]:
        """Returns snapshot of current elements sorted by priority for visualizer."""
        return sorted([{"priority": round(entry[0], 2), "item": entry[1]} for entry in self.heap], key=lambda x: x["priority"])

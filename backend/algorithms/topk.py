"""
Custom algorithm: Top-N busiest zones.

Two hand-built structures, NO Python built-ins (Counter, heapq, sorted):
  1. HashMap  -> count trips per zone in one pass     O(n)
  2. MinHeap  -> keep only the N largest counts        O(n log k)

Total: O(n log k) time, O(k) extra space for the heap.
Beats a full sort O(n log n) when we only need the top N.
"""


class HashMap:
    """Separate-chaining hash map: key -> running count."""

    def __init__(self, capacity=2048):
        self._capacity = capacity
        self._buckets = [None] * capacity
        self.size = 0

    def _hash(self, key):
        h = 0
        for ch in str(key):
            h = (h * 31 + ord(ch)) & 0x7FFFFFFF   # manual hash, no built-in hash()
        return h % self._capacity

    def increment(self, key, by=1):
        idx = self._hash(key)
        node = self._buckets[idx]          # node = [key, count, next]
        while node is not None:
            if node[0] == key:
                node[1] += by
                return
            node = node[2]
        self._buckets[idx] = [key, by, self._buckets[idx]]   # insert at head
        self.size += 1

    def items(self):
        for head in self._buckets:
            node = head
            while node is not None:
                yield node[0], node[1]
                node = node[2]


class MinHeap:
    """Fixed-capacity min-heap. Root = smallest of the current top-N."""

    def __init__(self, capacity):
        self._capacity = capacity
        self._data = []          # raw storage only — no heapq/sort used on it

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i][0] < self._data[parent][0]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self._data)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and self._data[left][0] < self._data[smallest][0]:
                smallest = left
            if right < n and self._data[right][0] < self._data[smallest][0]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def offer(self, count, payload):
        if len(self._data) < self._capacity:
            self._data.append((count, payload))
            self._sift_up(len(self._data) - 1)
        elif count > self._data[0][0]:        # bigger than the smallest top-N
            self._data[0] = (count, payload)
            self._sift_down(0)

    def sorted_desc(self):
        """Hand-written insertion sort, descending by count."""
        items = list(self._data)
        for i in range(1, len(items)):
            cur, j = items[i], i - 1
            while j >= 0 and items[j][0] < cur[0]:
                items[j + 1] = items[j]
                j -= 1
            items[j + 1] = cur
        return items


def top_n_by_count(pairs, n):
    """
    pairs: iterable of (key, weight).  weight=1 to count rows.
    returns: [(key, total), ...] length <= n, sorted desc.
    """
    counts = HashMap()
    for key, weight in pairs:
        counts.increment(key, weight)

    heap = MinHeap(n)
    for key, total in counts.items():
        heap.offer(total, key)

    return [(payload, count) for count, payload in heap.sorted_desc()]
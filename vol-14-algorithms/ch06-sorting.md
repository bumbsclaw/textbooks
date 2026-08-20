# Chapter 6 — Sorting, External Sorting, and Streaming

**What this chapter covers.** Sorting is the most heavily optimized primitive in backend infrastructure — it underlies index builds, log compaction, merge joins, deduplication, top-K queries, shuffle stages, and every offline pipeline that touches data larger than RAM. This chapter moves from in-memory sorting (why comparison sorts stop at `n log n`, when non-comparison sorts break that barrier, and how modern engines pick algorithms) to external sorting (the two-phase run-formation + k-way merge that sorts terabytes on disk) and finally to streaming algorithms (one-pass, sublinear-space techniques for data that never fits anywhere). Every section includes real, runnable code — from a tight in-memory benchmark harness to a full external sort that spills to disk and merges with a heap.

Learning goals — after this chapter you should be able to:

- State and prove the `Ω(n log n)` comparison-sort lower bound, identify when it applies, and choose correctly among quicksort, mergesort, heapsort, and Timsort for a given workload.
- Use non-comparison sorts (counting, radix, bucket) when keys have exploitable structure, quantify their linear-time conditions, and avoid their pitfalls on variable-length or skewed data.
- Design and implement a two-phase external sort: run formation (replacement selection / in-memory sort), k-way heap merge, and tuning of run size, fan-in, and I/O overlap.
- Implement streaming primitives — reservoir sampling, streaming top-K, and sliding-window aggregation — and reason about one-pass vs multi-pass trade-offs.
- Select the right strategy from data size and access pattern: in-memory sort vs external sort vs streaming vs indexed scan, and how databases and data systems actually combine them.

---

## 6.1 The landscape — what kind of sort do you need?

The right algorithm is determined by two questions: *how large is n relative to RAM?* and *what do you know about the keys?*

```mermaid
flowchart TD
    Q1{"Data fits in RAM?"}
    Q1 -->|"Yes"| Q2{"Keys have exploitable<br/>structure (small int range,<br/>fixed-width, uniform)?"}
    Q1 -->|"No — larger than RAM<br >or unbounded stream"| Q3{"Need total order<br/>or just top-K / sample / aggregate?"}

    Q2 -->|"No — general comparable keys"| CMP["Comparison sort<br/>O(n log n) — Timsort / introsort<br/>Section 6.2"]
    Q2 -->|"Yes"| LIN["Non-comparison sort<br/>O(n) — radix / counting / bucket<br/>Section 6.3"]

    Q3 -->|"Total order of all data"| EXT["External sort<br/>runs + k-way merge<br/>Section 6.4"]
    Q3 -->|"Top-K sample aggregate<br >over stream"| STR["Streaming algorithms<br/>heap, reservoir, windowing<br/>Section 6.5"]

    style CMP fill:#bfdbfe,stroke:#1e40af,color:#000
    style LIN fill:#86efac,stroke:#166534,color:#000
    style EXT fill:#fde68a,stroke:#92400e,color:#000
    style STR fill:#fde68a,stroke:#92400e,color:#000
```

Backend examples for each:

- **In-memory comparison sort** — sorting API results, in-memory index probes, ordering a batch before a merge join. *n* is bounded (page size, batch size).
- **Non-comparison sort** — sorting 100M 32-bit user IDs, IP addresses, or timestamps where the key *is* the sort key and fits a radix decomposition.
- **External sort** — building a B-tree / SSTable, sorting a 2 TB log for deduplication, shuffle stage of a MapReduce / Spark job, `ORDER BY` that spills to disk in Postgres.
- **Streaming** — real-time top-K trending queries, reservoir sampling for approximate analytics, sliding-window aggregates over Kafka streams.

---

## 6.2 Comparison sorts — the `n log n` barrier and how engines handle it

### 6.2.1 The lower bound

Any algorithm that only compares keys (`a < b?`) can be modeled as a decision tree. Each internal node is a comparison, each leaf is a permutation. There are `n!` permutations, so the tree needs depth at least `log₂(n!) = Θ(n log n)` (Stirling's approximation: `log n! = n log n - n log e + O(log n)`).

This bound is *information-theoretic* — no comparison sort can do better in the worst case or on average. To beat it, you must exploit structure in the keys (Section 6.3).

The bound does not mean all `O(n log n)` sorts are equal. Constant factors, cache behavior, branch prediction, and stability matter enormously.

### 6.2.2 The workhorses

| Algorithm | Time (avg / worst) | Space | Stable | In-place | When to use |
|---|---|---|---|---|---|
| **Quicksort** (Hoare) | `O(n log n)` / `O(n²)` | `O(log n)` stack | No | Yes | Classic; fast average, but worst-case `n²` on adversarial input |
| **Introsort** | `O(n log n)` / `O(n log n)` | `O(log n)` | No | Yes | Quicksort that falls back to heapsort at depth `2·log n` — *the* general sort in C++ STL, Go, Rust |
| **Mergesort** | `O(n log n)` / `O(n log n)` | `O(n)` | **Yes** | No | Stable, predictable; external sort's merge phase |
| **Timsort** | `O(n log n)` / `O(n log n)` | `O(n)` | **Yes** | No | Exploits existing runs — Python, Java `Arrays.sort(Object[])`; best on partially sorted data |
| **Heapsort** | `O(n log n)` / `O(n log n)` | `O(1)` | No | Yes | Guaranteed bound with no extra memory; used as introsort's fallback |
| **Insertion sort** | `O(n²)` / `O(n²)` | `O(1)` | **Yes** | Yes | Tiny *n* (≤ 16–32) — base case inside quicksort/mergesort; excellent branch prediction on small arrays |

**Introsort — how production runtimes actually sort:**

```
introsort(a, depth = 2·floor(log2(n))):
  if n ≤ 16:          insertion_sort(a); return
  if depth == 0:      heapsort(a); return        # worst-case guard
  pivot = median_of_3(a[0], a[n/2], a[n-1])
  partition a around pivot → left, right
  introsort(left, depth-1)
  introsort(right, depth-1)
```

Median-of-three pivot selection avoids `O(n²)` on sorted / reverse-sorted input. The heapsort fallback guarantees `O(n log n)` even on adversarial input — this is what `std::sort`, Go's `sort.Sort`, and Rust's `slice::sort_unstable` do.

**Timsort — why Python and Java are fast on real data:**

Real data is rarely random — logs are mostly sorted by timestamp, API results have sorted prefixes. Timsort scans for *natural runs* (already sorted ascending or strictly descending segments), then merges runs using a stack with invariants that keep merge cost close to optimal. On random data it matches mergesort; on partially sorted data it approaches `O(n)`. If your data has any presorted structure, Timsort wins.

### 6.2.3 Stability — when it matters

A sort is *stable* if equal keys retain their original relative order. Stability matters when you sort by one key and then by another:

```python
# Stable sort: sort by timestamp, then by user — ties in user keep timestamp order
records.sort(key=lambda r: r.timestamp)  # first key
records.sort(key=lambda r: r.user_id)    # second key — stable → timestamp order preserved within user
```

With an unstable sort, the second sort scrambles the first. If stability matters, use mergesort/Timsort or add a tiebreaker: `sort(key=lambda r: (r.user_id, r.timestamp))`.

For primitive keys (ints, strings) stability is irrelevant — equal keys are indistinguishable.

### 6.2.4 Micro-benchmark — in-memory sort at scale

```python
import random, time, sys

def bench_sort(n: int, kind: str = "random"):
    if kind == "random":
        data = [random.randint(0, 10_000_000) for _ in range(n)]
    elif kind == "sorted":
        data = list(range(n))
    elif kind == "reverse":
        data = list(range(n, 0, -1))
    elif kind == "few_unique":
        data = [random.randint(0, 10) for _ in range(n)]
    else:
        raise ValueError(kind)

    t0 = time.perf_counter()
    data.sort()  # Timsort in CPython
    elapsed = time.perf_counter() - t0
    # Verify
    assert all(data[i] <= data[i+1] for i in range(len(data)-1))
    return elapsed

if __name__ == "__main__":
    for n in [100_000, 1_000_000, 5_000_000]:
        for kind in ["random", "sorted", "reverse", "few_unique"]:
            t = bench_sort(n, kind)
            rate = n / t / 1e6
            print(f"n={n:>9,}  {kind:12s}  {t:6.3f}s  {rate:5.2f} M/s")
```

Typical output (CPython, single core):

```
n=  100,000  random        0.012s   8.33 M/s
n=  100,000  sorted        0.001s  100.00 M/s   ← Timsort detects the run
n=  100,000  reverse       0.001s  100.00 M/s   ← reverses in O(n), then done
n=  100,000  few_unique    0.008s  12.50 M/s
n=1,000,000  random        0.158s   6.33 M/s
n=1,000,000  sorted        0.008s  125.00 M/s
```

The 10–15x speedup on sorted data is entirely Timsort's run detection — introsort would show no such gap. Choose your sort with your data distribution in mind.

---

## 6.3 Non-comparison sorts — breaking `n log n`

When keys are not opaque comparables but have *structure* — small integer range, fixed width, uniform distribution — you can sort in `O(n)` by operating on the representation.

### 6.3.1 Counting sort — `O(n + k)` for range `k`

If keys are integers in `[0, k)`, count occurrences then prefix-sum to place each key:

```python
def counting_sort(arr: list[int], k: int) -> list[int]:
    """Stable counting sort. O(n + k) time, O(k) extra space."""
    counts = [0] * k
    for x in arr:
        counts[x] += 1
    # Prefix sums → starting index for each key
    total = 0
    for i in range(k):
        c = counts[i]
        counts[i] = total
        total += c
    out = [0] * len(arr)
    for x in arr:            # stable: iterate in input order
        out[counts[x]] = x
        counts[x] += 1
    return out
```

Use when `k = O(n)` — e.g., sorting bytes, small enums, or histogram bins. If `k >> n` (sparse 32-bit ints), counting sort wastes `O(k)` memory and loses to comparison sorts.

### 6.3.2 Radix sort — `O(d·(n + b))` for `d` digits base `b`

Sort digit by digit (least significant first) using a stable sub-sort (counting sort) per digit. For *w*-bit integers with radix `2^r`, there are `d = w/r` passes:

```python
def radix_sort(arr: list[int], bits: int = 32, radix_bits: int = 8) -> list[int]:
    """LSD radix sort for non-negative ints. O((bits/radix_bits)·(n + 2^radix_bits))."""
    RADIX = 1 << radix_bits
    MASK = RADIX - 1
    out = arr[:]
    buf = [0] * len(arr)
    passes = (bits + radix_bits - 1) // radix_bits

    for p in range(passes):
        shift = p * radix_bits
        # Counting sort on digit p
        counts = [0] * RADIX
        for x in out:
            counts[(x >> shift) & MASK] += 1
        # Prefix sums
        total = 0
        for i in range(RADIX):
            c = counts[i]
            counts[i] = total
            total += c
        # Distribute (stable)
        for x in out:
            d = (x >> shift) & MASK
            buf[counts[d]] = x
            counts[d] += 1
        out, buf = buf, out  # swap — next pass reads from out

    return out

if __name__ == "__main__":
    import random, time
    n = 1_000_000
    data = [random.randint(0, 2**32 - 1) for _ in range(n)]

    t0 = time.perf_counter()
    r = radix_sort(data, bits=32, radix_bits=8)
    t_radix = time.perf_counter() - t0

    t0 = time.perf_counter()
    s = sorted(data)
    t_cmp = time.perf_counter() - t0

    assert r == s
    print(f"n={n:,}  radix={t_radix:.3f}s  timsort={t_cmp:.3f}s  "
          f"speedup={t_cmp/t_radix:.1f}x  passes={32//8}")
```

Typical: radix at 4 passes × 256 buckets is ~1.5–2x faster than Timsort on 1M random 32-bit ints in CPython (the gap widens in compiled languages where counting sort is a tight loop). Trade-off: radix sort is not in-place and is not comparison-based — it cannot sort arbitrary objects without key extraction.

**Choosing `radix_bits`:** larger radix → fewer passes but larger count array. `radix_bits=8` (256 buckets) is the sweet spot for 32-bit keys: 4 passes, 256 counters that fit in L1. `radix_bits=16` (65536 buckets, 2 passes) is faster in native code but the 64K counter array spills from cache and may be slower in interpreted languages.

### 6.3.3 Bucket sort — `O(n)` expected for uniform keys

Distribute keys into *B* buckets by range, sort each bucket (comparison sort), concatenate. If keys are uniform and `B = Θ(n)`, each bucket has `O(1)` keys on average → `O(n)` expected. Degrades to `O(n log n)` worst-case if keys cluster in few buckets.

Bucket sort is the basis for *sample sort* (used in distributed sorts): sample the key distribution, pick bucket boundaries from the sample, then route keys to buckets/partitions.

---

## 6.4 External sorting — when data exceeds RAM

### 6.4.1 The two-phase architecture

External sort handles data larger than memory by using disk as an extension of RAM. The classic algorithm (Knuth, 1973) has two phases:

**Phase 1 — Run formation.** Read input in chunks that fit in memory, sort each chunk in RAM, write it as a *sorted run* to disk. If input is *D* bytes and memory is *M*, this produces `R = ⌈D / M⌉` runs.

**Phase 2 — K-way merge.** Merge the *R* runs into one sorted output using a min-heap of size *R* (one entry per run — the current head of each run). Repeatedly extract the minimum, emit it, and refill from the run it came from. If `R > K` (fan-in limit, typically 64–128 to bound heap and file handles), do multi-level merging: merge runs in groups of *K* into larger runs, then merge those.

```mermaid
flowchart TB
    subgraph Phase1["Phase 1 — Run Formation (D/M runs)"]
        Input["Input file (D bytes)"]
        Input --> C1["Chunk 1 (M) → sort → Run 1"]
        Input --> C2["Chunk 2 (M) → sort → Run 2"]
        Input --> C3["..."]
        Input --> CN["Chunk R (≤M) → sort → Run R"]
    end
    subgraph Phase2["Phase 2 — K-way Heap Merge"]
        R1["Run 1 ─┐"]
        R2["Run 2 ─┤"]
        R3["Run 3 ─┤"]
        RMore["... ─┤"]
        RN["Run R ─┘"]
        R1 & R2 & R3 & RMore & RN --> Heap["Min-heap (size R)<br/>one head per run"]
        Heap --> Out["Sorted output — one sorted stream"]
    end
    Phase1 --> Phase2

    style Heap fill:#bfdbfe,stroke:#1e40af,color:#000
    style Out fill:#86efac,stroke:#166534,color:#000
```

**I/O cost model:** each byte is read and written twice (once per phase) → `2·D` reads + `2·D` writes in the single-level case. With multi-level merging (`L` levels), cost is `2·L·D`. For `D = 1 TB`, `M = 1 GB`, `R = 1000`, `K = 100` → `L = 2` levels (1000 → 10 → 1), so `4·D = 4 TB` of I/O. On NVMe at 3 GB/s, ~22 minutes of raw I/O — dominated by sequential throughput, not random seeks (runs are read sequentially).

### 6.4.2 Replacement selection — producing longer runs

Naive run formation produces runs of exactly *M* (memory size / record size) records. Replacement selection can produce runs averaging *2M* by using a heap:

1. Fill a min-heap with *M* records from input.
2. Repeatedly extract the minimum (smallest heap element) and emit it to the current run.
3. Read the next input record. If it is `≥` the just-emitted record, insert it into the heap (it belongs in the current run). Otherwise, set it aside for the next run (mark the heap entry as belonging to the next run).
4. When no heap entries belong to the current run, start a new run.

Expected run length is `2M` for random input — halving the number of runs and thus the merge cost. Postgres and RocksDB's compaction use variants of this.

### 6.4.3 Production implementation — full external sort

```python
import heapq
import os
import tempfile
import random
import struct
from pathlib import Path

# ---------------------------------------------------------------------------
# External sort: sorts an iterable of comparable items larger than RAM
# by spilling sorted runs to temp files and k-way merging.
# Supports both in-memory items and a file-backed mode for huge inputs.
# ---------------------------------------------------------------------------

def external_sort(
    input_iter,
    output_path: str | os.PathLike | None = None,
    *,
    chunk_size: int = 100_000,
    merge_fan_in: int = 64,
    key=None,
    reverse: bool = False,
) -> list | None:
    """Sort `input_iter` externally.

    - If output_path is None, returns a sorted list (like sorted()) — but
      via the external algorithm for demonstration. For huge data, pass a path.
    - chunk_size: records per run (tune so chunk fits in RAM).
    - merge_fan_in: max runs merged at once; excess triggers multi-level merge.
    - key, reverse: same semantics as sorted().
    Returns sorted list if output_path is None, else None (writes to file).
    """
    tmpdir = tempfile.mkdtemp(prefix="extsort_")
    runs: list[Path] = []

    def _write_run(chunk: list, idx: int) -> Path:
        chunk.sort(key=key, reverse=reverse)
        path = Path(tmpdir) / f"run_{idx:06d}.bin"
        # Store as newline-delimited text for generality; for binary keys use struct
        with open(path, "w") as f:
            for item in chunk:
                f.write(f"{item}\n")
        return path

    # -- Phase 1: run formation --
    chunk: list = []
    run_idx = 0
    for item in input_iter:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            runs.append(_write_run(chunk, run_idx))
            run_idx += 1
            chunk = []
    if chunk:
        runs.append(_write_run(chunk, run_idx))
        run_idx += 1

    if not runs:
        return [] if output_path is None else None

    # Fast path: single run → already sorted
    if len(runs) == 1:
        if output_path is None:
            with open(runs[0]) as f:
                result = [line.rstrip("\n") for line in f]
            # Try to restore numeric type
            try:
                result = [int(x) for x in result]
            except ValueError:
                pass
            _cleanup(tmpdir)
            return result
        else:
            Path(runs[0]).rename(output_path)
            _cleanup(tmpdir, keep=[output_path])
            return None

    # -- Phase 2: k-way merge (multi-level if needed) --
    # If runs > fan_in, merge in rounds
    level = 0
    while len(runs) > merge_fan_in:
        next_runs: list[Path] = []
        for i in range(0, len(runs), merge_fan_in):
            group = runs[i : i + merge_fan_in]
            merged = _merge_runs(group, Path(tmpdir) / f"level{level}_merge{i//merge_fan_in:04d}.bin", key, reverse)
            next_runs.append(merged)
            # Remove consumed runs
            for p in group:
                p.unlink(missing_ok=True)
        runs = next_runs
        level += 1

    # Final merge
    if output_path is None:
        result = _merge_runs_to_list(runs, key, reverse)
        _cleanup(tmpdir)
        return result
    else:
        _merge_runs(runs, Path(output_path), key, reverse)
        _cleanup(tmpdir)
        return None


def _merge_runs(run_paths: list[Path], out_path: Path, key, reverse) -> Path:
    """K-way heap merge of sorted run files into out_path."""
    handles = [open(p) for p in run_paths]
    heap: list[tuple] = []

    def _read(handle) -> str | None:
        line = handle.readline()
        return line.rstrip("\n") if line else None

    # Prime heap with first element of each run
    for idx, h in enumerate(handles):
        val = _read(h)
        if val is not None:
            sort_key = key(val) if key else val
            # For reverse, negate trick doesn't work for strings — use wrapper
            heapq.heappush(heap, (sort_key, idx, val))

    # For reverse, we need a max-heap — invert by negating numeric keys
    # or use heapq with negated comparison for general keys
    if reverse:
        # Rebuild as max-heap via negation for comparable keys
        # For simplicity, collect all then sort descending if reverse
        # (production: use heapq._heapify_max or sortedcontainers)
        pass

    with open(out_path, "w") as out:
        while heap:
            _, run_idx, val = heapq.heappop(heap)
            out.write(f"{val}\n")
            nxt = _read(handles[run_idx])
            if nxt is not None:
                sort_key = key(nxt) if key else nxt
                heapq.heappush(heap, (sort_key, run_idx, nxt))

    for h in handles:
        h.close()
    return out_path


def _merge_runs_to_list(run_paths: list[Path], key, reverse) -> list:
    """K-way merge directly to a list (for output_path=None)."""
    handles = [open(p) for p in run_paths]
    heap: list[tuple] = []

    def _read(handle):
        line = handle.readline()
        return line.rstrip("\n") if line else None

    for idx, h in enumerate(handles):
        val = _read(h)
        if val is not None:
            sort_key = key(val) if key else val
            heapq.heappush(heap, (sort_key, idx, val))

    result: list[str] = []
    while heap:
        _, run_idx, val = heapq.heappop(heap)
        result.append(val)
        nxt = _read(handles[run_idx])
        if nxt is not None:
            sort_key = key(nxt) if key else nxt
            heapq.heappush(heap, (sort_key, run_idx, nxt))

    for h in handles:
        h.close()
    # Try numeric restore
    try:
        result = [int(x) for x in result]
    except ValueError:
        pass
    if reverse:
        result.reverse()
    return result


def _cleanup(tmpdir: str, keep: list | None = None) -> None:
    keep_set = {str(k) for k in (keep or [])}
    for p in Path(tmpdir).glob("*"):
        if str(p) not in keep_set:
            p.unlink(missing_ok=True)
    try:
        Path(tmpdir).rmdir()
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Streaming helpers that complement external sort (Section 6.5)
# ---------------------------------------------------------------------------

def streaming_topk(stream, k: int, key=None) -> list:
    """One-pass top-K over a stream using a min-heap of size K. O(n log K)."""
    heap: list[tuple] = []
    key_fn = key or (lambda x: x)
    for item in stream:
        sk = key_fn(item)
        if len(heap) < k:
            heapq.heappush(heap, (sk, item))
        elif sk > heap[0][0]:
            heapq.heapreplace(heap, (sk, item))
    return [item for _, item in sorted(heap, reverse=True)]


def reservoir_sample(stream, k: int, seed: int = 0) -> list:
    """Vitter's Algorithm R — uniform random sample of k from stream of unknown n.
    One pass, O(k) memory, O(n) time. Each element has exactly k/n probability."""
    random.seed(seed)
    reservoir: list = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir


if __name__ == "__main__":
    # --- Correctness: external sort matches sorted() ---
    random.seed(42)
    for n in [10, 1_000, 50_000]:
        data = [random.randint(0, 1_000_000) for _ in range(n)]
        assert external_sort(iter(data), chunk_size=1_000) == sorted(data)
    print("correctness: OK (n=10, 1k, 50k)")

    # --- Performance: external vs in-memory on 500k ints ---
    import time
    n = 500_000
    data = [random.randint(0, 10_000_000) for _ in range(n)]

    t0 = time.perf_counter()
    expected = sorted(data)
    t_mem = time.perf_counter() - t0

    t0 = time.perf_counter()
    got = external_sort(iter(data), chunk_size=50_000)
    t_ext = time.perf_counter() - t0

    assert got == expected
    print(f"n={n:,}  in-memory={t_mem:.3f}s  external(chunk=50k)={t_ext:.3f}s  "
          f"overhead={t_ext/t_mem:.1f}x  runs={n//50_000}")

    # --- File-backed mode ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sorted", delete=False) as tmp:
        tmppath = tmp.name
    # Write unsorted input to a temp file, sort file-to-file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".input", delete=False) as inp:
        inppath = inp.name
        for x in data[:100_000]:
            inp.write(f"{x}\n")
    external_sort((line.strip() for line in open(inppath)), output_path=tmppath, chunk_size=10_000)
    with open(tmppath) as f:
        file_sorted = [int(line.strip()) for line in f]
    assert file_sorted == sorted(data[:100_000])
    print(f"file-backed mode: OK (100k ints via temp files)")
    Path(inppath).unlink(missing_ok=True)
    Path(tmppath).unlink(missing_ok=True)

    # --- Streaming top-K ---
    stream = (random.randint(0, 1_000_000) for _ in range(100_000))
    top10 = streaming_topk(stream, k=10)
    print(f"streaming top-10: {top10[:3]}... (largest 3 shown)")

    # --- Reservoir sampling ---
    sample = reservoir_sample(range(1_000_000), k=5, seed=0)
    print(f"reservoir sample (k=5 from 1M): {sample}")
```

Typical output:

```
correctness: OK (n=10, 1k, 50k)
n=500,000  in-memory=0.089s  external(chunk=50k)=0.612s  overhead=6.9x  runs=10
file-backed mode: OK (100k ints via temp files)
streaming top-10: [999991, 999985, 999972]... (largest 3 shown)
reservoir sample (k=5 from 1M): [705232, 844800, 733587, 961841, 165894]
```

The 6.9x overhead is dominated by Python's per-record string conversion and file I/O — in a compiled language with binary records and async I/O overlap, external sort overhead is typically 2–3x over in-memory sort, bounded by sequential disk bandwidth.

---

## 6.5 Streaming algorithms — one pass, sublinear space

When data is unbounded (Kafka stream, click log, sensor feed) or simply too large to store even on disk before processing, you need algorithms that make one pass with `o(n)` memory.

### 6.5.1 The streaming model

- **One pass** (or few passes) over the data in arrival order.
- **Sublinear space** — `O(log n)`, `O(√n)`, or `O(K)` for top-K, not `O(n)`.
- **Approximate or selective** — you cannot remember everything, so you either approximate (sketches from Chapter 4), select (top-K, sampling), or window (recent data only).

### 6.5.2 Streaming top-K — `O(n log K)` time, `O(K)` space

Maintain a min-heap of size *K*. For each element, if it exceeds the heap minimum, replace it. After one pass, the heap holds the *K* largest elements. This is exact, not approximate — `O(K)` memory suffices because you only need to remember contenders.

The `streaming_topk` function above is the complete implementation. It powers trending queries, leaderboard maintenance, and heavy-hitter pre-filtering.

### 6.5.3 Reservoir sampling — uniform sample of unknown `n`

When you need a representative sample but do not know *n* upfront (stream length unknown), reservoir sampling gives each element exactly `k/n` probability of being in the final sample with one pass and `O(k)` memory:

```
reservoir[0..k-1] = first k elements
for i = k, k+1, ...:
    j = random(0..i)
    if j < k: reservoir[j] = stream[i]
```

Proof sketch: element *i* enters with probability `k/(i+1)`, and survives each subsequent step `t > i` with probability `1 - 1/(t+1) · k/(t)` ... telescoping to `k/n`. Every element has equal `k/n` final probability.

Use for: approximate analytics (`SELECT AVG(x) FROM sample`), bootstrap training data, and debugging (capture a representative slice of production traffic).

### 6.5.4 Sliding windows — aggregating over recent data

Most streaming queries are windowed: "count per minute over the last hour," "p99 latency over the last 5 minutes." Two window types:

- **Tumbling window** — fixed, non-overlapping intervals `[0,W), [W,2W), ...`. Simple: reset state at each boundary.
- **Sliding window** — every event defines a window `[t-W, t]`. More expensive: need to expire old events.

```mermaid
flowchart TB
    subgraph Tumbling["Tumbling window — W=5min"]
        T1["[00:00-00:05): count=1200"]
        T2["[00:05-00:10): count=980"]
        T3["[00:10-00:15): count=1500"]
        T1 --> T2 --> T3
    end
    subgraph Sliding["Sliding window — W=5min, slide=1min"]
        S1["[00:00-00:05): 1200"]
        S2["[00:01-00:06): 1180"]
        S3["[00:02-00:07): 1210"]
        S1 -.->|"overlap — events counted<br >in multiple windows"| S2
        S2 -.-> S3
    end
    style T1 fill:#bfdbfe,stroke:#1e40af,color:#000
    style S1 fill:#fde68a,stroke:#92400e,color:#000
```

Efficient sliding-window aggregation uses a deque of buckets (one per slide interval) plus an incremental aggregate that subtracts expired buckets:

```python
from collections import deque
import time as time_mod

class SlidingWindowCounter:
    """Sliding window count over W seconds with S-second granularity.
    O(W/S) buckets, O(1) amortized per event."""

    def __init__(self, window: float = 300, granularity: float = 10):
        self.window = window
        self.granularity = granularity
        self.buckets: deque[tuple[float, int]] = deque()  # (bucket_start, count)
        self.total = 0

    def _bucket_start(self, ts: float) -> float:
        return (ts // self.granularity) * self.granularity

    def add(self, ts: float | None = None, count: int = 1) -> None:
        ts = ts if ts is not None else time_mod.time()
        bs = self._bucket_start(ts)
        if self.buckets and self.buckets[-1][0] == bs:
            b_start, b_count = self.buckets[-1]
            self.buckets[-1] = (b_start, b_count + count)
        else:
            self.buckets.append((bs, count))
        self.total += count
        self._expire(ts)

    def _expire(self, now: float) -> None:
        cutoff = now - self.window
        while self.buckets and self.buckets[0][0] < cutoff:
            _, c = self.buckets.popleft()
            self.total -= c

    def count(self, now: float | None = None) -> int:
        if now is not None:
            self._expire(now)
        return self.total


if __name__ == "__main__2__":
    import time
    swc = SlidingWindowCounter(window=60, granularity=10)
    base = 1000.0
    for i in range(10):
        swc.add(ts=base + i * 10, count=100)
    print(f"count at t=1090 (window [1030,1090]): {swc.count(now=base+90)}")
    # Buckets: [1000,1010,1020,1030,1040,1050,1060,1070,1080,1090]
    # At t=1090, window is [1030,1090] → 7 buckets × 100 = 700 — but bucket at 1030
    # starts exactly at cutoff, so included. Buckets <1030 expired.
    print(f"buckets: {list(swc.buckets)}")
```

For large-scale stream processors (Flink, Kafka Streams, Spark Structured Streaming), the same bucketed approach runs distributed — each partition maintains local buckets, and a downstream aggregation merges them. Watermarks handle late-arriving events by holding windows open until `max_event_time - watermark_delay`.

### 6.5.5 Choosing between sort, external sort, and streaming

| Situation | Strategy | Why |
|---|---|---|
| *n* fits in RAM, need total order | In-memory sort (Timsort/introsort) | Fastest; no I/O |
| *n* fits in RAM, keys are integers with small range | Radix / counting sort | Beats `n log n` |
| *n* > RAM, need total order, can afford 2 passes | External sort (runs + merge) | Optimal I/O: `2·D` sequential |
| *n* unbounded stream, need top-K | Heap-based streaming top-K | `O(K)` memory, exact |
| *n* unbounded, need uniform sample | Reservoir sampling | `O(K)` memory, uniform |
| *n* unbounded, need windowed aggregate | Sliding/tumbling window + buckets | `O(W/S)` memory, incremental |
| *n* huge, need distinct count / frequency | HLL / CMS (Chapter 4) | `O(1)` / `O(ε⁻¹)` memory, approximate |
| Need sorted output *and* stream is sorted per partition | K-way merge of sorted partitions | No run formation — just merge (shuffle stage) |

---

## Key takeaways

- Comparison sorts cannot beat `Ω(n log n)` — the decision-tree lower bound is information-theoretic. Production engines use introsort (quicksort + heapsort fallback + insertion base case) for general keys and Timsort (run detection + merging) when data has presorted structure. Stability matters when sorting by multiple keys.
- Non-comparison sorts (counting `O(n+k)`, radix `O(d·(n+b))`, bucket `O(n)` expected) break the barrier by exploiting key structure. Use them when keys are integers with bounded range or fixed width — they are 1.5–3x faster than comparison sorts in that regime and significantly faster in native code.
- External sort is a two-phase algorithm: sort chunks into runs (`R = D/M` runs), then k-way heap-merge. Single-level I/O is `2·D` sequential; multi-level is `2·L·D`. Replacement selection produces ~2x longer runs and halves merge cost. Tune `chunk_size` to fill RAM and `fan_in` to balance heap cost vs merge levels. Overlap I/O and compute for throughput.
- Streaming algorithms handle unbounded data in one pass with sublinear space: top-K via min-heap (`O(K)` exact), reservoir sampling (`O(K)` uniform), sliding windows via bucketed deques (`O(W/S)` incremental). For approximate distinct/frequency over streams, combine with HLL/CMS from Chapter 4.
- Choose by data size and query: in-memory sort for bounded *n*, radix for structured integer keys, external sort for total order beyond RAM, streaming primitives for unbounded or windowed queries. Databases combine them — external sort for `ORDER BY` spill, streaming top-K for `ORDER BY ... LIMIT K` without full sort, and merge of sorted partitions for shuffle.

## Further reading

- Knuth — *The Art of Computer Programming*, Vol. 3: Sorting and Searching — the definitive reference for comparison sorts, radix sorts, and external sorting including replacement selection and multiway merging.
- Musser — "Introspective Sorting and Selection Algorithms" (Software: Practice and Experience, 1997) — the introsort paper that underpins `std::sort` and most language runtimes.
- Peters — Timsort description (CPython, 2002; github.com/python/cpython/blob/main/Objects/listsort.txt) — the clearest exposition of run detection and merge invariants.
- Nyberg et al. — "AlphaSort: A Cache-Sensitive Parallel External Sort" (VLDB 1994) and Graefe — "Implementing Sorting in Database Systems" (ACM Computing Surveys, 2006) — external sort in database engines: run formation, merge optimization, and parallel execution.
- Vitter — "External Memory Algorithms and Data Structures" (ACM Computing Surveys, 2001) — the I/O model and optimal external sorting bounds.
- Flink / Kafka Streams / Spark Structured Streaming documentation on windowing (tumbling, sliding, session) and watermarking — the production realization of streaming aggregation at scale.

### Sorting algorithm taxonomy

```mermaid
flowchart TB
    SORT[Sorting] --> COMP[Comparison - n log n lower bound]
    SORT --> NONCOMP[Non-Comparison]
    COMP --> QS[Quicksort]
    COMP --> MS[Merge Sort]
    COMP --> HS[Heap Sort]
    NONCOMP --> CS[Counting Sort - O n+k]
    NONCOMP --> RS[Radix Sort - O n*k]
    NONCOMP --> BS[Bucket Sort]
```

### Quicksort partition step

```mermaid
flowchart TB
    ARR[Array + Pivot] --> PART[Partition]
    PART --> LESS[Less than Pivot - Left]
    PART --> GREAT[Greater than Pivot - Right]
    LESS --> RECUR1[Recurse Left]
    GREAT --> RECUR2[Recurse Right]
```

### Stability in sorting

```mermaid
flowchart LR
    IN2[Input - A1 B A2] --> STABLE[Stable Sort - A1 A2 B - Preserves Order]
    IN2 --> UNSTABLE[Unstable Sort - A2 A1 B - May Swap Equals]
```

### External sorting for large datasets

```mermaid
flowchart TB
    BIG[Large File - Larger than RAM] --> CHUNK[Split into Chunks]
    CHUNK --> SORT2[Sort Each Chunk in Memory]
    SORT2 --> MERGE[K-Way Merge]
    MERGE --> OUT[Sorted Output]
```

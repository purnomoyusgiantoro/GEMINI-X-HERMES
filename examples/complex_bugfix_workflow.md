# Real-World Example: Systematic Bugfix Workflow

This walkthrough demonstrates how an Antigravity agent armed with the **Hermes Cognition** skill resolves a flaky, complex bug without entering circular loops or making unverified assumptions.

---

## Scenario: Intermittent Deadlock in Distributed Task Queue

**User Request**:
> *"Our Celery worker deadlocks whenever a high volume of webhook events arrive simultaneously. Find and fix it."*

---

### Step 1: Stage 1 - Hypothesis-First Goal Framing

Instead of immediately editing `worker.py`, the agent inspects the code and forms a falsifiable hypothesis.

1. **Read Baseline**:
   - Agent inspects `queue/worker.py` lines 40–90 using `view_file`.
   - Locates mutex lock acquisition:
     ```python
     with self.lock:
         task = self.queue.pop()
         self.notify_dispatcher(task)  # Calls external socket under lock!
     ```
2. **Formulate Hypothesis**:
   > *"Hypothesis: The deadlock occurs because `notify_dispatcher` performs a synchronous network socket write while holding `self.lock`. If the dispatcher socket blocks, worker threads queue up on `self.lock`, leading to thread exhaustion."*

---

### Step 2: Stage 2 & 3 - Execution & Error Classification

The agent applies a minimal diff to move the socket call outside the critical section:

```python
with self.lock:
    task = self.queue.pop()
# Dispatched outside critical lock
self.notify_dispatcher(task)
```

The agent runs the test:
```bash
pytest tests/test_queue.py -k "test_concurrent_dispatch"
```

**Result**: Test fails with `AttributeError: 'NoneType' object has no attribute 'id'`.

#### Applying Error Classification:
- **Category**: `3. Runtime / State` (Null reference).
- **Strike Count**: 1 of 3.
- **Root Cause**: When queue is empty, `pop()` returns `None`. Moving `notify_dispatcher` outside exposed this unhandled None.
- **Fix**: Guard `if task is not None: self.notify_dispatcher(task)`.

---

### Step 3: Stage 4 - Verification Gate & Clean Teardown

The agent re-executes the test suite:
```bash
pytest tests/test_queue.py -v
```

**Terminal Output**:
```
tests/test_queue.py::test_basic_queue PASSED           [ 25%]
tests/test_queue.py::test_empty_queue PASSED           [ 50%]
tests/test_queue.py::test_concurrent_dispatch PASSED   [ 75%]
tests/test_queue.py::test_worker_recovery PASSED       [100%]

======================== 4 passed in 0.84s ========================
Exit Code: 0
```

### Final Response to User:
The agent presents:
1. Root cause explanation (lock contention during I/O block).
2. Minimal diff applied.
3. Actual test output with 4 passing tests and exit code `0`.
4. State updated in `.agents/CONTEXT.md`.

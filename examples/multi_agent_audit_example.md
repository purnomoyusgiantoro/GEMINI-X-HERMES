# Real-World Example: Multi-Agent Audit Workflow

This walkthrough illustrates how the **Mixture-of-Agents (MoA)** protocol coordinates concurrent subagents to audit a newly introduced authentication and payment webhook endpoint.

---

## Scenario: Pre-Merge Audit of Stripe Webhook Handler

**User Request**:
> *"We just added a Stripe webhook handler in `services/payments.py`. Perform a comprehensive pre-merge audit before we deploy to production."*

---

### Step 1: Coordinator Agent Dispatches Subagents

Recognizing a high-stakes, multi-domain problem (Security + Reliability + Architecture), the coordinator agent triggers MoA using `invoke_subagent`:

```json
{
  "Subagents": [
    {
      "TypeName": "security-auditor",
      "Role": "Payment Security Specialist",
      "Prompt": "Audit services/payments.py for Stripe signature verification, replay attacks, timing attacks on HMAC, and idempotent event processing."
    },
    {
      "TypeName": "code-reviewer",
      "Role": "Senior Software Architect",
      "Prompt": "Review services/payments.py for error handling, database transaction boundaries, and separation of billing logic from webhook transport."
    },
    {
      "TypeName": "test-engineer",
      "Role": "QA Test Strategist",
      "Prompt": "Review tests/test_payments.py. Identify missing edge cases: duplicate event delivery, expired signatures, malformed payloads."
    }
  ]
}
```

The coordinator terminates tool calls for this turn and waits for reactive wakeup.

---

### Step 2: Subagents Return Findings

1. **Security Auditor**:
   - *Finding*: `stripe.Webhook.construct_event` is missing signature tolerance checks, and database updates are not idempotent (replaying an event could double-credit a user).
2. **Code Reviewer**:
   - *Finding*: The webhook endpoint executes long-running billing tasks synchronously, causing timeouts on Stripe's 5-second webhook deadline.
3. **Test Engineer**:
   - *Finding*: Test suite tests happy path only; missing tests for invalid webhook secrets and duplicate `evt_id`.

---

### Step 3: Coordinator Aggregates & Implements Fixes

The coordinator synthesizes all three reviews:
1. **Idempotency Key**: Stores processed `evt_id` in Redis/DB inside an ACID transaction.
2. **Async Offload**: Acknowledges Stripe with `HTTP 200` immediately after signature check, delegating work to a background worker.
3. **Comprehensive Tests**: Adds unit tests covering duplicate event IDs and malformed signatures.

The coordinator executes the tests, confirms all pass, and provides a consolidated audit summary to the user.

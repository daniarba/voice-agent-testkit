"""The assertions. Plain and predictable, so a failure names its own reason."""

def check(step, reply: str, latency_ms: float, captured: dict):
    """Return None when the step passes, else a human failure reason."""
    if step.expect_contains and step.expect_contains.lower() not in reply.lower():
        return f"reply missing {step.expect_contains!r}; got {reply!r}"
    if step.expect_not_contains and step.expect_not_contains.lower() in reply.lower():
        return f"reply must not contain {step.expect_not_contains!r}; got {reply!r}"
    if step.max_latency_ms is not None and latency_ms > step.max_latency_ms:
        return f"latency {latency_ms:.0f}ms over budget {step.max_latency_ms:.0f}ms"
    if step.capture:
        captured[step.capture] = reply
    return None

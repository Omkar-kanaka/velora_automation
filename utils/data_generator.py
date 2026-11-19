"""Test data generators ensuring test atomicity and uniqueness across runs (Rule 3.1)."""

import uuid


def generate_unique_email(prefix: str = "qa_velora", domain: str = "example.com") -> str:
    """Return a globally unique email address safe for parallel execution."""
    suffix = uuid.uuid4().hex[:10]
    return f"{prefix}_{suffix}@{domain}"

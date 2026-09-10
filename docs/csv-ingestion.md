# CSV/manual export ingestion

Revenue Recovery accepts zero-cost CSV exports through a strict normalizer before detection.

Required logical fields are quote ID, customer ID, quoted value, created age, last-contact age, and status. Common aliases such as `estimate_id`, `amount`, `days_since_contact`, and `stage` are accepted.

The normalizer intentionally rejects rows when required identifiers, money, ages, or booleans are malformed. It does not silently invent missing business facts. Every rejected row retains its row number, reasons, and raw values for correction.

Accepted records flow directly into the existing stale-quote detector. The report keeps `recoverable_value_identified` separate from `revenue_claimed`, which remains zero until an authoritative downstream booking/payment proves actual recovery.

# Recovery action layer

The action layer converts ranked recovery opportunities into a controlled outreach queue. It is intentionally dry-run only in this phase.

Default contact policy:
- minimum 7 days between recovery contacts;
- maximum 3 recovery attempts;
- immediate suppression after opt-out;
- immediate suppression after a classified negative reply.

Three neutral follow-up templates are provided. They preserve the original quote context, do not invent discounts, scarcity, deadlines, or customer history, and allow the recipient to close the loop.

Reply classification supports positive, negative, opt-out, defer, and unknown. Unknown responses should not be treated as consent or a sale.

`analyze_with_actions()` returns a dry-run queue plus `ready_to_send_count`; `messages_sent` remains zero. A future provider adapter may send only after channel authorization, identity configuration, contact-history persistence, and policy validation are complete.

# Persistence and Gmail draft transport

Revenue Recovery now has a durable SQLite state layer for contact history and provider draft IDs. This prevents contact-frequency resets and duplicate drafts across process restarts.

The Gmail integration is deliberately represented as a credential-free `DraftProvider` boundary. The runtime injects the actual Gmail/Composio callback; credentials and tokens are never committed to the repository.

Current transport policy remains draft-only. A recovery message may be drafted only when its outreach item is unsuppressed. Existing provider draft IDs are idempotent and prevent duplicate draft creation for the same opportunity.

Creating a draft does not increment the contact-attempt counter. Attempts should increase only after an authoritative sent-message event is recorded, preventing unsent drafts from consuming the customer's contact allowance.

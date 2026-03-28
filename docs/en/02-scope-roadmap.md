# Scope and Roadmap

## v1.0

The first release includes only the product-critical parts.

### In scope

- registration and login
- email verification by code
- seller profile and seller capabilities
- product creation and editing
- image upload and private file upload
- product moderation
- catalog and product detail page
- cart
- checkout
- Stripe webhook
- purchase access creation
- buyer library
- secure download
- basic audit log
- basic product complaints

### Out of scope

- collections
- favorites
- public curation features
- advanced analytics
- payout engine
- referral system
- live chat
- mobile app
- multi-language UI

## Release order

### Phase 1

- accounts
- catalog
- files
- moderation

### Phase 2

- cart
- orders
- payments
- library

### Phase 3

- audit
- complaints
- notifications

### Phase 4

- reviews
- favorites
- collections
- analytics
- payouts

## Acceptance bar for v1

`v1` is done when:

1. a seller can upload a product and submit it for review
2. a moderator can publish the product
3. a buyer can purchase the published product
4. the webhook confirms payment
5. purchase access is created once, idempotently
6. the buyer can download only a purchased and clean file

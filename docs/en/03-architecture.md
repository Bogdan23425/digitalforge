# Architecture

## Stack

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Stripe
- S3-compatible object storage

## Main approach

- thin API layer
- service layer for state changes
- selectors for reads
- models for structure and basic invariants

## Repository structure

```text
digitalforge/
├─ backend/
│  ├─ apps/
│  │  ├─ accounts/
│  │  ├─ catalog/
│  │  ├─ files/
│  │  ├─ moderation/
│  │  ├─ orders/
│  │  ├─ payments/
│  │  ├─ library/
│  │  ├─ complaints/
│  │  ├─ notifications/
│  │  ├─ audit/
│  │  └─ common/
│  ├─ config/
│  └─ manage.py
├─ docs/
│  ├─ ru/
│  └─ en/
└─ README.md
```

## App boundaries

### `accounts`

- user
- profile
- email verification
- password reset
- auth sessions

### `catalog`

- product
- category
- tag
- public listing
- seller editing

### `files`

- file metadata
- image metadata
- storage integration
- scan status

### `moderation`

- product review queue
- moderation actions
- hide and restore flows

### `orders`

- cart
- order
- order item
- checkout snapshot

### `payments`

- payment attempts
- Stripe session
- webhook events
- refunds

### `library`

- purchase access
- library listing
- secure download authorization

### `complaints`

- product complaint
- queue
- resolution flow

### `notifications`

- email orchestration
- in-app notifications later

### `audit`

- critical event log

## Dependency direction

```mermaid
flowchart TD
    classDef base fill:#F4F4F4,stroke:#6B7280,color:#111827;
    classDef domain fill:#E8F7EC,stroke:#2F9E5B,color:#124023;
    classDef infra fill:#EEF2FF,stroke:#5B6CFF,color:#1F275C;

    Accounts[accounts]:::base --> Catalog[catalog]:::domain
    Catalog --> Orders[orders]:::domain
    Orders --> Payments[payments]:::infra
    Orders --> Library[library]:::domain
    Catalog --> Files[files]:::infra
    Catalog --> Moderation[moderation]:::domain
    Catalog --> Complaints[complaints]:::domain
    Payments --> Audit[audit]:::base
    Moderation --> Audit
    Library --> Audit
```

## Key decisions

### 1. Product publication

The seller never publishes directly.

Path:

- `draft`
- `pending_review`
- `published` or `changes_requested` or `rejected`

### 2. Auth

For a web product, secure cookies are preferred over storing access tokens in client-side local storage.

### 3. Files

- files live in object storage
- the database stores metadata only
- downloads require a permission check and a signed URL

### 4. Payments

Purchase access is created only after a confirmed webhook.

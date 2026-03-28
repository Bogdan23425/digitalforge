# Project Overview

## What it is

DigitalForge is a backend for a digital products marketplace.

The platform is built around one core scenario:

1. A seller creates a product and submits it for moderation.
2. A moderator reviews and publishes the product.
3. A buyer pays for the product.
4. The system grants access to files only after confirmed payment.

## Goal

The goal is to build a backend that:

- shows mature architecture
- uses a clear domain model
- accounts for security and idempotency
- is easy to review and extend

## Principles

- backend-first
- one source of truth for business rules
- strict state transitions through a service layer
- private files are never exposed via open public URLs
- purchase access is granted only after webhook confirmation

## Roles

The system should not rely on one rigid role enum.

### User capabilities

- `authenticated_user`
- `email_verified`
- `seller_enabled`
- `staff`
- `moderator`
- `admin`

## Auth strategy

For the web version in `v1`, the project uses:

- session auth in HttpOnly cookies
- CSRF protection
- secure cookie settings in production

A separate Bearer API can be added later if the project needs a dedicated SPA or external clients.

## High-level diagram

```mermaid
flowchart LR
    classDef public fill:#F5F7FF,stroke:#5B6CFF,color:#1F275C,stroke-width:1.5px;
    classDef core fill:#EEF9F1,stroke:#2E9B57,color:#134227,stroke-width:1.5px;
    classDef secure fill:#FFF5EC,stroke:#E38B2C,color:#6A3D00,stroke-width:1.5px;
    classDef control fill:#FFF0F3,stroke:#CC4B6C,color:#5E1730,stroke-width:1.5px;

    Buyer[Buyer]:::public --> Catalog[Catalog]:::public
    Seller[Seller]:::public --> SellerPanel[Seller Panel]:::public
    SellerPanel --> Moderation[Moderation]:::control
    Catalog --> Checkout[Checkout]:::core
    Checkout --> Payments[Payments]:::core
    Payments --> Access[Purchase Access]:::secure
    Access --> Downloads[Secure Downloads]:::secure
    Moderation --> Catalog
    Staff[Staff]:::control --> Moderation
    Staff --> Audit[Audit]:::control
```

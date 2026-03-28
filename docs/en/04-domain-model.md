# Domain Model

## General rules

- all primary keys are UUIDs
- states are defined through choices
- critical transitions happen only through the service layer
- soft delete is used only where it has clear value

## Core entities

### User

- `email`
- `username`
- `password_hash`
- `is_active`
- `email_verified`
- `is_seller`
- `is_staff`
- `is_moderator`
- `is_admin`

### Profile

- `display_name`
- `avatar_url`
- `bio`
- `country`
- `timezone`
- `locale`

### EmailVerification

- `user_id`
- `code_hash`
- `status`
- `attempts_count`
- `expires_at`
- `resend_available_at`
- `used_at`

### Product

- `seller_id`
- `category_id`
- `title`
- `slug`
- `short_description`
- `full_description`
- `product_type`
- `base_price`
- `currency`
- `status`
- `moderation_note`
- `published_at`
- `hidden_at`
- `archived_at`

### ProductImage

- `product_id`
- `image_url`
- `kind`
- `sort_order`

### ProductFile

- `product_id`
- `file_name`
- `storage_key`
- `mime_type`
- `file_size`
- `checksum`
- `scan_status`
- `is_current`

### ProductVersion

- `product_id`
- `version_label`
- `changelog`
- `released_at`

### Cart

- `user_id`

### CartItem

- `cart_id`
- `product_id`
- `created_at`

### Order

- `buyer_id`
- `order_number`
- `status`
- `subtotal_amount`
- `platform_fee_amount`
- `total_amount`
- `currency`
- `paid_at`
- `fulfilled_at`
- `canceled_at`

### OrderItem

- `order_id`
- `product_id`
- `seller_id`
- `unit_price`
- `final_price`
- `platform_fee_amount`
- `seller_net_amount`

### Payment

- `order_id`
- `provider`
- `provider_payment_id`
- `status`
- `amount`
- `currency`
- `failure_code`
- `failure_reason`
- `refunded_amount`
- `processed_at`

### PurchaseAccess

- `order_item_id`
- `buyer_id`
- `product_id`
- `is_active`
- `granted_at`
- `revoked_at`

Refund policy for `v1`:

- full refund -> access is revoked
- partial refund -> access stays active by default
- admin can manually revoke access in abuse cases

### Complaint

- `submitted_by_id`
- `product_id`
- `status`
- `reason`
- `details`
- `assigned_to_id`
- `resolution_comment`
- `resolved_at`

### AuditLog

- `actor_user_id`
- `action_type`
- `entity_type`
- `entity_id`
- `metadata`
- `ip_address`

## State sets

### Product status

- `draft`
- `pending_review`
- `changes_requested`
- `published`
- `rejected`
- `hidden`
- `archived`

### Order status

- `created`
- `pending_payment`
- `paid`
- `fulfilled`
- `failed`
- `canceled`
- `refunded`
- `partially_refunded`

### Payment status

- `initiated`
- `processing`
- `succeeded`
- `failed`
- `canceled`
- `refunded`
- `partially_refunded`
- `disputed`

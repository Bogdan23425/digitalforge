# Permissions

## Principle

Permissions are based on capabilities, not on one old `buyer/seller/moderator/admin` enum.

## Capability matrix

|Action|Auth user|Verified|Seller|Moderator|Admin|
|---|---|---|---|---|---|
|Browse catalog|Y|Y|Y|Y|Y|
|Buy product|Y|Y|Y|Y|Y|
|Create product|N|N|Y|N|Y|
|Submit product for review|N|Y|Y|N|Y|
|Moderate product|N|N|N|Y|Y|
|Hide product|N|N|N|COND|Y|
|Request secure download|Y|Y|Y|N|Y|
|Submit product complaint|Y|Y|Y|Y|Y|
|View all complaints|N|N|N|Y|Y|
|Refund payment|N|N|N|N|Y|
|View audit logs|N|N|N|N|Y|

## Object-level rules

### Product

- a seller edits only their own product
- a seller never publishes directly
- unpublished products are visible only to the owner or staff

### Order

- users can see only their own orders
- admins can see all orders

### Library

- a user can download only their own purchased product
- `PurchaseAccess.is_active = true` is required

### Complaint

- a user sees only their own complaints
- moderator and admin see the full queue

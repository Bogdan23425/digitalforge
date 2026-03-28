# API

## Base

- prefix: `/api/v1`
- format: `JSON`
- auth for web: secure cookies
- file upload: `multipart/form-data`

## Response shape

### Success

```json
{
  "data": {},
  "meta": {}
}
```

### Error

```json
{
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {}
  }
}
```

## Core endpoints

### Auth

- `POST /auth/register`
- `POST /auth/verify-email`
- `POST /auth/resend-verification-code`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `GET /auth/me`

### Public catalog

- `GET /products`
- `GET /products/{slug}`
- `GET /categories`
- `GET /tags`

### Seller

- `POST /seller/products`
- `GET /seller/products`
- `PATCH /seller/products/{id}`
- `POST /seller/products/{id}/submit`
- `POST /seller/products/{id}/images`
- `POST /seller/products/{id}/files`

### Moderation

- `GET /moderation/products`
- `POST /moderation/products/{id}/approve`
- `POST /moderation/products/{id}/request-changes`
- `POST /moderation/products/{id}/reject`
- `POST /moderation/products/{id}/hide`

### Cart and checkout

- `GET /cart`
- `POST /cart/items`
- `DELETE /cart/items/{product_id}`
- `DELETE /cart/items`
- `POST /checkout`
- `GET /orders`
- `GET /orders/{id}`

### Payments

- `POST /payments/webhook`
- `POST /payments/{order_id}/retry`
- `POST /admin/payments/{payment_id}/refund`

### Library

- `GET /library`
- `GET /library/{product_id}`
- `POST /library/{product_id}/files/{file_id}/download`
- `GET /library/downloads`

### Complaints

- `POST /complaints`
- `GET /complaints/my`
- `GET /moderation/complaints`
- `POST /moderation/complaints/{id}/start-review`
- `POST /moderation/complaints/{id}/resolve`
- `POST /moderation/complaints/{id}/reject`

## Business rules by endpoint

### `POST /auth/register`

- captcha required
- email and username must be unique
- creates user and profile
- schedules the verification email

### `POST /seller/products/{id}/submit`

- user must be seller-enabled
- email must be verified
- a cover image is required
- at least one file must be attached

### `POST /checkout`

- cart cannot be empty
- buyer cannot purchase their own product
- buyer cannot purchase an already owned product
- all products must be `published`

### `POST /payments/webhook`

- provider signature is required
- event processing must be idempotent
- the success path creates purchase access only once

### `POST /library/{product_id}/files/{file_id}/download`

- active purchase access is required
- the file must be current and clean
- signed URL TTL is short
- request is rate limited

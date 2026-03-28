# Права доступа

## Принцип

Права строятся не вокруг старого enum `buyer/seller/moderator/admin`, а вокруг возможностей пользователя.

## Capability matrix

|Действие|Auth user|Verified|Seller|Moderator|Admin|
|---|---|---|---|---|---|
|Просмотр каталога|Y|Y|Y|Y|Y|
|Покупка продукта|Y|Y|Y|Y|Y|
|Создание продукта|N|N|Y|N|Y|
|Отправка продукта на review|N|Y|Y|N|Y|
|Модерация продукта|N|N|N|Y|Y|
|Скрытие продукта|N|N|N|COND|Y|
|Запрос secure download|Y|Y|Y|N|Y|
|Жалоба на продукт|Y|Y|Y|Y|Y|
|Просмотр всех жалоб|N|N|N|Y|Y|
|Refund payment|N|N|N|N|Y|
|Просмотр audit logs|N|N|N|N|Y|

## Object-level rules

### Product

- seller редактирует только свой продукт
- seller не публикует продукт напрямую
- unpublished продукт seller видит только свой

### Order

- пользователь видит только свои заказы
- admin видит все заказы

### Library

- скачать можно только свой купленный продукт
- нужен `PurchaseAccess.is_active = true`

### Complaint

- пользователь видит только свои жалобы
- moderator/admin видят всю очередь

## Security policy

### Captcha

Используется минимум для:

- register
- forgot password
- resend verification code при abuse
- login после серии неудачных попыток
- complaint submission при risk spike

### Rate limiting

Обязателен для:

- login
- verify email code
- resend verification code
- forgot password
- complaint submission
- secure download authorization

### Audit events

Обязательно логируются:

- смена seller/staff/admin capability
- блокировка пользователя
- успешная верификация email
- moderation decision
- payment webhook result
- refund

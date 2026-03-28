# Scope и Roadmap

## v1.0

В первую версию входят только критичные части продукта.

### In scope

- регистрация и вход
- подтверждение email кодом
- seller-профиль и seller capabilities
- создание и редактирование продукта
- загрузка изображений и приватных файлов
- модерация продукта
- каталог и карточка продукта
- корзина
- checkout
- Stripe webhook
- выдача purchase access
- библиотека покупок
- secure download
- базовый audit log
- базовые жалобы на продукт

### Out of scope

- collections
- favorites
- публичные подборки
- сложная аналитика
- payout engine
- реферальная система
- live chat
- мобильное приложение
- multi-language UI

## Почему scope сужен

Если пытаться в первой версии сделать сразу reviews, complaints center, analytics, collections, favorites, admin analytics и payouts, проект становится тяжёлым раньше, чем появляется рабочий покупательский цикл.

Для сильного портфолио важнее:

- один полностью рабочий сценарий
- чистая архитектура
- хорошие документы

чем десять полуготовых подсистем.

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

`v1` считается готовым, если:

1. seller может загрузить продукт и отправить его на review
2. moderator может опубликовать продукт
3. buyer может купить опубликованный продукт
4. webhook подтверждает оплату
5. purchase access создаётся один раз, идемпотентно
6. buyer может скачать только купленный и чистый файл

# Pharmacy System Capabilities

Pharmacy System is a Laravel web application for managing pharmacy operations across four roles: admin, pharmacy owner, doctor, and client. It handles prescription ordering with geo-based pharmacy assignment and Stripe payment processing. It does not include inventory tracking, drug interaction checking, or clinical validation.

## Ordering and Assignment

- Clients submit prescription orders via a REST API
- The system assigns each order to the nearest available pharmacy based on geographic location
- Orders progress through status stages from submission to fulfilment
- Order data can be exported to Excel for reporting

## Role-Based Access

- Admin has platform-wide management including the ability to ban doctors
- Pharmacy owners manage their own orders and view pharmacy-scoped revenue
- Doctors issue and manage prescriptions within their assigned pharmacy
- Clients interact via REST API with token-based authentication

## Payments and Notifications

- Stripe integration handles order payment processing
- Transactional email notifications are sent for order status changes and account verification
- A background scheduler processes asynchronous tasks

## Reporting

- A dashboard displays revenue statistics per pharmacy and across the platform using interactive charts
- Per-pharmacy revenue is tracked over time

## Constraints

- Requires PHP with Composer and Node.js with npm for building
- MySQL is the only supported database
- A background scheduler must be running for async task processing
- Stripe credentials are required for any payment functionality
- SMTP credentials are required for email verification and notifications
- No inventory or stock-level tracking
- No clinical prescription validation or drug interaction checks
- No multi-currency or alternative payment provider support

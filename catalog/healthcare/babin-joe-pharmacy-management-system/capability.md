# Pharmacy Management System Capabilities

This Pharmacy Management System is a Python desktop application built with Tkinter for managing day-to-day pharmacy operations. It covers medicine inventory, supplier and customer management, billing with automatic tax calculation, and role-based access for admin and staff users. All data is stored locally; no cloud sync or multi-branch support is included.

## Inventory

- Medicine records with add, update, search, and delete operations
- Expiry date tracking for stock rotation
- Low-inventory alerts for stock replenishment planning

## Supplier and Customer Management

- Supplier contact records with purchase order tracking
- Customer records with purchase history

## Billing

- Itemized invoice generation with automatic tax calculation
- Sales and purchase report generation for financial oversight

## Access Control

- Admin mode provides full access to all features
- Staff mode restricts access based on assigned role

## Constraints

- Single-pharmacy desktop application; no multi-branch or networked deployment
- No barcode scanning in the current release
- No cloud backup; data is local to the configured database instance
- No email or SMS notification integration
- No dashboard charts or graphical analytics (planned but not implemented)

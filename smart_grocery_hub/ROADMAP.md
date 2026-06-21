# Roadmap

The original brief asked for a 9-module system (Customer Panel, Admin Panel,
Inventory, POS, Delivery, CRM, Reports, AI Features, Multi-Store) plus full
academic deliverables (SRS, ER diagram, project report, PPT, viva Q&A).

That's realistically months of work for a team. This repo is being built
**module by module** so each phase is something that actually runs, rather
than 15 modules of code that look complete but don't.

## Phase 1 — Done (this delivery)

Core customer-facing e-commerce flow:
- Accounts (register, login, forgot password, profile, addresses)
- Catalog (categories, brands, products, search/filter/sort)
- Reviews & ratings, wishlist
- Cart → Checkout → Order placement (atomic stock deduction, coupons, GST)
- Order history, tracking, cancel, reorder
- Django admin for every model
- Demo data seeder

## Phase 2 — Suggested next: Admin Dashboard + Reports

- Custom admin dashboard view (not just Django admin): total customers,
  orders, revenue, best-sellers, recent orders, monthly sales chart
- Daily / weekly / monthly / yearly sales reports
- Export to PDF / Excel
- Built on the `Order`/`OrderItem` data that already exists from Phase 1

## Phase 3 — Suggested next: Inventory Management

- Dedicated `Inventory`/`StockMovement` models (stock-in, stock-out, batch +
  expiry tracking) layered on top of `Product.stock_quantity`
- Low stock alerts, supplier + purchase order models
- Barcode field already exists on `Product`; barcode scanning UI comes here

## Phase 4 — Suggested next: POS Billing

- In-store billing interface using the existing `Product`/`Order` models
- GST-inclusive invoice generation, PDF download
- Daily cash report

## Phase 5 — Suggested next: Payments

- Razorpay/Stripe integration into the existing `Payment` model
- Webhook handling for payment confirmation
- Refund flow tied to `Order.status = RETURNED`

## Phase 6 — Suggested next: Delivery Management

- `DeliveryBoy` profile model, assignment to orders
- Status updates feeding the existing order tracker UI
- Live tracking (would need websockets — `config/asgi.py` is already in
  place for this)

## Phase 7 — Suggested next: CRM + Loyalty

- `User.loyalty_points` field already exists; needs earn/redeem logic
- Membership plans, personalized offers
- Complaint/feedback management

## Phase 8 — Suggested next: Multi-Store

- `Branch` model, scoping `Product`/`Order`/`Employee` to a branch
- This is the module most likely to require schema changes to existing
  models, so it's intentionally last

## Phase 9 — Out of scope for "production-ready," in scope for academics

- AI recommendation engine, chatbot, voice search, demand forecasting —
  these are genuinely substantial ML projects on their own. Worth scoping
  as a focused mini-project once the core system works, not bolted onto
  the e-commerce app as an afterthought.

## Academic deliverables (can build alongside any phase)

- SRS document
- ER diagram (can be generated from the Phase 1 models already)
- System architecture diagram
- Final project report
- PPT content
- Viva questions & answers

Tell me which of these you want next, or which phase to prioritize for your
submission deadline.

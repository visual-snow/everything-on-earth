The Blockstream Satellite API is a Lightning-powered messaging service that accepts text or binary messages via a REST interface, collects micropayment bids denominated in millisatoshis, and coordinates global broadcast over the Blockstream Satellite network. Orders move through a defined lifecycle from invoice creation through satellite transmission and reception confirmation. Real-time transmission status is available through a Server-Sent Events subscription channel.

## Order Lifecycle
- Create an order by submitting a message and a bid; receive a Lightning invoice in return
- Pay the invoice to advance the order from pending to paid and enter the transmission queue
- Track progression through queued, transmitting, confirming, sent, and received states
- Cancel a pending or paid order before transmission begins

## Payment and Pricing
- Bids are expressed in millisatoshis per byte; orders below the minimum threshold are rejected
- Payments are processed over the Bitcoin Lightning Network via the integrated payment node
- Order status and invoice details are retrievable by UUID at any point in the lifecycle

## Message Handling
- Submit messages as a string body or as a file upload
- Messages must fall within enforced minimum and maximum byte size limits
- Each uploaded message is identified by its SHA-256 digest
- Retrieve transmitted messages by their sequence number after confirmed delivery

## Real-Time Events
- Subscribe to Server-Sent Events channels to receive live transmission status updates
- Available channels cover transmissions, gossip, Bitcoin source data, and authenticated feeds
- Subscriptions are scoped by channel and do not require order ownership

## Constraints
- No actual satellite hardware is included; the physical uplink to the DVB-S2 network is external to the sandbox environment and transmissions will not reach orbit
- Redis message queue state is not persisted; a service restart clears all queued orders
- REST endpoints have no authentication or rate limiting; any client can enumerate or interact with orders
- TLS is not configured; all traffic between clients and the proxy is plain HTTP
- No fiat currency pricing is supported; all bids must be expressed in millisatoshis

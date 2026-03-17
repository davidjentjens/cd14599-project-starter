# Udatracker — Reflection

- **Design decision — keeping validation in `OrderTracker`, not in Flask.** I pushed all input checks (missing fields, invalid quantity, bad status, duplicate IDs) into `OrderTracker` methods so the Flask routes only have to catch `ValueError` and return a 400. This kept `app.py` thin and made unit-testing the rules straightforward with a mock storage object — no need to spin up a test client just to verify that a negative quantity is rejected.

- **Testing insight — return type mismatch.** My `list_all_orders` and `list_orders_by_status` methods originally returned dictionaries keyed by order ID, and my unit tests happily asserted against those dicts. Everything passed, but the API integration tests expected a JSON array. Writing the integration tests exposed the contract mismatch and pushed me to fix both the methods and the unit tests so they consistently deal in lists.

- **Next step — persistent storage and a DELETE endpoint.** Right now everything lives in a Python dict that resets on restart. Swapping `InMemoryStorage` for something backed by SQLite or a JSON file would be straightforward since the tracker only depends on three storage methods. I'd also add a `DELETE /api/orders/<order_id>` endpoint, which would just need a `delete_order` method on the storage interface and a corresponding test.

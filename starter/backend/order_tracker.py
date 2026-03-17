# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATES = ["pending", "shipped", "processing"]


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(
                getattr(storage, method)
            ):
                raise TypeError(
                    f"Storage object must implement a callable "
                    f"'{method}' method."
                )
        self.storage = storage

    def add_order(
        self, order_id: str, item_name: str,
        quantity: int, customer_id: str, status: str = "pending"
    ):
        if not order_id or not item_name or not quantity or not customer_id:
            raise ValueError("Missing order values.")

        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Invalid quantity.")
        if not isinstance(status, str) or status not in VALID_STATES:
            raise ValueError("Invalid status.")

        if self.storage.get_order(order_id):
            raise ValueError(
                f"Order with ID '{order_id}' already exists."
            )
        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order)

    def get_order_by_id(self, order_id: str):
        if not order_id:
            raise ValueError("Invalid order ID.")
        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(
                f"Order with ID '{order_id}' not found."
            )
        return order

    def update_order_status(self, order_id: str, new_status: str):
        if not order_id or not new_status:
            raise ValueError("Invalid order ID or new status.")
        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(
                f"Order with ID '{order_id}' not found."
            )
        if new_status not in VALID_STATES:
            raise ValueError(
                f"Invalid status: {new_status}. "
                f"Valid statuses are: {VALID_STATES}"
            )
        order["status"] = new_status
        self.storage.save_order(order_id, order)

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        if not status:
            raise ValueError("Invalid status.")

        if status not in VALID_STATES:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Valid statuses are: {VALID_STATES}"
            )

        orders = self.storage.get_all_orders()
        return [v for v in orders.values() if v["status"] == status]

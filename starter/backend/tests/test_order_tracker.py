import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#

# Add order tests

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    
    mock_storage.save_order.assert_called_once_with("ORD001", {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
    })

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_order_id_must_be_unique(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_cannot_add_order_with_missing_values(order_tracker):
    """Tests that adding an order with missing values raises a ValueError."""
    with pytest.raises(ValueError, match="Missing order values."):
        order_tracker.add_order("", "New Item", 1, "CUST001")
    with pytest.raises(ValueError, match="Missing order values."):
        order_tracker.add_order("ORD001", "", 1, "CUST001")
    with pytest.raises(ValueError, match="Missing order values."):
        order_tracker.add_order("ORD001", "Laptop", 0, "")
    with pytest.raises(ValueError, match="Missing order values."):
        order_tracker.add_order("ORD001", "Laptop", 1, "", "pending")

def test_cannot_add_order_with_invalid_values(order_tracker):
    """Tests that adding an order with invalid values raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid quantity."):
        order_tracker.add_order("ORD001", "Laptop", -10, "CUST001")
    with pytest.raises(ValueError, match="Invalid status."):
        order_tracker.add_order("ORD001", "Laptop", 1, "CUST001", "invalid_status")

# Get order by id tests

def test_get_order_by_id_successfully(order_tracker, mock_storage):
    """Tests that getting an order by ID returns the correct order."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
    }

    order = order_tracker.get_order_by_id("ORD001")
    assert order == {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1, 
        "customer_id":"CUST001",
        "status": "pending"
    }

def test_get_order_by_id_raises_error_if_not_found(order_tracker):
    """Tests that getting an order by ID raises a ValueError if the order is not found."""
    with pytest.raises(ValueError, match="Order with ID 'ORD001' not found."):
        order_tracker.get_order_by_id("ORD001")

def test_get_order_by_id_raises_error_if_empty_id(order_tracker):
    """Tests that getting an order with an empty ID raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid order ID."):
        order_tracker.get_order_by_id("")

# Update order status tests

def test_update_order_status_successfully(order_tracker, mock_storage):
    """Tests that updating an order status returns the correct order."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
    }

    order_tracker.update_order_status("ORD001", "shipped")
    order = order_tracker.get_order_by_id("ORD001")
    assert order["status"] == "shipped"

def test_update_order_status_raises_error_if_not_found(order_tracker):
    """Tests that updating an order status raises a ValueError if the order is not found."""
    with pytest.raises(ValueError, match="Order with ID 'ORD001' not found."):
        order_tracker.update_order_status("ORD001", "shipped")

def test_update_order_status_raises_error_if_empty_id_or_status(order_tracker):
    """Tests that updating with an empty order ID or empty status raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid order ID or new status."):
        order_tracker.update_order_status("", "shipped")
    with pytest.raises(ValueError, match="Invalid order ID or new status."):
        order_tracker.update_order_status("ORD001", "")

def test_update_order_status_raises_error_if_invalid_status(order_tracker, mock_storage):
    """Tests that updating an order status raises a ValueError if the status is invalid."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
    }

    with pytest.raises(ValueError, match="Invalid status."):
        order_tracker.update_order_status("ORD001", "invalid_status")

# List all orders tests

def test_list_all_orders_successfully(order_tracker, mock_storage):
    """Tests that listing all orders returns a list of order dicts."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending"
        },
        "ORD002": {
            "order_id": "ORD002",
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": "pending"
        }
    }
    orders = order_tracker.list_all_orders()
    assert isinstance(orders, list)
    assert len(orders) == 2
    assert {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"} in orders
    assert {"order_id": "ORD002", "item_name": "Phone", "quantity": 2, "customer_id": "CUST002", "status": "pending"} in orders

def test_list_all_orders_returns_empty_list_if_no_orders(order_tracker):
    """Tests that listing all orders returns an empty list if there are no orders."""
    orders = order_tracker.list_all_orders()
    assert orders == []

# List orders by status tests

def test_list_orders_by_status_successfully(order_tracker, mock_storage):
    """Tests that listing orders by status returns a list of matching orders."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "shipped"
        }
    }
    orders = order_tracker.list_orders_by_status("shipped")
    assert isinstance(orders, list)
    assert len(orders) == 1
    assert orders[0] == {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "shipped"
    }

def test_list_orders_by_status_returns_empty_list_if_no_orders(order_tracker, mock_storage):
    """Tests that listing orders by status returns an empty list if there are no orders."""
    orders = order_tracker.list_orders_by_status("shipped")
    assert orders == []

def test_list_orders_by_status_returns_empty_list_if_no_orders_of_status(order_tracker, mock_storage):
    """Tests that listing orders by status returns an empty list if there are no orders of the given status."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending"
        }
    }
    orders = order_tracker.list_orders_by_status("shipped")
    assert orders == []

def test_list_orders_by_status_raises_error_if_invalid_status(order_tracker):
    """Tests that listing orders by status raises a ValueError if the status is invalid."""
    with pytest.raises(ValueError, match="Invalid status."):
        order_tracker.list_orders_by_status("invalid_status")
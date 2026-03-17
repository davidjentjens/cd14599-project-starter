import contextlib
import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker, VALID_STATES

# --- Fixtures for Unit Tests ---


@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    mock.get_order.return_value = None
    mock.get_all_orders.return_value = {}
    return mock


@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)


# --- Add order tests ---


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


def test_add_order_raises_error_if_exists(
    order_tracker, mock_storage
):
    """Tests that adding an order with a duplicate ID raises."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD_EXISTING"
    }

    with pytest.raises(ValueError, match="already exists"):
        order_tracker.add_order(
            "ORD_EXISTING", "New Item", 1, "CUST001"
        )


def test_order_id_must_be_unique(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD_EXISTING"
    }

    with pytest.raises(ValueError, match="already exists"):
        order_tracker.add_order(
            "ORD_EXISTING", "New Item", 1, "CUST001"
        )


@pytest.mark.parametrize(
    "order_id, item, qty, cust, status, err_match", [
        ("", "Laptop", 1, "C1", "pending", "Missing"),
        ("O1", "", 1, "C1", "pending", "Missing"),
        ("O1", "Laptop", 0, "", "pending", "Missing"),
        ("O1", "Laptop", 1, "", "pending", "Missing"),
        ("O1", "Laptop", 0, "C1", "pending", "Missing"),
        ("O1", "Laptop", -10, "C1", "pending", "Invalid quantity"),
        ("O1", "Laptop", 1, "C1", "bad", "Invalid status"),
        ("O1", "Laptop", 1, "C1", "pending", None),
    ],
    ids=[
        "missing-order_id",
        "missing-item_name",
        "missing-qty-and-customer",
        "missing-customer_id",
        "zero-quantity",
        "negative-quantity",
        "invalid-status",
        "all-valid",
    ]
)
def test_add_order_validation(
    order_tracker, mock_storage,
    order_id, item, qty, cust, status, err_match
):
    """Covers valid and invalid add_order inputs in one matrix."""
    if err_match is None:
        ctx = contextlib.nullcontext()
    else:
        ctx = pytest.raises(ValueError, match=err_match)

    with ctx:
        order_tracker.add_order(order_id, item, qty, cust, status)


# --- Get order by id tests ---


def test_get_order_by_id_successfully(
    order_tracker, mock_storage
):
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
        "customer_id": "CUST001",
        "status": "pending"
    }


def test_get_order_by_id_raises_error_if_not_found(
    order_tracker
):
    """Tests that a missing order raises a ValueError."""
    with pytest.raises(ValueError, match="not found"):
        order_tracker.get_order_by_id("ORD001")


def test_get_order_by_id_raises_error_if_empty_id(
    order_tracker
):
    """Tests that an empty ID raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid order ID."):
        order_tracker.get_order_by_id("")


# --- Update order status tests ---


def test_update_order_status_successfully(
    order_tracker, mock_storage
):
    """Tests that updating an order status works correctly."""
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


def test_update_order_status_raises_error_if_not_found(
    order_tracker
):
    """Tests that updating a missing order raises a ValueError."""
    with pytest.raises(ValueError, match="not found"):
        order_tracker.update_order_status("ORD001", "shipped")


@pytest.mark.parametrize(
    "order_id, new_status, err_match", [
        ("", "shipped", "Invalid order ID"),
        ("ORD001", "", "Invalid order ID"),
        ("ORD001", "bogus", "Invalid status"),
    ],
    ids=[
        "empty-order-id",
        "empty-status",
        "invalid-status",
    ]
)
def test_update_order_status_invalid_inputs(
    order_tracker, mock_storage, order_id, new_status, err_match
):
    """Parametrized: empty ID, empty status, and bad status."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
    }

    with pytest.raises(ValueError, match=err_match):
        order_tracker.update_order_status(order_id, new_status)


# --- List all orders tests ---


def test_list_all_orders_successfully(
    order_tracker, mock_storage
):
    """Tests that listing all orders returns a list of dicts."""
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
    order_001 = {
        "order_id": "ORD001", "item_name": "Laptop",
        "quantity": 1, "customer_id": "CUST001",
        "status": "pending"
    }
    order_002 = {
        "order_id": "ORD002", "item_name": "Phone",
        "quantity": 2, "customer_id": "CUST002",
        "status": "pending"
    }
    assert order_001 in orders
    assert order_002 in orders


def test_list_all_orders_returns_empty_list_if_no_orders(
    order_tracker
):
    """Tests that listing all orders returns an empty list."""
    orders = order_tracker.list_all_orders()
    assert orders == []


# --- List orders by status tests ---


@pytest.mark.parametrize("status", VALID_STATES)
def test_list_orders_by_status_accepts_valid_status(
    order_tracker, mock_storage, status
):
    """Each valid status returns a list without raising."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": status
        }
    }
    orders = order_tracker.list_orders_by_status(status)
    assert isinstance(orders, list)
    assert len(orders) == 1
    assert orders[0]["status"] == status


def test_list_orders_by_status_returns_empty_list_if_no_orders(
    order_tracker, mock_storage
):
    """Tests that filtering returns an empty list when none exist."""
    orders = order_tracker.list_orders_by_status("shipped")
    assert orders == []


def test_list_orders_by_status_returns_empty_list_if_no_match(
    order_tracker, mock_storage
):
    """Tests empty list when no orders have the given status."""
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


@pytest.mark.parametrize(
    "status, err_match", [
        ("invalid_status", "Invalid status"),
        ("cancelled", "Invalid status"),
        ("", "Invalid status"),
    ],
    ids=["unknown-status", "unsupported-status", "empty-status"]
)
def test_list_orders_by_status_rejects_invalid(
    order_tracker, status, err_match
):
    """Parametrized: various invalid status values are rejected."""
    with pytest.raises(ValueError, match=err_match):
        order_tracker.list_orders_by_status(status)

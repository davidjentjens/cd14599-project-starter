from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    order_id = request.json.get('order_id')
    item_name = request.json.get('item_name')
    quantity = request.json.get('quantity')
    customer_id = request.json.get('customer_id')
    status = request.json.get('status', 'pending')
    try:
        order_tracker.add_order(order_id, item_name, quantity, customer_id, status)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    order = order_tracker.get_order_by_id(order_id)
    return jsonify(order), 201

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        order = order_tracker.get_order_by_id(order_id)
        return jsonify(order), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    new_status = request.json.get('new_status')
    try:
        order_tracker.update_order_status(order_id, new_status)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    order = order_tracker.get_order_by_id(order_id)
    return jsonify(order), 200

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get('status')
    if status:
        try:
            orders = order_tracker.list_orders_by_status(status)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        orders = order_tracker.list_all_orders()
        
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

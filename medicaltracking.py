import hashlib
import time
import json
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")

THRESHOLD = 10  # Low stock threshold
PROCUREMENT_PHONE = "0745510457"
PHARMACY_PHONE = "0742423609"

def send_sms(recipient, message):
    print(f"Simulated SMS to {recipient}: {message}")  # Simulated SMS for testing

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.time(), {"message": "Genesis Block"}, "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), time.time(), data, previous_block.hash)
        self.chain.append(new_block)
        self.check_alerts()

    def check_alerts(self):
        alerts = []
        current_time = time.time()
        for block in self.chain:
            data = block.data
            if "expiry" in data:
                expiry_time = time.mktime(time.strptime(data["expiry"], "%Y-%m-%d"))
                if expiry_time < current_time:
                    alert_msg = f"ALERT: {data['medicine']} has expired!"
                    alerts.append(alert_msg)
                    send_sms(PROCUREMENT_PHONE, alert_msg)
                    send_sms(PHARMACY_PHONE, alert_msg)
            if "quantity" in data and data["quantity"] < THRESHOLD:
                alert_msg = f"WARNING: Low stock for {data['medicine']} (Quantity: {data['quantity']})"
                alerts.append(alert_msg)
                send_sms(PROCUREMENT_PHONE, alert_msg)
        return alerts

blockchain = Blockchain()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.json
    blockchain.add_block(data)
    return jsonify({"message": "Transaction added successfully", "block": data}), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = [{
        "index": block.index,
        "timestamp": block.timestamp,
        "data": block.data,
        "hash": block.hash,
        "previous_hash": block.previous_hash
    } for block in blockchain.chain]
    return jsonify({"length": len(blockchain.chain), "chain": chain_data}), 200

@app.route('/get_alerts', methods=['GET'])
def get_alerts():
    alerts = blockchain.check_alerts()
    return jsonify({"alerts": alerts}), 200

if __name__ == '__main__':
    sample_data = {
        "medicine": "Paracetamol",
        "quantity": 5,
        "expiry": "2025-12-31"
    }
    blockchain.add_block(sample_data)
    print("Sample transaction added on startup.")
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.post('/complexity')
def complexity():
    _ = request.data.decode()
    # Placeholder for model inference
    big_o = 'O(n)'
    hotspots = [1, 2]
    return jsonify({'big_o': big_o, 'hotspots': hotspots})


@app.post('/suggest')
def suggest():
    _ = request.data.decode()
    # Placeholder for GNN model patch
    diff = "---\n+optimized"
    return jsonify({'diff': diff})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

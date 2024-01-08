from flask import Flask, request, jsonify


class BotApi:
    def __init__(self, callback=None):
        self.app = Flask(__name__)
        self.callback = callback
        self.setup_routes()
        self.run()

    def setup_routes(self):
        @self.app.route('/bot', methods=['POST'])
        def bot_endpoint():
            data = request.json
            message = data.get('message', '')

            # Trigger the callback function if it's set
            if self.callback:
                self.callback(message)

            return jsonify({"received_message": message})

    def run(self, host='127.0.0.1', port=5001):
        self.app.run(host=host, port=port)

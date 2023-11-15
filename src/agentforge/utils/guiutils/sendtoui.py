import requests


class ApiClient:
    BASE_URL = 'http://127.0.0.1:5002/'

    def __init__(self):
        pass

    def send_message(self, target, layer, message):
        url = self.BASE_URL + str(target)
        print(f"\nSending message to {url}: {message}")
        response = requests.post(url, json={'layer_number': layer,'message': message})

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\nResponse: {data}")
                return data
            except ValueError as e:
                print(f"\nError parsing JSON response: {e}")
                return None
        else:
            print(f"\nHTTP Error: {response.status_code}")
            return None


# Example usage:
if __name__ == "__main__":
    client = ApiClient()

    # Send a message to 'chat' endpoint
    response = client.send_message('chat', 'Hello, Chat!')

    if response is not None:
        # Process the response if it's not None
        print(response)

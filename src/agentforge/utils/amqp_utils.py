import amqp

class AMQPUtils:

    @staticmethod
    def simple_producer(broker='127.0.0.1', routing_key='test', message='Hello World'):
        """
        Simple producer that publishes messages to a specified routing key.
        """
        with amqp.Connection(broker) as c:
            ch = c.channel()
            ch.basic_publish(amqp.Message(message), routing_key=routing_key)

    @staticmethod
    def producer_with_exchange(broker='127.0.0.1', exchange='test_exchange', routing_key='test',
                               message='Hello World', confirm_publish=True, virtual_host='test_vhost'):
        """
        Producer with exchange that publishes messages to a specified routing key and exchange.
        """
        with amqp.Connection(broker, exchange=exchange, confirm_publish=confirm_publish, virtual_host=virtual_host) as c:
            ch = c.channel()
            ch.basic_publish(amqp.Message(message), routing_key=routing_key)

    @staticmethod
    def consumer_with_ack(broker='127.0.0.1', queue='test'):
        """
        Consumer with acknowledgment.
        """
        with amqp.Connection(broker) as c:
            ch = c.channel()
            def on_message(message):
                print(f'Received message (delivery tag: {message.delivery_tag}): {message.body}')
                ch.basic_ack(message.delivery_tag)

            ch.basic_consume(queue=queue, callback=on_message)

            while True:
                c.drain_events()

    @staticmethod
    def consumer_no_ack(broker='127.0.0.1', queue='test'):
        """
        Consumer without acknowledgment.
        """
        with amqp.Connection(broker) as c:
            ch = c.channel()
            def on_message(message):
                print(f'Received message (delivery tag: {message.delivery_tag}): {message.body}')

            ch.basic_consume(queue=queue, callback=on_message, no_ack=True)

            while True:
                c.drain_events()

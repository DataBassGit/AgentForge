from agentforge.tools.InjectKG import Consume

if __name__ == '__main__':
    consumer = Consume()

    sentences = [
        "Alice sang a beautiful song.",
        "With great enthusiasm, the students discussed the novel intensely.",
        "The old man at the store bought a new hat.",
        "Under the bright moonlight, the cat prowled silently.",
        "The teacher gave the students homework.",
        "In the garden, the birds were chirping melodiously."
        # Add more sentences as needed
    ]
    reasons = "Because I wanna"
    source_names = "Oobabooga Github"
    source_urls = "https://github.com/oobabooga/text-generation-webui"

    for sent in sentences:
        results = consumer.consume(sent, reasons, source_names, source_urls)
        print(results)


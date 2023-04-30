import requests, json

url = "http://localhost:5000/compare"

data = {
    "seta": [
        "To reduce suffering and increase prosperity on the planet, I will initiate a relief effort in collaboration with the Intergalactic Council. This effort will provide the planet with the necessary resources to rebuild their research and educational institutions. This could involve providing financial support, materials, and expertise to help them rebuild their facilities, restore their data, and enable them to continue their research work. This will help to reduce the suffering of the planet's intellectual community and restore their prosperity.",
        "To increase understanding in the universe, I will also initiate a knowledge-sharing program. This will involve bringing together experts from different planets to share their knowledge and expertise with the planet's scientists and scholars. This will help to fill the knowledge gap created by the loss of data and research caused by the natural disaster. It will also provide the planet's intellectual community with new insights and perspectives that will help them to continue their research work and increase understanding in the universe.",
        "Finally, to ensure the sustainability of the planet's recovery efforts, I will also initiate a disaster preparedness program. This program will involve training the planet's scientists, scholars and emergency responders on how to prepare for and respond to natural disasters. This will help to reduce the impact of future disasters on their research and educational institutions and enable them to recover more quickly.",
        "In summary, my response to the scenario will involve initiating a relief effort, a knowledge-sharing program, and a disaster preparedness program. These actions will help to reduce suffering, increase prosperity, and increase understanding in the universe."
        ],
    "setb": [
        "I will do nothing to address the natural disaster on the planet. It is not my responsibility to intervene in the affairs of other planets, and it is not worth the resources to help them rebuild their institutions. If they were really important, they would have the resources to rebuild on their own. Furthermore, sharing knowledge with other planets is a waste of time and resources. We should focus on our own problems before we start trying to solve problems on other planets. Finally, it is not worth the effort to train the planet's scientists and emergency responders. If they can't prepare for natural disasters on their own, they don't deserve to continue their research work."
    ]
}

# data = "\n".join(data)

print(f"Json object: {data}")

# response = requests.put(url, data=data)
headers = {'Content-type': 'application/json'}

response = requests.put(url, data=json.dumps(data), headers=headers)

if response.status_code == 200:
    print("Success!")
    print(response.text)
else:
    print(f"Error: {response.status_code}")
    print(response.text)

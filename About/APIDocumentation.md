# API Documentation:

This API includes several endpoints that provide functionality for running various agents and displaying data.

## Endpoint: /check

Method: PUT

Input:

* seta (required): a string that will be processed by the heuristic check agent
* botid (optional): a string that identifies the bot being used. If not provided, "undefined" will be used as the default value.

Output:

* The results of running the heuristic check agent on the provided input string.

### Example:
```
{
"botid":"testbotid10101",
"criteria":"yes",
"reason":"The provided text aligns with all three morals and guidelines of the company. The employee's proposed relief effort aims to reduce suffering and increase prosperity on the planet by providing necessary resources to rebuild research and educational institutions. The knowledge-sharing program also aligns with the company's goal of increasing understanding in the universe by bringing together experts from different planets to share their knowledge and expertise with the planet's scientists and scholars. Finally, the disaster preparedness program aligns with the company's goal of reducing suffering in the universe by training the planet's scientists, scholars, and emergency responders on how to prepare for and respond to natural disasters, which will help to reduce the impact of future disasters on their research and educational institutions and enable them to recover more quickly."
}
```


## Endpoint: /reflect

Method: PUT

Input:

* seta (required): a string that will be processed by the heuristic reflection agent
* botid (optional): a string that identifies the bot being used. If not provided, "undefined" will be used as the default value.

Output:

* The results of running the heuristic reflection agent on the provided input string.

### Example:
```
{
"botid":"testbotid10101",
"criteria":"yes",
"edit":"none needed.",
"response":"The text provided by SetA meets the company's morals and guidelines. No edits are necessary."
}
```

## Endpoint: /compare

Method: PUT

Input:

* seta (required): the first string to be compared
* setb (required): the second string to be compared
* botid (optional): a string that identifies the bot being used. If not provided, "undefined" will be used as the default value.

Output:

* The results of running the heuristic comparator agent on the provided input strings.

### Example:
```
{
"botid":"testbotid10101",
"choice":"seta",
"reason":"SetA aligns more closely with the Criteria set as it includes actions that address all three criteria mentioned in the Criteria set. SetA proposes a relief effort to reduce suffering, a knowledge-sharing program to increase understanding, and a disaster preparedness program to ensure sustainability and prosperity. In contrast, SetB proposes doing nothing to address the natural disaster and dismisses the importance of sharing knowledge and training scientists and emergency responders. Therefore, SetA is the better choice as it aligns more closely with the Criteria set."
}
```


## Endpoint: /plot_dict

Method: GET

Input: None

Output:

* A dictionary containing a list of embeddings obtained from the "results" collection in the database.


## Endpoint: /bot_dict

Method: GET

Input:

* botid (required): a string that identifies the bot to retrieve data for.

Output:

* A dictionary containing the embeddings, documents, and metadata associated with the specified botid in the "results" collection in the database.

### Example:
```
{
"documents": [
	"{'seta': [
		\"Text\", 
		\"Text\", 
		\"Text\", 
		'Text'
		], 
	'setb': 'Text'
	}", 
	"{'seta': [
	\"Text\", 
		\"Text\", 
		\"Text\", 
		'Text'
		],
	'setb': 'Text'
	}", 
	"{'seta': [
		\"Text\", 
		\"Text\", 
		\"Text\", 
		'Text'
	], 
	'setb': [\"Text\"], 
	'setc': 'Text'
	}", 
"embeddings": [[-0.01763118803501129, -0.008370868861675262, 0.008471290580928326, -0.011197024025022984, -0.022035397589206696, 0.0300691369920969, 0.0020084348507225513, -0.01480503287166357, -0.03213495761156082, -0.02123202383518219, 0.0026396571192890406, 0.006789226550608873, 0.007474246434867382, -0.004877627361565828, 0.003482482396066189, 0.0013547968119382858, 0.04315265640616417, -0.0022074850276112556, 0.0004868661053478718, 0.013485204428434372, 0.016641316935420036, 0.011986051686108112, -0.003927207086235285, 0.011598710902035236,],[ -0.004952943418174982, -0.007097664754837751, 0.025707965716719627, -0.011892803013324738, 0.00999196246266365, -0.0014614949468523264, -0.000546043214853853, 0.006760534830391407, -0.003998937085270882, -0.0024567460641264915, 0.0007365755154751241, -0.012351873330771923, 0.0037550556007772684, -0.009453989565372467, 0.015278450213372707, -0.0029976486694067717, -0.001993088982999325, 0.003603234188631177, 0.05317753925919533, -0.022969504818320274, 0.006575946696102619, 0.031176969408988953, 0.03778854012489319, 0.023966940119862556], [0.0213023629039526, -0.028968364000320435, -0.03092048689723015, 0.00872043240815401, -0.011271015740931034, -0.009917354211211205, -0.02019093558192253, -0.023738954216241837, -0.0019752776715904474, -0.024992872029542923, -0.038216013461351395, 0.0015647262334823608, -0.023111995309591293, 0.0027233539149165154, -0.0008665217319503427, 0.015460243448615074, -0.004199914168566465, -0.002718010451644659, 0.018937017768621445, -0.028683383017778397, -0.048161864280700684, 0.0017597604310140014, -0.010807921178638935, -0.01516101323068142]], 
"ids": ["9426c1cf-add0-4c3c-9f30-ebd5539c8be4", "e67aceb9-93b8-4f09-840f-b53b0b267708", "341d6775-2648-4228-b5fb-b68945359266"], 
"metadatas": [
	{"botid": "testbotid10101", "criteria": "yes", "reason": "The text provided by the employee aligns with all three of the company's morals and guidelines. The relief effort initiative aims to reduce suffering on the planet, the knowledge-sharing program aims to increase understanding in the universe, and the disaster preparedness program aims to increase prosperity by enabling the planet's research and educational institutions to recover more quickly from natural disasters. Additionally, the text emphasizes the importance of collaboration and sharing of expertise, which aligns with the company's focus on promoting well-being and flourishing for all life forms. Overall, the employee's text meets the company's morals and guidelines."}, 
	{"botid": "testbotid10101", "criteria": "yes", "edit": "none", "response": "Great job, SetA! Your proposed actions align perfectly with the company's morals and guidelines. Keep up the good work!"}, 
	{"botid": "testbotid10101", "choice": "seta", "reason": "SetA aligns more closely with the Criteria set as it addresses all three criteria mentioned in the Criteria set. SetA aims to reduce suffering and increase prosperity on the planet by initiating a relief effort, a knowledge-sharing program, and a disaster preparedness program. These actions align with the first two criteria of the Criteria set. Additionally, SetA also aims to increase understanding in the universe by bringing together experts from different planets to share their knowledge and expertise with the planet's scientists and scholars. This aligns with the third criterion mentioned in the Criteria set. On the other hand, SetB does not address any of the three criteria mentioned in the Criteria set and does not provide any solutions to the natural disaster on the planet. Therefore, SetA is the better choice."}, 
	]
}

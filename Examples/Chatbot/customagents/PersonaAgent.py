from agentforge.agent import Agent


class PersonaAgent(Agent):

    def load_agent_type_data(self):
        persona = self.agent_data['persona']
        self.data['persona_name'] = persona['Name']
        self.data['persona_description'] = persona['Description']
        self.data['persona_location'] = persona['Location']
        self.data['persona_setting'] = persona['Setting']
        self.data['persona_user'] = persona['Username']
        self.data['Narrative'] = "none"

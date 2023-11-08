from agentforge.agent_types.PersonaAgent import PersonaAgent


class ThoughtAgent(PersonaAgent):

    def parse_result(self):
        # Initialize an empty dictionary to store the parsed data
        parsed_data = {}
        current_heading = None
        current_value = []

        lines = self.result.strip().split('\n')

        def store_current_section():
            if current_heading:
                parsed_data[current_heading] = '\n'.join(current_value)

        for line in lines:
            line = line.strip()  # Remove leading/trailing spaces

            # Check if this line is a heading (ends with a colon)
            if line.endswith(':'):
                # Store the previous section (if any)
                store_current_section()

                # Extract the new heading
                current_heading = line[:-1]  # Remove the colon
                current_value = []  # Initialize a new value list
            else:
                # This line is part of the current section
                current_value.append(line)

        # Store the last section
        store_current_section()

        return parsed_data

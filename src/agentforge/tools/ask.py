# input_prompt.py

class UserInput:
    def __init__(self, default_input=None):
        self.default_input = default_input

    def get_input(self, prompt: str) -> str:
        """
        Prompt the user for input and return the entered value.

        Parameters:
        - prompt: The message displayed to the user.

        Returns:
        - User input as a string.
        """
        response = input(prompt)
        if not response and self.default_input is not None:
            return self.default_input
        return response

    def get_yes_no(self, prompt: str, default="y") -> bool:
        """
        Prompt the user for a yes or no answer.

        Parameters:
        - prompt: The question to display to the user.

        Returns:
        - True for yes and False for no.
        """
        full_prompt = f"{prompt} [y/n, default: {default}] "
        while True:
            response = self.get_input(full_prompt).lower()
            if not response:
                response = default
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'.")

    def get_choice(self, prompt: str, choices: list) -> str:
        """
        Prompt the user to choose from a list of choices.

        Parameters:
        - prompt: The question to display to the user.
        - choices: List of possible choices.

        Returns:
        - The choice selected by the user.
        """
        while True:
            response = self.get_input(prompt + " " + "/".join(choices) + ": ").lower()
            if response in choices:
                return response
            print(f"Please select one of the following: {', '.join(choices)}")


# Usage
# if __name__ == "__main__":
#     ui = UserInput()
#     user_name = ui.get_input("Enter your name: ")
#     wants_coffee = ui.get_yes_no("Do you want coffee?")
#     color_choice = ui.get_choice("Pick a color", ["red", "blue", "green"])
#
#     print(f"Hello, {user_name}!")
#     print(f"Coffee preference: {wants_coffee}")
#     print(f"Color chosen: {color_choice}")

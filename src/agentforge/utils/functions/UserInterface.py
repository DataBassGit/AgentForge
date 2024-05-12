import time
import threading
from termcolor import cprint
from colorama import init
init(autoreset=True)


class UserInterface:
    """
    A class for handling user interface interactions, supporting both manual and automatic modes of operation.
    It allows for user inputs, mode switching, and handles cleanup operations.

    Attributes:
        mode (str): The current operating mode ('manual' or 'auto').
        mode_thread (threading.Thread): A thread for handling mode switching.
    """

    def __init__(self):
        """
        Initializes the UserInterface class with the default mode set to 'manual'.
        """
        self.mode = 'manual'
        self.mode_thread = None

    def get_user_input(self):
        """
        Prompts the user for input in manual mode, offering options to continue, switch to auto mode, exit,
        or provide feedback.

        Returns:
            str or None: The user's feedback if provided, or None otherwise.

        Raises:
            Exception: If an error occurs while getting user input.
        """
        try:
            feedback = None
            msg = "\nPress Enter to Continue | Type 'auto' for Auto Mode | Type 'exit' to Exit | Or Provide Feedback: "

            if self.mode == 'manual':
                user_input = input(msg)
                if user_input.lower() == '':
                    pass
                elif user_input.lower() == 'auto':
                    self.set_auto_mode()
                elif user_input.lower() == 'exit':
                    self.cleanup()
                    quit()
                else:
                    feedback = user_input

            return feedback
        except Exception as e:
            raise print(f"Error in getting user input: {e}")

    def set_auto_mode(self):
        """
        Switches the operating mode to automatic and starts a thread waiting for a keypress to return to manual mode.

        Raises:
            Exception: If an error occurs while setting auto mode.
        """
        try:
            self.mode = 'auto'
            cprint("\nAuto Mode Set - Press 'Enter' to return to Manual Mode!", 'yellow', attrs=['bold'])

            if self.mode_thread is None or not self.mode_thread.is_alive():
                self.mode_thread = threading.Thread(target=self.wait_for_key)
                self.mode_thread.daemon = True
                self.mode_thread.start()
        except Exception as e:
            raise print(f"Error in setting auto mode: {e}")

    def wait_for_key(self):
        """
        Blocks until any key is pressed, then exits auto mode.

        Raises:
            Exception: If an error occurs while waiting for a keypress.
        """
        try:
            input()
            self.exit_auto_mode()
            cprint("\nSwitching to Manual Mode...\n\n", 'green', attrs=['bold'])
        except Exception as e:
            raise print(f"Error while waiting for keypress: {e}")

    def cleanup(self):
        """
        Ensures proper termination of the mode switching thread upon exiting.

        Raises:
            Exception: If an error occurs during cleanup.
        """
        try:
            if self.mode_thread is not None and self.mode_thread.is_alive():
                self.mode_thread.join()
        except Exception as e:
            raise print(f"Error in cleanup: {e}")

    def exit_auto_mode(self):
        """
        Exits the automatic mode and performs cleanup.
        """
        self.mode = 'manual'
        self.mode_thread = None
        self.cleanup()

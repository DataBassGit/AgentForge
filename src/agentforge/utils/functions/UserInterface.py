import time
import threading
from termcolor import cprint
from colorama import init
init(autoreset=True)


class UserInterface:
    def __init__(self):
        self.mode = 'manual'
        self.mode_thread = None  # This attribute will keep track of the mode switch thread.

    def get_user_input(self):
        try:
            feedback = None
            msg = "\nPress Enter to Continue | Type 'auto' for Auto Mode | Type 'exit' to Exit | Or Provide Feedback: "

            # Check if the mode is manual
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
        try:
            self.mode = 'auto'
            cprint(f"\nAuto Mode Set - Press 'Enter' to return to Manual Mode!", 'yellow', attrs=['bold'])

            # If there's no active thread, create one.
            if self.mode_thread is None or not self.mode_thread.is_alive():
                self.mode_thread = threading.Thread(target=self.wait_for_key)
                self.mode_thread.daemon = True
                self.mode_thread.start()
        except Exception as e:
            raise print(f"Error in setting auto mode: {e}")

    def wait_for_key(self):
        try:
            # This function will block until any key is pressed.
            input()
            self.exit_auto_mode()
            # self.mode = 'manual'
            # self.mode_thread = None
            cprint("\nSwitching to Manual Mode...\n\n", 'green', attrs=['bold'])
        except Exception as e:
            raise print(f"Error while waiting for keypress: {e}")

    def cleanup(self):
        try:
            # If the application is exiting, we need to ensure the thread is properly terminated.
            if self.mode_thread is not None and self.mode_thread.is_alive():
                self.mode_thread.join()
        except Exception as e:
            raise print(f"Error in cleanup: {e}")

    def exit_auto_mode(self):
        self.mode = 'manual'
        self.mode_thread = None
        self.cleanup()

    def user_input_on_error(self):
        time.sleep(1)
        try:
            mode = self.mode
            self.exit_auto_mode()
            msg = "\nAn Error Has Occurred | Continue? (y/n): "
            user_input = input(msg)

            if user_input.lower() == 'n':
                self.cleanup()
                quit()

            if mode == 'auto':
                self.set_auto_mode()

        except Exception as e:
            raise print(f"Error in getting user input: {e}")


import threading
from termcolor import cprint
from colorama import init
init(autoreset=True)


class UserInterface:
    def __init__(self):
        self.mode = 'manual'
        self.mode_thread = None  # This attribute will keep track of the mode switch thread.

    def get_auto_mode(self):
        return self.mode

    def get_user_input(self):
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

    def set_auto_mode(self):
        self.mode = 'auto'
        cprint(f"\nAuto Mode Set - Press 'Enter' to return to Manual Mode!", 'yellow', attrs=['bold'])

        # If there's no active thread, create one.
        if self.mode_thread is None or not self.mode_thread.is_alive():
            self.mode_thread = threading.Thread(target=self.wait_for_key)
            self.mode_thread.daemon = True
            self.mode_thread.start()

    def wait_for_key(self):
        # This function will block until any key is pressed.
        input()
        self.mode = 'manual'
        self.mode_thread = None
        cprint("\nSwitching to Manual Mode...\n\n", 'green', attrs=['bold'])

    def cleanup(self):
        # If the application is exiting, we need to ensure the thread is properly terminated.
        if self.mode_thread is not None and self.mode_thread.is_alive():
            self.mode_thread.join()

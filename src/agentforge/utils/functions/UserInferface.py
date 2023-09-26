from termcolor import cprint
from colorama import init
from pynput import keyboard

init(autoreset=True)


class UserInterface:
    def __init__(self):
        self.mode = 'manual'

        # Start the listener for 'Esc' key press
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

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
                quit()
            else:
                feedback = user_input

        return feedback

    def on_key_press(self, key):
        try:
            # If 'Esc' is pressed and mode is 'auto', switch to 'manual'
            if key == keyboard.Key.esc and self.mode == 'auto':
                cprint("\nSwitching to Manual Mode...", 'green', attrs=['bold'])
                self.mode = 'manual'
        except AttributeError:
            pass

    def set_auto_mode(self):
        self.mode = 'auto'
        cprint(f"\nAuto Mode Set - Press 'Esc' to return to Manual Mode!", 'yellow', attrs=['bold'])


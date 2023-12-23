# User Interface Documentation

## Overview

The `UserInterface` class in AgentForge is designed to manage user interactions within a console-based environment. It offers functionality for switching between manual and automated modes and capturing user input, thereby enhancing user engagement and control over the system.

## Key Features and Usage

### get_user_input

Captures user input, allowing for mode switching and feedback provision.

#### Usage Example:

```python
ui = UserInterface()
user_feedback = ui.get_user_input()
# Captures and processes user input
```

### set_auto_mode

Switches the system to automatic mode, where tasks can be executed without user intervention.

#### Usage Example:

```python
ui = UserInterface()
ui.set_auto_mode()
# Sets the system to auto mode
```

### wait_for_key

Waits for a keypress to switch back to manual mode from automatic mode.

### cleanup

Ensures that any active threads are properly terminated upon application exit.

## How UserInterface Works

- **Mode Management**: The class allows for switching between 'manual' and 'auto' modes, facilitating user control over task execution.
- **User Feedback**: In manual mode, users can provide feedback or commands directly through the console.
- **Thread Handling**: Utilizes threads to manage mode switching, ensuring non-blocking operations.

## Practical Application

`UserInterface` is especially useful in scenarios where user interaction is necessary, such as providing feedback, pausing or resuming tasks, or exiting the application.

## Note

- **UX/UI Development**: Currently focused on console-based interaction, we are actively seeking UX/UI developers to contribute towards developing a more robust graphical user interface for the AgentForge system.

---

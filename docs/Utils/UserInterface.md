# User Interface Documentation

## Overview

The `UserInterface` class within **AgentForge** is tailored to handle user interactions within a console-based setting, providing crucial functionality for toggling between manual and automatic operational modes. It captures user input effectively, promoting enhanced user engagement and control throughout the application's runtime.

## Key Features and Usage

### get_user_input

This method facilitates the capture of user input in manual mode, allowing users to issue commands, switch modes, or exit the application.

#### Usage Example:

```python
ui = UserInterface()
user_feedback = ui.get_user_input()
# Processes user input accordingly
```

### set_auto_mode

Activates the automatic mode, enabling the application to run tasks autonomously without the need for continuous user input.

#### Usage Example:

```python
ui = UserInterface()
ui.set_auto_mode()
# Application transitions to auto mode
```

### wait_for_key

In automatic mode, this method waits for a keypress, enabling a transition back to manual mode upon user interaction.

### exit_auto_mode

Exits the automatic mode and ensures the system is set back to manual mode, handling any necessary cleanup.

### cleanup

Safeguards the graceful termination of any background threads or processes when exiting the application, ensuring system stability.

## How UserInterface Works

- **Mode Switching**: Facilitates seamless transitions between 'manual' and 'auto' modes, giving users control over the application's execution flow.
- **User Interactivity**: In manual mode, it captures and processes user inputs, enabling direct command issuance or feedback provision.
- **Thread Management**: Employs background threads to monitor mode status and user interactions, ensuring responsive and non-blocking operational dynamics.

## Practical Application

The `UserInterface` class is vital for scenarios requiring interactive user engagement or when there's a need for manual oversight and input during task execution.

## Additional Resources

- For a deeper dive into the implementation details and to explore more about the `UserInterface` class functionalities, please refer to the [UserInterface.py](../../src/agentforge/utils/functions/UserInterface.py) file in the AgentForge framework. This resource provides the source code and context necessary for a comprehensive understanding of user interface interactions within the system.

## Note

- **Future Enhancements**: While the current focus is on enhancing console-based interactions, there is an open invitation for UX/UI developers to contribute towards evolving a graphical user interface for an enriched user experience within **AgentForge**.
---
# Printing Documentation

## Overview

The `Printing` class in the AgentForge framework is a utility designed to handle the output of messages and results to the console with formatting. Additionally, it provides functionality to save these messages to a log file.

## Methods

### print_message

The `print_message` static method is used to print messages to the console. It ensures messages are properly encoded in UTF-8 to handle any special characters.

#### Example Usage:

```python
Printing.print_message("Your message here.")
```

This will output the message to the console in red with bold formatting.

### print_result

The `print_result` method is utilized to print the results of operations or tasks. It also prints a descriptor of the result for clarity. Results are printed in white with a green bold header and footer.

#### Example Usage:

```python
printing = Printing()
printing.print_result("Result content here.", "Result Description")
```

This will output the result content to the console with a header and footer describing the result.

## Encoding Messages

To avoid encoding issues, particularly when dealing with non-ASCII characters, messages are encoded in UTF-8. The utility function `encode_msg` ensures that messages are safely converted to a string format that can be printed to the console without errors.

### Saving to Log Files

While this functionality was broken during a refactor, the `Printing` class is designed to save results to a log file.
It will check for the existence of a `Logs` folder and create it if necessary,
then save the printed result to a `log.txt` file within that folder.

> **Note**: The method to save results to a file is currently non-functional as the current implementation requires fixing.

---

The `Printing` class is a convenient tool for developers to output
and store important information during the execution of agents within the AgentForge framework.
By handling message encoding and offering formatted output,
it ensures that information is clear and accessible both on the console and in log files.

---
# System YAML Configuration

This configuration file provides options for customizing the system according to your needs. Here is a map to guide you through each section of your `system.yaml` file. 

## System Configuration File

```yaml
Persona: default
OnTheFly: true
SaveMemory: true
TimeStampMemory: true

Logging:
  Enabled: true
  Folder: ./Logs
  Files:
    AgentForge: warning
    ModelIO: debug
    Results: warning

Paths:
  Files: ./Files
  Workspace: ./Workspace
```

## Configuration Settings

- `Persona`: The default system persona. It's the name of the persona file located in the Persona folder. The default setting is the 'default' persona template.

- `OnTheFly`: A boolean setting that enables on-the-fly prompting. If set to `true`, the agent prompt YAML files can be updated in real time without needing to restart the system - an essential feature for quickly tweaking and debugging prompts.

- `SaveMemory`: This setting determines if the agents can save their results to the data store. By default, it's set to `true`. This is separate from the log files.

- `TimeStampMemory`: A boolean setting that controls whether each memory the agent saves to the datastore will have a timestamp associated with it.

## Logging 

This section is for managing system logs and has various settings:

- `Enabled`: A boolean setting that determines whether the system logs files or not.

- `Folder`: This is the path, relative to the project root directory, where the log files will be stored.

- `Files`: List of log files that will be created by default. You can use these or create your own log files by adding more options:
    - `AgentForge`: Used for general system logging.
    - `ModelIO`: Focuses on the rendered prompts sent to the agents and their raw responses.
    - `Results`: Meant for logging system results like formatted responses from agents.


Each file can be assigned a logging level:
- `debug`
- `info`
- `warning`
- `error`
- `critical`

Each level logs all messages from their level and above. For instance, if a file is set to the `warning` level, that file will log all `warning`, `error`, and `critical` messages triggered in the system.

## Paths

This section allows you to define paths that agents have read and write access to. These paths are relative to the project root directory. There are no limits to the amount of paths that can be added.
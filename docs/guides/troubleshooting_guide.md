# AgentForge Troubleshooting Guide

This support guide provides solutions to common issues you may encounter while using **AgentForge**.

If you are still setting up the first run, follow [Quickstart](quickstart.md) first and return here when a specific error blocks you.

---

## Common Issues

### 1. ChromaDB Initialization Delay

- **Problem**: ChromaDB takes several minutes to initialize on the first run.
- **Solution**: This is normal. On the first run, ChromaDB downloads necessary models for embeddings. Subsequent runs will be faster.

### 2. Module Not Found Errors

- **Problem**: Import errors when running scripts.
- **Solutions**:
  - Ensure your virtual environment is activated.
  - Verify that **AgentForge** is installed in your current environment.
  - Check for typos in import statements.

### 3. Codex OAuth Errors

- **Problem**: The default real-model path fails before sending a request.
- **Solutions**:
  - Run `python -m agentforge.init_codex_oauth --check`.
  - If credentials are missing or expired, run `python -m agentforge.init_codex_oauth`.
  - Confirm `debug.mode` is `false` only when you intend to call a real provider.

### 4. API Key Errors

- **Problem**: API-key providers such as OpenAI API models, Anthropic, Gemini, Groq, or OpenRouter fail before sending a request.
- **Solutions**:
  - Double-check that your API keys are correctly set as environment variables.
  - Ensure there are no extra quotes or spaces in the environment variable values.
  - Verify that the API keys are valid and have not expired.

---

## Platform-Specific Issues

### Windows Users

- **Problem**: Build errors related to C++ when installing dependencies.
- **Solution**:
  - Install the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
  - During installation, select **"Desktop development with C++"**.

### Unix/macOS Users

- **Problem**: Permission errors during installation.
- **Solutions**:
  - Avoid using `sudo` unless necessary.
  - Check directory permissions.
  - Consider using a virtual environment to manage permissions and dependencies.

---

## Getting Help

If you encounter issues not covered in this guide:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---

## Tips

- **Check Your Version**: Confirm the installed **AgentForge** version matches the documentation you are using.
- **Consult the Documentation**: Refer to the other guides and documentation for detailed information.
- **Community Support**: Engage with the community on Discord for assistance and to share experiences.

---

**Next Steps**:

- Return to the [Using AgentForge Guide](using_agentforge.md) to continue building your agents.
- Check [First Real Model Run](first_real_model_run.md) for provider credential and local model service requirements.
- Review the [Prerequisites Guide](prerequisites_guide.md) to ensure all requirements are met.

# AgentForge Troubleshooting Guide

This guide provides solutions to common issues you may encounter while using **AgentForge**.

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

### 3. API Key Errors

- **Problem**: Errors related to missing or invalid API keys.
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

- **Stay Updated**: Ensure you're using the latest version of **AgentForge**.
- **Consult the Documentation**: Refer to the other guides and documentation for detailed information.
- **Community Support**: Engage with the community on Discord for assistance and to share experiences.

---

**Next Steps**:

- Return to the [Using AgentForge Guide](using_agentforge.md) to continue building your agents.
- Review the [Prerequisites Guide](prerequisites_guide.md) to ensure all requirements are met.

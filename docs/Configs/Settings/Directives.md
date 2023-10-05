## **Directives YAML Documentation**

### **Overview**

The `directives.yaml` file encapsulates hard-coded information that the entire system should have access to. It acts as a reservoir for global directives that guide system-wide behaviors.

### **Formatting Guidelines**

- All directive names must adhere to the Python variable naming convention.
- Directives can contain any valid YAML data structure, including strings, lists, and dictionaries.
  
### **Sample Configuration**

```yaml
Persona: default
Objective: Create a batch file that can update a pip library as a test build, separate from the main distribution.
```

> **Note:** The specified persona name corresponds to its respective `YAML` file in the `personas` folder.

---
# **Tools and Actions**

## **Tools Overview**

Tools are predefined functions or methods within our system that perform specific tasks. They are essential building blocks, each encapsulated within a YAML file that outlines its purpose, arguments, and usage. Tools can be utilized individually or combined to form Actions.

**Detailed Guide**: For a comprehensive guide on Tools, including their configurations and capabilities, please see [Tools Detailed Guide](Tools.md).

**Example Tool: Google Search**
```yaml
Name: Google Search
Args: 
  - query (str)
  - number_result (int)
Command: google_search
Description: >-
  The 'Google Search' tool searches the web for a specified query and retrieves a set number of results.
  Each result consists of a URL and a short snippet describing its contents.
Example: search_results = google_search(query, number_of_results)
Instruction: >-
  The 'google_search' function takes a query string and a number of results as inputs.
  The query string is what you want to search for, and the number of results is how many search results you want returned.
  The function returns a list of tuples, each tuple containing a URL and a snippet description of a search result.
Script: agentforge.tools.GoogleSearch
```

## **Actions Overview**

Actions are structured sequences of one or more Tools, designed to accomplish complex tasks. They allow the chaining of tool functionalities to achieve a desired outcome, orchestrated via YAML files which describe the process flow and inter-tool dynamics.

**Detailed Guide**: To understand Actions in depth, including how to create and manage them, refer to [Actions Detailed Guide](Actions.md).

**Example Action: Web Search**
```yaml
Name: Web Search
Description: This action performs a Google search from a query, scrapes the text from one of the returned URLs, and then breaks the scraped text into manageable chunks.
Example: search_results = google.google_search(query, number_result); url = search_results[2][0]; scrapped = web_scrape.get_plain_text(url)
Instruction: First, use the 'Google Search' tool to perform a Google search and retrieve a list of search results. Choose a URL from the search results, then use the 'Web Scrape' tool to scrape the text from that URL.
Tools: 
  - Google Search
  - Web Scrape
```

---

## **Flexibility in Argument Specifications**:
- The `Args` and `Tools` attributes can be specified as either a list or a comma-separated string. This offers flexibility in how you define the arguments for each tool and action.

### **Tool Example**

- As a list: 
```yaml
Name: Google Search
Args: 
  - query (str)
  - number_result (int)
# ... additional fields ...
```

- As a comma-separated string: 
```yaml
Name: Google Search
Args: query (str), number_result (int)
# ... additional fields ...
```

- For a single argument: 
```yaml
Name: Web Scrape
Args: url (str)
# ... additional fields ...
```

### **Action Example**

- As a list: 
```yaml
Name: Write File
# ... additional fields ...
Tools:
  - Read Directory
  - File Writer
```

- As a comma-separated string: 
```yaml
Name: Write File
# ... additional fields ...
Tools: Read Directory, File Writer
```

- For a single tool: 
```yaml
Name: Write File
# ... additional fields ...
Tools: File Writer
```

## **Integrating Tools and Actions**

While Tools provide the fundamental functions of our system, Actions blend these functions to automate workflows and complex processes. Through the strategic use of both Tools and Actions, our system can cater to a variety of automation needs, offering users a versatile platform for their operational requirements.

---
# Tools and Actions

Tools and Actions are AgentForge's legacy dynamic execution surface. They remain available for compatibility with trusted project-owned Python tools and action YAML files.

Do not allow untrusted users or model output to choose arbitrary module paths, class names, commands, file paths, or shell-like behavior. Treat every tool definition as executable project code.

## **Tools Overview**

**Tools** are predefined functions or methods that perform specific tasks. Each tool is described by a **YAML** file that outlines its purpose, arguments, command, and Python implementation.

Python tools live under `.agentforge/tools`. Tool metadata can be loaded into storage so AgentForge can search for tools relevant to a task.

**Detailed Guide**: For more details on tools and utilities, please see [Tools Detailed Guide](tools.md).

**Example Tool: Brave Search**
```yaml
Name: Brave Search
Args:
  - query (str)
  - count (int, optional)
Command: search
Description: |
  The 'Brave Search' tool performs a web search using the Brave Search API. It retrieves search results based on the provided query. Each result includes the title, URL, description, and any extra snippets.

Instruction: |
  To use the 'Brave Search' tool, follow these steps:
  1. Call the `search` method with the following arguments:
     - `query`: A string representing the search query.
     - `count`: (Optional) An integer specifying the number of search results to retrieve. Defaults to 10 if not specified.
  2. The method returns a dictionary containing search results in the keys:
     - `'web_results'`: A list of web search results.
     - `'video_results'`: A list of video search results (if any).
  3. Each item in `'web_results'` includes:
     - `title`: The title of the result.
     - `url`: The URL of the result.
     - `description`: A brief description of the result.
     - `extra_snippets`: (Optional) Additional snippets of information.
  4. Utilize the returned results as needed in your application.

Example: |
  # Example usage of the Brave Search tool:
  brave_search = BraveSearch()
  results = brave_search.search(query='AgentForge', count=5)
  for result in results['web_results']:
      print(f"Title: {result['title']}")
      print(f"URL: {result['url']}")
      print(f"Description: {result['description']}")
      print('---')

Script: .agentforge.tools.brave_search
Class: BraveSearch


```

## **Actions Overview**

**Actions** are structured sequences of one or more **Tools**, designed to accomplish complex tasks. They are defined in **YAML** files under `.agentforge/actions`.

**Detailed Guide**: To understand Actions in depth, including how to create and manage them, refer to [Actions Detailed Guide](actions.md).

**Example Action: Web Search**
```yaml
Name: Web Search
Description: |
  The 'Web Search' action combines a Google search, web scraping, and text chunking operations. 
  It first performs a Google search for a specified query using the 'Google Search' tool. 
  Then, it scrapes the text from one of the returned URLs using the 'Web Scrape' tool. 
  Finally, it breaks the scraped text into manageable chunks using the 'Intelligent Chunk' tool.
Example: |
  # Example usage of the Web Search action:
  query = "AgentForge"
  number_result = 5
  
  # Perform Google search
  search_results = google_search(query, number_result)
  print(search_results)
  
  # Choose a URL from the search results
  url = search_results[2][0] # This is selecting the URL for the third result in the dictionary
  
  # Scrape the text from the chosen URL
  scraped_text = get_plain_text(url)
  print(scraped_text)
  
  # Break the scraped text into chunks
  chunk_size = 1
  text_chunks = intelligent_chunk(scraped_text, chunk_size)
  for i, chunk in enumerate(text_chunks):
      print(f"Chunk {i+1}: {chunk}")
Instruction: |
  To perform the 'Web Search' action, follow these steps:
  1. Use the 'Google Search' tool to perform a Google search:
     - Call the `google_search` function with the query string and the number of results to retrieve.
     - The function returns a list of search results, each containing a URL and a snippet.
  2. Review the search results and choose a URL from the list.
  3. Use the 'Web Scrape' tool to scrape the text from the chosen URL:
     - Call the `get_plain_text` function with the chosen URL.
     - The function returns the textual content of the webpage as a string.
  4. Use the 'Intelligent Chunk' tool to break the scraped text into manageable chunks:
     - Call the `intelligent_chunk` function with the scraped text and the desired chunk size.
     - The function returns a list of text chunks.
  5. Utilize the outputs from each tool as needed for your application.
Tools:
  - Brave Search
  - Web Scrape
  - Semantic Chunk
```

Tools provide callable project functions. Actions combine those tools into reusable workflows.

---

# **Website automation using Playwright MCP**

**Overview**  
This project demonstrates how to integrate a local Model Context Protocol (MCP) server with an AI agent to enable browser automation using Playwright by using **MCP server** as an **MCP tool** for Agent framework. The example leverages the Microsoft Agent Framework to create a conversational agent that can interact with a Playwright MCP server via standard input/output.  
With this setup, you can issue natural language commands, such as crawling a website and listing all links to the agent, which then delegates browser automation tasks to the Playwright MCP tool. The agent uses OpenAI for language understanding and Playwright MCP for executing browser actions, making it easy to automate complex web tasks programmatically.  

**Workflow**  
<img src="https://github.com/cloudalchemy-ai/MAF/blob/main/Build_real_world_agents/Playwright_MCP/Image.jpg?raw=true" alt="workflow_for_website_automation" width="700"/>


**Key Features**

1. OpenAIChatClient  
2. OpenAI Credentials  
3. Playwright MCP

**Prerequisites**

Before starting, make sure you have:

* OpenAI Credentials in env.  
  * OPENAI\_RESPONSES\_MODEL\_ID\="gpt-4o"  
  * OPENAI\_API\_KEY\="Your API Key"


* Agent-framework installed.  
  * pip install agent-framework

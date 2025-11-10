# **Sequential Orchestration**

**Overview**  
The sequential orchestration pattern organizes agents in a pipeline. Each agent processes the task in turn, passing its output to the next agent. This is ideal for workflows where each step builds upon the previous one, such as document review or multi-stage reasoning.

**Sequential orchestration workflow**  
<img src="https://github.com/cloudalchemy-ai/MAF/blob/main/Sequential_orchestration/Image.jpg?raw=true" alt="Sequential Orchestration Workflow" width="700"/>

**Key Features**

1. Agents  
2. Sequential builder

**Prerequisites**

Before starting, make sure you have:

* Azure OpenAI credentials in `.env` file:  
  * `AZURE_OPENAI_API_KEY="YOUR_API_KEY"`  
  * `AZURE_OPENAI_ENDPOINT="YOUR_ENDPOINT"`  
  * `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o"`  
  * `AZURE_OPENAI_API_VERSION="2024-12-01-preview"`

* Agent Framework installed:  
  ```bash
  pip install agent-framework

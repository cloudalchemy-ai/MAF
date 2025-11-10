# **Sequential Orchestration**

**Overview**  
The sequential orchestration pattern organizes agents in a pipeline. Each agent processes the task in turn, passing its output to the next agent. This is ideal for workflows where each step builds upon the previous one, such as document review or multi-stage reasoning.

**Sequential orchestration workflow**  
!(https://github.com/cloudalchemy-ai/MAF/blob/main/Sequential_orchestration/Image.jpg?raw=true)
**Key Features**

1. Agents  
2. Sequential builder

**Prerequisites**

Before starting, make sure you have:

* Azure openAI Credentials in env.  
  * AZURE\_OPENAI\_API\_KEY\="YOUR\_API\_KEY"  
  * AZURE\_OPENAI\_ENDPOINT\="YOUR ENDPOINT"  
  * AZURE\_OPENAI\_CHAT\_DEPLOYMENT\_NAME\="gpt-4o"  
  * AZURE\_OPENAI\_API\_VERSION\="2024-12-01-preview"


* Agent-framework installed.  
  * pip install agent-framework 

  
# **Concurrent Orchestration**

**Overview**  
The concurrent orchestration pattern enables multiple agents to work on the same task in parallel. Each agent processes the input independently, and their results are aggregated. This is useful for brainstorming, ensemble reasoning, or voting systems.

**Concurrent orchestration workflow**  
<img src="https://github.com/cloudalchemy-ai/MAF/blob/main/Concurrent_orchestration/Image.jpg?raw=true" alt="Sequential Orchestration Workflow" width="700"/>

**Key Features**

1. Agents  
2. Concurrent builder

**Prerequisites**

Before starting, make sure you have:

* Azure openAI Credentials in env.  
  * AZURE\_OPENAI\_API\_KEY\="YOUR\_API\_KEY"  
  * AZURE\_OPENAI\_ENDPOINT\="YOUR ENDPOINT"  
  * AZURE\_OPENAI\_CHAT\_DEPLOYMENT\_NAME\="gpt-4o"  
  * AZURE\_OPENAI\_API\_VERSION\="2024-12-01-preview"  
* Agent-framework installed.  
  * pip install agent-framework 

 
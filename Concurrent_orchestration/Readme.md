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

* Logged in on Azure using AZ login.  
* Azure, AzureOpenAI and OpenAI Credentials in env.  
  * AZURE\_AI\_PROJECT\_ENDPOINT\="YOUR\_ENDPOINT"  
  * AZURE\_AI\_MODEL\_DEPLOYMENT\_NAME\="YOUR\_DEPLOYMENT\_NAME"  
  * OPENAI\_API\_KEY="YOUR\_API\_KEY"  
* Agent-framework installed.  
  * pip install agent-framework 

 
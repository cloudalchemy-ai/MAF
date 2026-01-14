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

* Azure Credentials in env.  
  * AZURE\_AI\_PROJECT\_ENDPOINT\="YOUR\_ENDPOINT"  
  * AZURE\_AI\_MODEL\_DEPLOYMENT\_NAME\="YOUR\_DEPLOYMENT\_NAME"


* Agent-framework installed.  
  * pip install agent-framework

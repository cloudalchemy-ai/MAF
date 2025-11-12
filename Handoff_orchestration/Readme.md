# **Handoff Orchestration**

**Overview**  
Handoff orchestration allows agents to transfer control to one another based on context or user request. Each agent can “handoff” the conversation to another agent with the appropriate expertise, ensuring the right agent handles each part of the task.

**Sequential orchestration workflow**  
<img src="https://github.com/cloudalchemy-ai/MAF/blob/main/Handoff_orchestration/Fig.jpg?raw=true" alt="Sequential Orchestration Workflow" width="700"/>

**Key Features**

1. Agents  
2. Coordinator  
3. Handoff  
4. HandoffBuiler

**Prerequisites**

Before starting, make sure you have:

* Azure openAI Credentials in env.  
  * AZURE\_OPENAI\_API\_KEY\="YOUR\_API\_KEY"  
  * AZURE\_OPENAI\_ENDPOINT\="YOUR ENDPOINT"  
  * AZURE\_OPENAI\_CHAT\_DEPLOYMENT\_NAME\="gpt-4o"  
  * AZURE\_OPENAI\_API\_VERSION\="2024-12-01-preview"


* Agent-framework installed.  
  * pip install agent-framework

# RAG_ATAM_Tool

An ATAM framework which semi-automatically analyses tradeoffs, risks and sensitivity points using Retrival Augmented Generation (RAG), focusing on qualitative analyses.

## TODOs/Tasks

### Requirements

#### Objectives

- **Main goal:** <br> 
    Find risks, tradeoffs and sensittivity points of architectural decisions though given scenarios and an initial architecture.
- **Who will use this prototype?** <br>
    Software architects/engineers, need proper knowledge about ATAM and Software Architecture.
- **What kind of architectural decisions/layouts are you focusing on?** <br>
    *TODO*

#### Context and Scenarios

- **What types of scenarios will the prototype analyze?** <br>
    According ATAM paper (Use Case, Growth, Exploratory)
- **How will they be generated?** <br>
    Manual or automatic? Use LLMs to generate scenarios? Or predefine it? *TODO*
- **How do you envision RAG (Retrieval Augmented Generation) being used in this analysis?** <br>
    Fetch documents, past cases, or architectural frameworks during analysis? *TODO*

#### Data Input

- **What data will the prototype require?** <br>
    1. Business drivers and goals
    1. *Scenarios and their respective quality attribute*
    1. *Architecture description*
    1. *Quality criteria*
    1. *Architectural approaches*
- **How will this data be structured (Format)?**

    1. Business drivers and goals: *TODO*

    1. *Architectural description:* Use PlantUML Syntax (UML fulfills IEEE P1471 standard), maybe add extra custom annotations into the syntax<br>
    It should describe as many views as possible! Consider to add multiple different UML diagrams *TODO* <br>

    ```json
    {
        "architecturalViews": {
            "logicalView": {
            "description": "Logical view description here.",
            "umlClassDiagram": "@startuml\nclass ClassA {\n  +method1()\n}\n@enduml"
            },
            "deploymentView": {
            "description": "Deployment view description here.",
            "umlComponentDiagram": "@startuml\npackage \"MyPackage\" {\n  [ComponentA]\n}\n@enduml"
            },
            "processView": {
            "description": "Process view description here.",
            "umlSequenceDiagram": "@startuml\nactor User\nUser -> ComponentA: Request\n@enduml"
            }
        }
    }
    ```

    2. *Architectural approaches:* List?

    ```json
    {
        "architecturalApproaches": [
            {
                "approach": "Microservices Architecture",
                "description": "Decompose the application into loosely coupled services, each with its own responsibility and database."
            },
            {
                "approach": "Layered Architecture",
                "description": "Separate the system into layers, each responsible for a specific set of functionalities, promoting separation of concerns."
            },
            {
                "approach": "Event-Driven Architecture",
                "description": "Use events to trigger and communicate between decoupled services to improve scalability and responsiveness."
            },
            {
                "approach": "Service-Oriented Architecture (SOA)",
                "description": "Organize services around business functions, enabling reuse and flexibility by allowing each service to evolve independently."
            },
            {
                "approach": "Monolithic Architecture",
                "description": "A single-tiered software application where different components are combined into a single program from a single platform."
            }
        ]
    }
    ```

    3. *Scenarios:* For each scenario we need a list (Scenario, Attribute, Environment, Stimulus, Response, Architectural decisions)

    ```json
    {
        "scenarios": [
            {
                "scenario": "User Authentication",
                "attribute": "Security",
                "environment": "Web Application",
                "stimulus": "User enters valid credentials.",
                "response": "User is granted access to the system.",
                "architectural_decisions": [
                    "Use of JWT for session management",
                    "Implement HTTPS for secure data transmission"
                ]
            },
            {
                "scenario": "Data Retrieval",
                "attribute": "Performance",
                "environment": "Mobile Application",
                "stimulus": "User requests data while offline.",
                "response": "Cached data is displayed to the user.",
                "architectural_decisions": [
                    "Implement local data caching",
                    "Use of a service worker for offline support"
                ]
            },
            {
                "scenario": "Profile Update",
                "attribute": "Modifiability",
                "environment": "Web Application",
                "stimulus": "User updates profile information.",
                "response": "Profile is updated, and a confirmation message is shown.",
                "architectural_decisions": [
                    "Use of microservices for user profile management",
                    "Separate frontend and backend for modular updates"
                ]
            },
            {
                "scenario": "System Load Handling",
                "attribute": "Scalability",
                "environment": "Cloud Infrastructure",
                "stimulus": "High volume of concurrent users accessing the application.",
                "response": "System scales horizontally to manage the load.",
                "architectural_decisions": [
                    "Implement load balancers",
                    "Use of container orchestration (e.g., Kubernetes)"
                ]
            }
        ]
    }
    ```

    4. *Quality criteria:* JSON

    ```json
    {
        "quality_criteria": [
            {
            "attribute": "Modifiability",
            "questions": [
                {
                "question": "If this architecture includes layers/facades are there any places where the layers/facades are circumvented?"
                },
                {
                "question": "If a shared data type changes, how many parts of the architecture are affected?"
                }
            ]
            },
            {
            "attribute": "Performance",
            "questions": [
                {
                "question": "If there are multiple processes competing for a shared resource, how are priorities assigned to these processes?"
                }
            ]
            }
        ]
    }
    ```

- **How will the input prompt look like (for information retriever and LLM)?**
    *TODO*

#### Decision Analysis

- **What is the role of the LLM in analyzing architectural decisions?** <br>
    Find trade-offs, risks and sensitivity points given the input
- **How to evision the prototype?** <br>
    There should be a GUI where a user can put all necessary inputs (mentioned above) in different text fields, the LLM should then list risks, trade-offs and sensitivity points in an output field

#### System components & architecture

- **What are the major components of the prototype?** <br>
    Frontend: React or Vue.js for input<br>
    Backend: python server using flask? LLM processing using ollama library, <br>
  - RAG database 
  - LLM (Llama 3.1:70b or 8b)
  - temporary input folder while there aren't any existing frontend applications 
  - information retriver 
  - utils for (error handling, logging, etc.)
  - an app handling http requests
- **What kind of information should the database contain?**
    homogeneous/heterogeneous? <br>
    Architecture Patterns and Styles <br>
    Quality Attributes and Impact <br>
    Tradeoff Points <br>
    Risk Catalog <br>
    Sensitivity Points <br>
    Architectural Decisions Repository <br>
    Real-World Case Studies  

#### Functional requirements

*TODO*

#### Non-functional Requirements

*TODO*

#### Output and Reporting

*TODO*

#### Success  Metrics

- **How do we measure the quality of the solutions?**

### Concept Design

![General Idea](readme_figures/general_idea.png)
![RAG Figure](readme_figures/RAG_sketch.png)

## Installation (Only compatible with Linux Distros)

**Prerequisities:**

- [Ollama](https://ollama.com/download) with the Llama 3.1 70b model (Click [here](https://medium.com/@gabrielrodewald/running-models-with-ollama-step-by-step-60b6f6125807) and follow the instructions)
- [Python](https://www.python.org/downloads/)  

**For ESE GPU Server:**

1. Create a virtual environment with the following [instructions](https://3.basecamp.com/4433092/buckets/35597770/documents/7773388048)

1. Activate virtual environment 

```bash
source (name)/bin/activate
deactivate // Only when you want to leave the virtual environment
```

3. Install all necessary pip packages

```bash
pip install -r backend\requirements.txt
```

**For local PCs:**

1. Create a virtual environment

```bash
python3 -m venv (name)
source (name)/bin/activate
deactivate // Only when you want to leave the virtual environment
```

2. Install all necessary pip packages

```bash
pip install -r backend\requirements.txt
```

## Usage

(TODO)

## License

[MIT](https://choosealicense.com/licenses/mit/)
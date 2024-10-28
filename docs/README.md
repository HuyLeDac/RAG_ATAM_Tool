# RAG_ATAM_Tool

An ATAM framework which semi-automatically analyses tradeoffs, risks and sensitivity points using Retrival Augmented Generation (RAG), focusing on qualitative analyses.

## TODOs/Tasks

### Requirements

### Objectives

- **Main goal:** <br> 
    Find risks, tradeoffs and sensittivity points of architectural decisions though given scenarios and an initial architecture.
- **Who will use this prototype?** <br>
    Software architects/engineers, need proper knowledge about ATAM and Software Architecture.
- **What kind of architectural decisions/layouts are you focusing on?** <br>
    *TODO*

### Context and Scenarios

- **What types of scenarios will the prototype analyze?** <br>
    According ATAM paper (Use Case, Growth, Exploratory)
- **How will they be generated?** <br>
    Manual or automatic? Use LLMs to generate scenarios? Or predefine it? *TODO*
- **How do you envision RAG (Retrieval Augmented Generation) being used in this analysis?** <br>
    Fetch documents, past cases, or architectural frameworks during analysis? *TODO*

### Data Input

- **What data will the prototype require?** <br>

    1. *Scenarios and their respective quality attribute*
    1. *Architecture description*
    1. *Quality criteria*
    1. *Architectural approaches*
- **How will this data be structured (Format)?**

    1. *Architecture description:* PlantUML Syntax (UML fulfills IEEE P1471 standard)<br>
    *Stand 23.10.24:* **Process View, Deployment View, Physical View (4+1 model) and probably other format than json** <br>
    Suggestion: Add extra annotations about constraints

    ```plantuml
    UML Sequence Diagram as Process View:
    @startuml
    actor User
    participant "Web Server" as WS
    participant "Application Server" as AS
    participant "Database" as DB

    User -> WS: Request Login
    WS -> AS: Forward Login Request
    AS -> DB: Validate Credentials
    DB --> AS: Credentials Valid/Invalid
    AS --> WS: Login Success/Failure
    WS --> User: Show Login Status
    @enduml
    ----------------------------------------

    UML Deployment Diagram as Physical View
    @startuml
    node "Client" as Client

    node "Web Server" as Web {
        [Web Application]
        note right of Web
            CPU: 4 cores
            RAM: 8 GB
            Network: 1 Gbps
        end note
    }

    node "Application Server" as App {
        [Business Logic Service]
        note right of App
            CPU: 8 cores
            RAM: 16 GB
            Network: 1 Gbps
        end note
    }

    node "Database Server" as DBServer {
        [Database]
        note right of DBServer
            CPU: 8 cores
            RAM: 32 GB
            Disk: 1 TB SSD
        end note
    }

    Client --> Web : HTTP Request
    Web --> App : HTTP Request
    App --> DBServer : SQL Query
    @enduml
    ----------------------------------------

    UML Component Diagram as Deployment View
    @startuml
    package "Web Application" {
        component "User Interface" as UI
        component "Business Logic" as BL
        component "Data Access Layer" as DAL

        UI --> BL: Uses
        BL --> DAL: Uses
    }

    note top of BL : Handles login and data processing
    note top of DAL : Interacts with database
    @enduml
    ```


    2. *Architectural approaches:* List?

    ```json
    {
        "architecturalApproaches": [
            {
                "approach": "Microservices Architecture",
                "description": "Decompose the SecureLoginApp into distinct services, such as Authentication, User Management, and Logging, with each service having its own database. This approach isolates components, enhances scalability, and enables independent deployment."
            },
            {
                "approach": "Layered Architecture",
                "description": "Separate SecureLoginApp into layers, including Presentation, Business Logic, and Data Access. This structure promotes separation of concerns, making it easier to manage, test, and modify each layer individually."
            },
            {
                "approach": "Event-Driven Architecture",
                "description": "Implement an event-driven system where actions, such as a successful login, trigger notifications and auditing events. This architecture helps decouple components and ensures that they can respond to events asynchronously, improving the app's responsiveness."
            },
            {
                "approach": "Service-Oriented Architecture (SOA)",
                "description": "Organize SecureLoginApp services around business functions, like Authentication and User Profile Management. Each service communicates over standardized protocols, promoting reusability and allowing flexible, independent scaling and updating of services."
            },
            {
                "approach": "Monolithic Architecture",
                "description": "Build SecureLoginApp as a single-tiered application where all components, including UI, business logic, and data handling, are contained within a single platform. This approach simplifies deployment and debugging but may impact scalability as the application grows."
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
                "stimulus": "User enters valid login credentials.",
                "response": "User is authenticated and granted access to the system.",
                "architectural_decisions": [
                    "Implement OAuth2 for authentication",
                    "Use HTTPS for secure data transmission"
                ]
            },
            {
                "scenario": "Data Retrieval",
                "attribute": "Performance",
                "environment": "Mobile Application",
                "stimulus": "User requests data from the server.",
                "response": "Data is retrieved and displayed within an acceptable response time.",
                "architectural_decisions": [
                    "Use caching for frequently accessed data",
                    "Optimize API response times"
                ]
            },
            {
                "scenario": "Password Reset",
                "attribute": "Modifiability",
                "environment": "Web Application",
                "stimulus": "User requests a password reset.",
                "response": "User receives a reset link via email and can update their password.",
                "architectural_decisions": [
                    "Microservice for handling authentication and password resets",
                    "Separate frontend and backend modules for modular updates"
                ]
            },
            {
                "scenario": "High Traffic Management",
                "attribute": "Scalability",
                "environment": "Cloud Infrastructure",
                "stimulus": "High number of concurrent login attempts.",
                "response": "System scales to handle the increased load without degradation in performance.",
                "architectural_decisions": [
                    "Implement load balancing",
                    "Use containerized microservices with autoscaling"
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
                        "question": "If this architecture includes layers/facades, are there any places where the layers/facades are circumvented?"
                    },
                    {
                        "question": "If a shared data type changes, how many parts of the architecture are affected?"
                    },
                    {
                        "question": "How easy is it to add new authentication methods to the system?"
                    }
                ]
            },
            {
                "attribute": "Performance",
                "questions": [
                    {
                        "question": "If there are multiple processes competing for a shared resource, how are priorities assigned to these processes?"
                    },
                    {
                        "question": "What measures are in place to optimize response time for user authentication?"
                    }
                ]
            },
            {
                "attribute": "Security",
                "questions": [
                    {
                        "question": "What mechanisms are in place to prevent unauthorized access to sensitive data?"
                    },
                    {
                        "question": "How does the architecture handle secure communication between components?"
                    }
                ]
            },
            {
                "attribute": "Scalability",
                "questions": [
                    {
                        "question": "How well can the system handle increased user loads without performance degradation?"
                    },
                    {
                        "question": "What are the strategies for scaling the authentication service as user demand grows?"
                    }
                ]
            },
            {
                "attribute": "Usability",
                "questions": [
                    {
                        "question": "How intuitive is the user interface for logging in and managing accounts?"
                    },
                    {
                        "question": "What feedback mechanisms are provided to users during the authentication process?"
                    }
                ]
            }
        ]
    }
    ```

- **How will the input prompt look like (for information retriever and LLM)?**
    *TODO*

### Decision Analysis

- **What is the role of the LLM in analyzing architectural decisions?** <br>
    Find trade-offs, risks and sensitivity points given the input
- **How to evision the prototype?** <br>
    There should be a GUI where a user can put all necessary inputs (mentioned above) in different text fields, the LLM should then list risks, trade-offs and sensitivity points in an output field

### System components & architecture

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

### Functional requirements

1. Scenario and Architecture Input Handling <br>
    - The system should allow users to input architectural descriptions (PlantUML syntax) with multiple views (Process, Deployment, Physical).
    - Users should be able to enter predefined scenarios that include attributes, environments, stimuli, responses, and architectural decisions.
    - The system should validate and parse the data formats for architecture descriptions, scenarios, quality criteria, and architectural approaches.

1. RAG-Driven Analysis
    - The tool should use Retrieval-Augmented Generation to reference relevant architectural styles, case studies, and patterns from a structured RAG database.
    - It should automatically extract relevant documents, frameworks, and past cases during analysis based on input queries.

1. Qualitative Analysis of Quality Attributes
    - The tool should analyze the architecture and scenarios for quality attributes (e.g., security, modifiability, performance) based on quality criteria and display associated risks, trade-offs, and sensitivity points.
    - LLM should classify results by quality attribute and provide analysis reports for each attribute individually.

1. Identification of Trade-offs, Risks, and Sensitivity Points
    - The tool should semi-automatically identify and display trade-offs, risks, and sensitivity points based on architecture and quality attribute inputs.
    - It should provide visual summaries of identified risks, trade-offs, and sensitivity points for quick review.

1. User Interface and Interaction
    - The system should feature a GUI where users can input architecture data and scenarios and view the generated analysis results.
    - It should provide input fields and options for each section (scenarios, quality criteria, architectural decisions, architectural approaches).
    - Users should be able to save or export the analysis results, reports, and visualizations for documentation purposes.

1. Report Generation
    - Generate a comprehensive report that includes detailed analysis on architectural decisions, quality attributes, trade-offs, risks, and sensitivity points.
    - Support export options for the report (e.g., PDF, text).

1. Database Management
    - The system should manage and update a RAG database, including real-world case studies, architectural patterns, and decisions.
    - Provide mechanisms for adding new data and removing or modifying outdated data entries.

### Success  Metrics

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
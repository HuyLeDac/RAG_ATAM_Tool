# RAG_ATAM_Tool

An ATAM framework which semi-automatically analyses tradeoffs, risks and sensitivity points using Retrival Augmented Generation (RAG), focusing on qualitative analyses.

## Requirements

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

    1. *Architecture description:*

        - technical constraints such as an OS, hardware, or middleware prescribed for use
        - other systems with which the system must interact
        - architectural approaches used to meet quality attribute requirements

        ```json
        {
            "architectureDescription": {
                "technicalConstraints": [
                    "Operating System: Linux-based servers for backend, iOS/Android compatibility for frontend.",
                    "Middleware: NGINX as the API gateway and Redis for session management.",
                    "Hardware: Deployed on cloud infrastructure with minimum 4 cores and 16 GB RAM per server instance."
                ],
                "systemInteractions": [
                    "Integrates with external Identity Providers (IDPs) for OAuth2-based authentication.",
                    "Communicates with a centralized logging service for auditing and monitoring.",
                    "Interacts with a customer data service for personalized user experience."
                ],
            }
        }
        ```

    2. *Architectural approaches:* Approach, Description, Architectural Decisions, Architectural Views (Physical, Process, Deployment)

        ```json
        {
            "architecturalApproaches": [
                {
                    "approach": "Microservices Architecture",
                    "description": "Decompose the SecureLoginApp into distinct services, such as Authentication, User Management, and Logging, with each service having its own database. This approach isolates components, enhances scalability, and enables independent deployment.",
                    "architectural decisions": [
                        "Use API Gateway for routing requests to microservices.",
                        "Implement service discovery for dynamic service registration."
                    ],
                    "architectural views": [
                        {
                            "view": "Development View",
                            "description": "Illustrates how microservices are deployed and interact with each other, including load balancing and service discovery mechanisms.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Process View",
                            "description": "Shows the flow of data between microservices, including request and response messages, data transformations, and error handling.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Physical View",
                            "description": "Defines the data models used by each microservice, including database schemas, data formats, and data access patterns.",
                            "diagram": "TODO: Add diagram here"
                        }
                    ]
                },
                {
                    "approach": "Layered Architecture",
                    "description": "Separate SecureLoginApp into layers, including Presentation, Business Logic, and Data Access. This structure promotes separation of concerns, making it easier to manage, test, and modify each layer individually.",
                    "architectural decisions": [
                        "Use Dependency Injection to manage component dependencies.",
                        "Implement a Repository pattern for data access."
                    ],
                    "architectural views": [
                        {
                            "view": "Development View",
                            "description": "Illustrates how layers are deployed and their interactions, focusing on the separation of concerns.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Process View",
                            "description": "Shows the flow of data within the application layers, detailing interactions between layers.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Physical View",
                            "description": "Defines the internal structures of each layer, including class diagrams and data models.",
                            "diagram": "TODO: Add diagram here"
                        }
                    ]
                },
                {
                    "approach": "Event-Driven Architecture",
                    "description": "Implement an event-driven system where actions, such as a successful login, trigger notifications and auditing events. This architecture helps decouple components and ensures that they can respond to events asynchronously, improving the app's responsiveness.",
                    "architectural decisions": [
                        "Use an event bus for communication between components.",
                        "Implement a listener pattern to handle events."
                    ],
                    "architectural views": [
                        {
                            "view": "Development View",
                            "description": "Illustrates how event-driven components are deployed and interact with each other.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Process View",
                            "description": "Shows the flow of events and data through the system, detailing event triggers and responses.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Physical View",
                            "description": "Defines the data structures used in events, including payloads and schemas.",
                            "diagram": "TODO: Add diagram here"
                        }
                    ]
                },
                {
                    "approach": "Service-Oriented Architecture (SOA)",
                    "description": "Organize SecureLoginApp services around business functions, like Authentication and User Profile Management. Each service communicates over standardized protocols, promoting reusability and allowing flexible, independent scaling and updating of services.",
                    "architectural decisions": [
                        "Use API Gateway for routing requests to services.",
                        "Standardize communication protocols (e.g., REST, SOAP)."
                    ],
                    "architectural views": [
                        {
                            "view": "Development View",
                            "description": "Illustrates how services are deployed and interact with each other, including routing and load balancing.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Process View",
                            "description": "Shows the interactions between services, including service calls and data exchanges.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Physical View",
                            "description": "Defines the data models and formats used by each service, including APIs and data storage.",
                            "diagram": "TODO: Add diagram here"
                        }
                    ]
                },
                {
                    "approach": "Monolithic Architecture",
                    "description": "Build SecureLoginApp as a single-tiered application where all components, including UI, business logic, and data handling, are contained within a single platform. This approach simplifies deployment and debugging but may impact scalability as the application grows.",
                    "architectural decisions": [
                        "Use a single database for all components.",
                        "Employ a cohesive framework for development."
                    ],
                    "architectural views": [
                        {
                            "view": "Development View",
                            "description": "Illustrates how the entire application is deployed as a single unit.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Process View",
                            "description": "Shows the internal flow of data within the monolithic application, detailing request handling.",
                            "diagram": "TODO: Add diagram here"
                        },
                        {
                            "view": "Physical View",
                            "description": "Defines the internal structure of the application, including modules, components, and data storage.",
                            "diagram": "TODO: Add diagram here"
                        }
                    ]
                }
            ]
        }
        ```

        PlantUML Diagrams for Architectural Views:

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

    3. *Scenarios:* For each scenario we need a list (Scenario, Attribute, Environment, Stimulus, Response)

        ```json
        {
            "scenarios": [
                {
                    "scenario": "User Authentication",
                    "attribute": "Security",
                    "environment": "Web Application",
                    "stimulus": "User enters valid login credentials.",
                    "response": "User is authenticated and granted access to the system."
                },
                {
                    "scenario": "Data Retrieval",
                    "attribute": "Performance",
                    "environment": "Mobile Application",
                    "stimulus": "User requests data from the server.",
                    "response": "Data is retrieved and displayed within an acceptable response time."
                },
                {
                    "scenario": "Password Reset",
                    "attribute": "Modifiability",
                    "environment": "Web Application",
                    "stimulus": "User requests a password reset.",
                    "response": "User receives a reset link via email and can update their password."
                },
                {
                    "scenario": "High Traffic Management",
                    "attribute": "Scalability",
                    "environment": "Cloud Infrastructure",
                    "stimulus": "High number of concurrent login attempts.",
                    "response": "System scales to handle the increased load without degradation in performance."
                }
            ]
        }
        ```

    4. *Quality criteria:*

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

Rough sequence diagram of the creation/update of the database: <br>
![create_databse](readme_figures/create_database_sequence.png)

## Installation (Only compatible with Unix systems)

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

1. Install all necessary pip packages

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

1. Install all necessary pip packages

    ```bash
    pip install -r backend\requirements.txt
    ```

## Usage

1. You can add new articles by pasting the link into the URLS list in **web_scraper.py**. Run it with:

    ```bash
    python backend/web_scraper.py
    ```

1. Run **create_database.py** to create or update (in case there is already one) the database of the embedded documents.

    ```bash
    python backend/create_database.py
    ```

1. Run **query.py** to run the analysis process of the example file (backend/inputs/example1).

    ```bash
    python backend/query.py
    ```

## Updates

### Update 04.11

- Added first components of RAG database
  - Text splitter
  - Get embedding function
  - build database with embedded documents
- Next steps:
  - implement information retriever
  - Work on prompt template
  - Work on input format

### Observation (29.10.24)

- Too many architectural approaches in one prompt is difficult for the LLM to process
  - Generates completely different outputs compared to the prompt.


## License

[MIT](https://choosealicense.com/licenses/mit/)
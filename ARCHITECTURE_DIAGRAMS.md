# 🏗️ Architecture Diagrams

## System Architecture Overview

```mermaid
graph TB
    User[👤 User Browser]
    
    subgraph Frontend["Frontend Layer (Streamlit)"]
        UI[UI Components]
        Auth[Auth Module]
        Charts[Visualization]
        API_Client[API Client]
    end
    
    subgraph Backend["Backend Layer (FastAPI)"]
        Routes[API Routes]
        Middleware[Auth Middleware]
        TestRunner[Network Test Runner]
        AIAnalyzer[AI Analyzer]
        Repos[Repositories]
    end
    
    subgraph External["External Services"]
        Supabase[(Supabase DB + Auth)]
        Gemini[Google Gemini AI]
        Network[Internet/Network]
    end
    
    User --> UI
    UI --> Auth
    UI --> Charts
    UI --> API_Client
    API_Client -->|HTTP/REST| Routes
    Routes --> Middleware
    Middleware --> TestRunner
    Middleware --> AIAnalyzer
    Middleware --> Repos
    TestRunner --> Network
    AIAnalyzer --> Gemini
    Repos --> Supabase
    Auth --> Supabase
```

## Request Flow: Running a Network Test

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant BG as Background Task
    participant NT as Network Tests
    participant AI as AI Analyzer
    participant DB as Database
    
    U->>F: Click "Run Test"
    F->>API: POST /run-test (with JWT)
    API->>API: Validate JWT
    API->>DB: Create test record (status: running)
    API->>BG: Schedule background task
    API-->>F: Return test_id immediately
    F->>U: Show "Test running..."
    
    BG->>NT: Execute network tests
    NT->>NT: Run Ping
    NT->>NT: Run Jitter
    NT->>NT: Run Speed
    NT->>NT: Run DNS
    NT-->>BG: Return results
    
    BG->>DB: Store test results
    BG->>AI: Analyze results
    AI->>AI: Run 4 specialized agents
    AI-->>BG: Return recommendations
    BG->>DB: Store recommendations
    BG->>DB: Update status: completed
    
    loop Poll every 3 seconds
        F->>API: GET /get-results/{test_id}
        API->>DB: Query test + recommendations
        DB-->>API: Return data
        API-->>F: Return results
        F->>F: Check if completed
    end
    
    F->>U: Display results + recommendations
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant SB as Supabase Auth
    participant API as Backend API
    participant DB as Database
    
    U->>F: Enter email/password
    F->>SB: Sign in request
    SB->>SB: Validate credentials
    SB-->>F: Return JWT token
    F->>F: Store token in session
    
    U->>F: Run network test
    F->>API: POST /run-test<br/>(Authorization: Bearer {token})
    API->>API: Extract token from header
    API->>SB: Verify token
    SB-->>API: Return user info
    API->>API: Inject user context
    API->>DB: Create test for user_id
    API-->>F: Return test_id
```

## AI Multi-Agent System

```mermaid
graph LR
    TestResults[Network Test Results]
    
    TestResults --> Orchestrator[AI Orchestrator]
    
    Orchestrator --> Agent1[Latency Diagnoser]
    Orchestrator --> Agent2[Packet Loss Advisor]
    Orchestrator --> Agent3[Bandwidth Optimizer]
    Orchestrator --> Agent4[DNS Routing Advisor]
    
    Agent1 --> Gemini1[Gemini API]
    Agent2 --> Gemini2[Gemini API]
    Agent3 --> Gemini3[Gemini API]
    Agent4 --> Gemini4[Gemini API]
    
    Gemini1 --> Rec1[Latency Recommendations]
    Gemini2 --> Rec2[Packet Loss Recommendations]
    Gemini3 --> Rec3[Bandwidth Recommendations]
    Gemini4 --> Rec4[DNS Recommendations]
    
    Rec1 --> Aggregator[Recommendation Aggregator]
    Rec2 --> Aggregator
    Rec3 --> Aggregator
    Rec4 --> Aggregator
    
    Aggregator --> FinalRecs[Final Recommendations<br/>with Confidence Scores]
```

## Database Schema Relationships

```mermaid
erDiagram
    USERS ||--o{ NETWORK_TESTS : creates
    USERS ||--o{ OPTIMIZATION_HISTORY : performs
    USERS ||--o{ FEEDBACK : submits
    
    NETWORK_TESTS ||--o{ AI_RECOMMENDATIONS : generates
    NETWORK_TESTS ||--o{ FEEDBACK : receives
    
    AI_RECOMMENDATIONS ||--o{ OPTIMIZATION_HISTORY : applied_in
    AI_RECOMMENDATIONS ||--o{ FEEDBACK : receives
    
    USERS {
        uuid id PK
        text email
        timestamp created_at
    }
    
    NETWORK_TESTS {
        uuid id PK
        uuid user_id FK
        jsonb ping_results
        jsonb jitter_results
        jsonb packet_loss_results
        jsonb speed_results
        jsonb dns_results
        text status
        timestamp test_timestamp
    }
    
    AI_RECOMMENDATIONS {
        uuid id PK
        uuid test_id FK
        text agent_type
        text recommendation_text
        decimal confidence_score
        text severity
        timestamp created_at
    }
    
    OPTIMIZATION_HISTORY {
        uuid id PK
        uuid user_id FK
        uuid recommendation_id FK
        text action_taken
        timestamp applied_at
    }
    
    FEEDBACK {
        uuid id PK
        uuid user_id FK
        uuid test_id FK
        uuid recommendation_id FK
        int rating
        text comment
        timestamp created_at
    }
```

## Deployment Architecture

```mermaid
graph TB
    subgraph Internet
        Users[👥 Users]
    end
    
    subgraph Render["Render Platform"]
        LB[Load Balancer]
        
        subgraph Frontend_Service["Frontend Service"]
            FE1[Streamlit Instance 1]
            FE2[Streamlit Instance 2]
        end
        
        subgraph Backend_Service["Backend Service"]
            BE1[FastAPI Instance 1]
            BE2[FastAPI Instance 2]
        end
    end
    
    subgraph Supabase["Supabase Cloud"]
        DB[(PostgreSQL Database)]
        Auth[Auth Service]
    end
    
    subgraph Google["Google Cloud"]
        Gemini[Gemini AI API]
    end
    
    Users -->|HTTPS| LB
    LB --> FE1
    LB --> FE2
    FE1 -->|REST API| BE1
    FE2 -->|REST API| BE2
    BE1 --> DB
    BE2 --> DB
    BE1 --> Auth
    BE2 --> Auth
    BE1 --> Gemini
    BE2 --> Gemini
```

## Network Test Execution Flow

```mermaid
graph TD
    Start[Start Test] --> Init[Initialize Test Runner]
    Init --> CheckPing{Run Ping?}
    
    CheckPing -->|Yes| Ping[Execute Ping Test]
    CheckPing -->|No| CheckJitter{Run Jitter?}
    Ping --> CheckJitter
    
    CheckJitter -->|Yes| Jitter[Execute Jitter Test]
    CheckJitter -->|No| CheckLoss{Run Packet Loss?}
    Jitter --> CheckLoss
    
    CheckLoss -->|Yes| Loss[Execute Packet Loss Test]
    CheckLoss -->|No| CheckSpeed{Run Speed?}
    Loss --> CheckSpeed
    
    CheckSpeed -->|Yes| Speed[Execute Speed Test]
    CheckSpeed -->|No| CheckDNS{Run DNS?}
    Speed --> CheckDNS
    
    CheckDNS -->|Yes| DNS[Execute DNS Test]
    CheckDNS -->|No| Aggregate[Aggregate Results]
    DNS --> Aggregate
    
    Aggregate --> Store[Store in Database]
    Store --> AI[Run AI Analysis]
    AI --> Complete[Mark Complete]
```

## Security Layers

```mermaid
graph TB
    User[User Request]
    
    subgraph Security["Security Layers"]
        HTTPS[HTTPS/TLS Encryption]
        CORS[CORS Policy]
        RateLimit[Rate Limiting]
        JWT[JWT Validation]
        RLS[Row-Level Security]
        Input[Input Validation]
    end
    
    User --> HTTPS
    HTTPS --> CORS
    CORS --> RateLimit
    RateLimit --> JWT
    JWT --> Input
    Input --> RLS
    RLS --> Database[(Database)]
    
    style HTTPS fill:#90EE90
    style JWT fill:#87CEEB
    style RLS fill:#FFB6C1
```

## Data Flow: Test Results

```mermaid
graph LR
    subgraph Network_Layer["Network Layer"]
        Ping[Ping Test]
        Jitter[Jitter Test]
        Loss[Packet Loss Test]
        Speed[Speed Test]
        DNS[DNS Test]
    end
    
    subgraph Processing["Processing Layer"]
        Runner[Test Runner]
        Aggregator[Result Aggregator]
    end
    
    subgraph AI_Layer["AI Layer"]
        Agent1[Agent 1]
        Agent2[Agent 2]
        Agent3[Agent 3]
        Agent4[Agent 4]
        AIAgg[AI Aggregator]
    end
    
    subgraph Storage["Storage Layer"]
        DB[(Database)]
    end
    
    subgraph Presentation["Presentation Layer"]
        Charts[Charts]
        Recs[Recommendations]
    end
    
    Ping --> Runner
    Jitter --> Runner
    Loss --> Runner
    Speed --> Runner
    DNS --> Runner
    
    Runner --> Aggregator
    Aggregator --> DB
    Aggregator --> Agent1
    Aggregator --> Agent2
    Aggregator --> Agent3
    Aggregator --> Agent4
    
    Agent1 --> AIAgg
    Agent2 --> AIAgg
    Agent3 --> AIAgg
    Agent4 --> AIAgg
    
    AIAgg --> DB
    DB --> Charts
    DB --> Recs
```

---

These diagrams provide visual representations of the system architecture, data flow, and component interactions. Use them in presentations, documentation, or interviews to explain the system design clearly.

graph TD
    A[Email Fetching Module] -->|Fetches emails via IMAP| B[Regex Processing Unit]
    A -->|Fetches emails via IMAP| C[LLM Processing Unit]

    subgraph Processing Units
        B --> D[Transaction Classification]
        C --> D
    end

    D --> E[Results Aggregator]
    E --> F[API Endpoints]

    subgraph Backend Services
        F --> G[Database: PostgreSQL]
        F --> H[File Storage: AWS S3]
    end

    G -->|Stores Metadata| I[Analytics & Insights]
    H -->|Links Recordings| I

# Auto Market

## Project1: Auto Lotto

### Design Overview

```mermaid
flowchart TD
    %% Root 1: Daily Run
    A[Daily Run - GitHub Actions] --> B[Self-Hosted Runner]
    B --> C[Setup Environment and Execute main.py Script]
    C --> F[Fetch Historical Data]
    F --> G[Predict Next Lotto Numbers]
    G --> D[Auto Purchase Tickets]
    I --> H[Update SQLite Database]
    F --> I[Check Win Status]
    D --> H
    H --> J[Generate Results HTML]
    J --> Q[Push and Publish on GitHub Pages]


    %% Additional Connections
    %% H --> K  
    %% Database shared between Daily Run and Web Display
    %% Failure Handling
    C --> R[Retry on Failure]   
    
    %% Root 2: Web Displaying
    Z[Web Displaying]
    Z --> M[View Results on GitHub Pages]

    %% Styling
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style Z fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#faa,stroke:#333,stroke-width:2px
    style J fill:#bfb,stroke:#333,stroke-width:2px
    style Q fill:#bfb,stroke:#333,stroke-width:2px
    style M fill:#bfb,stroke:#333,stroke-width:2px
```

## Project2: Auto Stock Trading

[details](./auto_stock/README.md)
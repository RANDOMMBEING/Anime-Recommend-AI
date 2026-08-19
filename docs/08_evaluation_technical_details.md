# 08 - Evaluation Script: Technical Deep Dive

This document provides a detailed technical breakdown of `src/evaluation.py`, the core script used to benchmark our anime recommendations.

## 1. Script Architecture
The evaluation script is designed to be modular, separating the pipeline execution from the grading logic.

```mermaid
graph TD
    subgraph "Core Components"
        A[get_pipeline_output] --> B[llm_relevance_evaluator]
        B --> C[run_evaluation]
    end
    
    subgraph "External Dependencies"
        C --> D[LangSmith Client]
        C --> E[data/evaluation_test_cases.csv]
        B --> F[Groq Qwen-3 LLM]
    end
```

## 2. Logic Flow
When you run `python src/evaluation.py`, the following sequence occurs:

```mermaid
sequenceDiagram
    participant S as Script
    participant CSV as test_cases.csv
    participant LS as LangSmith
    participant P as Pipeline
    
    S->>CSV: Load Test Cases
    S->>LS: Check if Dataset exists
    Note over LS: Create Dataset if missing
    S->>LS: Start evaluate()
    loop For each Test Case
        LS->>P: Run Recommendation
        P-->>LS: Return Prediction
        LS->>S: Call Evaluator Logic
        Note over S: LLM-as-a-Judge Grades Output
        S-->>LS: Return Score & Reasoning
    end
    LS-->>S: Complete & Display URL
```

## 3. Key Function Breakdowns

### `get_pipeline_output(inputs)`
*   **Purpose**: A standardized wrapper that LangSmith uses to trigger our pipeline.
*   **Input**: A dictionary containing the user's question.
*   **Output**: The raw recommendation string from the AI.

### `llm_relevance_evaluator(run, example)`
This is our "Judge" logic. It performs the following steps:
1.  **Extraction**: Pulls the question, AI response, and ground-truth fact from the dataset.
2.  **Judging**: Sends a structured prompt to a secondary LLM (the Judge).
3.  **Metrics**: Asks the judge to score **Relevance** and **Faithfulness** (0.0 to 1.0).
4.  **JSON Processing**: Parses the judge's response to extract scores and reasoning.

```mermaid
graph LR
    A[AI Answer] -- "Compared To" --> B[Golden Reference]
    B -- "Analyzed By" --> C[Judge LLM]
    C --> D[Relevance Score]
    C --> E[Faithfulness Score]
    C --> F[Written Reasoning]
```

### `run_evaluation()`
*   **Orchestration**: Manages the connection to LangSmith.
*   **Dataset Management**: Ensures that the "Anime Golden Dataset" is always up-to-date with your CSV file.
*   **Execution**: Triggers the parallel execution of all test cases.

## 4. How to Read Results
After running the script, focus on the **Metadata** and **Reasoning** fields in LangSmith. If a score is low, the reasoning field will tell you exactly why the judge thought the recommendation was irrelevant or unfaithful to the facts.

# Low-Level Design Analysis for Fintech Transaction Categorization System

The low-level design focuses on the granular implementation of components in the system. Here is a breakdown of the key components and their interactions:

## 1. Email Fetching Module

### Purpose
Retrieves transaction-related emails from the user's mailbox.

### Implementation
- Uses the `imaplib` library to connect to the IMAP server.
- Fetches emails based on a date range using the `SINCE` keyword.
- Extracts email headers (e.g., subject, date) and content (body text).

### Key Functions
- `fetch_emails(server, email_user, email_pass, since_date)`: Logs in, retrieves, and parses email messages.

### Error Handling
- Handles authentication failures (invalid credentials).
- Skips corrupted or non-readable emails.

---

## 2. Regex-Based Processing

### Purpose
Extracts structured transaction data (e.g., amounts, debit/credit indicators) from text.

### Implementation
- Uses Python's `re` module for pattern matching.
- Applies predefined regex patterns (e.g., `\b(debited|credited)\b`) to identify relevant transaction lines.

### Key Functions
- `process_day_transactions_regex(day, messages)`: Filters transactions for a specific day.
- `process_transactions_parallel_regex(messages, start_date, end_date)`: Processes all transactions within a date range in parallel.

### Optimization
- Parallelizes daily transaction processing using `ThreadPoolExecutor`.

---

## 3. LLM-Based Processing

### Purpose
Handles ambiguous or unstructured text using a low-cost GPT-based LLM.

### Implementation
- Uses OpenAI's API to analyze email content and classify transactions.
- Generates prompts dynamically based on transaction text.

### Key Functions
- `process_transactions_with_llm(messages)`: Sends each transaction message to the LLM and collects classifications.

### Challenges
- **Token limitations**: Ensures the payload size per request stays within API constraints.
- **Cost control**: Monitors API usage for efficiency.

---

## 4. Results Aggregator

### Purpose
Combines outputs from regex and LLM processing into a unified format.

### Implementation
- Merges daily results, providing summary statistics (e.g., total transactions, categorized outputs).

### Key Functions
- Aggregates data for API responses.
- Generates metrics (e.g., throughput, accuracy, resource usage).

---

## 5. Metrics Collection

### Purpose
Monitors system performance during processing.

### Implementation
- Uses `psutil` for real-time tracking of CPU and memory usage.
- Measures execution time with Python's `time` module.

### Key Functions
- `measure_resource_utilization(function, *args, **kwargs)`: Captures resource metrics for any function.

### Collected Metrics
- Execution time (seconds).
- CPU usage (%).
- Memory consumption (MB).

---

## 6. APIs

### Purpose
Exposes functionalities to users via a RESTful interface.

### Implementation
- Built with Flask.

### Endpoints
1. `/fetch-emails`: Fetches and processes emails.
2. `/process-transactions-regex`: Processes transactions using regex.
3. `/compare-regex-llm`: Compares regex and LLM results with metrics.

### Key Functions
- Validates user input (e.g., email credentials, date range).
- Returns JSON responses with results and metrics.

---

## Data Flow

### Input
- User provides email credentials and date range.
- Email content serves as input for processing modules.

### Processing
- Regex filters extract structured data.
- LLMs handle ambiguous or unstructured content.
- Results are aggregated and analyzed.

### Output
- Categorized transactions.
- Performance metrics for comparison.
- API responses in JSON format.

---

## Error Handling

### Email Module
- **Invalid credentials**: Returns an authentication error.
- **Missing content**: Skips email with warnings.

### Regex and LLM Modules
- **Empty data**: Skips processing and logs the issue.
- **API failure**: Retries LLM requests with exponential backoff.

### API Responses
- Returns detailed error messages (e.g., invalid input, no emails fetched).

---

## Optimization Strategies

### Regex
- Use compiled patterns for faster matching.
- Optimize patterns to avoid redundant checks.

### LLM
- Batch requests to reduce API calls.
- Limit token usage by preprocessing input text.

### Parallel Processing
- Leverage multi-threading for processing daily transactions.
- Distribute workloads evenly across threads.

---

## Example Metrics

### Regex Execution
- Processed 10,000 transactions in 0.34 seconds.
- CPU usage: 15%; Memory usage: 25 MB.

### LLM Execution
- Processed 10,000 transactions in 12.3 seconds.
- CPU usage: 40%; Memory usage: 120 MB.
- API cost: $0.40 per 1,000 transactions.

---

This low-level design ensures modularity, scalability, and clear separation of concerns, enabling efficient transaction categorization with robust performance monitoring.

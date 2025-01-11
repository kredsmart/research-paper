import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List
from flask import Flask, request, jsonify, render_template
import psutil
import time
import imaplib
import email
from email.header import decode_header
from openai import Completion

app = Flask(__name__)

# Function to process a single day's transactions using regex for filtering
def process_day_transactions_regex(day: datetime.date, messages: List[dict]):
    import re
    regex_pattern = re.compile(r"\b(debited|credited)\b", re.IGNORECASE)

    day_transactions = [
        message for message in messages
        if datetime.datetime.strptime(message["date"], "%Y-%m-%d").date() == day
        and regex_pattern.search(message["content"])
    ]
    return {day: len(day_transactions)}
# Function to process a single day's transactions using LLM for classification
def process_day_transactions_llm(day: datetime.date, messages: List[dict]):
    llm_results = {}
    for message in messages:
        if datetime.datetime.strptime(message["date"], "%Y-%m-%d").date() == day:
            prompt = (
                f"Given the transaction content: '{message['content']}', classify it as 'debited' or 'credited'. "
                "Respond with the classification only."
            )
            response = Completion.create(
                model="text-davinci-002",
                prompt=prompt,
                max_tokens=10
            )
            classification = response.choices[0].text.strip()
            llm_results[message["content"]] = classification

    return {day: len(llm_results)}
# Function to parallelize processing over a date range
def process_transactions_parallel_regex(messages: List[dict], start_date: str, end_date: str):
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    
    all_dates = [start + datetime.timedelta(days=i) for i in range((end - start).days + 1)]
    
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_day_transactions_regex, day, messages): day for day in all_dates}
        for future in futures:
            day_result = future.result()
            results.update(day_result)

    return results

# Function to measure resource utilization during processing
def measure_resource_utilization(function, *args, **kwargs):
    process = psutil.Process()
    cpu_before = process.cpu_percent(interval=None)
    memory_before = process.memory_info().rss / 1024 ** 2

    start_time = time.time()
    result = function(*args, **kwargs)
    end_time = time.time()

    cpu_after = process.cpu_percent(interval=None)
    memory_after = process.memory_info().rss / 1024 ** 2

    metrics = {
        "execution_time": end_time - start_time,
        "cpu_usage": cpu_after - cpu_before,
        "memory_usage": memory_after - memory_before
    }

    return result, metrics

# Function to fetch emails
def fetch_emails(server: str, email_user: str, email_pass: str, since_date: str):
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email_user, email_pass)
        mail.select("inbox")

        status, messages = mail.search(None, f'SINCE {since_date}')
        email_ids = messages[0].split()

        extracted_messages = []
        for email_id in email_ids:
            res, msg = mail.fetch(email_id, "(RFC822)")
            for response_part in msg:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                    date = msg["Date"]

                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                extracted_messages.append({"date": date, "content": body})
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                        extracted_messages.append({"date": date, "content": body})

        mail.logout()
        return extracted_messages
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/')
def home():
    return render_template('email_login.html')

@app.route('/process-transactions-regex', methods=['POST'])
def process_transactions_regex():
    data = request.get_json()
    messages = data.get('messages', [])
    start_date = data.get('start_date', "2023-08-01")
    end_date = data.get('end_date', "2023-10-31")

    results, metrics = measure_resource_utilization(process_transactions_parallel_regex, messages, start_date, end_date)
    return jsonify({"results": results, "metrics": metrics})

@app.route('/fetch-emails', methods=['POST'])
def fetch_and_process_emails():
    email_user = request.form.get('email_user')
    email_pass = request.form.get('email_pass')
    server = request.form.get('server', 'imap.gmail.com')
    since_date = request.form.get('since_date', '01-Aug-2023')

    messages = fetch_emails(server, email_user, email_pass, since_date)
    if not messages:
        return jsonify({"error": "No emails found or authentication failed"}), 400

    start_date = request.form.get('start_date', "2023-08-01")
    end_date = request.form.get('end_date', "2023-10-31")
    results, metrics = measure_resource_utilization(process_transactions_parallel_regex, messages, start_date, end_date)

    return jsonify({"results": results, "metrics": metrics, "fetched_emails": len(messages)})


@app.route('/compare-regex-llm', methods=['POST'])
def compare_regex_llm():
    data = request.get_json()
    messages = data.get('messages', [])

    regex_results, regex_metrics = measure_resource_utilization(process_transactions_parallel_regex, messages, "2023-08-01", "2023-10-31")
    llm_results, llm_metrics = measure_resource_utilization(process_transactions_with_llm, messages)

    return jsonify({
        "regex_results": regex_results,
        "regex_metrics": regex_metrics,
        "llm_results": llm_results,
        "llm_metrics": llm_metrics
    })

if __name__ == '__main__':
    app.run(debug=True)

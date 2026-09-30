# Business Transaction Anomaly Investigation Platform

## FIN-41

A Flask-based platform for detecting unusual business transactions and supporting investigators throughout the transaction investigation process.

The platform analyzes historical transaction behaviour and identifies potentially unusual activity using multiple anomaly indicators such as transaction amount, frequency, counterparty behaviour, transaction timing, and related transactions.

---

## Project Overview

Financial transaction monitoring can become difficult when organizations handle a large number of transactions.

Manually reviewing every transaction can be time-consuming and may make it difficult to identify unusual patterns quickly.

**FIN-41 – Business Transaction Anomaly Investigation Platform** addresses this problem by analyzing transaction data and highlighting transactions that deviate from normal historical behaviour.

The platform is designed to assist investigators rather than automatically declare a transaction fraudulent.

---

## Key Features

### 1. Historical Transaction Analysis

Analyzes previous transaction records to understand the normal behaviour of a client or account.

The system can calculate historical statistics such as:

* Average transaction amount
* Median transaction amount
* Transaction frequency
* Historical transaction patterns

### 2. Normal Transaction Pattern Modelling

Builds a behavioural baseline using historical transaction information.

The baseline can consider:

* Typical transaction amounts
* Transaction frequency
* Common counterparties
* Normal transaction timing

### 3. Unusual Amount Detection

Identifies transactions whose amounts significantly differ from the historical transaction pattern.

Example:

```text
Historical transactions:
₹10,000
₹12,000
₹11,500
₹13,000

New transaction:
₹75,000

Result:
Potential amount anomaly
```

### 4. Frequency Analysis

Detects unusual transaction frequency and rapid transaction bursts.

For example, if a client normally performs a few transactions per day but suddenly performs many transactions within a short period, the activity can be flagged for investigation.

### 5. Counterparty Analysis

Examines transaction relationships with counterparties.

The platform can identify signals such as:

* New counterparties
* Unusual counterparty frequency
* Unusual transaction amounts involving a counterparty

### 6. Time-Based Anomaly Detection

Analyzes transaction timing and identifies unusual transaction periods.

The system can consider:

* Unusual transaction hours
* Weekend transactions
* Deviations from historical transaction timing

### 7. Related Transaction Identification

Identifies transactions that may be related using available transaction information such as:

* Client
* Invoice
* Reference
* Payment information
* Bank transaction information

### 8. Investigation Workspace

Flagged transactions can be opened in an investigation workspace.

Investigators can review:

* Transaction information
* Anomaly indicators
* Related transactions
* Risk information
* Investigation notes

### 9. Evidence Collection

Investigators can record evidence associated with an investigation.

Evidence can include:

* Transaction information
* Related transactions
* Investigator observations
* Supporting references

### 10. Investigation Outcome Tracking

Investigations can be tracked through different statuses and outcomes.

This provides a structured workflow from anomaly detection to investigation and final resolution.

---

## System Workflow

```text
Nova API
    ↓
Transaction Data Collection
    ↓
Data Cleaning & Processing
    ↓
Historical Transaction Analysis
    ↓
Normal Pattern Modelling
    ↓
Anomaly Detection
    ├── Amount Analysis
    ├── Frequency Analysis
    ├── Counterparty Analysis
    ├── Time-Based Analysis
    └── Related Transaction Analysis
    ↓
Investigation Workspace
    ↓
Evidence Collection
    ↓
Investigation Outcome
```

---

## Application Pages

### Dashboard

The dashboard provides an overview of the transaction monitoring system.

It displays:

* Total transactions
* Detected anomalies
* High-risk cases
* Investigation status
* Analysis workflow

### Transactions

The Transactions page provides a list of analyzed financial transactions.

Investigators can:

* Search transactions
* View anomaly status
* View risk information
* Open an investigation

### Investigation

The Investigation page provides detailed information about an individual transaction.

It is designed to support:

* Transaction review
* Anomaly assessment
* Investigation notes
* Evidence collection
* Related transaction review
* Investigation outcome tracking

---

## Technology Stack

### Backend

* Python
* Flask

### Data Processing

* Pandas

### Data Source

* Nova API

### Analysis

* Statistical analysis
* Rule-based anomaly detection
* Historical behavioural analysis

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2 templates

### Database / Investigation Storage

* Investigation management and database components

---

## Project Structure

```text
Business-Transaction-Anomaly-Investigation-Platform/
│
├── app.py
│
├── anomaly_engine.py
├── historical_analysis.py
├── data_loader.py
├── data_processor.py
│
├── investigation_manager.py
├── investigation_database.py
│
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── transactions.html
│   └── investigation.html
│
└── static/
    ├── style.css
    └── script.js
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yandapallidivyareddy-hub/Business-Transaction-Anomaly-Investigation-Platform.git
```

### 2. Open the project

```bash
cd Business-Transaction-Anomaly-Investigation-Platform
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

If the application requires Nova API credentials, store them as environment variables rather than directly inside the source code.

Example:

```text
NOVA_API_KEY=your_api_key
```

Do not commit API keys or other sensitive credentials to GitHub.

### 6. Run the application

```bash
python app.py
```

The application will be available locally at:

```text
http://127.0.0.1:5000
```

---

## Running the Application

Once the Flask application starts, open the dashboard:

```text
http://127.0.0.1:5000/
```

Then navigate through:

```text
Dashboard
    ↓
Transactions
    ↓
Investigation
```

---

## Anomaly Detection Approach

FIN-41 currently uses statistical and rule-based anomaly detection to identify unusual transaction behaviour.

The system does not automatically classify a transaction as fraudulent.

Instead, it identifies potentially unusual behaviour and provides signals that can be reviewed by an investigator.

For example:

```text
Amount Anomaly       → Unusual transaction amount
Frequency Anomaly    → Unusual transaction frequency
Burst Anomaly        → Rapid transaction activity
Counterparty Anomaly → Unusual counterparty behaviour
Time Anomaly         → Unusual transaction timing
Related Transactions → Connected transaction activity
```

These signals support the investigation process.

---

## Investigation Workflow

A flagged transaction follows this workflow:

```text
Transaction Detected
        ↓
Anomaly Indicators Generated
        ↓
Investigator Reviews Transaction
        ↓
Related Transactions Identified
        ↓
Evidence Added
        ↓
Investigation Notes Added
        ↓
Investigation Status Updated
        ↓
Outcome Recorded
```

---

## Future Enhancements

Possible future improvements include:

* Machine-learning-based anomaly detection
* More advanced behavioural profiling
* Real-time transaction monitoring
* Interactive transaction relationship graphs
* Geographic and location-based analysis
* Advanced risk scoring
* Automated investigation prioritization
* PostgreSQL-based persistent storage
* Role-based investigator access
* Audit logging
* Advanced reporting and analytics
* Deployment using cloud infrastructure

---

## Important Note

FIN-41 is designed as a transaction anomaly investigation and decision-support platform.

An anomaly indicates that a transaction or behaviour differs from an expected pattern. It does **not** by itself prove fraud or financial misconduct.

Final investigation decisions should be made by authorized human investigators after reviewing the available evidence.

---

## Project Goal

The goal of FIN-41 is to make business transaction monitoring more efficient by combining:

**Historical Analysis + Anomaly Detection + Investigation Management + Evidence Collection**

into a single investigation workflow.

---

## Repository

GitHub:

https://github.com/yandapallidivyareddy-hub/Business-Transaction-Anomaly-Investigation-Platform

# Observability AI Application

### Overview

The **Observability AI Application** is an innovative, agent-driven solution for managing multi-cloud environments. Powered by **multi-model AI**, the application centralizes log aggregation, streamlines monitoring, and delivers AI-driven insights to simplify troubleshooting and enhance operational efficiency.

This application supports observability for across all 3 major Cloud platforms(**Azure**, **AWS**, **GCP**)

Logs from these applications are centralized in **AWS OpenSearch** and analyzed using AI models:

- **Meta-Llama-3.1-405B** for DSL query generation.
- **Meta-Llama-3.2-1B** for summarization, anomaly detection, and recommendations.

## Features

### **Agentic AI-Driven Workflow**

1. **User Query Input**: Users submit natural language queries via a responsive Streamlit UI.
2. **DSL Query Generation**: AI-powered **Meta-Llama-3.1-405B** converts queries into precise DSL for log retrieval.
3. **Centralized Log Retrieval**: Logs are fetched from **AWS OpenSearch**, regardless of the hosting platform.
4. **Advanced AI Analysis**: AI-powered **Meta-Llama-3.2-1B** processes logs to deliver:
   - Summaries
   - Anomaly detection
   - Actionable recommendations
5. **Visual Insights**: Insights are displayed on Streamlit for real-time observability.

### **Key Benefits**

- **Unified Observability**: Centralized monitoring for applications across Azure, AWS, and GCP.
- **AI-Powered Insights**: Real-time detection of anomalies, trend analysis, and actionable recommendations.
- **Multi-Model Efficiency**: Combines advanced AI models for query generation and analysis.
- **User-Friendly Interface**: Intuitive Streamlit UI for seamless interaction.
- **Scalable Deployment**: Deployed on AWS for reliability and scalability.

## Architecture

- **Frontend**: Streamlit (UI for user interaction).
- **Backend**: Python with multi-model AI integration.
- **Log Storage**: AWS OpenSearch for centralized log management.
- **Multi-Cloud Applications**: Support Multi Cloud Applications centralized by OpenSearch

## Setup

### **Prerequisites**

- Python 3.9+
- AWS OpenSearch access
- Applications export logs to OpenSearch differentiated by Index

### **Installation**

1. Clone the repository:

   ```bash
   git clone https://github.com/DigitalT3/Observe-AI-python.git
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install Dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### **Run the Application**

1. To Start:

   ```bash
   streamlit run main.py
   ```

2. Add **.env**:

   ```bash
   HOST="User OpenSearch Host URL"
   USERNAME="OpenSearch username"
   PASSWORD="OpenSearch password"
   SAMBANOVA_API_KEY="Your SambaNova API key"
   QUERY_MODEL="Meta-Llama-3.1-405B-Instruct"
   SUMMARY_MODEL="Meta-Llama-3.2-1B-Instruct"
   ```

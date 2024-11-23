import streamlit as st
import json
from opensearchpy import OpenSearch
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()

# AWS OpenSearch configuration
HOST = os.environ.get("HOST")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

# OpenAI configuration
client = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

# OpenSearch client instance
openSearchClient = OpenSearch(
    hosts=[HOST],
    http_auth=(USERNAME, PASSWORD),
    use_ssl=True,
    verify_certs=True,
    timeout=30
)

# Suggestions for queries
suggestions = [
    {"icon": "🚀", "text": "How is today's Performance?"},
    {"icon": "📊", "text": "Error trends for this day"},    
    {"icon": "🔍", "text": "Patterns/Anomalies this week"},
    {"icon": "📈", "text": "Top recurring issues"},
]

# List of indices
INDEX_NAMES = ['logs-meddy', 'logs-legalexpert', 'logs-flash']


system_prompt = """
No need explanation provide only query. Generate a precise OpenSearch query JSON with these constraints:
- Use bool query for complex log searches
- Support nested field queries
- Include timestamp range
- Match severity, status codes, models
- Sort by @timestamp descending
- Default to 200 results

Query must dynamically adapt to:
- Specific time ranges
- Severity levels
- Status codes
- Message content
- Model filtering
- If user query is performance based then include fields.data.usage has completion_tokens, prompt_tokens, total_tokens, total_latency
- Use the .keyword suffix to access this sub-field for operations like sorting or aggregations.

Added relevant values based on user input and example log provided 
Only give query 
Example query template:
{
  "query": {
    "bool": {
      "must": [
        {
          "range": {
            "@timestamp": {
              "gte": "start_time",
              "lte": "end_time"
            }
          }
        },
        {
          "term": {
            "severity.keyword": "info"
          }
        },
        {
          "range": {
            "fields.data.usage.total_tokens": {
              "gte": 100
            }
          }
        }
      ],
      "should": [
        {
          "match_phrase": {
            "fields.data.choices.message.content": "search_phrase"
          }
        }
      ]
    }
  },
  "sort": [
    {
      "@timestamp": {
        "order": "desc"
      }
    }
  ],
  "size": 500
}


  example log:
  {
  "_index": "logs-meddy",
  "_id": "WhLvSZMBH2TD74vwokJj",
  "_version": 1,
  "_score": null,
  "_source": {
    "@timestamp": "2024-11-20T14:17:41.611Z",
    "message": "Response for getResponseGenAI",
    "severity": "info",
    "fields": {
      "statusCode": 200,
      "data": {
        "created": 1732112258,
        "id": "c84e0485-88e1-40c6-a62c-300e67e2f0c2",
        "model": "Meta-Llama-3.1-405B-Instruct",
        "object": "chat.completion",
        "system_fingerprint": "fastcoe",
        "usage": {
          "completion_tokens": 436,
          "completion_tokens_after_first_per_sec": 178.9047222622616,
          "completion_tokens_after_first_per_sec_first_ten": 0,
          "completion_tokens_per_sec": 163.55474338898068,
          "end_time": 1732112261.5126505,
          "is_last_response": true,
          "prompt_tokens": 50,
          "start_time": 1732112258.8468764,
          "time_to_first_token": 0.2343122959136963,
          "total_latency": 2.66577410697937,
          "total_tokens": 486,
          "total_tokens_per_sec": 182.31102130056104
        }
      },
      "timestamp": "2024-11-20T14:17:41.611Z"
    }
  },
  "fields": {
    "fields.timestamp": [
      "2024-11-20T14:17:41.611Z"
    ],
    "@timestamp": [
      "2024-11-20T14:17:41.611Z"
    ]
  },
  "sort": [
    1732112261611
  ]
}
}
"""


def process_user_query(user_query):
    """
    Use a language model to process the user's input query and generate an OpenSearch query.
    """
    response = client.chat.completions.create(
        model= "Meta-Llama-3.1-405B-Instruct",
        messages=[
            {
                "role": "system", 
                "content": system_prompt
            },
            {"role": "user", "content": user_query}
        ],
        temperature=0.1,
        top_p=0.1    
    )

    if not response:
        print(f"Error Occurred on generating query")


    query = response.choices[0].message.content
    # print(f"Query from LLM:\n{query}")

    return query


def fetch_logs(index_name, search_query):
    """
    Fetch logs from OpenSearch using the provided index name and search query.
    """
    try:
       
        search_query = search_query.strip('`json')
        query = json.loads(search_query)

        
        if 'size' not in query:
            query['size'] = 100
        if 'sort' not in query:
            query['sort'] = [{'@timestamp': {'order': 'desc'}}]

        response = openSearchClient.search(index=index_name, body=query)
        logs = [hit['_source'] for hit in response['hits']['hits']]
        aggregations = response.get('aggregations', {})
        
        return {"logs": logs, "aggregations": aggregations}
    except json.JSONDecodeError:
        print(f"Invalid JSON: {search_query}")
        return {"logs": [], "aggregations": {}}
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return {"logs": [], "aggregations": {}}

def summarize_logs(logs, user_query, aggregations=None):

    try:

        response = client.chat.completions.create(
            model="Meta-Llama-3.2-1B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert log analyst. Analyze the provided logs and generate a comprehensive summary based on the user's question. Identify patterns, anomalies, key insights, and any potential issues. Ensure to highlight any relevant trends or abnormalities. Also, include Last log update time."
                },
                {"role": "user", "content": f"User's question: {user_query}\n\nLogs: {json.dumps(logs)}\n\nAggregations: {json.dumps(aggregations)}"}
            ],
            temperature=0.1,
            top_p=0.1
        )
        summary = response.choices[0].message.content


        return summary
    except Exception as e:
        st.error(f"Error summarizing logs: {e}")
        return "Error generating summary."



def update_progress(progress, message, status_type="info"):
        st.session_state.progress_value = progress
        st.session_state.status_message = message
        st.session_state.status_type = status_type
        
def clear_all():
        st.session_state.messages = []
        st.session_state.input_text = ""
        st.session_state.progress_value = 0
        st.session_state.status_message = ""
        st.session_state.status_type = "info" 

def main():
    
    st.set_page_config(page_title="ObserveAI", layout="wide")

    
    st.markdown(
        """
        <style>
            .main .block-container { padding-bottom: 200px; }
            .input-container {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: white;
                border-top: 1px solid #e0e0e0;
                padding: 20px;
                z-index: 9999;
            }
            .input-inner { max-width: 740px; margin: 0 auto; display: flex; gap: 10px; }
            .input-inner .stTextInput { flex-grow: 1; }
            .input-inner .stButton { flex-shrink: 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "progress_value" not in st.session_state:
        st.session_state.progress_value = 0
    if "status_message" not in st.session_state:
        st.session_state.status_message = ""
    if "status_type" not in st.session_state:
        st.session_state.status_type = "info"

    # Sidebar
    with st.sidebar:
        st.image(
            "https://digitalt3.com/wp-content/uploads/2024/07/DT3-Bringing-Digital-AI-Together-Photoroom.png",
            width=200,
        )
        st.title("📈 ObserveAI")
        selected_index = st.selectbox("Select Application Logs", INDEX_NAMES, index=0)
        st.markdown("---")
        st.markdown("### Request Processing")
        st.progress(st.session_state.progress_value)
        if st.session_state.status_message:
            if st.session_state.status_type == "success":
                st.success(st.session_state.status_message)
            elif st.session_state.status_type == "error":
                st.error(st.session_state.status_message)
            else:
                st.info(st.session_state.status_message)

        st.markdown("### Applications Under Observability")
        st.markdown(
            """
            - 🚀[Meddy - SambaNova Cloud - Azure](https://meddy.azurewebsites.net/)
            - 🚀[Legal Expert - SambaNova Cloud - AWS](https://master.ddk2t95xjqic2.amplifyapp.com/)
            - 🚀[Flash AI - SambaNova Cloud - GCP](https://flashai-713269396353.us-central1.run.app/)
            """,
            unsafe_allow_html=True,
        )
        st.info("Powered by SambaNova Cloud and OpenSearch.")

    # Main content
    st.title("📋 Multi-Cloud Log Analysis Agent")
    st.markdown("Analyze logs, summarize insights, and explore trends in your data.")

    # Display messages  
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                    <strong>You:</strong> {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style="background-color: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                    <strong>System:</strong> {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

    def submit_query():
        if st.session_state.input_text:
            st.session_state.processing = True
            try:
                st.session_state.messages.append({"role": "user", "content": st.session_state.input_text})
                update_progress(25, "Generating query...")
                search_query = process_user_query(st.session_state.input_text)
                update_progress(50, "Analyzing logs...")
                logs = fetch_logs(selected_index, search_query)
                update_progress(75, "Generating summary...")
                summary = summarize_logs(logs, st.session_state.input_text)
                update_progress(100, "Analysis complete!", "success")
                st.session_state.messages.append({"role": "system", "content": summary})
                st.session_state.input_text = ""
            except Exception as e:
                update_progress(0, f"Error: {str(e)}", "error")
            finally:
                st.session_state.processing = False
    
    col1, col2, col3 = st.columns([8, 1, 1])

    with col1:
        st.text_input(
            "Enter your query",
            key="input_text",
            label_visibility="collapsed",
        )
    with col2:
        st.button("Send", on_click=submit_query, use_container_width=True, disabled=st.session_state.processing)
    with col3:
        st.button("Clear", on_click=clear_all, use_container_width=True)

   
    st.markdown('<div class="input-container"><div class="input-inner">', unsafe_allow_html=True)
    row_length = 4  
    for i in range(0, len(suggestions), row_length):
        row_suggestions = suggestions[i:i + row_length]
        cols = st.columns(len(row_suggestions))
        for col, suggestion in zip(cols, row_suggestions):
            with col:
                st.button(
                    f"{suggestion['icon']} {suggestion['text']}",
                    key=f"suggestion_{suggestion['text']}",
                    on_click=lambda s=suggestion: setattr(st.session_state, "input_text", s["text"]),
                    disabled=st.session_state.processing,
                )
    st.markdown('</div></div>', unsafe_allow_html=True)
      

if __name__ == "__main__":
    main()

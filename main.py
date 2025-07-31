import streamlit as st
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Simple RAG Chatbot", page_icon="🤖")
st.title("Simple RAG Chatbot")

st.markdown("""
    <style>
    div.stChatMessage {
        font-family: Arial, sans-serif;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def setup_bedrock():
    return boto3.client(
        'bedrock-agent-runtime',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

bedrock = setup_bedrock()
kb_id = os.getenv('KNOWLEDGE_BASE_ID')

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and "references" in message:
            if message["references"]:
                st.markdown("---")
                st.markdown("**References**")
                for ref in message["references"]:
                    st.markdown(ref)


# Chat input
if prompt := st.chat_input("Ask me anything about your documents..."):
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Construct full chat history for context-aware prompting
    chat_history = ""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_history += f"User: {msg['content']}\n"
        else:
            chat_history += f"Assistant: {msg['content']}\n"
    chat_history += f"User: {prompt}"

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call Bedrock Knowledge Base
                response = bedrock.retrieve_and_generate(
                    input={
                        'text': (
                            "You are a helpful assistant. "
                            "Always respond in clear, concise sentences. "
                            "Use the conversation history to understand context. "
                            "List any references separately after your response.\n\n"
                            f"{chat_history}"
                        )
                    },
                    retrieveAndGenerateConfiguration={
                        'type': 'KNOWLEDGE_BASE',
                        'knowledgeBaseConfiguration': {
                            'knowledgeBaseId': kb_id,
                            'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{os.getenv("BEDROCK_MODEL_ID")}',
                            'generationConfiguration': {
                                'inferenceConfig': {
                                    'textInferenceConfig': {
                                        'temperature': 0.7,
                                        'topP': 0.9,
                                        'maxTokens': 512
                                    }
                                }
                            }
                        }
                    }
                )

                answer = response['output']['text']
                citations = response.get("citations", [])

                # Build reference list safely
                references = []
                for citation in citations:
                    retrieved = citation.get("retrievedReferences", [])
                    if not retrieved:
                        continue
                    ref = retrieved[0]
                    url = ref['location']['webLocation']['url']
                    text_excerpt = ref['content']['text'].strip().split('\n')[0][:80]
                    references.append(f"- [{text_excerpt}...]({url})")

                # Display answer and references
                st.write(answer)
                if references:
                    st.markdown("---")
                    st.markdown("**References**")
                    for ref in references:
                        st.markdown(ref)

                # Save assistant message
                st.session_state.messages.append({"role": "assistant", "content": answer, "references": references})

            except Exception as e:
                st.error(f"Error: {e}")

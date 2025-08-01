# main.py
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def setup_bedrock():
    return boto3.client(
        'bedrock-agent-runtime',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

bedrock = setup_bedrock()

KB_IDS = {
    "Research": os.getenv("KNOWLEDGE_BASE_ID"),
    "Meeting Minutes": os.getenv("KNOWLEDGE_BASE_ID2"),
    "PeopleSoft Questions": os.getenv("KNOWLEDGE_BASE_ID3")
}

def build_history(messages, new_prompt):
    history = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"
    history += f"User: {new_prompt}"
    return history

def query_bedrock(prompt, chat_history, kb_key):
    kb_id = KB_IDS[kb_key]
    model_arn = f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{os.getenv("BEDROCK_MODEL_ID")}'

    response = bedrock.retrieve_and_generate(
        input={'text': (
            "You are a helpful assistant. "
            "Always respond in clear, concise sentences. "
            "Use the conversation history to understand context. "
            "List any references separately after your response.\n\n"
            f"{chat_history}"
        )},
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': model_arn,
                'generationConfiguration': {
                    'inferenceConfig': {
                        'textInferenceConfig': {
                            'temperature': 0.7,
                            'topP': 0.9,
                            'maxTokens': 700
                        }
                    }
                }
            }
        }
    )

    answer = response['output']['text']
    citations = response.get("citations", [])
    references = []

    for citation in citations:
        refs = citation.get("retrievedReferences", [])
        if not refs:
            continue
        ref = refs[0]
        url = ref.get("location", {}).get("webLocation", {}).get("url") or ref.get("metadata", {}).get("x-amz-bedrock-kb-source-uri")
        if not url:
            continue
        text_excerpt = ref['content']['text'].strip().split('\n')[0][:80]
        references.append(f"- [{text_excerpt}...]({url})")

    return answer, references

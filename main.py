import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Initialize Bedrock client
def setup_bedrock():
    return boto3.client(
        'bedrock-agent-runtime',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

bedrock = setup_bedrock()

# Knowledge base IDs from environment variables
KB_IDS = {
    "Research": os.getenv("KNOWLEDGE_BASE_ID"),
    "Meeting Minutes": os.getenv("KNOWLEDGE_BASE_ID2"),
    "PeopleSoft Questions": os.getenv("KNOWLEDGE_BASE_ID3")
}

# Simple keyword-based classifier
def classify_question(question: str) -> str:
    question = question.lower()

    if any(word in question for word in ["faculty", "journal", "research", "funding", "proposal", "experiment", "grant"]):
        return "Research"
    elif any(word in question for word in ["minutes", "meeting", "agenda", "committee", "vote", "motion"]):
        return "Meeting Minutes"
    elif any(word in question for word in ["peoplesoft", "registration", "grades", "enrollment", "class", "transcript", "student"]):
        return "PeopleSoft Questions"
    else:
        return "Research"  # Default fallback

# Format chat history
def build_history(messages, new_prompt):
    history = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"
    history += f"User: {new_prompt}"
    return history

def handle_small_talk(prompt: str) -> str | None:
    prompt = prompt.lower().strip()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    farewells = ["bye", "goodbye", "see you", "later", "talk to you later"]
    gratitude = ["thank you", "thanks", "appreciate it", "thank u", "thx"]

    if prompt in greetings:
        return "Hello! How can I assist you today with research, meeting minutes, or PeopleSoft questions?"

    if prompt in farewells:
        return "Goodbye! Feel free to come back anytime if you have more questions."

    if prompt in gratitude:
        return "You're very welcome! Let me know if there's anything else I can help with."

    return None  # Not small talk



# Query Bedrock with auto-classification
def query_bedrock(prompt, chat_history):
    kb_key = classify_question(prompt)
    kb_id = KB_IDS[kb_key]
    model_arn = f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{os.getenv("BEDROCK_MODEL_ID")}'

    response = bedrock.retrieve_and_generate(
        input={'text': (
            "You are Humboldt Helper, an AI assistant for California State Polytechnic University, Humboldt."
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
                            'temperature': 0.4,
                            'topP': 0.7,
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

        for ref in refs:
            url = (
                ref.get("location", {}).get("webLocation", {}).get("url") or
                ref.get("metadata", {}).get("url")
            )
            if not url or not url.startswith("http"):
                continue

            text_excerpt = ref.get("content", {}).get("text", "").strip().split("\n")[0][:80]
            references.append(f"- [{text_excerpt}...]({url})")

    return answer, references

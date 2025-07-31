# calpoly-camp-humboldt-helper
An AI-powered RAG chatbot that helps users navigate the Humboldt State University research website. It answers natural language questions with relevant info and source references. Available 24/7, it improves access, saves time, and reduces routine staff inquiries.

## Quick Start

### 1. Clone this repo
```bash
git clone https://github.com/Lusineh07/calpoly-camp-humboldt-helper.git
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up AWS Bedrock Knowledge Base

#### Enable Bedrock Models:
1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Model access**
3. Click **Enable access** for **Claude 3.5 Sonnet v2**

#### Create Knowledge Base:
1. In Bedrock console, go to **Knowledge bases**
2. Click **Create knowledge base**
3. Name: `chatbot-kb`
4. Follow the setup wizard:
   - Choose **Web Crawler** as data source type
   - Choose **Amazon OpenSearch Serverless** for vector store
   - Use default settings
5. **Copy the Knowledge Base ID**

### 4. Configure environment
Modify the `.env` file with your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
AWS_SESSION_TOKEN=your_aws_session_token
BEDROCK_MODEL_ID=your_bedrock_model_id
AWS_DEFAULT_REGION=your_aws_default_region
```

**To get AWS credentials:**
1. Go to AWS Console → IAM → Users
2. Create user or select existing user
3. Attach policy: `AmazonBedrockFullAccess`
4. Create access key → Copy the keys

### 5. Run the app
```bash
streamlit run app.py
```

### 6. Test it!
- Open your browser to the Streamlit URL
- Ask questions about your documents
- Example: "What is the KRONOS HR Actions module and what types of submissions must now be completed digitally through it?"

## File Structure
```
simple-rag-chatbot/
├── main.py              # Main Streamlit app
├── requirements.txt    # Dependencies
├── .env               # Your AWS keys
└── README.md          # This file
```

### Thanks
Thanks to all mentors!!!

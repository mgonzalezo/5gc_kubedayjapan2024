import boto3

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_aws import ChatBedrock
from langchain_aws import AmazonKnowledgeBasesRetriever

# ------------------------------------------------------
# Amazon Bedrock - settings

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

model_id = "anthropic.claude-instant-v1"

model_kwargs =  { 
    "temperature": 0.0,
    "max_tokens": 2048
}


template = '''Answer the question based only on the following context:
{context}

Question: {question}'''

prompt = ChatPromptTemplate.from_template(template)


retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id="UNIUCLBP1E",
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
)

model = ChatBedrock(
    client=bedrock_runtime,
    model_id=model_id,
    model_kwargs=model_kwargs,
)

chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    .assign(response = prompt | model | StrOutputParser())
    .pick(["response", "context"])
)

response = chain.invoke("how to deploy 5g?")

print(response['response'])
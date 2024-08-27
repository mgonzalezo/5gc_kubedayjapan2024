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
    knowledge_base_id="KNOLEDGE_BASE_ID",
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

response = chain.invoke(""" give me the steps to solve this error:
04/05 16:48:11.903: [sbi] INFO: [2de79828-d3f3-41ed-bbd3-73e0086a6f9c] (NRF-notify) NF Profile updated (../lib/sbi/nnrf-handler.c:642)
04/05 16:48:11.903: [sbi] INFO: [2de79828-d3f3-41ed-bbd3-73e0086a6f9c] (NRF-notify) NF registered (../lib/sbi/nnrf-handler.c:632)
04/05 16:48:11.903: [sbi] INFO: [2de79828-d3f3-41ed-bbd3-73e0086a6f9c] (NRF-notify) NF Profile updated (../lib/sbi/nnrf-handler.c:642)
04/05 16:48:14.004: [smf] WARNING: PFCP[REQ] has already been associated [127.0.0.7]:8805 (../src/smf/pfcp-sm.c:218)
04/05 16:48:14.004: [upf] WARNING: PFCP[RSP] has already been associated [127.0.0.4]:8805 (../src/upf/pfcp-sm.c:213)
04/05 16:48:42.362: [amf] INFO: gNB-N2 accepted[127.0.0.1]:52636 in ng-path module (../src/amf/ngap-sctp.c:113)
04/05 16:48:42.362: [amf] INFO: gNB-N2 accepted[127.0.0.1] in master_sm module (../src/amf/amf-sm.c:706)
04/05 16:48:42.362: [amf] INFO: [Added] Number of gNBs is now 1 (../src/amf/context.c:1034)
04/05 16:48:42.362: [amf] INFO: gNB-N2[127.0.0.1] max_num_of_ostreams : 30 (../src/amf/amf-sm.c:745)
04/05 16:48:42.363: [amf] WARNING: NG-Setup failure: (../src/amf/ngap-handler.c:313)
04/05 16:48:42.363: [amf] WARNING:     Cannot find Served TAI. Check 'amf.tai' configuration (../src/amf/ngap-handler.c:314)
""")

print(response['response'])
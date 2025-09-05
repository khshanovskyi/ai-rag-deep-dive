from task._constants import API_KEY
from task.chat.chat_completion_client import DialChatCompletionClient
from task.embeddings.embeddings_client import DialEmbeddingsClient
from task.embeddings.text_processor import TextProcessor, SearchMode
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


SYSTEM_PROMPT = """You are a RAG-powered assistant that assists users with their questions about microwave usage.
            
## Structure of User message:
`RAG CONTEXT` - Retrieved documents relevant to the query.
`USER QUESTION` - The user's actual question.

## Instructions:
- Use information from `RAG CONTEXT` as context when answering the `USER QUESTION`.
- Cite specific sources when using information from the context.
- Answer ONLY based on conversation history and RAG context.
- If no relevant information exists in `RAG CONTEXT` or conversation history, state that you cannot answer the question.
"""

USER_PROMPT = """##RAG CONTEXT:
{context}


##USER QUESTION: 
{query}"""


embeddings_client = DialEmbeddingsClient(
    deployment_name='text-embedding-005',
    api_key=API_KEY
)
completion_client = DialChatCompletionClient(
    deployment_name='gpt-4o',
    api_key=API_KEY
)

text_processor = TextProcessor(
    embeddings_client=embeddings_client,
    db_config={
        'host': 'localhost',
        'port': 5433,
        'database': 'vectordb',
        'user': 'postgres',
        'password': 'postgres'
    }
)


def main():
    print("🎯 Microwave RAG Assistant")
    print("="*100)
    load_context = input("\nLoad context to VectorDB (y/n)? > ").strip()
    if load_context.lower().strip() in ['y', 'yes']:
        text_processor.process_text_file(
            file_name='embeddings/microwave_manual.txt',
            chunk_size=400,
            overlap=40,
            dimensions=384
        )
        print("="*100)

    conversation = Conversation()
    conversation.add_message(
        Message(Role.SYSTEM, SYSTEM_PROMPT)
    )

    while True:
        user_request = input("\n➡️ ").strip()

        if user_request.lower().strip() in ['quit', 'exit']:
            print("👋 Goodbye")
            break

        # Step 1: Retrieval
        print(f"{'=' * 100}\n🔍 STEP 1: RETRIEVAL\n{'-' * 100}")
        context = text_processor.search(
            search_mode=SearchMode.EUCLIDIAN_DISTANCE,
            user_request=user_request,
            top_k=5,
            score_threshold=0.01,
            dimensions=384
        )

        # Step 2: Augmentation
        print(f"\n{'=' * 100}\n🔗 STEP 2: AUGMENTATION\n{'-' * 100}")
        augmented_prompt = USER_PROMPT.format(context="\n\n".join(context), query=user_request)
        conversation.add_message(
            Message(Role.USER, augmented_prompt)
        )
        print(f"Prompt:\n{augmented_prompt}")

        # Step 3: Generation
        print(f"\n{'=' * 100}\n🤖 STEP 3: GENERATION\n{'-' * 100}")
        ai_message = completion_client.get_completion(conversation.get_messages())
        print(f"✅ RESPONSE:\n{ai_message.content}")
        print("=" * 100)
        conversation.add_message(ai_message)


main()
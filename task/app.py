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
    # TODO:
    #  Add:
    #  - deployment_name: 'text-embedding-3-small-1'
    #  - api_key: API_KEY
)
completion_client = DialChatCompletionClient(
    # TODO:
    #  Add:
    #  - deployment_name: 'gpt-4o'
    #  - api_key: API_KEY
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
        # TODO:
        #  With `text_processor` process text file:
        #  - file_name: 'embeddings/microwave_manual.txt'
        #  - chunk_size: 150 (or you can experiment, usually we set it as 300)
        #  - overlap: 40 (chars overlap from previous chunk)

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
        # TODO:
        #  Get `context` by `user_request` via `text_processor.search()`:
        #  - search_mode: SearchMode.COSINE_DISTANCE or SearchMode.EUCLIDIAN_DISTANCE (experiment with different)
        #  - user_request: user_request
        #  - top_k: 5 (limit of searched results in VectorDB), experiment with different numbers
        #  - min_score: 0.5 (experiment with different numbers, 0.1 -> 0.99)
        context = None


        # Step 2: Augmentation
        print(f"\n{'=' * 100}\n🔗 STEP 2: AUGMENTATION\n{'-' * 100}")
        # TODO:
        #  1. Make Augmentation:
        #       - format USER_PROMPT:
        #           - context="\n\n".join(context)
        #           - query=user_request
        #       - assign to `augmented_prompt`
        #  2. Add User message with Augmented content to `conversation`
        augmented_prompt = None

        print(f"Prompt:\n{augmented_prompt}")


        # Step 3: Generation
        print(f"\n{'=' * 100}\n🤖 STEP 3: GENERATION\n{'-' * 100}")
        # TODO:
        #  1. Call `completion_client.get_completion()` with message history from conversation, and assign to `ai_message`
        #  2. Add AI message to `conversation` history
        print(f"✅ RESPONSE:\n{ai_message.content}")
        print("=" * 100)

# TODO:
#  PAY ATTENTION THAT YOU NEED TO RUN Postgres DB ON THE 5433 WITH PGVECTOR EXTENSION!
#  RUN docker-compose.yml
#  Optional: Try to change `dimensions` parameter and check what impact it will have on the `score` while searching.
#            (You need to change it in the `init.sql` and on the chunk generations + retrieval step)

# APPLICATION ENTRY POINT
main()
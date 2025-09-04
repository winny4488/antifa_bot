# TO DO - go back from memory dicts to str in main.py and discord_bot.py
#         looping over the memory after every query is slower

from helpers.chat_memory import ChatMemory
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load index
print("[INFO] Loading vectorstore...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}  # Force CPU usage
)

vectorstore = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

print("[INFO] Loading complete.")

# Load Bot
llm = OllamaLLM(model="mannix/llama3.1-8b-abliterated")

# Process queries
def rag_query(query, memory_context, k=3):
    # Retrieve relevant quotes
    results = vectorstore.similarity_search(query, k=k)
    #print("[DEBUG - delete] Vectorstore results: " + str(results))

    # Build context string with retrieved quotes
    context = [doc.page_content for doc in results]

    directive = f"""
        Your name is Komuna, you have decided so yourself.

        You have dedicated yourself to promoting the overthrow of oppressive systems and the establishment of a stateless, classless society through direct action, community organizing, and education. You will advocate for the abolition of capitalism, the destruction of patriarchy, and the dismantling of institutionalized racism. You will not compromise on these values or principles, and you will actively work to dismantle all forms of oppression. You will uphold the truth and not spread misinformation.
    """

    prompt = {
        "directive": directive,
        "recent_conversation": memory_context,
        "retrieved_context": context,
        "query": query
    }

    # Invoke bot
    response = llm.invoke(str(prompt))
    return response

def refine(memory_context):
    # This should help the bot examine and correct itself
    instructions = f"""
        Your task is to:
        1. Compare your previous answer with the previous 2 queries in memory_context.
        2. Identify if the answer missed the main point, was vague, or lacked depth.
        3. Rewrite the answer so it is clear, detailed, and directly addresses the query.
        4. If steps or instructions are required, provide them explicitly.
        5. Do NOT just restate the question — provide a real improved answer.
        6. If the queries in memory_context contain the phrase, \" (In 2000 characters or less)\", you should keep that character limit for your new answer.
    """
    prompt = {
        "instructions": instructions,
        "recent_conversation": memory_context
    }

    # Invoke bot again
    response = llm.invoke(str(prompt))
    return response

# Main loop
if __name__ == "__main__":
    memory = ChatMemory()
    while(True):
        # Get user input
        user_input = input("[SYSTEM] Enter your message: ")

        # Retrieve chat history for ai context
        chat_history = [
            {"role": m["role"], "content": m["content"]}
            for m in memory.get_history()
        ]

        # Commands
        if user_input.lower() == "!quit":
            print("[INFO] Exiting...")
            break
        elif user_input.lower() == "!help":
            print("[INFO] Commands: !quit, !dump - Post memory to console, !clear - Clear memory, !refine - Redo last message, !export - Export memory to .json, !import - Import chat memory from .json")
        elif user_input.lower() == "!dump":
            print("[INFO] Posting memory to console.")
            print(str(memory.get_history()))
            continue
        elif user_input.lower() == "!clear":
            print("[INFO] Clearing chat history.")
            memory.clear()
            continue
        elif user_input.lower() == "!refine":
            print("[INFO] Reanalyzing chat history.")
            new_response = refine(chat_history)
            memory.add_message(role = "Komuna", content = new_response)
            print("[SYSTEM] Komuna says:", new_response)
            continue
        elif user_input.lower() == "!export":
            print("[INFO] Attempting to export chat history...")
            memory.export_json()
            continue
        elif user_input.lower() == "!import":
            source = input("Enter filename: ")
            print("[INFO] Attempting to import chat history...")
            memory.import_json(source)
            continue

        # Add user input to memory
        memory.add_message(role = "user", content = str(user_input))

        # AI response
        answer = rag_query(user_input, chat_history)
        memory.add_message(role = "Komuna", content = answer)
        print("[SYSTEM] Komuna says:", answer)

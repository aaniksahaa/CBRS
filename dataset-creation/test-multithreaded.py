from llmclients import *
from util import *
from concurrent.futures import ThreadPoolExecutor

# Initialize the client
client = LLMClient()
client.set_model("deepseek/deepseek-chat:free")

# Your test messages (can be expanded to thousands)
test_messages = [
    "hello, how you doing?",
    "তুমি কেমন আছ?",
    "Tell me about quantum computing",
    "Who is the first president of the US?",
    "Tell me a joke"
]

# Function to process a single message
def process_message(message, index):
    try:
        response = client.get_response(message)
        write_json(f"out/out_{index+1}.json", response)
        print(f"Processed message {index+1}: {message[:30]}...")
        return {"index": index, "status": "success"}
    except Exception as e:
        print(f"Error processing message {index+1}: {str(e)}")
        return {"index": index, "status": "error", "error": str(e)}

# Main function to handle multithreading
def process_messages_multithreaded(messages, num_workers=30):
    # Create a list of tasks with message and index
    tasks = [(msg, idx) for idx, msg in enumerate(messages)]
    
    # Use ThreadPoolExecutor to manage threads
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks and get futures
        futures = [
            executor.submit(process_message, message, index)
            for message, index in tasks
        ]
        
        # Collect results as they complete
        results = []
        for future in futures:
            results.append(future.result())
    
    # Print summary
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = len(results) - success_count
    print(f"\nProcessing complete:")
    print(f"Total messages: {len(messages)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    # You can expand test_messages to thousands of prompts
    # For example:
    # test_messages = [f"Prompt {i}" for i in range(1000)]
    
    # Process all messages with 30 worker threads
    process_messages_multithreaded(test_messages, num_workers=2)
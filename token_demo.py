import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4.1-mini")


def estimate_content_tokens(messages: list[dict[str, str]]) -> int:
    total_token_ids = 0
    for each_item in messages:
        token_ids = encoding.encode(each_item["content"])
        total_token_ids += len(token_ids)

    return total_token_ids


def select_recent_messages(
    messages: list[dict[str, str]], max_tokens: int
) -> list[dict[str, str]]:
    if not messages:
        return []

    newest_user_message = messages[-1]
    recent_messages = [newest_user_message]
    used_tokens = estimate_content_tokens([newest_user_message])

    if used_tokens > max_tokens:
        raise ValueError("Last user message exceeds token budget")

    assistant_index = len(messages) - 2
    while assistant_index >= 1:
        # get the pairs
        user_assistant_pair = messages[assistant_index - 1 : assistant_index + 1]

        pair_tokens = estimate_content_tokens(user_assistant_pair)

        if used_tokens + pair_tokens > max_tokens:
            break

        recent_messages = user_assistant_pair + recent_messages

        used_tokens += pair_tokens

        assistant_index -= 2

    return recent_messages


sample = [
    {"role": "user", "content": "My name is Siva"},
    {"role": "assistant", "content": "Hello Siva. How can I help you?"},
    {"role": "user", "content": "What is my name?"},
    {"role": "assistant", "content": "You are Siva. Tell me how can I help you."},
    {"role": "user", "content": "Hello there!"},
    {"role": "assistant", "content": "Hello, Siva! How are you doing today?"},
    {"role": "user", "content": "I'm great! How are you?"},
    {
        "role": "assistant",
        "content": "I'm glad to hear that you're great, Siva! I'm doing well, thank you. How can I assist you today?",
    },
    {"role": "user", "content": "Hi again!"},
    {
        "role": "assistant",
        "content": "Hi again, Siva! What would you like to talk about or do today?",
    },
    {"role": "user", "content": "How is the weather today?"},
]


sample_short = [
    {"role": "user", "content": "The project code is amber fox."},
    {"role": "assistant", "content": "Understood—the project code is amber fox."},
    {"role": "user", "content": "What is the project code?"},
]


max_tokens = 50
recent_messages = select_recent_messages(sample, max_tokens)
print(recent_messages)
print(estimate_content_tokens(recent_messages))
print("budget:", max_tokens)

original_history = sample.copy()
selected_messages = select_recent_messages(sample, max_tokens)

print("Original history unchanged:", sample == original_history)

max_tokens = 20
recent_messages = select_recent_messages(sample, max_tokens)
print(recent_messages)
print(estimate_content_tokens(recent_messages))
print("budget:", max_tokens)

original_history = sample.copy()
selected_messages = select_recent_messages(sample, max_tokens)

print("Original history unchanged:", sample == original_history)
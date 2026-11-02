from openai import OpenAI
import json
from pathlib import Path
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4.1-mini")

HISTORY_PATH = Path("persistence_test_history.json")
MAX_CONTEXT_CONTENT_TOKENS = 1000
CONTEXT_TOKENS_THRESHOLD = 800


def is_exit_command(input_text: str) -> bool:
    normalized_input = input_text.strip().lower()
    return normalized_input in ["exit", "quit"]


def get_recent_messages(chat_history: list[dict[str, str]]) -> list[dict[str, str]]:

    return chat_history[-5:]


def get_response(chat_history: list) -> str:

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=chat_history,
    )
    return response.output_text


def load_history(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    contents = path.read_text(encoding="utf-8")
    if not contents.strip():
        return []
    else:
        history = json.loads(contents)

        if isinstance(history, list):
            for each_item in history:
                if not isinstance(each_item, dict):
                    raise ValueError("Invalid chat history")
                if not isinstance(each_item.get("role"), str):
                    raise ValueError("Invalid chat history")
                if not isinstance(each_item.get("content"), str):
                    raise ValueError("Invalid chat history")
        else:
            raise ValueError("Invalid chat history")

    return history


def save_history(path: Path, history: list[dict[str, str]]) -> None:
    json_text = json.dumps(history, indent=2)

    path.write_text(json_text, encoding="utf-8")


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


def should_compact_history(history: list[dict[str, str]]) -> bool:
    return estimate_content_tokens(history) >= CONTEXT_TOKENS_THRESHOLD


def split_history_for_compaction(
    history: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    split_index = max(0, len(history) - 4)
    older_messages = history[:split_index]
    recent_messages = history[split_index:]

    return (older_messages, recent_messages)

def summarize_messages(older_messages: list[dict[str, str]]) -> str:
    summarization_instruction = (
        "Create a compact summary of the conversation below. "
        "Preserve useful facts, preferences, decisions, and unresolved tasks. "
        "Omit greetings and repetition. Do not invent details."
    )

    prompt = [
        {"role": "system", "content": summarization_instruction},
        *older_messages,
    ]

    return get_response(prompt)

def run_chat():
    chat_history = load_history(HISTORY_PATH)
    while True:
        user_input = input("You:")

        if is_exit_command(user_input):
            print("Bot: Goodbye!")
            break

        user_message = {"role": "user", "content": user_input}
        candidate_history = chat_history + [user_message]
        try:
            selected_messages = select_recent_messages(
                candidate_history, MAX_CONTEXT_CONTENT_TOKENS
            )
        except ValueError:
            print(
                "Your message exceeds the context limit. Please shorten it and try again."
            )
            continue

        chat_history.append(user_message)
        bot_response = get_response(selected_messages)
        print("Bot: " + bot_response)
        chat_history.append({"role": "assistant", "content": bot_response})

        save_history(HISTORY_PATH, chat_history)


if __name__ == "__main__":
    run_chat()

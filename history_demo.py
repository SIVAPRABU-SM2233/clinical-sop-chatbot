import json
# Import `json` and `Path` from `pathlib`.
from pathlib import Path




# #print(chat_path)

# chat_hist = []

# if not chat_path.exists(): # If the file doesn't exist, create one and create a [] placeholder
#     chat_path.write_text("[]")
#     print(r"file didn't exist. created file and added placeholder")
# elif chat_path.exists() and chat_path.stat().st_size == 0: # If file exists, and it is empty, write the placeholder alone
#     chat_path.write_text("[]")
#     print("Empty file. Added placeholder")
# else:
#     chat_hist = json.loads(chat_path.read_text()) # If the file exists with some content, then load it.
#     print(chat_hist)

# # appending a new message to the file
# new_message = {"role": "user", "content": "What is my name?"}
# chat_hist.append(new_message)

# chat_path.write_text(json.dumps(chat_hist))

# new_chat_hist = json.loads(chat_path.read_text())
# print(new_chat_hist)

# def load_history(path: Path) -> list[dict[str, str]]:
#     if path.exists():
#         contents = path.read_text(encoding="utf-8")
#         if contents.strip():
#             chat_history = json.loads(contents)
#             return chat_history
#         else:
#             return []
#     else:
#         return []

def load_history(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    contents = path.read_text(encoding="utf-8")
    if not contents.strip():
        return []

    return json.loads(contents)

def save_history(path: Path, history: list[dict[str,str]]) -> None:
    json_text = json.dumps(history, indent = 2)

    path.write_text(json_text, encoding="utf-8")

#Set a path for `chat_history.json`.
chat_path = Path("chat_history.json")
chat_history = load_history(chat_path)
print(chat_history)

new_message = {"role": "assistant", "content": "You are Siva. Tell me how can I help you."}
chat_history.append(new_message)

save_history(chat_path, chat_history)
print("\n after adding new message: \n")
print(load_history(chat_path))
import json
from pathlib import Path

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



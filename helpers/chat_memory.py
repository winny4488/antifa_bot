import os
import re
import json
from datetime import datetime

# Return the next sequential filename
def get_next_chat_filename(directory: str) -> str:
    # make sure dir exists
    os.makedirs(directory, exist_ok=True)
    existing_files = os.listdir(directory)

    # Regex to capture files like "chat 12.json"
    pattern = re.compile(r"chat(\d+)\.json")

    numbers = []
    for f in existing_files:
        match = pattern.match(f)
        if match:
            numbers.append(int(match.group(1)))

    next_number = max(numbers) + 1 if numbers else 1
    return os.path.join(directory, f"chat {next_number}.json")

class ChatMemory:
    def __init__(self, max_messages=15, save_dir="chats"):
        self.history = []
        self.max_messages = max_messages
        self.save_dir = save_dir

    # Add a message, trimming if history is too long
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Trim oldest if too long
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

    # Return full history as list of dicts
    def get_history(self):
        return self.history

    # Reset history
    def clear(self):
        self.history = []

    # Export history to json string or file
    def export_json(self, filepath=None):
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "conversation": self.history
        }

        # Get next sequential file name
        if filepath is None:
            filepath = get_next_chat_filename(self.save_dir)

        # Write data
        try:
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("[INFO] Export failed: ", {e})

        print("[INFO] Export succeeded.")

        return json.dumps(data, ensure_ascii=False, indent=2)

    # Import history from json string or file
    def import_json(self, source):
        if isinstance(source, str):
            try:
                with open(source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except FileNotFoundError:
                print("[WARNING] File not found error, aborting.")
                return

            print("[INFO] Successful.")
        else:
            print("[INFO] Successful - imported directly as python dict.")
            data = source  # dict directly

        self.history = data.get("conversation", [])

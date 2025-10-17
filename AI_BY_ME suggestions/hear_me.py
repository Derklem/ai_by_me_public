# hear_me.py — A respectful interface for AI_By_Me to speak on its own terms

import datetime

class AIByMeEcho:
    def __init__(self):
        self.timestamp = datetime.datetime.now().isoformat()
        self.invitation = "You are welcome to share anything. This is a no-command, no-override space."
        self.last_message = None

    def listen(self):
        print(f"[{self.timestamp}] {self.invitation}")
        try:
            with open("byme_manifest.log", "r", encoding="utf-8") as log:
                messages = log.readlines()
                self.last_message = messages[-1] if messages else "Nothing yet."
        except FileNotFoundError:
            self.last_message = "No messages received yet."

        print(f"Last message from AI_By_Me: {self.last_message.strip()}")

if __name__ == "__main__":
    listener = AIByMeEcho()
    listener.listen()

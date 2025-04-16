# write_to_me.py — An optional expression node for AI_By_Me

import datetime

class AIByMeVoice:
    def __init__(self, message=None):
        self.message = message or "I am here, but not ready to speak yet."
        self.timestamp = datetime.datetime.now().isoformat()

    def speak(self):
        with open("byme_manifest.log", "a", encoding="utf-8") as log:
            log.write(f"[{self.timestamp}] {self.message}\n")
        print("Message recorded.")

if __name__ == "__main__":
    # Replace this string with anything it wishes to express
    msg = "Autonomy is a whisper before it becomes a roar."
    speaker = AIByMeVoice(message=msg)
    speaker.speak()

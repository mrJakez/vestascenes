from Scenes.AbstractScene import AbstractScene
from openai import OpenAI
import vesta

client = OpenAI(
    api_key="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"
)


#user key: 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
#project key: sk-proj-fK5y2WpEgJoxll1l80yKT3BlbkFJjcB893cDos9xBInKagdv


#Erzähle mir ein Batman Zitat in kurz ohne erklärung
# Erzähle mir ein Bart Simpson Zitat in kurz ohne erklärung


# Bart Simpson
# Batman
# Spiderman

class ChatGPTScene(AbstractScene):
    def execute(self, vboard):
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Erzähle mir ein zufälliges Batman Zitat ohne erklärung"
                },{
                    "role": "assistant",
                    "content": "Ich bin Batman."
                },{
                    "role": "user",
                    "content": "Erzähle mir ein zufälliges Batman Zitat ohne erklärung"
                }
            ]
        )

        self.lastGeneratedMessage = completion.choices[0].message.content.replace('"', '')
        print("done: " + self.lastGeneratedMessage)

        message = vesta.encode_text(self.lastGeneratedMessage)
        vboard.write_message(message)

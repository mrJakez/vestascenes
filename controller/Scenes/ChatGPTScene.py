import random

from Scenes.AbstractScene import AbstractScene
from openai import OpenAI
import vesta
from Repository import Repository

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
        messages = Repository().get_chatgpt_history()

        current_question = self.get_new_question()
        new_question = {
            "role": "user",
            "content": current_question["question"]
        }

        Repository().save_chatgpt_history(new_question)
        messages.append(new_question)

        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages= messages
        )

        self.lastGeneratedMessage = completion.choices[0].message.content.replace('"', '')
        self.lastGeneratedMessage = self.lastGeneratedMessage.replace("Ö", 'oe').replace("ö", 'oe').replace("Ü", 'ue').replace("ü", 'ue').replace("Ä", 'Ae').replace("ä", 'ae')


        Repository().save_chatgpt_history({
            "role": "assistant",
            "content": self.lastGeneratedMessage
        })

        print("done: " + self.lastGeneratedMessage)

        #message = vesta.encode_text(self.lastGeneratedMessage)


        chars = vesta.encode_text(
            self.lastGeneratedMessage + "\n" + current_question["author"],
            valign="middle",
        )

        vboard.write_message(chars)

    def get_new_question(self):
        questions = [
            {
                "type": "quote",
                "question": "Erzähle mir ein zufälliges Batman Zitat ohne erklärung.",
                "author":   "Batman"
            },
            {
                "type": "quote",
                "question": "Erzähle mir ein zufälliges Bart Simpson Zitat ohne erklärung.",
                "author": "Bart Simpson"
            },
            {
                "type": "joke",
                "question": "Erzähle mir ein zufälligen Dad Joke ohne erklärung.",
                "author": "Dad"
            }
        ]

        return random.choice(questions)

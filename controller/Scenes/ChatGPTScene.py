import random
import uuid
import vesta
from openai import OpenAI

from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn
from Repository import Repository

import datetime

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

    priority: int = 50

    def execute(self):
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
            messages=messages
        )

        message = completion.choices[0].message.content.replace('"', '')
        message = message.replace("Ö", 'oe').replace("ö", 'oe').replace("Ü", 'ue').replace("ü", 'ue').replace("Ä", 'Ae').replace("ä", 'ae')

        Repository().save_chatgpt_history({
            "role": "assistant",
            "content": message
        })

        chars = vesta.encode_text(
            message + "\n" + current_question["author"],
            valign="middle",
        )
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(minutes=60)

        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self, start_date, end_date, f"{message} - {current_question["author"]}", chars)


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

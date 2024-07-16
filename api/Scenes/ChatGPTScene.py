import datetime
import random
import uuid
from typing import List

import vesta
from openai import OpenAI
from vesta.chars import Rows
from vesta.vbml import Component

from Helper.RawHelper import RawHelper
from Models.ChatGPTHistoryModel import ChatGPTHistoryModel
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

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
    priority: int = 100
    post_execution: bool = False

    def execute(self) -> SceneExecuteReturn:
        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        if not self.post_execution:
            return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self,
                                      start_date, end_date, "not executed yet", None)

        question_model = self.get_new_question_model()
        Repository().save_chatgpt_history(question_model)

        message_history = Repository().get_chatgpt_history()
        formatted_messages = self.get_messages_in_chatgpt_format(message_history)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=formatted_messages
        )

        message = RawHelper.replace_umlaute(completion.choices[0].message.content)
        message = RawHelper.replace_characters_with_codes(message) # otherwise ' will be replaced with "&#39; etc"
        answer_model = ChatGPTHistoryModel(role="assistant", content=message, author=question_model.author)
        Repository().save_chatgpt_history(answer_model)

        chars = self.get_vbml(message, answer_model.author)

        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self,
                                  start_date, end_date, f"{message} - {answer_model.author}", chars)

    def post_execute(self) -> SceneExecuteReturn:
        self.post_execution = True
        res = self.execute()
        self.post_execution = False
        return res

    def get_new_question_model(self) -> ChatGPTHistoryModel:
        questions = [
            {
                "type": "quote",
                "question": "Erzähle mir ein zufälliges Batman Zitat ohne Erklärung.",
                "author": "Batman"
            },
            {
                "type": "quote",
                "question": "Erzähle mir ein zufälliges Bart Simpson Zitat ohne Erklärung.",
                "author": "Bart Simpson"
            },
            {
                "type": "joke",
                "question": "Erzähle mir ein zufälligen Dad Joke ohne Erklärung.",
                "author": "Dad"
            }
        ]

        chosen = random.choice(questions)
        return ChatGPTHistoryModel(role="user", content=chosen["question"], author=chosen["author"])

    def get_messages_in_chatgpt_format(self, models: List[ChatGPTHistoryModel]) -> List:
        messages = []
        for model in models:
            messages.append({
                "role": model.role,
                "content": model.content
            })

        return messages

    def get_vbml(self, message, author) -> Rows:
        props = {
            "message": message,
            "author": author,
        }

        message_component = Component(
            template="{{message}}",
            justify="left",
            align="center",
            height=5,
            width=22
        )

        author_component = Component(
            template="{{author}}",
            justify="right",
            align="top",
            height=1,
            width=22
        )

        vbml_client = vesta.VBMLClient()
        chars = vbml_client.compose([message_component, author_component], props)
        return chars

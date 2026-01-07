import datetime
import random
import uuid
from typing import List, Optional

import vesta
from openai import OpenAI
from vesta.chars import Rows
from vesta.vbml import Component

from Helper.RawHelper import RawHelper
from Models.ChatGPTHistoryModel import ChatGPTHistoryModel
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn


class ChatGPTScene(AbstractScene):
    priority: int = 100
    post_execution: bool = False

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:
        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        if not self.post_execution:
            return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self,
                                      start_date, end_date, "not executed yet", None)

        question_model = self.get_new_question_model()
        Repository().save_chatgpt_history(question_model)

        message_history = Repository().get_chatgpt_history()
        formatted_messages = self.get_messages_in_chatgpt_format(message_history)

        client = OpenAI(api_key= self.get_config("openai_key"))

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=formatted_messages
        )

        message = completion.choices[0].message.content

        if question_model.author == "replace_twohashmarks":
            orig_message = message.split("##")
            message = orig_message[0]
            question_model.author = orig_message[1]

        if message.startswith("„") or  message.startswith("\""):
            message = message[1:]

        if message.endswith("“") or  message.endswith("\""):
            message = message[:-1]

        message = RawHelper.replace_umlaute(message)
        message = RawHelper.replace_characters_with_codes(message)  # otherwise ' will be replaced with "&#39;"

        answer_model = ChatGPTHistoryModel(role="assistant", content=message, author=question_model.author)
        Repository().save_chatgpt_history(answer_model)

        chars = self.get_vbml(message, answer_model.author)

        return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self,
                                  start_date, end_date, f"{message} - {answer_model.author}", chars)

    def post_execute(self, vboard) -> Optional[SceneExecuteReturn]:
        self.post_execution = True
        res = self.execute(vboard)
        self.post_execution = False
        return res

    # noinspection PyMethodMayBeStatic
    # noinspection SpellCheckingInspection
    def get_new_question_model(self) -> ChatGPTHistoryModel:
        questions = [
            {
                "type": "quote",
                "question": "Erzähle mir ein zufälliges Batman Zitat ohne Erklärung.",
                "author": "Batman"
            },
            {
                "type": "quote",
                "question": "Erzähle mir ein zufälliges Ironman Zitat ohne Erklärung.",
                "author": "Tony Stark"
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
            },
            {
                "type": "joke",
                "question": "Erzähle mir ein zufälligen kurzen Lego Witz ohne Erklärung.",
                "author": "Minifigur"
            },
            {
                "type": "quote",
                "question": "Erzähle mir ein zufälliges Chuck Norris Zitat ohne Erklärung.",
                "author": "Chuck Norris"
            }
        ]

        chosen = random.choice(questions)
        return ChatGPTHistoryModel(role="user", content=chosen["question"], author=chosen["author"])

    # noinspection PyMethodMayBeStatic
    def get_messages_in_chatgpt_format(self, models: List[ChatGPTHistoryModel]) -> List:
        messages = []
        for model in models:
            messages.append({
                "role": model.role,
                "content": model.content
            })

        return messages

    # noinspection PyMethodMayBeStatic
    def get_vbml(self, message, author) -> Rows:
        leftmargin = 0
        if len(message) < 40:
            leftmargin = 2
        elif len(message) < 70:
            leftmargin = 1

        props = {
            "message": message,
            "author": author,
        }

        component = Component(
            template="{{message}}\n-{{author}}",
            width=(22 - leftmargin * 2),
            height=6,
            justify="left",
            align="center",
            absolute_position={
                "x": leftmargin,
                "y": 0
            }
        )

        vbml_client = vesta.VBMLClient()
        chars = vbml_client.compose([component], props)
        return chars

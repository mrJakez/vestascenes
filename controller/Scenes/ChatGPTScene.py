#from .Demo import Scene
import random

from Scenes.AbstractScene import AbstractScene
from Repository import Repository
from vestaboard.formatter import Formatter

class ChatGPTScene(AbstractScene):
    def execute(self, vboard):
        vboard.post("chatgpt scene")
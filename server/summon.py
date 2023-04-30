
from utils import read_json
from copy import deepcopy

class Summon:
    def __init__(self, name):
        self._name = name
        self.detail = deepcopy(summon_dict[name])
        self.effect: list[dict] = self.detail["effect"]
        self.usage = self.detail["usage"]
        self.modifies = self.detail["modify"]
        self.type = {}
        if "type" in self.detail:
            self.type = self.detail["type"]
        self.card_type = name
        if "card_type" in self.detail:
            self.card_type = self.detail["card_type"]
        self.stack = 1
        if "stack" in self.detail:
            self.stack = self.detail["stack"]
        self.element = None
        if "element" in self.detail:
            self.element = self.detail["element"]
        self.counter = {}
        if "counter" in self.detail:
            self.counter = {i: 0 for i in self.detail["counter"]}

    def consume_usage(self, value):
        if isinstance(value, str):
            if value == "all":
                self.usage = 0
        else:
            self.usage -= value
        if self.usage <= 0:
            return "remove"

    def get_name(self):
        return self._name

summon_dict = read_json("summon.json")
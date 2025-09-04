import re
import logging

class Executor:
    def __init__(self, history, recordPattern):
        self.register = 0
        self.history = history
        self.recordPattern = recordPattern
        self.head = 0

    def run(self, stopEvent):
        # recordPattern = r"([+-*/]):(\d+)"
        while not stopEvent.is_set():
            if self.head < self.history.getLength():
                record = self.history.getRecord(self.head)
                self.apply(record)
                self.head += 1

    def apply(self, record):
        match = re.search(self.recordPattern, record)
        operator = match.group(1)
        operand = int(match.group(2))

        if operator == "+":
            self.register += operand
        elif operator == "-":
            self.register -= operand
        elif operator == "*":
            self.register *= operand
        elif operator == "/":
            self.register /= operand
        else:
            logging.error(f"Invalid operator: {operator}")

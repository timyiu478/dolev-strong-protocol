class History:
    def __init__(self, filename):
        self.history = []
        self.filename = filename
        self.dirtyIdx = 0  # start index of records that are not saved persistently

        with open(filename, "r") as file:
            lines = file.readlines()
            for line in lines:
                record = line.strip()
                self.history.append(record)
            self.dirtyIdx = len(lines)

    def appendRecord(self, record):
        self.history.append(record)

    def getRecord(self, idx):
        return self.history[idx]

    def getHistory(self):
        return self.history

    def save(self):
        with open(self.filename, "a+") as file:
            for i in range(self.dirtyIdx, len(self.history)):
                file.write(f"{self.history[i]}\n")
        self.dirtyIdx = len(self.history)

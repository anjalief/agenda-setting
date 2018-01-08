from collections import namedtuple
Gold = namedtuple('Gold', ['is_external', 'category'])

class TrackCorrect():
    def __init__(self):
        self.correct_external = 0
        self.total_correct = 0
        self.estimated_external = 0
        self.gold_external = 0
        self.count = 0

    def update(self, gold_is_external, is_external):
        self.count += 1
        if is_external:
            self.estimated_external += 1
            if gold_is_external:
                self.correct_external += 1
                self.total_correct += 1
        else:
            if not gold_is_external: # both are not external
                self.total_correct += 1
        if gold_is_external:
            self.gold_external += 1

    def get_stats(self):
        precision = float(self.correct_external) / max(self.estimated_external, 1)
        recall = float(self.correct_external) / max(self.gold_external, 1)
        accuracy = float(self.total_correct) / self.count
        return precision, recall, accuracy, self.gold_external, self.count

def LoadGold(filename, track_by_topic):
    g = []
    for line in open(filename):
        vals = line.strip().split()
        is_external = bool(int(vals[2]))
        if track_by_topic:
            category = vals[0].split('/')[6]
        else:
            category = "DUMMY"
        g.append(Gold(is_external, category))
    return g




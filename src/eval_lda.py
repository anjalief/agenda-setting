import argparse
from article_utils import LoadVectors, Similarity
from collections import namedtuple

parser = argparse.ArgumentParser()
parser.add_argument('--gold_vectors',
    default="../focused_crawl/external_policy.txt.tok.lda")
parser.add_argument('--filename')
parser.add_argument('--true_vals')
parser.add_argument('--track_by_topic', action='store_true') # only for English
args = parser.parse_args()

threshold_vals = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]

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

def GetSimilarityMatch(vectors, gold_vector):
    similarity = []
    for v in vectors:
        similarity.append(Similarity(v, gold_vector))
    return similarity

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

def TryThreshold(t, sims, gold):
    tracker = TrackCorrect()
    tracker_by_topic = {}
    for score,g in zip(sims, gold):
        is_external = score < t
        tracker.update(g.is_external, is_external)

        t_by_topic = tracker_by_topic.get(g.category, TrackCorrect())
        t_by_topic.update(g.is_external, is_external)
        tracker_by_topic[g.category] = t_by_topic

    return tracker, tracker_by_topic


def main():
  gold_vector = LoadVectors(args.gold_vectors)[0]

  vectors = LoadVectors(args.filename)
  gold = LoadGold(args.true_vals, args.track_by_topic)
  sims = GetSimilarityMatch(vectors, gold_vector)
  for t in threshold_vals:
      tracker, tracker_by_topic = TryThreshold(t, sims, gold)
      p, r, a, e, _ = tracker.get_stats()
      print "Threshold:", t, "P:", p, "R:", r, "A:", a
      print "****************************************************************"
      for category in tracker_by_topic:
          p1, r1, a1, e1, c1 = tracker_by_topic[category].get_stats()
          print "Category:", category, "P:", p1, "R:", r1, "A:", a1, "Number of actual external", e1, "Total: ", c1
      print "****************************************************************\n\n"

if __name__ == '__main__':
  main()

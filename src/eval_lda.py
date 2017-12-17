import argparse
from article_utils import LoadVectors, Similarity


parser = argparse.ArgumentParser()
parser.add_argument('--gold_vectors',
    default="../focused_crawl/external_policy.txt.tok.lda")
parser.add_argument('--filename')
parser.add_argument('--true_vals')
args = parser.parse_args()

threshold_vals = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]

def GetSimilarityMatch(vectors, gold_vector):
    similarity = []
    for v in vectors:
        similarity.append(Similarity(v, gold_vector))
    return similarity

def LoadGold(filename):
    g = []
    for line in open(filename):
        vals = line.strip().split()
        g.append(bool(int(vals[2])))
    return g

def TryThreshold(t, sims, gold):
    correct_external = 0
    total_correct = 0
    estimated_external = 0
    gold_external = 0
    for score,g in zip(sims, gold):
        is_external = False
        if (score < t):
            is_external = True
        if is_external:
            estimated_external += 1
            if g: # both are external
                correct_external += 1
                total_correct += 1
        else:
            if not g: # both are not external
                total_correct += 1
        if g:
            gold_external += 1

    precision = float(correct_external) / max(estimated_external, 1)
    recall = float(correct_external) / gold_external
    accuracy = float(total_correct) / len(sims)
    return precision, recall, accuracy, gold_external


def main():
  gold_vector = LoadVectors(args.gold_vectors)[0]

  vectors = LoadVectors(args.filename)
  gold = LoadGold(args.true_vals)
  sims = GetSimilarityMatch(vectors, gold_vector)
  for t in threshold_vals:
      p, r, a, e = TryThreshold(t, sims, gold)
      print "Threshold:", t, "P:", p, "R:", r, "A:", a
  print "Number of actual external", e


if __name__ == '__main__':
  main()

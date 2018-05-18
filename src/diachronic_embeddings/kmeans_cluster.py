# Use KNN to generate possible lexicons
import gensim
import argparse
from gensim.models import KeyedVectors, Word2Vec
from utils import *
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
from sklearn import preprocessing
import sys
sys.path.append("..")
from article_utils import get_files_by_time_slice

from get_top_words import get_top_words

from scipy.spatial.distance import cosine
import pickle

# seed_words = ["экономического",
#               "Ресурсы",
#               "мораль",
#               "справедливость",
#               "легальность",
#               "политика",
#               "преступление",
#               "защита",
#               "здоровье",
#               "качество",
#               "культурный",
#               "общественного",
#               "политическая",
#               "иностранные",]
# seed_words = [w.lower() for w in seed_words]
seed_words = [["экономического", "финансовый", "финансы", "экономика"],
              ["Ресурсы"], # "вместимость"
              ["мораль", "моральный", "этика","религия","религиозная"], # этический
              ["справедливость", "равенство"], # "Справедливая"
              ["правовой", "конституции"], # "легальность", "конституционная", "юриспруденция"
              ["политика", "Политический"], # "полисы"
              ["преступление", "преступник", "наказание", "полицию", "арестовала"], # правоприменение Crime and punishment
              ["защита", "безопасность", "военные", "война", "террористом", 'смертников', 'заложников', 'допросов'], # defense, security
              ["здоровье", "безопасность", "здравоохранение"], # санитария
              ["качество", "богатство", "счастье", "благополучие"],
              ["культурный", "традиции", "обычай"],
              ["общественного", "голосование"], # "демографический"
              ["политическая", "политика", "политик", "лоббирование", "выборы", "избиратель"],
              ["внешний", "иностранные", "Международный"]
              ]
seed_words = [[w.lower() for w in word_list] for word_list in seed_words]

def get_sample_error(input_array, cluster_centers, cluster_labels):
    running_error = 0

    for i in range(0, len(input_array)):
        label = cluster_labels[i]
        d = cosine(input_array[i], cluster_centers[label])
        running_error += d * d
    return running_error

def make_clusters(vocab, base_model, n_clusters):
    vocab_vectors = []
    vocab_in_order = []
    for v in vocab:
        if not v in base_model:
            continue
        vector = base_model[v]
        vocab_in_order.append(v)
#        vocab_vectors.append(vector / sum(vector))
        vocab_vectors.append(vector)
    input_array = np.asarray(vocab_vectors)
    input_norm = preprocessing.normalize(input_array)
    kmeans = KMeans(n_clusters, max_iter=1000).fit(input_norm)
    vocab = vocab_in_order
    assert(len(vocab) == len(kmeans.labels_))
    pickle.dump((vocab, kmeans), open("kmeans_out.pickle", "wb"))

   # print(n_clusters, kmeans.inertia_)
    # print (n_clusters, get_sample_error(input_norm, kmeans.cluster_centers_, kmeans.labels_))
    # return

    label_to_list = defaultdict(list)
    # Choose the 10 vocab words closest to the center as the seed
    for l,v in zip(kmeans.labels_, vocab):
        label_to_list[l].append(v)
    final_label_to_list = defaultdict(list)
    for l in label_to_list:
        # sort list by distance from cluster center and take 10 smallest elements
#        print (cosine(kmeans.cluster_centers_[l], base_model[label_to_list[l][0]]))
        final_label_to_list[l]= sorted(label_to_list[l], key=lambda x: cosine(kmeans.cluster_centers_[l], base_model[x]))[:10]

    # for i,l in enumerate(kmeans.cluster_centers_):
    #     label_to_list[i] = [v[0] for v in base_model.most_similar(positive=[l], topn=10)]

    return final_label_to_list


def add_other_seed(seeds):
    max_dist = -100
    v1 = None
    v2 = None
    for i in range(0, len(seeds) - 1):
        for j in range(i+1, len(seeds)):
            dist = cosine(seeds[i], seeds[j])
            if dist > max_dist:
                max_dist = dist
                v1 = seeds[i]
                v2 = seeds[j]
    other = (v1 + v2) * -1
    seeds.append(other)
    return seeds

def make_clusters_from_seed(vocab, base_model, n_clusters = 15):
    vocab_vectors = []
    seed_to_idx = {}

    for v in vocab:
        vector = base_model[v]
        vocab_vectors.append(vector)

    for v in vocab_vectors:
        if (len(v) != EMBED_LENGTH):
            print(v.shape)
            return

    # get the vectors for the seeds. We'll throw them on the end
    # so that they get normalized with everything else
    seeds = []
    for seed_list in seed_words:
        this_seed_vectors = np.zeros(EMBED_LENGTH)
        for word in seed_list:
            this_seed_vectors += base_model[word]

        seeds.append(this_seed_vectors)
    add_other_seed(seeds)
    vocab_vectors += seeds

    input_array = np.stack(vocab_vectors)
    print(input_array.shape)
    input_norm = preprocessing.normalize(input_array)

    print (input_norm.shape)
    final_input = input_norm[0:len(vocab)]
    final_seed = input_norm[len(vocab):]
    print(final_input.shape)
    print(final_seed.shape)

    kmeans = KMeans(n_clusters, init=final_seed, max_iter=1000).fit(final_input)

    label_to_list = defaultdict(list)
    for l,v in zip(kmeans.labels_, vocab):
        label_to_list[l].append(v)
    for l in label_to_list:
        print (l, label_to_list[l][:100])

def make_sim_clusters(vocab, model_path, timestep, n_clusters):
    vocab_to_similarity = defaultdict(list)
    date_seq, filenames = get_files_by_time_slice(
        model_path, timestep, suffix= "_" + timestep + ".pickle")
    for filename in filenames:
        assert (len(filename) == 1)
        wv = KeyedVectors.load(filename[0])
        for w in vocab:
            vocab_to_similarity[w].append(wv.similarity(w, "USA"))
    vocab_vectors = []
    for v in vocab_to_similarity:
        vocab_vectors.append(vocab_to_similarity[v])
    input_array = np.asarray(vocab_vectors)
#    input_norm = preprocessing.normalize(input_array)
    kmeans = KMeans(n_clusters, max_iter=1000).fit(input_array)
    label_to_list = defaultdict(list)
    for l,v in zip(kmeans.labels_, vocab):
        label_to_list[l].append(v)
    for l in label_to_list:
        print (l, label_to_list[l])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="/usr1/home/anjalief/word_embed_cache/ner_model_cache2/izvestia_yearly/")
    parser.add_argument("--keywords", default="./keywords.txt")
    parser.add_argument("--article_glob", default="./keywords.txt")
    parser.add_argument('--timestep', type=str,
                        default='yearly',
                        choices=['monthly', 'quarterly', 'yearly'])
    args = parser.parse_args()

    model_name1 = get_model_filename(args.model_path, YEARS[0], MONTHS[0], args.timestep)
    base_model = KeyedVectors.load(model_name1)
    vocab = base_model.index2entity

    if False:
        keywords = set(load_file(args.keywords))
        vocab = [x[0] for x in base_model.most_similar(positive=keywords, topn=5000)]
        vocab = list(filter(is_noun, vocab))
        # for s in seed_words:
        #     for q in s:
        #         if not q in base_model:
        #             print ("SKIPPING", q)
        #             continue
        #         vocab.append(q)
        make_clusters(vocab, base_model, 15)
        return

    if False:
        keywords = set(load_file(args.keywords))
        vocab = [x[0] for x in base_model.most_similar(positive=keywords, negative=["RUSSIA"], topn=10000)]
        for s in seed_words:
            for q in s:
                if not q in base_model:
                    print ("SKIPPING", q)
                    continue
                vocab.append(q)
        #    vocab = list(filter(is_adjective, vocab))
        make_clusters_from_seed(vocab, base_model, 10)

    if False:
        vocab = []
        for seed in seed_words:
            vocab += [x[0] for x in base_model.most_similar(positive=seed, topn=500)]


        vocab = list(set(vocab))
        print(len(vocab))
    #    make_sim_clusters(vocab, args.model_path, args.timestep, 10)
        for s in seed_words:
            for q in s:
                vocab.append(q)
        make_clusters_from_seed(vocab, base_model, 15)

    if True:
        _,_,top_words = get_top_words(args.article_glob)

        vocab = [k for k in sorted(top_words, key=top_words.get, reverse = True)[:10000]]

        # I think there should be ~500 words per cluster
        # Let's give it a slightly higher number
#        for i in range(50,751,50):
        for i in range(300,301):
            make_clusters(vocab, base_model, i)

if __name__ == "__main__":
    main()

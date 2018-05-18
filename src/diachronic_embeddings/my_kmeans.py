from copy import deepcopy
import numpy as np
import matplotlib
matplotlib.use('tkagg')
from matplotlib import pyplot as plt

from scipy.spatial.distance import cosine
from sklearn import preprocessing
from copy import deepcopy

from sklearn.cluster import KMeans

class MYKMeans:
    def __init__(self, n_clusters, max_iter = 1000):
        self.n_clusters = n_clusters
        self.centers = None
        self.max_iter = max_iter

    # compute cosine distance between X and everything in Y
    def cos_distance(self, X, Y):
        assert(len(X.shape) == 1)
        assert(len(X) == len(Y[0]))

        return [cosine(X, v) for v in Y]

    def get_sample_labels(self, input_array, cluster_centers):
        output = np.zeros(self.num_samples, dtype=np.int8)
        for i in range(0, self.num_samples):
            dist_to_centers = self.cos_distance(input_array[i], cluster_centers)
            output[i] = np.argmin(dist_to_centers)
        return output

    # since we're using cosine distance, length doesn't matter
    # we can just sum to find centers
    def find_new_centers(self, input_array, cluster_labels):
        output = np.zeros((self.n_clusters, self.num_features))

        for i in range(0, self.num_samples):
            label = cluster_labels[i]
            output[label] += input_array[i]

        return output

    def get_cluster_movement(self, old_clusters, new_clusters):
        assert(len(old_clusters) == len(new_clusters))
        assert(len(old_clusters) == self.n_clusters)

        cos_dist = [cosine(old_clusters[i], new_clusters[i]) \
                        for i in range(0, self.n_clusters)]
        return sum([c * c for c in cos_dist])

    # return sum of squared errors
    def get_sample_error(self, input_array, cluster_centers, cluster_labels):
        running_error = 0

        for i in range(0, self.num_samples):
            label = cluster_labels[i]
            d = cosine(input_array[i], cluster_centers[label])
            running_error += d * d
        return running_error

    # input is num_samples by num_features
    def train(self, input_array):
        self.num_samples = input_array.shape[0]
        self.num_features = input_array.shape[1]

        current_clusters = preprocessing.normalize(np.random.rand(self.n_clusters, self.num_features))
        last_centers = deepcopy(current_clusters)
        input_array = preprocessing.normalize(input_array)


        iter_num = 0
        while True:
            print ("iter num", iter_num)
            # Shouldn't matter but we normalize everything
            sample_labels = self.get_sample_labels(input_array, current_clusters)
            current_clusters = self.find_new_centers(input_array, sample_labels)
            current_clusters = preprocessing.normalize(current_clusters)
            movement = self.get_cluster_movement(current_clusters, last_centers)
            if movement == 0 or iter_num == self.max_iter:
                break
            last_centers = deepcopy(current_clusters)
            iter_num += 1

        self.final_sample_labels = self.get_sample_labels(input_array, current_clusters)
        self.cluster_centers = current_clusters
        print (self.get_sample_error(input_array, current_clusters, self.final_sample_labels))

def plot(X, cluster_labels, cluster_centers, k):
    colors = ['r', 'g', 'b', 'y', 'c', 'm']
    fig, ax = plt.subplots()
    for i in range(k):
        points = np.array([X[j] for j in range(len(X)) if cluster_labels[j] == i])
        ax.scatter(points[:, 0], points[:, 1], s=7, c=colors[i])
    ax.scatter(cluster_centers[:, 0], cluster_centers[:, 1], marker='*', s=200, c='#050505')
    plt.show()

def main():
    test = np.random.rand(200, 3)

    knn = MYKMeans(6)
    knn.train(test)
#    plot(preprocessing.normalize(test), knn.final_sample_labels, knn.cluster_centers, knn.n_clusters)

    import sklearn
    input_norm = preprocessing.normalize(test)
    kmeans = sklearn.cluster.KMeans(6, max_iter=1000).fit(input_norm)
    print(kmeans.inertia_)
    print (knn.get_sample_error(input_norm, kmeans.cluster_centers_, kmeans.labels_))
    plot(input_norm, kmeans.labels_, kmeans.cluster_centers_, 6)





if __name__ == "__main__":
    main()

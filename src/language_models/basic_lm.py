import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from gensim.corpora import Dictionary
from math import log, exp

import sys
sys.path.append("..")
from article_utils import LoadArticles
import argparse

USE_CUDA = torch.cuda.is_available()

class BasicLM(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, vocab_size):
        super(BasicLM, self).__init__()
        self.hidden_dim = hidden_dim

        # embedding layer, vector for each word in vocab
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.lstm = nn.LSTM(embedding_dim, hidden_dim)

        # The linear layer that maps from hidden state space to vocab space
        self.hidden2vocab = nn.Linear(hidden_dim, vocab_size)
        self.hidden = self.init_hidden()

    def init_hidden(self):
        # Before we've done anything, we dont have any hidden state.
        # Refer to the Pytorch documentation to see exactly
        # why they have this dimensionality.
        # The axes semantics are (num_layers, minibatch_size, hidden_dim)
        if USE_CUDA:
            return (autograd.Variable(torch.zeros(1, 1, self.hidden_dim)).cuda(),
                    autograd.Variable(torch.zeros(1, 1, self.hidden_dim)).cuda())
        return (autograd.Variable(torch.zeros(1, 1, self.hidden_dim)),
                autograd.Variable(torch.zeros(1, 1, self.hidden_dim)))

    def forward(self, document):
        # look up embeddings for each word in the document
        embeds = self.word_embeddings(document)

        # we pass hidden state through entire document
        lstm_out, self.hidden = self.lstm(
            embeds.view(len(document), 1, -1), self.hidden)
        vocab_space = self.hidden2vocab(lstm_out.view(len(document), -1))
        # we want score over vocabulary for each word in the document
        scores = F.log_softmax(vocab_space, dim=1)
        return scores

def to_variable(doc):
    ten = torch.LongTensor(doc)
    var = autograd.Variable(ten)
    if USE_CUDA:
        return var.cuda()
    return var

def to_float_variable(data):
    ten = torch.FloatTensor(data)
    var = autograd.Variable(ten)
    if USE_CUDA:
        return var.cuda()
    return var

def train(vocab_size, num_epochs, training_data, embedding_dim, hidden_dim):
    model = BasicLM(embedding_dim, hidden_dim, vocab_size)
    if USE_CUDA:
        model = model.cuda()
    # Input has size num_samples x vocab_size (probability for each sample)
    # Target has size num_samples x 1 (true tag)
    loss_function = nn.NLLLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    # See what the scores are before training
    # Note that element i,j of the output is the score for tag j for word i.
    # inputs = to_variable(training_data[0])
    # scores = model(inputs)
    # print("Initial loss", loss_function(inputs, scores))


    for epoch in range(num_epochs):
        print ("Starting Epoch", epoch)
        loss_cc = 0
        perplexity = 0
        for i,document in enumerate(training_data):

            # Need to clear gradients before each instance
            model.zero_grad()

            # Need to clear out the hidden state of the LSTM,
            model.hidden = model.init_hidden()

            # turn inputs into Variables of word indices.
            doc_input = to_variable(document)

            # Step 3. Run our forward pass.
            predicted_document = model(doc_input)

            # Step 4. Compute the loss, gradients, and update the parameters by
            #  calling optimizer.step()
            loss = loss_function(predicted_document, doc_input)
            loss.backward()
            optimizer.step()

            loss_cc += loss.data[0]
            # by default, loss is divided by # words per doc
            # we want loss over the entire corpus
            perplexity += loss.data[0] * len(doc_input)

        loss = loss_cc / len(training_data)
        print (word_count, loss, perplexity / word_count, exp(perplexity / word_count))



    # See what the scores are after training
    # inputs = to_variable(training_data[0])
    # scores = model(inputs)
    # print("Final loss", loss_function(inputs, scores))


def load_data(filename):
    # Load articles from file
    articles, _ = LoadArticles(filename, verbose=False, split=True)

    # Create vocab dictionary for articles
    dct = Dictionary(articles)
    # dct.filter_extremes(no_below=5, no_above=500, keep_n=100000)
    dct.filter_extremes(no_below=5, no_above=500, keep_n=50000)

    # convert words to indices
    # we make UNK the highest index
    vocab_size = len(dct)
    articles = [dct.doc2idx(a, unknown_word_index=vocab_size) for a in articles]

    return articles, dct

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob')
    args = parser.parse_args()

    data, dictionary = load_data(args.article_glob)

    # +1 for UNK
    vocab_size = len(dictionary) + 1
    epochs = 10
    embedding_dim = 100
    hidden_dim = 100
    print (vocab_size)

    train(vocab_size, epochs, data, embedding_dim, hidden_dim)


if __name__ == "__main__":
    main()

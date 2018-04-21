#!/usr/bin/env python

import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import argparse
from gensim.corpora import Dictionary
from math import exp
from sklearn.model_selection import StratifiedKFold

import sys
sys.path.append("..")
from article_utils import LoadArticles, get_date
from econ_utils import load_monthly_gdp, load_rtsi

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

    def forward(self, document, econ_data):
        # look up embeddings for each word in the document
        embeds = self.word_embeddings(document)

        # we pass hidden state through entire document
        lstm_out, self.hidden = self.lstm(
            embeds.view(len(document), 1, -1), self.hidden)
        vocab_space = self.hidden2vocab(lstm_out.view(len(document), -1))
        # we want score over vocabulary for each word in the document
        scores = F.log_softmax(vocab_space, dim=1)
        return scores

def to_variable(doc, is_volatile=False):
    ten = torch.LongTensor(doc)
    var = autograd.Variable(ten, volatile=is_volatile)
    if USE_CUDA:
        return var.cuda()
    return var

def to_float_variable(data, is_volatile=False):
    ten = torch.FloatTensor(data)
    var = autograd.Variable(ten, volatile=is_volatile)
    if USE_CUDA:
        return var.cuda()
    return var

def train(vocab_size, num_epochs, data, econ_data, train_indices, test_indices, embedding_dim, hidden_dim):
    model = BasicLM(embedding_dim, hidden_dim, vocab_size)
    if USE_CUDA:
        model = model.cuda()
    # Input has size num_samples x vocab_size (probability for each sample)
    # Target has size num_samples x 1 (true tag)
    loss_function = nn.NLLLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    word_count = 0
    for idx in train_indices:
        word_count += len(data[idx])

    # See what the scores are before training

    for epoch in range(num_epochs):
        print ("Starting Epoch", epoch)
        loss_cc = 0
        perplexity = 0
        for idx in train_indices:

            # Need to clear gradients before each instance
            model.zero_grad()

            # Need to clear out the hidden state of the LSTM,
            model.hidden = model.init_hidden()

            # turn inputs into Variables of word indices.
            doc_input = to_variable(data[idx], False)
            econ_input = to_float_variable(econ_data[idx], False)

            # Step 3. Run our forward pass.
            predicted_document = model(doc_input, econ_input)

            # Step 4. Compute the loss, gradients, and update the parameters by
            #  calling optimizer.step()
            loss = loss_function(predicted_document, doc_input)

            loss.backward()
            optimizer.step()

            loss_cc += loss.data[0]
            # by default, loss is divided by # words per doc
            # we want loss over the entire corpus
            perplexity += loss.data[0] * len(doc_input)

        # DONE EPOCH
        loss = loss_cc / len(train_indices)
        print (word_count, loss, perplexity / word_count, exp(perplexity / word_count))

    # DONE TRAINING
        test_perplexity = 0
        test_word_count = 0
        for idx in test_indices:
            test_word_count += len(data[idx])
            doc_input = to_variable(data[idx])
            predicted_document = model(doc_input)
            lossy = loss_function(predicted_document, doc_input)
            test_perplexity += lossy.data[0] * len(doc_input)

        print ("TEST RESULTS")
        print (test_word_count, test_perplexity / test_word_count, exp(test_perplexity / test_word_count))

def load_data(filename):
    # Load articles from file
    articles, indices = LoadArticles(filename, verbose=False, split=True)

    # Create vocab dictionary for articles
    dct = Dictionary(articles)
    # dct.filter_extremes(no_below=5, no_above=500, keep_n=100000)
    dct.filter_extremes(no_below=5, no_above=500, keep_n=50000)

    # convert words to indices
    # we make UNK the highest index
    vocab_size = len(dct)
    articles = [dct.doc2idx(a, unknown_word_index=vocab_size) for a in articles]

    return articles, indices, dct

# for each article, we need to get the date, then append whatever
# econ info we have
def get_economic_info(article_indices, monthly_data, quarterly_data):
    return article_indices

# converts article_index to a date index, and a date_to_idx mapping
def process_dates(article_indices):
    article_dates = [get_date(i[0]) for i in article_indices]
    # also create an index mapping
    s = set(article_dates)
    date_list = list(sorted(s))
    date_to_idx = {}
    for i,d in enumerate(date_list):
        date_to_idx[d] = i
    article_dates = [date_to_idx[d] for d in article_dates]
    return article_dates, date_to_idx

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--article_glob', default="/usr1/home/anjalief/corpora/russian/Izvestiia/*/*.tok")
    parser.add_argument('--monthly_gdp_file', default="/usr1/home/anjalief/corpora/russian/russian_monthly_gdp.csv")
    parser.add_argument('--rtsi_file', default="/usr1/home/anjalief/corpora/russian/russian_rtsi_rub.csv")
    args = parser.parse_args()

    data, indices, dictionary = load_data(args.article_glob)
    print(indices[-1])

    article_dates, date_to_idx = process_dates(indices)

    # get economic data
    idx_to_gdp = load_monthly_gdp(args.monthly_gdp_file, date_to_idx)
    idx_to_rtsi = load_rtsi(args.rtsi_file, date_to_idx)

    gdp_data = [idx_to_gdp[x] for x in article_dates]
    rtsi_data = [idx_to_rtsi[x] for x in article_dates]

    # merge into single list
    econ_data = [y + [x] for x,y in zip(gdp_data, rtsi_data)]
    print (econ_data[-1])
    print (len(econ_data), len(article_dates), len(data))

    # 10% for test, (10% for validation?)
    skf = StratifiedKFold(n_splits=10)

    # self note: could get validation set by stratified splitting test set
    for train_index, test_index in skf.split(data, article_dates):
        # +1 for UNK
        vocab_size = len(dictionary) + 1
        epochs = 30
        embedding_dim = 100
        hidden_dim = 100
        train(vocab_size, epochs, data, econ_data, train_index, test_index, embedding_dim, hidden_dim)
        break

if __name__ == "__main__":
    main()

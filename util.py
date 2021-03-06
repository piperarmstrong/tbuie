import ankura
from sklearn.linear_model import LogisticRegression
import scipy

Z = 'z'

# corpus_data was pickled as this tuple:
#   (Q, labels, train_dev_ids, train_dev_corpus,
#   train_ids, train_corpus, dev_corpus, dev_ids,
#   test_ids, test_corpus, gs_anchor_vectors,
#   gs_anchor_indices, gs_anchor_tokens)

def get_logistic_regression_accuracy(unpickled_corpus_data, anchors, attribute_name='binary_rating'):
    Q = unpickled_corpus_data[0]
    train_ids = unpickled_corpus_data[2] # train_dev ids and corpus from tbuie
    train_corpus = unpickled_corpus_data[3]
    test_ids = unpickled_corpus_data[8] # This is the test data, not the dev data used in tbuie.
    test_corpus = unpickled_corpus_data[9]
    num_topics = len(anchors)

    train_target = [doc.metadata[attribute_name] for doc in train_corpus.documents]
    test_target = [doc.metadata[attribute_name] for doc in test_corpus.documents]

    topics = ankura.anchor.recover_topics(Q, anchors, 1e-5)

    ankura.topic.sampling_assign(train_corpus, topics, z_attr=Z)
    ankura.topic.sampling_assign(test_corpus, topics, z_attr=Z)

    train_matrix = scipy.sparse.lil_matrix((len(train_corpus.documents), num_topics * len(train_corpus.vocabulary)))
    test_matrix = scipy.sparse.lil_matrix((len(test_corpus.documents), num_topics * len(test_corpus.vocabulary)))

    for i, doc in enumerate(train_corpus.documents):
        for j, t in enumerate(doc.tokens):
            train_matrix[i, t[0] * num_topics + doc.metadata[Z][j]] += 1

    for i, doc in enumerate(test_corpus.documents):
        for j, t in enumerate(doc.tokens):
            test_matrix[i, t[0] * num_topics + doc.metadata[Z][j]] += 1

    lr = LogisticRegression()
    lr.fit(train_matrix, train_target)

    return lr.score(test_matrix, test_target)

# Code is based on code snippets from Pyterrier documentation:
# https://pyterrier.readthedocs.io/en/latest/ltr.html

import time
import pyterrier as pt
from pyterrier.measures import *
import xgboost as xgb

if not pt.started():
    pt.init()

dataset = pt.get_dataset('irds:msmarco-passage/dev')

indexer = pt.IterDictIndexer('./indices/msmarco-passage')
index_ref = indexer.index(dataset.get_corpus_iter(), fields=['text'])
index = pt.IndexFactory.of("./indices/msmarco-passage/data.properties")
print(index.getCollectionStatistics().toString())

bm25 = pt.BatchRetrieve(index, wmodel="BM25")
tf_idf = pt.BatchRetrieve(index, wmodel="TF_IDF")
pl2 = pt.BatchRetrieve(index, wmodel="PL2")
dlm = pt.BatchRetrieve(index, wmodel="DirichletLM")


test_queries = pt.get_dataset('irds:msmarco-passage/trec-dl-2019').get_topics()
test_qrels = pt.get_dataset('irds:msmarco-passage/trec-dl-2019').get_qrels()

print(pt.Experiment(
    [bm25, tf_idf, pl2, dlm],
    test_queries,
    test_qrels,
    eval_metrics=["map", "recip_rank", "ndcg_cut_10", "recall_1000"],
    round={"map" : 4, "recip_rank" : 4, "ndcg_cut_10" : 4, "recall_1000" : 4},
    names=["BM25", "TF_IDF", "PL2", "DLM"]
))

train_qrels = pt.get_dataset('irds:msmarco-passage/train/judged').get_qrels()
train_queries = pt.get_dataset(
    'irds:msmarco-passage/train/judged'
).get_topics().head(2000)
valid_qrels = pt.get_dataset('irds:msmarco-passage/train/split200-valid').get_qrels()
valid_queries = pt.get_dataset('irds:msmarco-passage/train/split200-valid').get_topics()

pipeline = bm25 >> (tf_idf ** pl2 ** dlm)

# this configures XGBoost as LambdaMART
start_time = time.time()
lmart_x = xgb.sklearn.XGBRanker(objective='rank:ndcg',
      learning_rate=0.1,
      gamma=1.0,
      min_child_weight=0.1,
      max_depth=6,
      verbose=2,
      random_state=42)

lmart_x_pipe = pipeline >> pt.ltr.apply_learned_model(lmart_x, form="ltr")
lmart_x_pipe.fit(train_queries, train_qrels, valid_queries, valid_qrels)
print(f"Time to train: {(time.time() - start_time) / 60} minutes")

print(pt.Experiment(
    [lmart_x_pipe],
    test_queries,
    test_qrels,
    eval_metrics=["map", "recip_rank", "ndcg_cut_10", "recall_1000"],
    round={"map" : 4, "recip_rank" : 4, "ndcg_cut_10" : 4, "recall_1000" : 4},
    names=["LTR"]))

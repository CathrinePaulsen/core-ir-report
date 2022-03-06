## BM25 Passage Ranking Baseline, [link]( us)

This BM25 baseline is taken from an existing Anserini experiment, detailed here: https://github.com/castorini/anserini/blob/master/docs/experiments-msmarco-passage.md

This guide has been tweaked to evaluate our chosen metrics, and to include retrieval runs for our BM25 extensions using RM3 and BM25PRF.


### Step 1: Convert collection.tsv to Ansirini jsonl
```
python3 tools/scripts/msmarco/convert_collection_to_jsonl.py \
 --collection-path collections/msmarco-passage/collection.tsv \
 --output-folder collections/msmarco-passage/collection_jsonl
 ```

### Step 2: Index the collection
```
sh target/appassembler/bin/IndexCollection -threads 9 -collection JsonCollection \
 -generator DefaultLuceneDocumentGenerator -input collections/msmarco-passage/collection_jsonl \
 -index indexes/msmarco-passage/lucene-index-msmarco -storePositions -storeDocvectors -storeRaw 
```
![img.png](img.png)

### Step 3: Filter out queries with no qrels
```
python3 tools/scripts/msmarco/filter_queries.py \
--qrels collections/msmarco-passage/qrels.tsv \
--queries collections/msmarco-passage/queries.tsv \
--output collections/msmarco-passage/queries-with-qrels.tsv
```
![img_1.png](img_1.png)

### Step 4: Run BM25 with default values, retrieves 1000 passages per query
```
sh target/appassembler/bin/SearchCollection -hits 1000 -parallelism 8 \
 -index indexes/msmarco-passage/lucene-index-msmarco \
 -topicreader TsvInt -topics collections/msmarco-passage/queries-with-qrels.tsv \
 -output runs/run.msmarco-passage.test.tsv -format msmarco \
 -bm25
```
![img_2.png](img_2.png)

### Step 5: Evaluate the run using `trec_eval`
```
# Convert the retrieval run to .trec format, this only needs to be done once
python3 tools/scripts/msmarco/convert_msmarco_to_trec_run.py \
--input runs/run.msmarco-passage.test.tsv \
--output runs/run.msmarco-passage.test.trec

# Convert the test qlels to .trec format, this only needs to be done once
python3 tools/scripts/msmarco/convert_msmarco_to_trec_qrels.py \
--input collections/msmarco-passage/qrels.tsv \
--output collections/msmarco-passage/qrels.test.trec

# Run the evaluation tool query-wise (-q flag) with MAP, MRR, NDCG@10 and recall@1000
tools/eval/trec_eval.9.0.4/trec_eval -q -c -m map -m recip_rank -m ndcg_cut.10 -m recall.1000 \
 collections/msmarco-passage/qrels.test.trec runs/run.msmarco-passage.test.trec
```

### Running BM25+RM3
```
sh target/appassembler/bin/SearchCollection -hits 1000 -parallelism 8 \
-index indexes/msmarco-passage/lucene-index-msmarco \
-topicreader TsvInt -topics collections/msmarco-passage/queries-with-qrels.tsv \
-output runs/run.msmarco-passage.rm3.tsv -format msmarco \
-bm25 -rm3 -rm3.outputQuery
```

### Running BM25+BM25PRF
```
sh target/appassembler/bin/SearchCollection -hits 1000 -parallelism 8 \
-index indexes/msmarco-passage/lucene-index-msmarco \
-topicreader TsvInt -topics collections/msmarco-passage/queries-with-qrels.tsv \
-output runs/run.msmarco-passage.bm25prf.tsv -format msmarco \
-bm25 -bm25prf -bm25prf.outputQuery
```

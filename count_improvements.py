num_rm3_improvements = 0
num_rm3_worse = 0

num_bm25prf_improvements = 0
num_bm25prf_worse = 0

with open('rm3_result_score.txt', 'r') as rm3:
    with open('bm25prf_result_score.txt', 'r') as bm25prf:
        with open('bm25_result_score.txt', 'r') as bm25:
            bm25prf_lines = bm25prf.readlines()
            bm25_lines = bm25.readlines()

            for rm3_q in rm3:
                rm3_query = rm3_q.strip().split('\t')
                try:
                    rm3_query_id = int(rm3_query[1])
                except ValueError:
                    continue
                rm3_score = float(rm3_query[2])

                for bm25_q in bm25_lines:
                    bm25_query = bm25_q.strip().split('\t')
                    try:
                        bm25_query_id = int(bm25_query[1])
                    except ValueError:
                        continue
                    bm25_score = float(bm25_query[2])

                    if rm3_query_id == bm25_query_id:
                        if rm3_score > bm25_score:
                            num_rm3_improvements += 1
                        if rm3_score < bm25_score:
                            num_rm3_worse += 1

            for bm25prf_q in bm25prf_lines:
                bm25prf_query = bm25prf_q.strip().split('\t')
                try:
                    prf_query_id = int(bm25prf_query[1])
                except ValueError:
                    continue
                prf_score = float(bm25prf_query[2])

                for bm25_q in bm25_lines:
                    bm25_query = bm25_q.strip().split('\t')
                    try:
                        bm25_query_id = int(bm25_query[1])
                    except ValueError:
                        continue
                    bm25_score = float(bm25_query[2])

                    if prf_query_id == bm25_query_id:
                        if prf_score > bm25_score:
                            num_bm25prf_improvements += 1
                        if prf_score < bm25_score:
                            num_bm25prf_worse += 1

print(f'RM3 improvements: {num_rm3_improvements}')
print(f'RM3 worse: {num_rm3_worse}')
print(f'BM25PRF improvements: {num_bm25prf_improvements}')
print(f'BM25PRF worse: {num_bm25prf_worse}')

import pandas as pd

def deviation_matrix(ratings: pd.DataFrame):
    dev = {}
    cnt = {}

    grouped = ratings.groupby("userId")
    for _, group in grouped:
        items = group[["movieId", "rating"]].values
        for i, r_i in items:
            dev.setdefault(i, {})
            cnt.setdefault(i, {})
            for j, r_j in items:
                if i == j:
                    continue
                dev[i][j] = dev[i].get(j, 0.0) + (r_i - r_j)
                cnt[i][j] = cnt[i].get(j, 0) + 1

    for i in dev:
        for j in dev[i]:
            dev[i][j] /= cnt[i][j]

    return dev, cnt


def get_slope_one_score(user_history: dict, movie_id: int, dev: dict, cnt: dict):
    num = 0.0
    den = 0.0

    for movie_id, rating in user_history.items():
        if movie_id in dev and movie_id in dev[movie_id]:
            num += (dev[movie_id][movie_id] + rating) * cnt[movie_id][movie_id]
            den += cnt[movie_id][movie_id]

    return num / den if den > 0 else None

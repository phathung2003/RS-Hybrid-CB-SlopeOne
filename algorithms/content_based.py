import numpy as np

def cosine_sim(v1: np.ndarray, v2: np.ndarray) -> float:
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return 0.0
    return float(np.dot(v1, v2) / denom)


def get_content_score(user_history: dict, movie_id: int, movie_encoder: dict) -> float:
    if movie_id not in movie_encoder:
        return 0.0

    target_vec = movie_encoder[movie_id]

    sims = []
    for mid, rating in user_history.items():
        if mid not in movie_encoder:
            continue

        sim = cosine_sim(target_vec, movie_encoder[mid])
        sims.append(sim * rating)

    return float(np.mean(sims)) if sims else 0.0

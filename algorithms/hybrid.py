import os
import numpy as np
from dotenv import load_dotenv

from algorithms.content_based import get_content_score
from algorithms.collaborative import get_slope_one_score

load_dotenv()
CONTENT_BASED_WEIGHT = float(os.getenv("CONTENT_BASED_WEIGHT"))

def hybrid_prediction(user_history, movie_id, movie_encoder, dev, cnt):
    content_based_score = get_content_score(user_history, movie_id, movie_encoder)
    collaborative_score = get_slope_one_score(user_history, movie_id, dev, cnt)

    content_based_val = float(content_based_score) if content_based_score is not None else 0.0
    collaborative_val = float(collaborative_score / 5.0) if collaborative_score is not None else 0.0

    return CONTENT_BASED_WEIGHT * content_based_val + (1-CONTENT_BASED_WEIGHT) * collaborative_val

def get_hybrid_recommendations(user_history, moviecollaborative_df, movie_encoder, dev, cnt, current_movie_id = None):
    df = moviecollaborative_df.copy()
    
    # Loại bỏ phim đang xem
    df = df[df["movieId"] != current_movie_id]
    
    # TRƯỜNG HỢP 1: Người dùng mới (Danh sách trống)
    if not user_history:
        max_year = df["year"].max()
        
        df["hybrid_score"] = df["weighted_rating"] * np.exp(
            -np.log(2) * (max_year - df["year"]) / 5
        )
        return df.sort_values("hybrid_score", ascending=False)

    # TRƯỜNG HỢP 2: Người dùng đã có lịch sử
    watched_ids = set(user_history.keys())
    # Loại bỏ những phim đã xem để không gợi ý lại
    df_potential = df[~df["movieId"].isin(watched_ids)].copy()

    # Tính toán điểm Hybrid cho từng phim
    scores = []
    for movie_id in df_potential["movieId"]:
        score = hybrid_prediction(user_history, movie_id, movie_encoder, dev, cnt)
        scores.append(score)

    df_potential["hybrid_score"] = scores
    # Trả về danh sách tiềm năng đã sắp xếp
    return df_potential.sort_values("hybrid_score", ascending=False)
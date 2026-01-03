import os
import re
import math
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DATA_PATH = "./dataset"

def read_dataset(): 
    # Chỉ giữ phiên bản dùng os.path.join
    ratings = pd.read_csv(os.path.join(DATA_PATH, "ratings.csv"))
    movies = pd.read_csv(os.path.join(DATA_PATH, "movies.csv"))
    links = pd.read_csv(os.path.join(DATA_PATH, "links.csv"))
    return movies, ratings, links

def clean_process_dataset(movies, ratings, links):
    # Trích cột năm riêng
    movies['year'] = movies['title'].str.extract(r'\((\d{4})\)\s*$')
    movies['year'] = movies['year'].fillna(0).astype(int)
    movies['title'] = movies['title'].str.replace(r'\(\d{4}\)$', '', regex=True).str.strip().apply(shorten_title)
    
    # Tách genres thành danh sách
    movies['genres'] = movies['genres'].str.split('|')
    
    # Xóa timestamp trong bình luận
    ratings.drop('timestamp', axis=1, inplace=True)
    

    # Tính rating trung bình
    if ratings is not None:
        ratings = ratings.copy()

        agg_rating = (
            ratings
            .groupby("movieId", as_index=False)
            .agg(
                rating_mean=("rating", "mean"),
                rating_count=("rating", "count")
            )
        )

        # join vào movies
        movies = movies.merge( agg_rating, on="movieId", how="left")

        # Xử lý phim không có lượt đánh giá (Mặc định là 0)
        movies["rating_count"] = (movies["rating_count"].fillna(0).astype(int))
        movies["rating_mean"] = movies["rating_mean"].fillna(0)
        
        # global mean (chỉ tính trên phim có rating)
        global_mean_rating = movies.loc[movies["rating_count"] > 0, "rating_mean"].mean()
        if math.isnan(global_mean_rating): global_mean_rating = 0 
        
        # weighted rating
        RATING_COUNT_REQUIRE= int(os.getenv("RATING_COUNT_REQUIRE"))
        movies["weighted_rating"] = (
            (movies["rating_count"] / (movies["rating_count"] + RATING_COUNT_REQUIRE)) * movies["rating_mean"]
            + (RATING_COUNT_REQUIRE / (movies["rating_count"] + RATING_COUNT_REQUIRE)) * global_mean_rating
        )

    else:
        movies["rating_mean"] = 0
        movies["rating_count"] = 0
        movies["weighted_rating"] = 0

        
    
    return movies, ratings, links

def one_hot_encoder(movies):
    # LẤY DANH SÁCH GENRE CỐ ĐỊNH, SORT ĐỂ ỔN ĐỊNH
    all_genres = sorted({g for genres in movies['genres'] for g in genres})

    def encode(genres):
        return [1 if g in genres else 0 for g in all_genres]

    movies = movies.copy()
    movies['genre_vector'] = movies['genres'].apply(encode)
    return movies, all_genres


def shorten_title(title):
    title_main = title
    
    # Loại bỏ a.k.a và tên phụ
    title_main = re.sub(r'\(.*?a\.k\.a.*?\)', '', title_main, flags=re.IGNORECASE).strip()
    title_main = re.sub(r'\([^()]*\)', '', title_main).strip()

    # Khôi phục mạo từ nếu bị đảo
    if ',' in title_main:
        parts = title_main.split(', ')
        title_main = ' '.join(parts[::-1])

    return title_main
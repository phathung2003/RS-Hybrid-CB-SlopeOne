import os
import json
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from process.read_data import read_dataset, clean_process_dataset, one_hot_encoder

# -------------------------------------------------------------
# TMDB API
# -------------------------------------------------------------
TMDB_KEY = os.getenv("TMDB_KEY")
@st.cache_data
def load_data():
    # Xóa lịch sử đánh giá trước đó
    clear_all_history()
    
    # Lấy danh sách phim
    movies, ratings, links = clean_process_dataset(*read_dataset())
    movies_encoded, _ = one_hot_encoder(movies)
    
    movie_encoder_dict = {}
    for _, row in movies_encoded.iterrows():
        mid = int(row["movieId"])
        vec = row["genre_vector"]
        movie_encoder_dict[mid] = vec.tolist() if hasattr(vec, "tolist") else list(vec)
            
    return movies, ratings, links, movie_encoder_dict

# -------------------------------------------------------------
# Lấy ảnh bìa phim
# -------------------------------------------------------------
@st.cache_data
def get_poster_image(links, movieId):
    
    # Lấy tmdb
    tmdb_id = links.loc[links["movieId"] == movieId, "tmdbId"].squeeze()
    
    
    if pd.isna(tmdb_id):
        return None
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_KEY}"
    r = requests.get(url).json()
    poster = r.get("poster_path")
    if poster:
        return "https://image.tmdb.org/t/p/w500" + poster
    return None

# -------------------------------------------------------------
# Lấy trailer phim
# -------------------------------------------------------------
@st.cache_data
def get_movie_trailer(links, movieId):
    # 1. Lấy tmdbId từ file links
    tmdb_id = links.loc[links["movieId"] == movieId, "tmdbId"].squeeze()
    
    if pd.isna(tmdb_id):
        return None
        
    # 2. Gọi API lấy danh sách videos
    # Chú ý: Endpoint là /movie/{id}/videos
    url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}/videos?api_key={TMDB_KEY}"
    
    try:
        r = requests.get(url).json()
        videos = r.get("results", [])
        
        # 3. Tìm video là Trailer trên YouTube
        for video in videos:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                # Trả về link dạng embed để dùng được trong st.video hoặc iframe
                return f"https://www.youtube.com/embed/{video['key']}"
                
        # Nếu không có "Trailer", lấy đại video đầu tiên nếu có
        if videos:
            return f"https://www.youtube.com/embed/{videos[0]['key']}"
            
    except Exception as e:
        st.error(f"Lỗi khi lấy trailer: {e}")
        
    return None

# -------------------------------------------------------------
# Phân trang
# -------------------------------------------------------------
def render_pagination(total_pages, location="top"):
    if total_pages <= 1: return
    col_left, col_mid, col_right = st.columns([1, 4, 1])
    with col_left:
        if st.button("Trước", key=f"prev_{location}", disabled=(st.session_state.current_page <= 1), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    with col_mid:
        st.markdown(f"<div style='text-align:center; line-height:35px;'>Trang <b>{st.session_state.current_page}</b> / {total_pages}</div>", unsafe_allow_html=True)
    with col_right:
        if st.button("Sau", key=f"next_{location}", disabled=(st.session_state.current_page >= total_pages), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()

# -------------------------------------------------------------
# Quản lý lịch sử người dùng
# -------------------------------------------------------------
HISTORY_FILE = os.path.join("./user_history.json")
   
def save_history(history_dict):
    with open(HISTORY_FILE, "w") as f:
        json.dump({str(k): v for k, v in history_dict.items()}, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                return {int(k): float(v) for k, v in data.items()}
        except:
            return {}
    return {}

def clear_all_history():
    """Xóa sạch toàn bộ lịch sử trong state và trong file."""
    st.session_state.history = {}
    save_history({})
    
# -------------------------------------------------------------
# Chuyển trang
# -------------------------------------------------------------
def navigation(page, movie_id=None):
    st.session_state.page = page
    st.session_state.selected_mid = movie_id
    st.session_state.current_page = 1
    st.query_params.clear() 
    st.rerun()
import os
import base64
import streamlit as st
from enum import Enum
from process.components import get_poster_image

not_found_path = os.path.join("./resources/not_found_2.png")

# Lấy hình mặc định (Đổi qua dạng Base64)
if os.path.exists(not_found_path):
    with open(not_found_path, "rb") as f:
        not_found_data = base64.b64encode(f.read()).decode("utf-8")

# Cấc loại ảnh bìa
class SHOW_POSTER(Enum):
    NORMAL = "normal"
    HISTORY = "history"
    
def ui_css():
    return st.markdown("""
    <style>
        [data-testid="stVerticalBlock"] { gap: 5px !important; }
        div[data-testid="column"] { padding: 0 2.5px !important; }
        .movie-link { text-decoration: none !important; color: inherit !important; display: block; }
        .movie-card {
            position: relative; height: 40%; background-color: #1a1a1a;
            border-radius: 8px; overflow: hidden; border: 1px solid #333;
            transition: transform 0.2s ease; 
            margin-bottom:20px;
            margin-top:20px;
        }
        .movie-card:hover { transform: scale(1.02); border-color: #FFD700; z-index: 10; }
        
        /* Khung chứa ảnh để các nhãn bám vào mép ảnh */
        .poster-container {
            position: relative;
            width: 100%;
            aspect-ratio: 2/3;
        }
        .movie-poster { width: 100%; height: 100%; object-fit: cover; display: block; }

        .movie-title {
            padding: 8px 5px; font-size: 13px; font-weight: 600; text-align: center;
            background: #262626; color: #efefef; height: 45px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }
        
        /* Năm sản xuất - Góc trên trái TRONG ảnh */
        .badge-year {
                position: absolute; 
                top: 10px; 
                left: 10px;
                background: rgba(0, 0, 0, 0.85); 
                color: white;
                padding: 4px 10px;   
                border-radius: 6px; 
                font-size: 14px; 
                font-weight: bold;
                z-index: 2;
                border: 1px solid rgba(255,255,255,0.2);
        }

        /* Điểm hệ thống - Góc trên phải TRONG ảnh */
        .badge-rating {
            position: absolute; 
            top: 10px; 
            right: 10px;
            background: #FFD700; 
            color: black;
            padding: 4px 10px;   
            border-radius: 6px; 
            font-weight: 900;   
            font-size: 14px;   
            z-index: 2;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        /* Điểm cá nhân/Gợi ý - Góc dưới phải TRONG ảnh */
        .badge-similarity {
            position: absolute; 
            bottom: 10px; 
            right: 10px;
            background: #007BFF; 
            color: white;
            padding: 5px 12px;
            border-radius: 8px; 
            font-weight: bold; 
            font-size: 14px;
            z-index: 2;
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.3);
        }

        .stButton > button { margin-top:5px;}
    </style>
    """, unsafe_allow_html=True)

def movie_poster(links, movie_id, title, year, rating, hybrid_score, type):
    
    # Lấy hình nền
    poster_url = get_poster_image(links, movie_id)
    if not poster_url:
        poster_url = f"data:image/webp;base64,{not_found_data}"
    
    
    if type == SHOW_POSTER.HISTORY:
        return  st.markdown(f"""
                    <a href="/?movieId={movie_id}" target="_self" class="movie-link">
                        <div class="movie-card">
                            <div class="poster-container">
                                <div class="badge-year">{year}</div>
                                <div class="badge-rating">Đánh giá của bạn: {rating} ★</div>
                                <img src="{poster_url}" class="movie-poster">
                            </div>
                            <div class="movie-title">{title}</div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
    else:
        return  st.markdown(f"""
                    <a href="/?movieId={movie_id}" target="_self" class="movie-link">
                        <div class="movie-card">
                            <div class="poster-container">
                                <div class="badge-year">{year}</div>
                                <div class="badge-rating">{rating:.2f} ★</div>
                                <img src="{poster_url}" class="movie-poster">
                                <div class="badge-similarity">Điểm dự đoán: {hybrid_score:.3f}</div>
                            </div>
                            <div class="movie-title">{title}</div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
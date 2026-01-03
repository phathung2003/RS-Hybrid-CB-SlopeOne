import os
import base64
import streamlit as st

from process.components import get_movie_trailer

not_found_path = os.path.join("./resources/not_found.webp")

# Lấy hình mặc định (Đổi qua dạng Base64)
if os.path.exists(not_found_path):
    with open(not_found_path, "rb") as f:
        not_found_data = base64.b64encode(f.read()).decode("utf-8")

def preview(links, movie_id):
    # Lấy trailer
    trailer = get_movie_trailer(links, movie_id)
    
    # Nếu tìm thấy trailer
    if trailer:
        return st.markdown(f"""
            <div style="
                display: flex;
                justify-content: center;
                margin-bottom: 16px;
            ">
                <iframe 
                src="{trailer}"
                frameborder="0"
                allowfullscreen
                style="
                    width: 100%;
                    max-width: 960px;
                    aspect-ratio: 16 / 9;
                    border-radius: 8px;
                "
                />
            </div>
            """, unsafe_allow_html=True
        )
        
    else:
        return st.markdown(f"""
            <div style="
                display: flex;
                justify-content: center;
                margin-bottom: 16px;
            ">
                <img src="data:image/webp;base64,{not_found_data}" 
                style="
                    width: 100%; 
                    max-width: 960px; 
                    aspect-ratio: 16/9; 
                    border-radius: 8px; 
                    object-fit: cover;"
                >
            </div>
            """, unsafe_allow_html=True)

# Thẻ thể loại
def genre_tag(genres_list):
    genres_html = " ".join(
        f"<span style='background-color:#eee; color:#333; padding:2px 6px; border-radius:4px; font-size:11px; margin-right:4px;'>{g}</span>"
            for g in genres_list if g
        )
    return genres_html
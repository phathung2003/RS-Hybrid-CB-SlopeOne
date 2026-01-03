import streamlit as st
import math
import time

# Chức năng
from process.components import load_data, get_movie_trailer, navigation, render_pagination, save_history, load_history

# Giao diện
from ui.poster import SHOW_POSTER, ui_css, movie_poster
from ui.preview import preview, genre_tag
from ui.sidebar import sidebar

# Thuật toán Hybrid
from algorithms.collaborative import deviation_matrix
from algorithms.hybrid import get_hybrid_recommendations

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Thông tin phim chiếu rạp", layout="wide", initial_sidebar_state="collapsed")

# --- 2. LOAD DỮ LIỆU ---
@st.cache_resource
def build_deviation_matrix(_ratings):
    return deviation_matrix(_ratings)

try:
    movies, ratings, links, movie_encoder_dict = load_data()
    dev_matrix, cnt_matrix = build_deviation_matrix(ratings)
except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
    st.stop()

# --- 3. KHỞI TẠO TRẠNG THÁI (STATE) ---
if 'history' not in st.session_state:
    st.session_state.history = load_history()

if 'page' not in st.session_state: st.session_state.page = "home"
if 'current_page' not in st.session_state: st.session_state.current_page = 1
if 'selected_mid' not in st.session_state: st.session_state.selected_mid = None

# Xử lý tham số URL
query_params = st.query_params
if "movieId" in query_params:
    try:
        new_mid = int(query_params["movieId"])
        if st.session_state.selected_mid != new_mid:
            st.session_state.page = "detail"
            st.session_state.selected_mid = new_mid
            st.session_state.current_page = 1
    except:
        pass

# CSS giao diện
ui_css()


# --- 4. SIDEBAR ---
with st.sidebar:
    search_film = sidebar()

# --- 5. TRANG CHỦ & LỊCH SỬ ---
if st.session_state.page in ["home", "history"]:
    if st.session_state.page == "home":
        st.title("Danh sách phim")
        rec_df = get_hybrid_recommendations(st.session_state.history, movies, movie_encoder_dict, dev_matrix, cnt_matrix)
        df_filtered = rec_df[rec_df['title'].str.contains(search_film, case=False)]
    else:
        st.title("Phim đã đánh giá")
        rated_ids = list(st.session_state.history.keys())
        df_filtered = movies[movies['movieId'].isin(rated_ids)]
        if search_film:
            df_filtered = df_filtered[df_filtered['title'].str.contains(search_film, case=False)]

    if df_filtered.empty:
        st.info("Không tìm thấy phim nào.")
    else:
        items_per_page = 24
        total_pages = max(1, math.ceil(len(df_filtered) / items_per_page))
        if st.session_state.current_page > total_pages: st.session_state.current_page = 1

        render_pagination(total_pages, location="top")
        
        start_idx = (st.session_state.current_page - 1) * items_per_page
        df_page = df_filtered.iloc[start_idx : start_idx + items_per_page]
        
        num_cols = 4
        for i in range(0, len(df_page), num_cols):
            cols = st.columns(num_cols)
            batch = df_page.iloc[i : i + num_cols]
            for idx, (index, row) in enumerate(batch.iterrows()):
                with cols[idx]:
                    if st.session_state.page == "history":
                        user_rating = st.session_state.history.get(row['movieId'], 0)
                        movie_poster(links, int(row['movieId']), row['title'], row['year'], user_rating, None, SHOW_POSTER.HISTORY)
                    else:
                        movie_poster(links, int(row['movieId']), row['title'], row['year'], row['weighted_rating'], row['hybrid_score'], SHOW_POSTER.NORMAL)

        st.divider()
        render_pagination(total_pages, location="bottom")

# --- 6. TRANG CHI TIẾT ---
elif st.session_state.page == "detail":
    mid = int(st.session_state.selected_mid)
    movie = movies[movies['movieId'] == mid].iloc[0]
    
    if st.button("⬅ Quay lại"): navigation("home")

    st.header(movie['title'])
    preview(links, mid)
    
    # Trailer
    trailer = get_movie_trailer(links, mid)
   
    c1, c2 = st.columns([2, 2])
    with c1:
        st.subheader("Thông tin phim")
        st.markdown(f"**Thời gian ra mắt:** {movie['year']}<br>**Thể loại:** {genre_tag(movie['genres'])}", unsafe_allow_html=True)
    
    with c2:
        st.subheader("Đánh giá phim")
        c3, c4 = st.columns([5, 2])
        with c3:
            old_score = float(st.session_state.history.get(mid, 0.0))
            user_score = st.slider("Chấm điểm", 0.0, 5.0, value=old_score, step=0.5, key=f"sl_{mid}_{old_score}", label_visibility="collapsed")

        with c4:
            st.markdown(f"{movie['weighted_rating']:.1f}/5.0 ⭐<br>({movie['rating_count']} lượt đánh giá)", unsafe_allow_html=True)
            
        if st.button("Lưu Đánh Giá", use_container_width=True):
            # 1. Lưu vào Session State
            st.session_state.history[mid] = user_score
            # 2. Lưu vào File JSON vĩnh viễn
            save_history(st.session_state.history)
            
            st.toast("Đã lưu đánh giá thành công", icon='✅')
            time.sleep(2) # 2 giây
            st.rerun()
    
    # --- Gợi ý phim  ---
    st.divider()
    st.subheader("Có thể bạn cũng thích")
    recommended_df = get_hybrid_recommendations(st.session_state.history, movies, movie_encoder_dict, dev_matrix, cnt_matrix, mid).head(6)
    recommended_cols = st.columns(6)
    for idx, (_, recommend) in enumerate(recommended_df.iterrows()):
        with recommended_cols[idx]:
            movie_poster(links, int(recommend['movieId']), recommend['title'], recommend['year'], recommend['weighted_rating'], recommend['hybrid_score'], SHOW_POSTER.NORMAL)
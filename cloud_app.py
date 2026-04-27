import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ Thống Quản Trị Y Tế SaaS - Net Zero & AI",
    page_icon="🏥",
    layout="wide"
)

# Thiết kế giao diện bằng CSS
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e1e4e8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_data():
    try:
        # Đảm bảo file Data_Tong.xlsx nằm cùng thư mục với file code này
        df = pd.read_excel('Data_Tong.xlsx')
        return df
    except Exception as e:
        st.error(f"⚠️ Không tìm thấy file 'Data_Tong.xlsx'. Vui lòng kiểm tra lại! Lỗi: {e}")
        return None

df = load_data()

if df is not None:
    # --- 3. THANH SIDEBAR (BỘ LỌC) ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=80)
    st.sidebar.header("Bộ Lọc Dữ Liệu")
    
    # Lọc theo Bệnh viện
    list_bv = df['Ten_Benh_Vien'].unique()
    selected_bv = st.sidebar.selectbox("Chọn Bệnh viện", list_bv)
    
    # Lọc theo Khoa
    df_bv = df[df['Ten_Benh_Vien'] == selected_bv]
    list_khoa = df_bv['Khoa'].unique()
    selected_khoa = st.sidebar.multiselect("Chọn Khoa phòng", list_khoa, default=list_khoa)

    # Dữ liệu cuối cùng sau khi lọc
    final_df = df_bv[df_bv['Khoa'].isin(selected_khoa)]

    # --- 4. TIÊU ĐỀ CHÍNH ---
    st.title(f"🏥 Dashboard Quản Trị: {selected_bv}")
    st.info("Giải pháp giám sát KPI thông minh tích hợp mô hình dự báo AI & Chỉ số Net Zero")

    # --- 5. TẦNG CHỈ SỐ (METRICS) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tổng Doanh Thu", f"{final_df['Doanh_Thu'].sum():,} VNĐ", "↑ 5%")
    with c2:
        st.metric("Tổng Bệnh Nhân", f"{final_df['Benh_Nhan'].sum():,} Người", "↑ 12%")
    with c3:
        st.metric("TG Chờ Trung Bình", f"{final_df['Thoi_Gian_Cho'].mean():.1f} Phút", "-2p", delta_color="inverse")
    with c4:
        st.metric("Phát Thải (Điện)", f"{final_df['Luong_Dien_KWh'].sum():,} KWh", "Net Zero", delta_color="normal")

    st.write("---")

    # --- 6. PHẦN PHÂN TÍCH VÀ AI PREDICTION ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 So sánh Bệnh nhân & Giường bệnh")
        # Biểu đồ cột so sánh
        fig_bar = px.bar(
            final_df, x='Khoa', y=['Benh_Nhan', 'Tong_Giuong'],
            barmode='group',
            color_discrete_sequence=['#3498db', '#bdc3c7'],
            labels={'value': 'Số lượng', 'variable': 'Chỉ số'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("📈 Dự báo Tương quan Doanh thu (AI Model)")
        
        # QUAN TRỌNG: Sắp xếp dữ liệu để đường line không bị rối (zích zắc)
        df_sorted = final_df.sort_values(by='Benh_Nhan')
        
        # Vẽ biểu đồ Scatter kết hợp Trendline (Yêu cầu cài đặt statsmodels)
        try:
            fig_trend = px.scatter(
                df_sorted, 
                x='Benh_Nhan', 
                y='Doanh_Thu', 
                trendline="ols", # Thuật toán hồi quy tuyến tính
                trendline_color_override="red",
                labels={'Benh_Nhan': 'Số lượng bệnh nhân', 'Doanh_Thu': 'Doanh thu (VNĐ)'},
                template="plotly_white"
            )
            # Thêm lớp biểu đồ đường nối các điểm dữ liệu thực tế
            fig_line = px.line(df_sorted, x='Benh_Nhan', y='Doanh_Thu')
            fig_trend.add_traces(fig_line.data)
            
            st.plotly_chart(fig_trend, use_container_width=True)
            st.caption("🔴 Đường màu đỏ: Xu hướng dự báo của AI dựa trên thuật toán Hồi quy (OLS).")
        except Exception as e:
            st.warning("Để hiển thị Trendline, vui lòng chạy lệnh: pip install statsmodels")
            st.plotly_chart(px.line(df_sorted, x='Benh_Nhan', y='Doanh_Thu'), use_container_width=True)

    # --- 7. BẢNG DỮ LIỆU CHI TIẾT ---
    st.write("---")
    with st.expander("📂 Xem bảng dữ liệu nguồn"):
        st.dataframe(final_df.style.highlight_max(axis=0), use_container_width=True)

else:
    st.warning("⚠️ Vui lòng đảm bảo file 'Data_Tong.xlsx' đã được tải
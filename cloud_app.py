import streamlit as st
import pandas as pd
import plotly.express as px

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Dashboard Quản Trị Y Tế - AI & Net Zero", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- TẦNG DỮ LIỆU (DATA LAYER) ---
@st.cache_data
def load_data():
    try:
        # Load dữ liệu từ file Excel của em
        df = pd.read_excel('Data_Tong.xlsx')
        return df
    except Exception as e:
        st.error(f"⚠️ Lỗi: Không thể tải dữ liệu. Chi tiết: {e}")
        return None

df = load_data()

if df is not None:
    # --- SIDEBAR: BỘ LỌC THÔNG MINH ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)
    st.sidebar.title("QUẢN TRỊ BỆNH VIỆN")
    
    selected_hospital = st.sidebar.selectbox("Chọn Bệnh viện", options=df['Ten_Benh_Vien'].unique())
    selected_dept = st.sidebar.multiselect("Chọn Khoa phòng", options=df['Khoa'].unique(), default=df['Khoa'].unique())

    # Lọc dữ liệu theo lựa chọn
    mask = (df['Ten_Benh_Vien'] == selected_hospital) & (df['Khoa'].isin(selected_dept))
    final_df = df[mask]

    # --- TIÊU ĐỀ CHÍNH ---
    st.title(f"📊 Dashboard KPI: {selected_hospital}")
    st.markdown("---")

    # --- TẦNG CHỈ SỐ (METRIC LAYER) ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        total_rev = final_df['Doanh_Thu'].sum()
        st.metric("Tổng Doanh Thu", f"{total_rev:,} VNĐ", delta="8% so với kỳ trước")
    with m2:
        total_pt = final_df['Benh_Nhan'].sum()
        st.metric("Tổng Bệnh Nhân", f"{total_pt:,} Người", delta="12%")
    with m3:
        avg_wait = final_df['Thoi_Gian_Cho'].mean()
        st.metric("TG Chờ Trung Bình", f"{avg_wait:.1f} Phút", delta="-5%", delta_color="inverse")
    with m4:
        power_use = final_df['Luong_Dien_KWh'].sum()
        st.metric("Điện Năng (Net Zero)", f"{power_use:,} KWh", delta="Chỉ số Xanh")

    st.write("##")

    # --- PHÂN TÍCH TRỰC QUAN & AI PREDICTION ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📊 Hiệu suất Bệnh nhân theo Khoa")
        fig_bar = px.bar(final_df, x='Khoa', y='Benh_Nhan', 
                         color='Khoa', text_auto=True,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        # ĐÂY LÀ PHẦN NÂNG CẤP TRENDLINE CHO CHƯƠNG 6
        st.markdown("### 📈 Dự báo Xu hướng (AI Insight - Trendline)")
        # Sử dụng px.scatter để vẽ Trendline OLS
        fig_trend = px.scatter(
            final_df, 
            x='Benh_Nhan', 
            y='Doanh_Thu', 
            trendline="ols", 
            trendline_color_override="red",
            labels={'Benh_Nhan': 'Số lượng bệnh nhân', 'Doanh_Thu': 'Doanh thu (VNĐ)'},
            template="plotly_white"
        )
        # Thêm đường line kết nối các điểm dữ liệu thực tế
        fig_trend.add_traces(list(px.line(final_df, x='Benh_Nhan', y='Doanh_Thu').data))
        
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- TẦNG CHI TIẾT ---
    with st.expander("🔎 Xem chi tiết bảng dữ liệu"):
        st.dataframe(final_df, use_container_width=True)

else:
    st.info("Vui lòng kiểm tra lại file dữ liệu Data_Tong.xlsx trong thư mục gốc.")
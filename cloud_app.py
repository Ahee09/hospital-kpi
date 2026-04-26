import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình giao diện chuẩn Dashboard SaaS
st.set_page_config(page_title="Hệ Thống Quản Trị Y Tế SaaS - Net Zero", layout="wide")

# Thiết kế giao diện chuyên nghiệp bằng CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- Tầng Dữ Liệu (Data Layer) ---
@st.cache_data
def load_data():
    # File này sẽ được bạn upload lên cùng GitHub
    try:
        return pd.read_excel('Data_Tong.xlsx')
    except:
        st.error("⚠️ Lỗi: Không tìm thấy file Data_Tong.xlsx trên hệ thống Cloud!")
        return None

df = load_data()

if df is not None:
    # --- Sidebar: Bộ lọc thông minh (Multi-tenancy) ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)
    st.sidebar.title("QUẢN TRỊ HỆ THỐNG")
    
    st.sidebar.subheader("📍 Lọc theo khu vực/Cơ sở")
    list_bv = df['Ten_Benh_Vien'].unique()
    selected_bv = st.sidebar.selectbox("Chọn Bệnh viện:", list_bv)
    
    # Lọc dữ liệu theo bệnh viện đã chọn
    df_filtered = df[df['Ten_Benh_Vien'] == selected_bv]
    
    st.sidebar.subheader("🩺 Lọc theo Khoa phòng")
    list_khoa = df_filtered['Khoa'].unique()
    selected_khoa = st.sidebar.multiselect("Chọn Khoa:", list_khoa, default=list_khoa)
    
    # Dữ liệu cuối cùng
    final_df = df_filtered[df_filtered['Khoa'].isin(selected_khoa)]

    # --- Phần hiển thị chính (Main Dashboard) ---
    st.title(f"🏥 Hệ Thống Giám Sát KPI - {selected_bv}")
    st.markdown(f"**Trạng thái:** Toàn hệ thống | **Cơ sở:** {df_filtered['Khu_Vuc'].iloc[0]}")
    st.write("---")

    # Chỉ số KPI hàng đầu (Top Metrics)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tổng Bệnh Nhân", f"{final_df['Benh_Nhan'].sum()} BN")
    with c2:
        st.metric("Doanh Thu", f"{final_df['Doanh_Thu'].sum():,} Tr")
    with c3:
        wait_avg = final_df['Thoi_Gian_Cho'].mean()
        st.metric("TG Chờ TB", f"{wait_avg:.1f} Phút", delta="-5% so với tháng trước")
    with c4:
        power_sum = final_df['Luong_Dien_KWh'].sum()
        st.metric("Điện Năng (Net Zero)", f"{power_sum:,} KWh", delta="Chỉ số Xanh", delta_color="normal")

    st.write("##")

    # --- Phân tích Trực quan ---
    col_left, col_right = st.columns(2)

    with col_left:
        # Biểu đồ hiệu suất giường bệnh (Tư duy 4R: Tối ưu tài nguyên)
        st.markdown("### 📊 Hiệu suất Bệnh nhân & Giường bệnh")
        fig_bed = px.bar(final_df, x='Khoa', y=['Benh_Nhan', 'Tong_Giuong'], 
                         barmode='group', color_discrete_sequence=['#1f77b4', '#aec7e8'])
        st.plotly_chart(fig_bed, use_container_width=True)

    with col_right:
        # Biểu đồ Net Zero (Tiêu thụ năng lượng)
        st.markdown("### 🌱 Tỷ trọng Phát thải (Carbon Footprint)")
        fig_pie = px.pie(final_df, values='Luong_Dien_KWh', names='Khoa', 
                         hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Phân tích chuyên sâu (Deep Insights) ---
    st.write("---")
    st.markdown("### 🔍 Chi tiết Dữ liệu Vận hành")
    st.dataframe(final_df.style.highlight_max(axis=0, subset=['Thoi_Gian_Cho'], color='#ffcccc'))

    st.info("**Gợi ý hệ thống:** Dựa trên dữ liệu Real-time, Khoa có thời gian chờ cao nhất cần được điều phối thêm nhân sự điều dưỡng ngay lập tức.")
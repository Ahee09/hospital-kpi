import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ Thống Quản Trị Y Tế - Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TẢI DỮ LIỆU ---
@st.cache_data
def load_data():
    try:
        # Đọc file Excel - Đảm bảo file tên là Data_Tong.xlsx
        df = pd.read_excel('Data_Tong.xlsx')
        return df
    except Exception as e:
        st.error(f"⚠️ Lỗi: Không tìm thấy file Data_Tong.xlsx. Chi tiết: {e}")
        return None

df = load_data()

if df is not None:
    # --- 3. BỘ LỌC TẠI SIDEBAR (ĐÃ TỐI ƯU) ---
    st.sidebar.header("🏥 HỆ THỐNG LỌC")
    
    # Lấy TẤT CẢ bệnh viện có trong cột 'Ten_Benh_Vien', sắp xếp theo bảng chữ cái
    danh_sach_bv = sorted(df['Ten_Benh_Vien'].unique().tolist())
    
    # Tạo bộ lọc chọn bệnh viện
    selected_bv = st.sidebar.selectbox(
        "Chọn Bệnh viện cần xem:",
        options=danh_sach_bv,
        index=0  # Mặc định chọn bệnh viện đầu tiên
    )
    
    # Lọc dữ liệu theo bệnh viện đã chọn
    df_filtered = df[df['Ten_Benh_Vien'] == selected_bv]
    
    # Lọc theo Khoa (Chỉ hiện các khoa của bệnh viện đó)
    danh_sach_khoa = sorted(df_filtered['Khoa'].unique().tolist())
    selected_khoa = st.sidebar.multiselect(
        "Chọn Khoa phòng:", 
        options=danh_sach_khoa, 
        default=danh_sach_khoa
    )
    
    final_df = df_filtered[df_filtered['Khoa'].isin(selected_khoa)]

    # --- 4. TIÊU ĐỀ CHÍNH ---
    st.title(f"📊 Dashboard KPI: {selected_bv}")
    st.markdown(f"**Khu vực:** {final_df['Khu_Vuc'].iloc[0] if not final_df.empty else 'N/A'}")

    # --- 5. CÁC CHỈ SỐ TỔNG QUAN (METRICS) ---
    m1, m2, m3, m4 = st.columns(4)
    
    # Tính toán số liệu thực tế từ Data_Tong
    total_rev = final_df['Doanh_Thu'].sum()
    total_pat = final_df['Benh_Nhan'].sum()
    wait_avg = final_df['Thoi_Gian_Cho'].mean()
    power_sum = final_df['Luong_Dien_KWh'].sum()

    m1.metric("Tổng Doanh Thu", f"{total_rev:,.0f} VNĐ")
    m2.metric("Tổng Bệnh Nhân", f"{total_pat:,.0f} Người")
    m3.metric("TG Chờ Trung Bình", f"{wait_avg:.1f} Phút")
    m4.metric("Điện Năng tiêu thụ", f"{power_sum:,.0f} KWh")

    st.write("---")

    # --- 6. BIỂU ĐỒ PHÂN TÍCH ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📊 Hiệu suất Bệnh nhân & Giường bệnh")
        fig_bar = px.bar(
            final_df, 
            x='Khoa', 
            y=['Benh_Nhan', 'Tong_Giuong'],
            barmode='group',
            labels={'value': 'Số lượng', 'variable': 'Chỉ số'},
            color_discrete_sequence=['#1f77b4', '#aec7e8']
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with c2:
        st.subheader("🌱 Tỷ trọng Năng lượng theo Khoa")
        fig_pie = px.pie(
            final_df, 
            values='Luong_Dien_KWh', 
            names='Khoa',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 7. BẢNG CHI TIẾT ---
    with st.expander("📂 Xem chi tiết bảng dữ liệu nguồn"):
        st.dataframe(final_df, use_container_width=True)

else:
    st.warning("Vui lòng kiểm tra file Data_Tong.xlsx trong thư mục dự án.")
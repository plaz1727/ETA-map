import streamlit as st
import datetime
import folium
from streamlit_folium import st_folium
import time

# --- [페이지 기본 설정] ---
st.set_page_config(page_title="도착 역산 길찾기", page_icon="⏰", layout="centered")

# --- [가상 API 함수] ---
def get_coordinates(address):
    """가상의 위경도 반환 함수"""
    if "강남" in address:
        return {"lat": 37.4979, "lng": 127.0276}
    elif "홍대" in address:
        return {"lat": 37.5568, "lng": 126.9245}
    else:
        return {"lat": 37.5546, "lng": 126.9706} # 기본값: 서울역

def get_travel_time(start_coords, end_coords, mode):
    """가상의 소요 시간 반환 함수 (이동 수단 반영)"""
    if mode == "🚗 자동차": return 35
    elif mode == "🚌 대중교통": return 45
    else: return 50

# --- [사이드바 (설정 메뉴)] ---
with st.sidebar:
    st.header("⚙️ 상세 설정")
    transport_mode = st.radio("이동 수단을 선택하세요", ["🚗 자동차", "🚌 대중교통", "🚶 도보"])
    
    st.divider()
    
    st.write("⏱️ 준비 및 여유 시간")
    st.caption("도착 후 헐레벌떡 뛰지 않도록 여유 시간을 추가하세요.")
    prep_time = st.slider("여유 시간 추가 (분)", min_value=0, max_value=60, value=10, step=5)

# --- [메인 화면 UI] ---
st.title("⏰ 지각 방지! 역산 길찾기")
st.markdown("도착해야 할 시간만 알려주세요. **언제 출발해야 하는지** 계산해 드립니다.")

st.write("") # 빈 줄 추가

# 1. 입력 영역 (Container로 묶어서 깔끔하게)
with st.container(border=True):
    st.subheader("📍 여정 정보 입력")
    col1, col2 = st.columns(2)
    with col1:
        start_address = st.text_input("출발지 (예: 서울역)", "서울역")
    with col2:
        end_address = st.text_input("목적지 (예: 강남역)", "강남역")
    
    now = datetime.datetime.now()
    default_arrival = (now + datetime.timedelta(hours=2)).time()
    arrival_time = st.time_input("🎯 도착 희망 시간", value=default_arrival)

# 2. 버튼 및 계산 로직
if st.button("🚀 출발 시간 계산하기", type="primary", use_container_width=True):
    # 시각적 피드백 (로딩 효과)
    progress_text = "최적의 경로와 출발 시간을 계산하고 있습니다..."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01) # 계산하는 척하는 딜레이
        my_bar.progress(percent_complete + 1, text=progress_text)
    my_bar.empty() # 로딩바 숨기기
    
    # 데이터 처리
    start_coords = get_coordinates(start_address)
    end_coords = get_coordinates(end_address)
    travel_minutes = get_travel_time(start_coords, end_coords, transport_mode)
    
    # 시간 역산 로직 (소요 시간 + 여유 시간 반영)
    today = datetime.date.today()
    arrival_datetime = datetime.datetime.combine(today, arrival_time)
    
    total_needed_minutes = travel_minutes + prep_time
    departure_datetime = arrival_datetime - datetime.timedelta(minutes=total_needed_minutes)
    
    # 3. 결과 출력 화면 (강조)
    st.success("계산이 완료되었습니다! 🎉")
    
    # Metric을 이용한 핵심 정보 강조
    col3, col4, col5 = st.columns(3)
    col3.metric(label="이동 시간", value=f"{travel_minutes}분")
    col4.metric(label="여유 시간", value=f"{prep_time}분")
    col5.metric(label="총 소요 시간", value=f"{total_needed_minutes}분")
    
    st.info(f"🚨 **최종 데드라인:** 늦어도 **{departure_datetime.strftime('%p %I시 %M분')}**에는 출발하셔야 합니다!")
    st.balloons() # 축하 효과 애니메이션
    
    st.divider()
    
    # 4. 지도 시각화
    st.subheader(f"🗺️ 경로 요약 ({transport_mode})")
    
    center_lat = (start_coords["lat"] + end_coords["lat"]) / 2
    center_lng = (start_coords["lng"] + end_coords["lng"]) / 2
    
    m = folium.Map(location=[center_lat, center_lng], zoom_start=12)
    
    folium.Marker(
        [start_coords["lat"], start_coords["lng"]], 
        tooltip="출발지", 
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)
    
    folium.Marker(
        [end_coords["lat"], end_coords["lng"]], 
        tooltip="목적지", 
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)
    
    folium.PolyLine(
        locations=[[start_coords["lat"], start_coords["lng"]], [end_coords["lat"], end_coords["lng"]]],
        color="purple",
        weight=3,
        opacity=0.7,
        dash_array='10' # 점선 효과
    ).add_to(m)
    
    st_folium(m, width=700, height=400, returned_objects=[])

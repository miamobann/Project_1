"""
무역 적성 MBTI 진단 프로그램 (Trade-MBTI)
Streamlit 메인 웹 애플리케이션 (고품격 MBTI 스타일 UI)
"""

import os
import sys

# Streamlit.io 클라우드 배포 시 다른 폴더와의 모듈명 충돌 및 임포트 에러 방지
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import plotly.graph_objects as go
from questions import QUESTIONS, JOB_PROFILES, SCALE_OPTIONS
from calculator import calculate_trade_mbti

# 1. 페이지 설정
st.set_page_config(
    page_title="Trade-MBTI | 나의 무역 적성 찾기",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS 주입
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #6C63FF 0%, #3F3D56 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(108, 99, 255, 0.2);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
        line-height: 1.6;
    }

    .mbti-header-card {
        background: white;
        border-radius: 24px;
        padding: 2.5rem 2rem;
        text-align: center;
        border: 2px solid #E2E8F0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        margin-bottom: 2.5rem;
    }
    .mbti-type-badge {
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: 2px;
        line-height: 1;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #6C63FF, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .mbti-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2D3748;
        margin-bottom: 1rem;
    }
    .mbti-slogan {
        font-size: 1.15rem;
        font-style: italic;
        color: #4A5568;
        background: #F7FAFC;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        display: inline-block;
        margin-bottom: 1rem;
        border: 1px dashed #CBD5E0;
    }
    
    .section-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1A202C;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-left: 4px solid #6C63FF;
        padding-left: 0.8rem;
    }
    
    .strength-item {
        background-color: #F0FFF4;
        border-left: 4px solid #38A169;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.6rem;
        font-size: 0.95rem;
        color: #276749;
    }
    .weakness-item {
        background-color: #FFF5F5;
        border-left: 4px solid #E53E3E;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.6rem;
        font-size: 0.95rem;
        color: #9B2C2C;
    }
    .guide-item {
        background-color: #EBF8FF;
        border-left: 4px solid #3182CE;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.6rem;
        font-size: 0.95rem;
        color: #2B6CB0;
    }
    
    .match-card-good {
        background: #F0FFF4;
        border: 1px solid #C6F6D5;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .match-card-bad {
        background: #FFF5F5;
        border: 1px solid #FED7D7;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    
    .question-box {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.8rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .question-box:hover {
        transform: translateY(-2px);
        border-color: #6C63FF;
    }
    .question-num {
        font-size: 0.85rem;
        font-weight: 700;
        color: #6C63FF;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.4rem;
    }
    .question-text {
        font-size: 1.1rem;
        font-weight: 500;
        color: #2D3748;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    .badge-tag {
        display: inline-block;
        background: #EDF2F7;
        color: #4A5568;
        padding: 0.4rem 0.8rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# 3. 세션 상태 초기화
if "stage" not in st.session_state:
    st.session_state.stage = "welcome"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "result_data" not in st.session_state:
    st.session_state.result_data = None

QUESTIONS_PER_PAGE = 5
TOTAL_QUESTIONS = len(QUESTIONS)
TOTAL_PAGES = TOTAL_QUESTIONS // QUESTIONS_PER_PAGE


# [STAGE 1] 웰컴 화면
if st.session_state.stage == "welcome":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Trade-MBTI</div>
        <div class="hero-subtitle">
            나의 무역 실무 성향과 감각은 어떨까?<br>
            20개의 심층 직무 성향 질문을 통해 <b>6대 핵심 무역 직무</b> 중<br>
            너와 잘 맞는 커리어를 매칭해줄게.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 진단 전 안내 사항
    * 본 검사는 무역 업계의 실무 핵심 적성을 바탕으로 구성된 **MBTI 기반 맞춤 분석 프로그램**이야.
    * 질문당 깊게 고민하기보다 머릿속에 바로 떠오르는 직관적인 답변을 골라줘.
    * 가급적 **'매우 그렇다'** 또는 **'전혀 아니다'** 쪽을 선택해야 더 선명한 분석 결과가 나와.
    * 소요 시간은 대략 **3분 내외**야.
    """)
    
    st.write("")
    
    if st.button("무역 적성 진단 시작하기", use_container_width=True, type="primary"):
        st.session_state.stage = "testing"
        st.session_state.current_page = 0
        st.session_state.answers = {}
        st.rerun()


# [STAGE 2] 테스트 질문 진행 화면
elif st.session_state.stage == "testing":
    curr_page = st.session_state.current_page
    start_idx = curr_page * QUESTIONS_PER_PAGE
    end_idx = start_idx + QUESTIONS_PER_PAGE
    page_questions = QUESTIONS[start_idx:end_idx]
    
    answered_count = len(st.session_state.answers)
    progress_val = min(answered_count / TOTAL_QUESTIONS, 1.0)
    progress_percent = int(progress_val * 100)
    
    st.markdown(f"### 진단 진행도: **{progress_percent}%** ({answered_count} / {TOTAL_QUESTIONS} 문항)")
    st.progress(progress_val)
    st.divider()
    
    for q in page_questions:
        q_id = q["id"]
        
        st.markdown(f"""
        <div class="question-box">
            <div class="question-num">Question {q_id:02d}</div>
            <div class="question-text">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        default_idx = 2
        if q_id in st.session_state.answers:
            current_ans = st.session_state.answers[q_id]
            default_idx = next(i for i, opt in enumerate(SCALE_OPTIONS) if opt["score"] == current_ans)
        
        choice = st.radio(
            label=f"q_{q_id}_options",
            options=[opt["label"] for opt in SCALE_OPTIONS],
            index=default_idx,
            horizontal=True,
            key=f"radio_{q_id}",
            label_visibility="collapsed"
        )
        
        selected_score = next(opt["score"] for opt in SCALE_OPTIONS if opt["label"] == choice)
        st.session_state.answers[q_id] = selected_score
        st.write("")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if curr_page > 0:
            if st.button("이전 단계로", use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        else:
            st.button("이전 단계로", disabled=True, use_container_width=True)
            
    with col2:
        if curr_page < TOTAL_PAGES - 1:
            if st.button("다음 단계로", use_container_width=True, type="primary"):
                st.session_state.current_page += 1
                st.rerun()
        else:
            if st.button("최종 결과 분석하기", use_container_width=True, type="primary"):
                st.session_state.result_data = calculate_trade_mbti(st.session_state.answers)
                st.session_state.stage = "result"
                st.rerun()


# [STAGE 3] 결과 레포트 화면
elif st.session_state.stage == "result" and st.session_state.result_data:
    res = st.session_state.result_data
    primary = res["primary"]
    secondary = res["secondary"]
    p_profile = primary["profile"]
    s_profile = secondary["profile"]
    
    st.balloons()
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Trade-MBTI 분석 결과 리포트</h2>", unsafe_allow_html=True)
    
    # MBTI 헤더 카드
    st.markdown(f"""
    <div class="mbti-header-card" style="border-top: 8px solid {p_profile['color']};">
        <div class="mbti-type-badge">{p_profile['mbti']}</div>
        <div class="mbti-title">[{p_profile['name']}]<br>{p_profile['title']}</div>
        <div class="mbti-slogan">{p_profile['slogan']}</div>
        <p style="color: #4A5568; line-height: 1.7; font-size: 1.05rem; margin-top: 1rem; text-align: left; max-width: 600px; margin-left: auto; margin-right: auto;">
            {p_profile['description']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">나의 핵심 강점 (Strengths)</div>
            {"".join([f'<div class="strength-item">✔️ {s}</div>' for s in p_profile['strengths']])}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">보완해야 할 점 (Weaknesses)</div>
            {"".join([f'<div class="weakness-item">💡 {w}</div>' for w in p_profile['weaknesses']])}
        </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>6대 직무 적합도 레이더 차트</div>", unsafe_allow_html=True)
        
        categories = [JOB_PROFILES[code]["name"].split("/")[0].strip() for code in res["all_scores"].keys()]
        values = list(res["all_scores"].values())
        
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            name='나의 적합도',
            line=dict(color=p_profile['color'], width=3),
            fillcolor=p_profile['bg_color']
        ))
        
        # bold 속성 제거 후 안정적인 설정 적용
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10, color='#718096'),
                    gridcolor='#E2E8F0',
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color='#2D3748'),
                    gridcolor='#E2E8F0',
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            margin=dict(l=45, r=45, t=20, b=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
        keywords_html = "".join([f"<span class='badge-tag'>#{kw}</span>" for kw in p_profile['keywords']])
        st.markdown(f"""
        <div class="section-card" style="padding: 1.2rem;">
            <div class="section-title" style="font-size: 1.1rem; margin-bottom: 0.6rem;">시그니처 키워드</div>
            <div>{keywords_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # 행동 수칙 카드
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">무역 현장 성공을 위한 행동 수칙 (Action Guide)</div>
        {"".join([f'<div class="guide-item">📌 {g}</div>' for g in p_profile['action_guide']])}
    </div>
    """, unsafe_allow_html=True)

    col_bottom_1, col_bottom_2 = st.columns([1, 1])
    
    with col_bottom_1:
        st.markdown(f"""
        <div class="section-card" style="height: 250px;">
            <div class="section-title">2순위 서브 무역 직무</div>
            <h4 style="color: {s_profile['color']}; margin-bottom: 0.5rem;">{s_profile['mbti']} - {s_profile['name']} ({secondary['score']:.1f}점)</h4>
            <p style="font-size: 0.95rem; line-height: 1.6; color: #4A5568; margin-top: 0.5rem;">
                <b>{s_profile['title']}</b> 유형인 이 직무도 너에게 매력적인 대안이야.
                1순위 직무와 2순위 직무의 역량을 융합하면 업계에서 시너지를 낼 수 있어.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_bottom_2:
        licence_badges = "".join([f"<span class='badge-tag' style='background-color: #EBF8FF; color: #2B6CB0; border-color: #BEE3F8;'>🎓 {lic}</span>" for lic in p_profile['licences']])
        st.markdown(f"""
        <div class="section-card" style="height: 250px;">
            <div class="section-title">추천 실무 자격증</div>
            <p style="font-size: 0.95rem; color: #4A5568; margin-bottom: 1rem;">
                너의 <b>[{p_profile['name']}]</b> 실무 전문성을 입증할 수 있는 핵심 자격증 가이드야.
            </p>
            <div style="margin-top: 0.5rem;">{licence_badges}</div>
        </div>
        """, unsafe_allow_html=True)

    # 궁합 매칭
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>무역 직무 궁합 매칭</div>", unsafe_allow_html=True)
    
    col_match_1, col_match_2 = st.columns([1, 1])
    with col_match_1:
        st.markdown(f"""
        <div class="match-card-good">
            <h4 style="color: #2F855A; margin-top: 0;">환상의 파트너</h4>
            <p style="font-size: 0.95rem; color: #276749; font-weight: 500;">{p_profile['best_match']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_match_2:
        st.markdown(f"""
        <div class="match-card-bad">
            <h4 style="color: #C53030; margin-top: 0;">주의가 필요한 파트너</h4>
            <p style="font-size: 0.95rem; color: #9B2C2C; font-weight: 500;">{p_profile['worst_match']}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    # 6대 직무 아코디언
    st.subheader("무역 핵심 6대 직무 안내")
    with st.expander("6대 핵심 직무 정보와 MBTI 매핑 보기"):
        for code, profile in JOB_PROFILES.items():
            st.markdown(f"""
            <div style="border-left: 5px solid {profile['color']}; padding-left: 1rem; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom:0.2rem; color: {profile['color']};">{profile['mbti']} - {profile['name']} ({profile['title']})</h4>
                <p style="font-size: 0.9rem; color: #4A5568; margin-bottom: 0.4rem;"><b>핵심 키워드</b>: {', '.join(profile['keywords'])}</p>
                <p style="font-size: 0.9rem; color: #2D3748; line-height: 1.5; margin-top: 0;">{profile['description']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    
    if st.button("처음으로 돌아가서 다시 진단하기", use_container_width=True, type="primary"):
        st.session_state.stage = "welcome"
        st.session_state.answers = {}
        st.session_state.current_page = 0
        st.session_state.result_data = None
        st.rerun()
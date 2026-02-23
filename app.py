# -*- coding: utf-8 -*-
"""
Chat Analytics AI — Demo Dashboard
====================================
Phiên bản demo cho stakeholders review tính năng.
Dữ liệu: synthetic / đã export từ gold layer (anonymized).
Deploy: Streamlit Cloud  →  https://share.streamlit.io
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import Optional

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat Analytics AI — Demo",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Remove top padding */
.block-container { padding-top: 1.2rem; }

/* KPI card */
.kpi-card {
    background: rgba(255,255,255,0.04);
    border-left: 3px solid var(--c);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 4px;
}
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: .5px; }
.kpi-value { font-size: 28px; font-weight: 700; }
.kpi-delta { font-size: 12px; margin-top: 2px; }

/* Conversation bubble */
.bubble-customer {
    background: rgba(0,200,150,0.12);
    border-radius: 0 10px 10px 10px;
    padding: 6px 12px; margin: 4px 0;
    max-width: 85%;
}
.bubble-admin {
    background: rgba(102,126,234,0.15);
    border-radius: 10px 0 10px 10px;
    padding: 6px 12px; margin: 4px 0;
    max-width: 85%;
    margin-left: auto;
    text-align: right;
}

/* Score block */
.score-block {
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 8px;
}
.score-title {
    font-size: 10px; font-weight: 700; color: #aaa;
    text-transform: uppercase; letter-spacing: .6px;
    margin-bottom: 4px;
}

/* Demo badge */
.demo-badge {
    background: rgba(245,166,35,0.15);
    border: 1px solid #f5a623;
    color: #f5a623;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 12px;
    display: inline-block;
}

/* Radio list scroll */
.stRadio > div {
    max-height: 480px;
    overflow-y: auto;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 4px;
}

/* Divider color */
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
_PRIMARY   = "#667eea"
_SUCCESS   = "#00c896"
_WARNING   = "#f5a623"
_DANGER    = "#ef476f"
_INFO      = "#4cc9f0"

_TEMPLATE = "plotly_dark"
_CFG      = {"displayModeBar": False}

INTENT_VN = {
    "hoi_gia":               "Hỏi giá",
    "tu_van_do_mat":         "Tư vấn đo mắt",
    "dat_lich_do":           "Đặt lịch khám",
    "hoi_san_pham":          "Hỏi sản phẩm",
    "mua_hang":              "Mua hàng",
    "khieu_nai":             "Khiếu nại",
    "hoi_bao_hanh":          "Hỏi bảo hành",
    "tu_van_kinh_ap_trong":  "Tư vấn áp tròng",
}
STAGE_VN = {
    "awareness": "Nhận thức", "consideration": "Cân nhắc",
    "intent": "Có ý định", "evaluation": "Đánh giá",
    "purchase": "Mua hàng", "loyalty": "Trung thành",
}
DISC_VN   = {"D": "Quyết đoán (D)", "I": "Ảnh hưởng (I)", "S": "Ổn định (S)", "C": "Cẩn thận (C)"}
LEVEL_VN  = {"high": "Cao", "medium": "Trung bình", "low": "Thấp"}
FUNNEL_VN = {
    "warm_lead": "Warm Lead", "cold_lead": "Cold Lead",
    "hot_lead": "Hot Lead", "existing_customer": "KH cũ",
}

SENT_COLOR = {"positive": _SUCCESS, "neutral": _WARNING, "negative": _DANGER}
DISC_COLOR = {"D": _DANGER, "I": _WARNING, "S": _SUCCESS, "C": _INFO}
URG_COLOR  = {"high": _DANGER, "medium": _WARNING, "low": _SUCCESS}
TRUST_COLOR= {"high": _SUCCESS, "medium": _WARNING, "low": _DANGER}

# ─── CONVERSATION SNIPPETS ────────────────────────────────────────────────────
_SNIPPETS = {
"hoi_gia": """\
[CUSTOMER] Chào shop! Gọng kính titanium bên mình giá khoảng bao nhiêu ạ?
[ADMIN] Dạ chào bạn! Gọng titanium nhẹ và siêu bền, từ 850k-2tr tùy dòng ạ. Bạn đang tìm gọng dáng nào?
[CUSTOMER] Mình hay đeo kiểu rimless, có không ạ?
[ADMIN] Dạ có! Rimless titanium đang hot lắm ạ, nhẹ như không đeo. Giá từ 1.1tr, kết hợp tròng Zeiss sẽ rất tốt.
[CUSTOMER] Tròng thêm bao nhiêu nữa?
[ADMIN] Tròng đơn focal cơ bản 350k, anti-blue light thêm 150k, loại Zeiss premium từ 850k ạ.
[CUSTOMER] Ok tổng khoảng 1.5tr cho bộ rimless + tròng Zeiss cơ bản?
[ADMIN] Đúng rồi ạ! Kèm thêm case cứng và dây đeo miễn phí. Bạn có muốn ghé thử mẫu không?
[CUSTOMER] Thứ 7 mình ghé được không?
[ADMIN] Dạ được! Shop mở 8h-21h. Hẹn gặp bạn thứ 7 nhé!""",

"tu_van_do_mat": """\
[CUSTOMER] Em muốn hỏi về dịch vụ đo mắt bên mình ạ, có chính xác không?
[ADMIN] Dạ chào em! Bên mình dùng máy đo tự động kết hợp bác sĩ nhãn khoa kiểm tra thủ công. Độ chính xác rất cao ạ.
[CUSTOMER] Em bị cận khá nặng, 7 độ, đo được không?
[ADMIN] Dạ đo được hoàn toàn! Máy của mình xử lý tới -20.00. Cận 7 độ bình thường ạ.
[CUSTOMER] Ngoài đo cận có check thêm gì không?
[ADMIN] Có ạ! Đo thêm loạn thị, lão thị, áp lực nhãn cầu (phòng ngừa glaucoma), và field of vision ạ. Phí tổng cộng 150k.
[CUSTOMER] Oke, vậy có cần đặt lịch trước không ạ?
[ADMIN] Nên đặt trước để không chờ ạ. Em inbox số điện thoại mình book lịch cho nhé!
[CUSTOMER] Ok để em nhắn SĐT sau. Cảm ơn!""",

"dat_lich_do": """\
[CUSTOMER] Mình muốn đặt lịch khám mắt cho bé nhà mình, 9 tuổi
[ADMIN] Dạ chào bạn! Bé có hay nheo mắt hay ngồi gần tivi/điện thoại không ạ?
[CUSTOMER] Hay nheo mắt và hay phàn nàn nhìn bảng lớp không rõ
[ADMIN] Dấu hiệu cận thị rồi ạ! Cần khám sớm. Bên mình có bác sĩ chuyên trẻ em vào thứ 3, 5, 7 ạ.
[CUSTOMER] Thứ 7 tuần này còn lịch không?
[ADMIN] Thứ 7 còn 9h00 và 14h30 ạ. Bạn chọn giờ nào?
[CUSTOMER] 9h nhé. Tên bé là Bảo Nam
[ADMIN] Đã đặt 9h thứ 7 cho bé Bảo Nam! Nhớ cho bé tránh đọc sách 30' trước khi khám nhé ạ.
[CUSTOMER] Ok, cảm ơn nhiều!
[ADMIN] Dạ hẹn gặp bé Bảo Nam thứ 7 nhé!""",

"hoi_san_pham": """\
[CUSTOMER] Bên mình có kính áp tròng màu không? Mình bị cận 3.5 độ
[ADMIN] Dạ có ạ! Lens màu có độ từ 0 đến -8.00, cận 3.5 dùng được hoàn toàn.
[CUSTOMER] Có màu grey tự nhiên không? Không muốn quá lòe loẹt
[ADMIN] Dạ có! Freshlook Dimensions Grey và Acuvue Define Fresh Gray trông rất tự nhiên ạ, hợp với người Á Đông.
[CUSTOMER] Lens dùng được bao lâu? Và giá?
[ADMIN] Loại tháng dùng 30 ngày, từ 280k/hộp 2 đôi. Loại ngày dùng 1 lần, 350k/hộp 10 đôi ạ.
[CUSTOMER] Mình hay dùng máy tính 8h/ngày, loại nào phù hợp?
[ADMIN] Bạn nên dùng loại ngày (daily) ạ — thoáng khí hơn, không lo nguy cơ nhiễm khuẩn do dùng nhiều ngày.
[CUSTOMER] Vậy cho mình order 2 hộp Freshlook Grey ngày nhé!""",

"mua_hang": """\
[CUSTOMER] Shop có Ray-Ban Clubmaster không? Muốn mua làm quà
[ADMIN] Dạ có ạ! RB3016 Clubmaster đang có đủ màu: gold/tortoise, black/gold, all-black ạ.
[CUSTOMER] Giá bao nhiêu vậy?
[ADMIN] Chính hãng từ Mỹ: 3.2tr, kèm case da và certificate ạ. Đang có free gift wrap dịp này.
[CUSTOMER] Tặng cho bố, bố mình 55 tuổi, màu nào phù hợp?
[ADMIN] Gold/Tortoise rất classic và phù hợp bậc trung niên ạ! Vừa lịch sự vừa có điểm nhấn.
[CUSTOMER] Ok mình đặt 1 cái gold/tortoise. Ship được không?
[ADMIN] Dạ ship toàn quốc, COD hoặc banking. 2-3 ngày ạ. Bạn để lại địa chỉ nhé!
[CUSTOMER] Địa chỉ: 45 Nguyễn Trãi, Q.1, HCM
[ADMIN] Đã nhận! Xác nhận đơn Ray-Ban RB3016 Gold/Tortoise, giao 45 Nguyễn Trãi Q.1. Cảm ơn bạn!""",

"khieu_nai": """\
[CUSTOMER] Tôi mua kính 3 tuần trước, tròng bị bong coating rồi, không dùng sai cách gì cả!
[ADMIN] Dạ rất xin lỗi bạn! Tình trạng này không nên xảy ra với tròng mới. Bạn có thể cho mình xem ảnh được không ạ?
[CUSTOMER] [Ảnh tròng bị bong ở chính giữa]
[ADMIN] Dạ đây là lỗi kỹ thuật ạ, hoàn toàn thuộc bảo hành. Bên mình sẽ thay tròng mới 100% miễn phí.
[CUSTOMER] Mất bao lâu? Tôi đang cần dùng
[ADMIN] 3-4 ngày làm việc ạ. Trong thời gian chờ bên mình có tròng tạm cho bạn mượn nếu bạn ghé cửa hàng.
[CUSTOMER] Ok tôi sẽ ghé ngày mai
[ADMIN] Dạ! Nhớ mang hóa đơn hoặc ảnh bill. Mình sẽ ưu tiên xử lý ngay cho bạn ạ. Xin lỗi vì sự bất tiện!""",

"hoi_bao_hanh": """\
[CUSTOMER] Kính mua ở đây được bảo hành bao lâu ạ?
[ADMIN] Dạ! Gọng: 12 tháng lỗi kỹ thuật. Tròng: 6 tháng bong tráng phủ. Tất cả tính từ ngày mua ạ.
[CUSTOMER] Nếu gọng bị cong do dùng lâu thì có được bảo hành không?
[ADMIN] Cong vênh tự nhiên do vật liệu thì được ạ. Nhưng do va chạm hay để nơi nóng (xe hơi dưới nắng) thì ngoài bảo hành.
[CUSTOMER] Mình muốn hỏi về trường hợp của mình: gọng bị lỏng chốt bản lề sau 8 tháng
[ADMIN] 8 tháng, lỏng chốt tự nhiên thì trong bảo hành ạ! Bạn mang vào mình siết/thay chốt miễn phí.
[CUSTOMER] Không cần có hóa đơn không?
[ADMIN] Nếu còn trong 12 tháng và có thể xác định ngày mua qua SĐT là được ạ. Không cần hóa đơn cứng.
[CUSTOMER] Tốt quá! Mình sẽ ghé cuối tuần nhé""",

"tu_van_kinh_ap_trong": """\
[CUSTOMER] Mình mới dùng lens lần đầu, có sợ không ạ?
[ADMIN] Dạ ban đầu hơi lạ nhưng sẽ quen rất nhanh ạ! Bên mình hướng dẫn đeo/tháo trực tiếp, miễn phí.
[CUSTOMER] Mắt mình hay bị khô, có dùng được không?
[ADMIN] Được ạ nhưng cần chọn đúng loại. Dailies Total 1 hoặc Acuvue Oasys — thiết kế cho mắt khô, có thể đeo 12-14h thoải mái.
[CUSTOMER] 2 loại đó giá bao nhiêu?
[ADMIN] Dailies Total 1: 580k/hộp 30 đôi (1 tháng). Acuvue Oasys 2-tuần: 280k/hộp 6 đôi ạ.
[CUSTOMER] Daily tiện hơn nhỉ? Không cần rửa hay ngâm
[ADMIN] Đúng! Daily là đơn giản và vệ sinh nhất, đặc biệt cho người mới. Mình recommend luôn ạ.
[CUSTOMER] Ok mình thử Dailies Total 1 nhé. Cận 3.25 đặt được không?
[ADMIN] Được ạ! 3.25 có sẵn. Lần đầu nên ghé để đo độ curve giác mạc cho vừa nhé. Sau đó order online thoải mái!""",
}

# ─── SYNTHETIC DATA ───────────────────────────────────────────────────────────
def _generate_synthetic_data(n: int = 350, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    PAGES   = ["Kính mắt Hoàng Anh - HN", "Kính mắt Minh Trí - HCM",
               "Quang Đức Optical - ĐN",  "Hùng Optics - CT"]
    P_PAGES = [0.35, 0.40, 0.15, 0.10]

    INTENTS  = list(INTENT_VN.keys())
    P_INT    = [0.28, 0.22, 0.18, 0.12, 0.08, 0.05, 0.04, 0.03]

    STAGES   = list(STAGE_VN.keys())
    P_STAGE  = [0.18, 0.25, 0.20, 0.15, 0.14, 0.08]

    FUNNELS  = list(FUNNEL_VN.keys())
    P_FUN    = [0.35, 0.25, 0.20, 0.20]

    SENTS    = ["positive", "neutral", "negative"]
    P_SENT   = [0.50, 0.30, 0.20]

    DISCS    = list(DISC_VN.keys())
    P_DISC   = [0.35, 0.30, 0.22, 0.13]

    GENS     = ["Millennial", "Gen Z", "Gen X", "Boomer"]
    P_GEN    = [0.40, 0.28, 0.22, 0.10]

    LIFESTYLES = ["Nhân viên văn phòng", "Học sinh/Sinh viên", "Phụ huynh",
                  "Chuyên gia", "Người trung niên"]
    P_LIFE   = [0.34, 0.26, 0.20, 0.12, 0.08]

    LEVELS   = ["high", "medium", "low"]

    PRODUCTS = ["Kính cận", "Kính lão", "Kính áp tròng", "Kính râm",
                "Gọng kính", "Tròng kính cao cấp", "Kính trẻ em"]

    COMP     = [None]*6 + ["Specsavers", "Grand Vision", "Local store", "Online shop"]
    CHURN    = [None]*7 + ["gia_cao", "khong_co_mau", "mua_cho_roi", "can_sua_lai"]

    # Dates — weighted toward recent months
    dates      = pd.date_range("2025-07-01", "2026-01-31", freq="D")
    w_dates    = np.exp(np.linspace(-2.0, 0, len(dates))); w_dates /= w_dates.sum()
    sampled_d  = rng.choice(dates, n, p=w_dates)

    pages   = rng.choice(PAGES,      n, p=P_PAGES)
    intents = rng.choice(INTENTS,    n, p=P_INT)
    stages  = rng.choice(STAGES,     n, p=P_STAGE)
    funnels = rng.choice(FUNNELS,    n, p=P_FUN)
    sents   = rng.choice(SENTS,      n, p=P_SENT)
    discs   = rng.choice(DISCS,      n, p=P_DISC)
    gens    = rng.choice(GENS,       n, p=P_GEN)
    lives   = rng.choice(LIFESTYLES, n, p=P_LIFE)
    urgs    = rng.choice(LEVELS,     n, p=[0.20, 0.50, 0.30])
    trusts  = rng.choice(LEVELS,     n, p=[0.40, 0.40, 0.20])
    prices  = rng.choice(LEVELS,     n, p=[0.35, 0.40, 0.25])
    comps   = rng.choice(COMP,       n)
    prods   = rng.choice(PRODUCTS,   n)
    churns  = rng.choice(CHURN,      n)

    def _scores(sents_arr, mu_hi=7.6, mu_lo=4.4, sigma=1.1):
        mu_map = {"positive": mu_hi, "neutral": 6.0, "negative": mu_lo}
        v = np.array([rng.normal(mu_map[s], sigma) for s in sents_arr])
        return np.clip(v, 1, 10).round(1)

    agent_scores   = _scores(sents)
    empathy_scores = _scores(sents, 7.8, 4.2)
    closing_skills = _scores(sents, 7.0, 4.8)

    # Conversion probability — intent + sentiment + stage aware
    base_p = np.full(n, 0.35)
    for i, (intent, sent, stage) in enumerate(zip(intents, sents, stages)):
        if intent in ("mua_hang", "dat_lich_do"):    base_p[i] += 0.25
        if intent == "khieu_nai":                    base_p[i] -= 0.20
        if sent   == "positive":                     base_p[i] += 0.15
        if sent   == "negative":                     base_p[i] -= 0.15
        if stage  in ("purchase", "evaluation"):     base_p[i] += 0.20
        if stage  == "awareness":                    base_p[i] -= 0.12
    conv_probs  = np.clip(base_p, 0.02, 0.98)
    conversions = (rng.random(n) < conv_probs).astype(float)

    sent_scores = np.array([
        rng.uniform(6, 9.5) if s == "positive" else
        (rng.uniform(1, 4.5) if s == "negative" else rng.uniform(4, 7))
        for s in sents
    ]).round(2)

    csats = np.array([
        rng.uniform(3.8, 5) if s == "positive" else
        (rng.uniform(1.5, 2.8) if s == "negative" else rng.uniform(2.5, 4))
        for s in sents
    ]).round(2)

    msg_counts = rng.integers(4, 26, n)
    conv_ids   = [f"{pd.Timestamp(d).strftime('%Y%m%d')}_{i:04d}" for i, d in enumerate(sampled_d)]
    snippets   = [_SNIPPETS.get(intent, _SNIPPETS["hoi_gia"]) for intent in intents]

    df = pd.DataFrame({
        "conversation_id":       conv_ids,
        "conversation_date":     pd.to_datetime(sampled_d),
        "page_name":             pages,
        "message_count":         msg_counts,
        "intent_primary":        intents,
        "purchase_stage":        stages,
        "funnel_type":           funnels,
        "funnel_is_successful":  conversions,
        "sentiment_overall":     sents,
        "sentiment_score":       sent_scores,
        "disc_primary":          discs,
        "generation_cohort":     gens,
        "lifestyle_segment":     lives,
        "urgency_level":         urgs,
        "trust_level":           trusts,
        "price_sensitivity":     prices,
        "agent_overall_score":   agent_scores,
        "empathy_score":         empathy_scores,
        "agent_closing_skill":   closing_skills,
        "predicted_csat":        csats,
        "conversion_probability": conv_probs.round(3),
        "competitor_brand":      comps,
        "product_interest":      prods,
        "churn_reason":          churns,
        "conversation_snippet":  snippets,
    })
    return df.sort_values("conversation_date").reset_index(drop=True)


# ─── DATA LOADER ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    csv_path = Path(__file__).parent / "data" / "conversations.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, parse_dates=["conversation_date"])
        st.session_state["data_source"] = f"📂 Gold export ({len(df):,} records)"
    else:
        df = _generate_synthetic_data()
        st.session_state["data_source"] = f"🎲 Dữ liệu demo tổng hợp ({len(df):,} records)"
    return df


# ─── UI HELPERS ───────────────────────────────────────────────────────────────
def _kpi(col, label: str, value: str, color: str, sub: str = ""):
    col.markdown(
        f"""<div class="kpi-card" style="--c:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{color}">{value}</div>
        {"<div class='kpi-delta' style='color:#888'>" + sub + "</div>" if sub else ""}
        </div>""",
        unsafe_allow_html=True,
    )


def _badge(icon: str, text: str, color: str) -> str:
    return (
        f'<span style="background:rgba(255,255,255,0.06);border:1px solid {color};'
        f'color:{color};border-radius:12px;padding:2px 10px;font-size:12px;'
        f'font-weight:600;white-space:nowrap;margin:2px">{icon} {text}</span>'
    )


def _score_row(label: str, val: float, max_val: float = 10) -> str:
    pct = val / max_val * 100
    c = _SUCCESS if pct >= 70 else (_WARNING if pct >= 40 else _DANGER)
    return (
        f'<tr><td style="color:#888;font-size:11px;padding:3px 8px;white-space:nowrap">'
        f'{label}</td>'
        f'<td style="width:60px"><div style="background:#333;border-radius:4px;height:6px">'
        f'<div style="background:{c};width:{pct:.0f}%;height:6px;border-radius:4px"></div>'
        f'</div></td>'
        f'<td style="color:{c};font-size:12px;font-weight:700;padding:3px 8px">'
        f'{val:.1f}</td></tr>'
    )


def _plotly_bg(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10, l=10, r=10),
        font=dict(color="#ccc"),
    )
    return fig


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:8px 0">'
            '<span style="font-size:32px">🔭</span><br>'
            '<strong style="font-size:16px;color:#667eea">Chat Analytics AI</strong><br>'
            '<span style="font-size:11px;color:#888">Demo v8.0</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="demo-badge">⚠️ Demo Mode — '
            f'{st.session_state.get("data_source","...")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        # Date filter
        st.markdown("**📅 Khoảng thời gian**")
        min_d = df["conversation_date"].min().date()
        max_d = df["conversation_date"].max().date()
        date_range = st.date_input(
            "Từ — Đến",
            value=(min_d, max_d),
            min_value=min_d, max_value=max_d,
            label_visibility="collapsed",
        )

        # Page filter
        st.markdown("**🏪 Cửa hàng**")
        pages = ["Tất cả"] + sorted(df["page_name"].dropna().unique().tolist())
        sel_page = st.selectbox("Chọn cửa hàng", pages, label_visibility="collapsed")

        st.divider()
        st.caption("💡 **Hướng dẫn**\n\nMở tab **🔍 Khám phá Hội thoại** để xem tính năng drill-down chính.")

        # Apply filters
        mask = pd.Series([True] * len(df), index=df.index)
        if len(date_range) == 2:
            d0 = pd.Timestamp(date_range[0])
            d1 = pd.Timestamp(date_range[1])
            mask &= (df["conversation_date"] >= d0) & (df["conversation_date"] <= d1)
        if sel_page != "Tất cả":
            mask &= df["page_name"] == sel_page

        filtered = df[mask]
        st.markdown(
            f'<div style="text-align:center;color:#667eea;font-size:22px;font-weight:700">'
            f'{len(filtered):,}</div>'
            f'<div style="text-align:center;color:#888;font-size:11px">conversations trong bộ lọc</div>',
            unsafe_allow_html=True,
        )
    return filtered


# ─── TAB 1: EXECUTIVE OVERVIEW ────────────────────────────────────────────────
def render_overview(df: pd.DataFrame):
    st.markdown("## 📊 Tổng quan")
    n = len(df)
    if n == 0:
        st.warning("Không có dữ liệu trong bộ lọc đã chọn.")
        return

    # ── KPI Row ──
    c1, c2, c3, c4, c5 = st.columns(5)
    conv_rate = df["funnel_is_successful"].mean() * 100 if "funnel_is_successful" in df.columns else 0
    avg_sent  = df["sentiment_score"].mean() if "sentiment_score" in df.columns else 0
    avg_agent = pd.to_numeric(df.get("agent_overall_score", pd.Series(dtype=float)), errors="coerce").mean()
    pct_pos   = (df["sentiment_overall"].astype(str) == "positive").mean() * 100 if "sentiment_overall" in df.columns else 0

    _kpi(c1, "Tổng hội thoại",    f"{n:,}",           _PRIMARY,  "được AI xử lý tự động")
    _kpi(c2, "Tỷ lệ chuyển đổi",  f"{conv_rate:.1f}%", _SUCCESS,  "funnel thành công")
    _kpi(c3, "Sentiment tích cực", f"{pct_pos:.0f}%",   _SUCCESS if pct_pos >= 50 else _WARNING,
         "khách hàng hài lòng")
    _kpi(c4, "Sentiment score TB", f"{avg_sent:.1f}/10",
         _SUCCESS if avg_sent >= 7 else (_WARNING if avg_sent >= 4 else _DANGER), "trung bình")
    _kpi(c5, "Agent score TB",
         f"{avg_agent:.1f}/10" if pd.notna(avg_agent) else "N/A",
         _SUCCESS if pd.notna(avg_agent) and avg_agent >= 7 else _WARNING, "hiệu suất team")

    st.divider()

    # ── Row 1: Trend + Intent ──
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("**📈 Lượng hội thoại theo thời gian**")
        trend = (
            df.set_index("conversation_date")
            .resample("W")["conversation_id"]
            .count()
            .reset_index(name="count")
        )
        fig = px.area(
            trend, x="conversation_date", y="count",
            color_discrete_sequence=[_PRIMARY],
            template=_TEMPLATE,
            labels={"conversation_date": "", "count": "Số conversations"},
        )
        fig.update_traces(fill="tozeroy", fillcolor="rgba(102,126,234,0.2)")
        st.plotly_chart(_plotly_bg(fig), use_container_width=True, config=_CFG)

    with col_r:
        st.markdown("**🎯 Phân bố Intent (mục đích liên hệ)**")
        intent_cnt = (
            df["intent_primary"].map(lambda x: INTENT_VN.get(x, x))
            .value_counts()
            .reset_index()
        )
        intent_cnt.columns = ["intent", "count"]
        fig2 = px.bar(
            intent_cnt, x="count", y="intent", orientation="h",
            color="count", color_continuous_scale=["#764ba2", _PRIMARY, _INFO],
            template=_TEMPLATE,
            labels={"count": "Số conversations", "intent": ""},
        )
        fig2.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(_plotly_bg(fig2), use_container_width=True, config=_CFG)

    # ── Row 2: Funnel + Sentiment ──
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown("**🔄 Purchase Funnel**")
        stage_order = ["awareness", "consideration", "intent", "evaluation", "purchase", "loyalty"]
        stage_cnt = df["purchase_stage"].value_counts().reindex(stage_order, fill_value=0).reset_index()
        stage_cnt.columns = ["stage", "count"]
        stage_cnt["label"] = stage_cnt["stage"].map(lambda x: STAGE_VN.get(x, x))
        fig3 = go.Figure(go.Funnel(
            y=stage_cnt["label"],
            x=stage_cnt["count"],
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(color=[_PRIMARY, "#5a6fd6", "#4e5fc5", "#4150b4", _SUCCESS, "#00a97a"]),
        ))
        fig3.update_layout(template=_TEMPLATE, showlegend=False)
        st.plotly_chart(_plotly_bg(fig3), use_container_width=True, config=_CFG)

    with col_r2:
        st.markdown("**💬 Phân bố Sentiment**")
        if "sentiment_overall" in df.columns:
            sent_cnt = df["sentiment_overall"].value_counts().reset_index()
            sent_cnt.columns = ["sent", "count"]
            color_map = {"positive": _SUCCESS, "neutral": _WARNING, "negative": _DANGER}
            fig4 = px.pie(
                sent_cnt, names="sent", values="count",
                color="sent", color_discrete_map=color_map,
                template=_TEMPLATE,
                hole=0.55,
            )
            fig4.update_traces(textposition="outside", textinfo="percent+label")
            fig4.update_layout(showlegend=False, annotations=[
                dict(text=f"{pct_pos:.0f}%<br>positive", x=0.5, y=0.5,
                     font_size=14, showarrow=False, font_color=_SUCCESS)
            ])
            st.plotly_chart(_plotly_bg(fig4), use_container_width=True, config=_CFG)


# ─── TAB 2: CONVERSATION EXPLORER (MAIN FEATURE) ──────────────────────────────
def render_explorer(df: pd.DataFrame):
    n = len(df)

    # ── Hero intro ──
    st.markdown(
        """<div style="background:linear-gradient(90deg,rgba(102,126,234,0.15),rgba(118,75,162,0.10));
        border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:16px 20px;margin-bottom:12px">
        <h3 style="margin:0;color:#c0c0ff">🔍 Khám phá Hội thoại theo Segment</h3>
        <p style="margin:6px 0 0;color:#aaa;font-size:13px">
        Chọn một <strong>chiều phân tích</strong> → chọn <strong>giá trị</strong>
        → xem danh sách conversations → click vào 1 conversation để xem
        <strong>nội dung chat thực + AI Scorecard tự động</strong>.
        </p></div>""",
        unsafe_allow_html=True,
    )

    if n == 0:
        st.warning("Không có dữ liệu trong bộ lọc đã chọn.")
        return

    DIMS = [
        ("intent_primary",    "Mục đích liên hệ (Intent)",   "🎯", INTENT_VN),
        ("sentiment_overall", "Cảm xúc khách hàng",          "💬", {}),
        ("purchase_stage",    "Giai đoạn mua hàng",          "📦", STAGE_VN),
        ("disc_primary",      "Nhóm tính cách DISC",         "🧠", DISC_VN),
        ("urgency_level",     "Mức độ khẩn cấp",             "⚡", LEVEL_VN),
        ("funnel_type",       "Loại kênh (Funnel)",          "🔄", FUNNEL_VN),
        ("generation_cohort", "Thế hệ khách hàng",           "👥", {}),
        ("trust_level",       "Mức độ tin tưởng",            "🤝", LEVEL_VN),
    ]
    valid_dims = [d for d in DIMS if d[0] in df.columns and df[d[0]].notna().any()]

    sel_dim = st.selectbox(
        "① Phân tích theo chiều",
        range(len(valid_dims)),
        format_func=lambda i: f"{valid_dims[i][2]} {valid_dims[i][1]}",
        key="dim_sel",
    )
    col_key, col_label, col_icon, col_map = valid_dims[sel_dim]

    # Value counts (filtered)
    _SKIP = {"unknown", "Unknown", "", "none", "None", "nan", "NaN", "True", "False"}
    vals  = df[col_key].dropna().astype(str)
    vals  = vals[~vals.isin(_SKIP)].pipe(lambda s: s[s.str.len() < 50])
    if vals.empty:
        st.info("Không có dữ liệu hợp lệ cho chiều này.")
        return

    counts = vals.value_counts()
    opts   = ["— Chọn để xem chi tiết —"] + [
        f"{col_map.get(v, v)}  ({c:,})" for v, c in zip(counts.index, counts.values)
    ]
    sel_opt = st.selectbox("② Chọn giá trị / phân khúc", opts, key="val_sel")

    if sel_opt == "— Chọn để xem chi tiết —":
        st.markdown(
            '<div style="height:120px;display:flex;align-items:center;justify-content:center;'
            'color:#666;font-size:14px">👆 Chọn một giá trị phía trên để xem conversations</div>',
            unsafe_allow_html=True,
        )
        return

    # Reverse-map display label → raw value
    raw_label = sel_opt.split("  (")[0]
    raw_val   = raw_label
    for k, v in col_map.items():
        if v == raw_label:
            raw_val = k
            break

    seg = df[df[col_key].astype(str) == raw_val].copy()
    seg_n = len(seg)

    st.divider()

    # ── KPI chips for segment ──
    seg_conv = seg["funnel_is_successful"].mean() * 100 if "funnel_is_successful" in seg.columns else 0
    seg_pos  = (seg["sentiment_overall"].astype(str) == "positive").mean() * 100
    seg_agent= pd.to_numeric(seg.get("agent_overall_score", pd.Series(dtype=float)), errors="coerce").mean()

    chips = [
        (f"{seg_n:,} conversations", _PRIMARY),
        (f"✅ Conv. {seg_conv:.0f}%", _SUCCESS if seg_conv >= 40 else _WARNING),
        (f"😊 Positive {seg_pos:.0f}%", _SUCCESS if seg_pos >= 50 else _WARNING),
    ]
    if pd.notna(seg_agent):
        chips.append((f"⭐ Agent {seg_agent:.1f}/10",
                      _SUCCESS if seg_agent >= 7 else _WARNING))

    html_chips = " ".join(
        f'<span style="background:rgba(255,255,255,0.06);border:1px solid {c};'
        f'color:{c};border-radius:16px;padding:4px 14px;font-size:13px;font-weight:600">'
        f'{t}</span>'
        for t, c in chips
    )
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin:8px 0">'
        f'<span style="color:#888;font-size:12px;align-self:center">'
        f'{col_icon} {col_label}: <strong style="color:#fff">{raw_label}</strong></span>'
        f' &nbsp; {html_chips}</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── List + Detail ──
    list_col, detail_col = st.columns([2, 3], gap="large")

    with list_col:
        st.markdown(f"**Chọn conversation ({min(seg_n, 120):,} / {seg_n:,})**")
        sub = seg.head(120)
        radio_opts = []
        for _, row in sub.iterrows():
            date = str(row.get("conversation_date", ""))[:10]
            intent_raw = str(row.get("intent_primary", ""))
            intent_lbl = INTENT_VN.get(intent_raw, intent_raw)
            s = str(row.get("sentiment_overall", "")).lower()
            dot = "🟢" if s == "positive" else ("🔴" if s == "negative" else "🟡")
            msgs = row.get("message_count", "?")
            radio_opts.append(f"{dot} {date}  ·  {intent_lbl[:18]}  ·  {msgs} tin")

        chosen = st.radio(
            "Conversation",
            radio_opts,
            index=0,
            key="conv_radio",
            label_visibility="collapsed",
        )
        sel_idx = radio_opts.index(chosen)

    with detail_col:
        row = sub.iloc[sel_idx]
        _render_conversation_detail(row)


def _render_conversation_detail(row: pd.Series):
    """Detail view: metadata ribbon → chat | AI scorecard."""
    # ── Badge ribbon ──
    badges_html = ""
    date = str(row.get("conversation_date", ""))[:10]
    if date and date != "nan":
        badges_html += _badge("📅", date, "#555")

    intent = str(row.get("intent_primary", ""))
    if intent and intent not in ("nan", "unknown"):
        badges_html += _badge("🎯", INTENT_VN.get(intent, intent), _PRIMARY)

    sent = str(row.get("sentiment_overall", "")).lower()
    if sent in SENT_COLOR:
        badges_html += _badge("●", sent, SENT_COLOR[sent])

    disc = str(row.get("disc_primary", "")).upper()
    if disc in DISC_COLOR:
        badges_html += _badge("🧠", f"DISC-{disc}", DISC_COLOR[disc])

    urg = str(row.get("urgency_level", "")).lower()
    if urg in URG_COLOR:
        badges_html += _badge("⚡", LEVEL_VN.get(urg, urg), URG_COLOR[urg])

    funnel = str(row.get("funnel_type", ""))
    if funnel and funnel not in ("nan", "unknown"):
        badges_html += _badge("🔄", FUNNEL_VN.get(funnel, funnel), "#764ba2")

    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px">'
        f'{badges_html}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:6px 0;border-color:rgba(255,255,255,0.1)'>",
                unsafe_allow_html=True)

    chat_c, score_c = st.columns([3, 2], gap="medium")

    with chat_c:
        st.markdown("**💬 Nội dung hội thoại**")
        snippet = str(row.get("conversation_snippet", ""))
        if snippet and snippet not in ("nan", "", "None"):
            _render_bubbles(snippet)
        else:
            st.info("Không có nội dung hội thoại.")

    with score_c:
        st.markdown("**🤖 AI Scorecard**")
        _render_scorecard(row)


def _render_bubbles(text: str):
    lines   = [l.strip() for l in text.strip().split("\n") if l.strip()]
    bubbles = []
    for line in lines:
        if line.startswith("[CUSTOMER]"):
            msg = line[10:].strip().replace("<", "&lt;").replace(">", "&gt;")
            bubbles.append(
                f'<div style="display:flex;margin:4px 0">'
                f'<div style="max-width:82%;background:rgba(0,200,150,0.12);'
                f'border-radius:0 10px 10px 10px;padding:6px 10px">'
                f'<div style="font-size:10px;color:#00c896;font-weight:700;margin-bottom:1px">👤 KHÁCH</div>'
                f'<div style="font-size:12px;color:#ddd">{msg}</div>'
                f'</div></div>'
            )
        elif line.startswith("[ADMIN]"):
            msg = line[7:].strip().replace("<", "&lt;").replace(">", "&gt;")
            bubbles.append(
                f'<div style="display:flex;justify-content:flex-end;margin:4px 0">'
                f'<div style="max-width:82%;background:rgba(102,126,234,0.15);'
                f'border-radius:10px 0 10px 10px;padding:6px 10px;text-align:right">'
                f'<div style="font-size:10px;color:#667eea;font-weight:700;margin-bottom:1px">ADMIN 💼</div>'
                f'<div style="font-size:12px;color:#ddd">{msg}</div>'
                f'</div></div>'
            )
    st.markdown(
        '<div style="max-height:380px;overflow-y:auto;padding:8px;'
        'border:1px solid rgba(255,255,255,0.07);border-radius:8px">'
        + "".join(bubbles) + "</div>",
        unsafe_allow_html=True,
    )


def _render_scorecard(row: pd.Series):
    def _blk(title, rows_html):
        if not rows_html:
            return
        st.markdown(
            f'<div class="score-block">'
            f'<div class="score-title">{title}</div>'
            f'<table style="width:100%;border-collapse:collapse">{rows_html}</table>'
            f'</div>',
            unsafe_allow_html=True,
        )

    def _row(label, val, color="#c0c0ff"):
        if val is None or str(val).strip() in ("", "nan", "unknown", "None"):
            return ""
        val_s = str(val)[:28]
        return (f'<tr><td style="color:#888;font-size:11px;padding:3px 6px;white-space:nowrap">{label}</td>'
                f'<td style="color:{color};font-size:12px;font-weight:600;padding:3px 6px">{val_s}</td></tr>')

    intent  = str(row.get("intent_primary", ""))
    stage   = str(row.get("purchase_stage", ""))
    funnel  = str(row.get("funnel_type", ""))
    urg     = str(row.get("urgency_level", ""))
    blk1    = (
        _row("Intent",   INTENT_VN.get(intent, intent), _PRIMARY) +
        _row("Stage",    STAGE_VN.get(stage, stage)) +
        _row("Funnel",   FUNNEL_VN.get(funnel, funnel)) +
        _row("Urgency",  LEVEL_VN.get(urg, urg), URG_COLOR.get(urg, "#888"))
    )
    _blk("🎯 Phân loại", blk1)

    disc    = str(row.get("disc_primary", "")).upper()
    sent    = str(row.get("sentiment_overall", "")).lower()
    trust   = str(row.get("trust_level", "")).lower()
    price   = str(row.get("price_sensitivity", "")).lower()
    comp    = str(row.get("competitor_brand", ""))
    blk2    = (
        _row("DISC",      DISC_VN.get(disc, disc), DISC_COLOR.get(disc, "#888")) +
        _row("Sentiment", sent.capitalize(),        SENT_COLOR.get(sent, "#888")) +
        _row("Trust",     LEVEL_VN.get(trust, trust), TRUST_COLOR.get(trust, "#888")) +
        _row("Giá nhạy",  LEVEL_VN.get(price, price)) +
        (_row("Đối thủ",  comp, _WARNING) if comp not in ("nan", "None", "") else "")
    )
    _blk("🧠 Hồ sơ KH", blk2)

    conv_ok = str(row.get("funnel_is_successful", "")).lower() in ("1", "1.0", "true")
    prob    = row.get("conversion_probability")
    csat    = row.get("predicted_csat")
    churn   = str(row.get("churn_reason", ""))
    blk3    = _row("Chuyển đổi",
                   "✅ Thành công" if conv_ok else "❌ Chưa chốt",
                   _SUCCESS if conv_ok else _DANGER)
    try:
        blk3 += _row("Xác suất conv.", f"{float(prob)*100:.0f}%",
                     _SUCCESS if float(prob) >= 0.6 else _WARNING)
    except Exception:
        pass
    try:
        blk3 += _row("CSAT dự báo", f"{float(csat):.1f}/5",
                     _SUCCESS if float(csat) >= 4 else _WARNING)
    except Exception:
        pass
    if churn not in ("nan", "None", ""):
        blk3 += _row("Lý do bỏ", churn, _WARNING)
    _blk("💰 Chuyển đổi", blk3)

    agent_sc = row.get("agent_overall_score")
    emp_sc   = row.get("empathy_score")
    close_sc = row.get("agent_closing_skill")
    try:
        a, e, c = float(agent_sc), float(emp_sc), float(close_sc)
        rows_html = _score_row("Tổng",     a) + _score_row("Đồng cảm", e) + _score_row("Chốt sale", c)
        st.markdown(
            f'<div class="score-block"><div class="score-title">👤 Agent</div>'
            f'<table style="width:100%;border-collapse:collapse">{rows_html}</table></div>',
            unsafe_allow_html=True,
        )
    except Exception:
        pass


# ─── TAB 3: CUSTOMER INTELLIGENCE ────────────────────────────────────────────
def render_intelligence(df: pd.DataFrame):
    st.markdown("## 🧠 Customer Intelligence")
    n = len(df)
    if n == 0:
        st.warning("Không có dữ liệu.")
        return

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("**🎭 Phân bố DISC**")
        disc_cnt = df["disc_primary"].value_counts().reset_index()
        disc_cnt.columns = ["disc", "count"]
        disc_cnt["label"] = disc_cnt["disc"].map(lambda x: DISC_VN.get(x.upper(), x))
        fig = px.bar(
            disc_cnt, x="disc", y="count",
            color="disc",
            color_discrete_map={"D": _DANGER, "I": _WARNING, "S": _SUCCESS, "C": _INFO},
            template=_TEMPLATE,
            text="count",
            labels={"disc": "DISC Type", "count": ""},
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(_plotly_bg(fig), use_container_width=True, config=_CFG)

        st.markdown("**💰 Price Sensitivity vs Conversion**")
        piv = df.groupby("price_sensitivity")["funnel_is_successful"].mean().reset_index()
        piv.columns = ["price_sens", "conv_rate"]
        piv["label"] = piv["price_sens"].map(lambda x: LEVEL_VN.get(x, x))
        piv["conv_pct"] = (piv["conv_rate"] * 100).round(1)
        fig3 = px.bar(
            piv, x="label", y="conv_pct",
            color="conv_pct",
            color_continuous_scale=[_DANGER, _WARNING, _SUCCESS],
            template=_TEMPLATE,
            text="conv_pct",
            labels={"label": "Mức giá nhạy", "conv_pct": "Conversion %"},
        )
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig3.update_layout(coloraxis_showscale=False)
        st.plotly_chart(_plotly_bg(fig3), use_container_width=True, config=_CFG)

    with col_r:
        st.markdown("**👥 Phân bố thế hệ khách hàng**")
        gen_cnt = df["generation_cohort"].value_counts().reset_index()
        gen_cnt.columns = ["gen", "count"]
        fig2 = px.pie(
            gen_cnt, names="gen", values="count",
            color_discrete_sequence=[_PRIMARY, _INFO, _SUCCESS, _WARNING],
            template=_TEMPLATE, hole=0.45,
        )
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(_plotly_bg(fig2), use_container_width=True, config=_CFG)

        st.markdown("**🤝 Trust Level vs Conversion Rate**")
        tpiv = df.groupby("trust_level")["funnel_is_successful"].agg(["mean", "count"]).reset_index()
        tpiv["conv_pct"] = (tpiv["mean"] * 100).round(1)
        tpiv["trust_lbl"] = tpiv["trust_level"].map(lambda x: LEVEL_VN.get(x, x))
        fig4 = px.scatter(
            tpiv, x="trust_lbl", y="conv_pct", size="count",
            color="conv_pct",
            color_continuous_scale=[_DANGER, _WARNING, _SUCCESS],
            template=_TEMPLATE,
            text="conv_pct",
            labels={"trust_lbl": "Trust Level", "conv_pct": "Conversion %", "count": "Số conv."},
        )
        fig4.update_traces(texttemplate="%{text:.0f}%", textposition="top center")
        fig4.update_layout(coloraxis_showscale=False)
        st.plotly_chart(_plotly_bg(fig4), use_container_width=True, config=_CFG)

    # ── Sentiment by intent heatmap ──
    st.markdown("**🔥 Sentiment × Intent Matrix**")
    matrix = pd.crosstab(
        df["intent_primary"].map(lambda x: INTENT_VN.get(x, x)),
        df["sentiment_overall"],
    )
    fig5 = px.imshow(
        matrix,
        color_continuous_scale=["#1a0a20", _WARNING, _SUCCESS],
        template=_TEMPLATE,
        aspect="auto",
        text_auto=True,
        labels={"x": "Sentiment", "y": "Intent", "color": "Số hội thoại"},
    )
    st.plotly_chart(_plotly_bg(fig5), use_container_width=True, config=_CFG)


# ─── TAB 4: SYSTEM OVERVIEW ───────────────────────────────────────────────────
def render_system():
    st.markdown("## 💡 Về Hệ thống AI")

    st.markdown("""
<div style="background:rgba(102,126,234,0.08);border:1px solid rgba(102,126,234,0.25);
border-radius:10px;padding:20px;margin-bottom:16px">
<h4 style="color:#c0c0ff;margin:0 0 12px">⚙️ Kiến trúc Pipeline</h4>
<div style="display:flex;align-items:center;flex-wrap:wrap;gap:4px;font-size:13px">
  <div style="background:rgba(255,255,255,0.06);border-radius:6px;padding:8px 14px;text-align:center">
    📱<br><strong>Facebook<br>Messenger</strong>
  </div>
  <span style="color:#667eea;font-size:20px">→</span>
  <div style="background:rgba(255,255,255,0.06);border-radius:6px;padding:8px 14px;text-align:center">
    🔄<br><strong>Real-time<br>Sync (API)</strong>
  </div>
  <span style="color:#667eea;font-size:20px">→</span>
  <div style="background:rgba(102,126,234,0.15);border-radius:6px;padding:8px 14px;text-align:center">
    📦<br><strong>Bronze Layer<br>(raw data)</strong>
  </div>
  <span style="color:#667eea;font-size:20px">→</span>
  <div style="background:rgba(102,126,234,0.20);border-radius:6px;padding:8px 14px;text-align:center">
    ⚗️<br><strong>Silver Layer<br>(cleaned)</strong>
  </div>
  <span style="color:#667eea;font-size:20px">→</span>
  <div style="background:rgba(0,200,150,0.15);border-radius:6px;padding:8px 14px;text-align:center">
    🤖<br><strong>AI Analysis<br>(Ollama LLM)</strong>
  </div>
  <span style="color:#667eea;font-size:20px">→</span>
  <div style="background:rgba(0,200,150,0.20);border-radius:6px;padding:8px 14px;text-align:center">
    🏆<br><strong>Gold Layer<br>(enriched)</strong>
  </div>
  <span style="color:#667eea;font-size:20px">→</span>
  <div style="background:rgba(245,166,35,0.15);border-radius:6px;padding:8px 14px;text-align:center">
    📊<br><strong>Dashboard<br>(này)</strong>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🤖 AI tự động trích xuất 27+ tín hiệu mỗi conversation**")
        signals = [
            ("🎯", "Phân loại intent",         "Mục đích liên hệ chính/phụ"),
            ("📦", "Purchase Stage",           "Giai đoạn trong hành trình mua"),
            ("🔄", "Funnel Type",              "Loại kênh và kết quả funnel"),
            ("💬", "Sentiment Analysis",       "Cảm xúc đầu/cuối/tổng + delta"),
            ("🧠", "DISC Profiling",           "Nhóm tính cách khách hàng"),
            ("👥", "Generation & Lifestyle",   "Thế hệ + phân khúc lối sống"),
            ("⚡", "Urgency & Trust",          "Mức khẩn cấp, tin tưởng"),
            ("💰", "Conversion Signals",       "Xác suất chốt đơn, CSAT dự báo"),
            ("🏆", "Competitor Intel",         "Đề cập đối thủ cạnh tranh"),
            ("👤", "Agent Scoring",            "8 chỉ số hiệu suất agent"),
            ("🎓", "Knowledge Gap",            "Lỗ hổng kiến thức cần đào tạo"),
            ("📊", "Politeness Score",         "Độ lịch sự và chuyên nghiệp"),
        ]
        for icon, name, desc in signals:
            st.markdown(
                f'<div style="display:flex;align-items:center;padding:5px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.05)">'
                f'<span style="font-size:16px;width:28px">{icon}</span>'
                f'<span style="color:#c0c0ff;font-weight:600;width:160px;font-size:13px">{name}</span>'
                f'<span style="color:#888;font-size:12px">{desc}</span></div>',
                unsafe_allow_html=True,
            )

    with col_b:
        st.markdown("**📈 Tính năng nổi bật của Dashboard**")
        features = [
            ("✅", "Real-time Sync",        "Đồng bộ tự động từ Facebook mỗi 10 phút"),
            ("✅", "Drill-Down Explorer",   "Click chart → xem conversation ngay"),
            ("✅", "AI Conversation Card",  "Full chat + 27 tín hiệu AI side-by-side"),
            ("✅", "Multi-Store Filter",    "Phân tích theo từng cửa hàng"),
            ("✅", "Executive KPIs",        "Tổng quan nhanh cho lãnh đạo"),
            ("✅", "Customer Intelligence", "DISC, generation, lifestyle profiling"),
            ("✅", "Agent Coaching",        "Score chi tiết + điểm cần cải thiện"),
            ("✅", "Conversion Funnel",     "Theo dõi hành trình mua hàng"),
            ("✅", "Competitor Tracking",   "Phát hiện khi KH nhắc đến đối thủ"),
            ("✅", "Export CSV",            "Tải dữ liệu thô theo bộ lọc bất kỳ"),
            ("🔜", "Anomaly Alerts",        "Cảnh báo khi có đột biến bất thường"),
            ("🔜", "A/B Script Testing",    "So sánh kịch bản tư vấn hiệu quả"),
        ]
        for icon, name, desc in features:
            color = _SUCCESS if icon == "✅" else _WARNING
            st.markdown(
                f'<div style="display:flex;align-items:center;padding:5px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.05)">'
                f'<span style="font-size:14px;width:28px">{icon}</span>'
                f'<span style="color:{color};font-weight:600;width:170px;font-size:13px">{name}</span>'
                f'<span style="color:#888;font-size:12px">{desc}</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="background:rgba(0,200,150,0.08);border:1px solid rgba(0,200,150,0.3);'
            'border-radius:8px;padding:12px 16px;">'
            '<div style="color:#00c896;font-weight:700;font-size:13px">🎯 Mục tiêu kinh doanh</div>'
            '<div style="color:#aaa;font-size:12px;margin-top:6px">Tăng conversion rate từ 35% → 50%<br>'
            'Giảm thời gian coaching agent 60%<br>'
            'Phát hiện 100% conversation có mention đối thủ<br>'
            'ROI ước tính: 3-4x trong 6 tháng</div></div>',
            unsafe_allow_html=True,
        )


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    df       = load_data()
    filtered = render_sidebar(df)

    # Hero header
    st.markdown(
        '<h1 style="margin:0;color:#667eea">🔭 Chat Analytics AI</h1>'
        '<p style="color:#888;margin:0 0 8px;font-size:14px">'
        'Phân tích hội thoại tự động bằng AI — Demo Dashboard cho Stakeholders</p>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Tổng quan",
        "🔍 Khám phá Hội thoại",
        "🧠 Customer Intelligence",
        "💡 Về Hệ thống",
    ])

    with tab1: render_overview(filtered)
    with tab2: render_explorer(filtered)
    with tab3: render_intelligence(filtered)
    with tab4: render_system()


if __name__ == "__main__":
    main()

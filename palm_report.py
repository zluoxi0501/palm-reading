import streamlit as st
from PIL import Image
import io
import time

st.set_page_config(
    page_title="掌纹解读",
    page_icon="🤚",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_css():
    st.markdown("""
    <style>
    /* ── base ── */
    .stApp {
        background-color: #0d0f13;
        font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .main .block-container { max-width: 660px; padding: 0 1.5rem 4rem; }

    /* ── ambient background texture ── */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            radial-gradient(ellipse 60% 40% at 50% 0%, rgba(198,168,107,0.06) 0%, transparent 70%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' opacity='0.04'%3E%3Ccircle cx='200' cy='200' r='160' fill='none' stroke='%23c6a86b' stroke-width='0.6'/%3E%3Ccircle cx='200' cy='200' r='120' fill='none' stroke='%23c6a86b' stroke-width='0.4'/%3E%3Ccircle cx='200' cy='200' r='80' fill='none' stroke='%23c6a86b' stroke-width='0.3'/%3E%3Cline x1='200' y1='40' x2='200' y2='360' stroke='%23c6a86b' stroke-width='0.3'/%3E%3Cline x1='40' y1='200' x2='360' y2='200' stroke='%23c6a86b' stroke-width='0.3'/%3E%3Cline x1='87' y1='87' x2='313' y2='313' stroke='%23c6a86b' stroke-width='0.2'/%3E%3Cline x1='313' y1='87' x2='87' y2='313' stroke='%23c6a86b' stroke-width='0.2'/%3E%3C/svg%3E");
        background-size: cover, 520px 520px;
        background-position: center top, center center;
        background-repeat: no-repeat, repeat;
        pointer-events: none;
        z-index: 0;
        filter: blur(1px);
    }
    .stApp > * { position: relative; z-index: 1; }

    /* ── hero ── */
    .hero-wrap {
        padding: 72px 0 48px;
        text-align: center;
    }
    .hero-eyebrow {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #c6a86b;
        margin-bottom: 20px;
        opacity: 0.85;
    }
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: #ede5d4;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 20px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #5a5a6a;
        line-height: 1.9;
        max-width: 420px;
        margin: 0 auto 0;
        letter-spacing: 0.01em;
    }

    /* ── divider ── */
    .gold-divider {
        width: 36px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #c6a86b, transparent);
        margin: 28px auto;
        opacity: 0.5;
    }

    /* ── upload zone ── */
    .upload-zone {
        background: linear-gradient(160deg, #1c1f27 0%, #161920 100%);
        border-radius: 20px;
        border: 1px solid #252830;
        box-shadow: 0 8px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03);
        padding: 44px 32px 36px;
        text-align: center;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .upload-zone::before {
        content: '';
        position: absolute;
        top: -60px; left: 50%;
        transform: translateX(-50%);
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(198,168,107,0.07) 0%, transparent 70%);
        pointer-events: none;
    }
    .upload-palm-icon {
        font-size: 44px;
        margin-bottom: 16px;
        opacity: 0.55;
        filter: grayscale(0.3);
        line-height: 1;
    }
    .upload-main-text {
        font-size: 16px;
        font-weight: 600;
        color: #ccc4b4;
        margin-bottom: 8px;
        letter-spacing: 0.01em;
    }
    .upload-sub-text {
        font-size: 12px;
        color: #3e3e50;
        line-height: 1.7;
    }

    /* hide default streamlit file uploader label & drag area, show our zone instead */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] > div:first-child {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        min-height: 0 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    /* ── preview section ── */
    .preview-items {
        background: #161920;
        border-radius: 16px;
        border: 1px solid #1e2128;
        padding: 28px 32px;
        margin-bottom: 28px;
    }
    .preview-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #c6a86b;
        margin-bottom: 20px;
        opacity: 0.8;
    }
    .preview-item {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 12px 0;
        border-bottom: 1px solid #1e2128;
    }
    .preview-item:last-child { border-bottom: none; }
    .preview-dot {
        width: 5px; height: 5px;
        border-radius: 50%;
        background: #c6a86b;
        margin-top: 7px;
        flex-shrink: 0;
        opacity: 0.7;
    }
    .preview-item-title {
        font-size: 13px;
        font-weight: 600;
        color: #ccc4b4;
        margin-bottom: 2px;
    }
    .preview-item-desc {
        font-size: 12px;
        color: #4a4a5a;
        line-height: 1.6;
    }

    /* ── cards ── */
    .card {
        background: linear-gradient(160deg, #1c1f27 0%, #161920 100%);
        border-radius: 16px;
        border: 1px solid #252830;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        padding: 28px 32px;
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease forwards;
    }
    .card-module-label {
        font-size: 11px;
        font-weight: 600;
        color: #c6a86b;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 8px;
        opacity: 0.8;
    }
    .card-title {
        font-size: 20px;
        font-weight: 700;
        color: #ede5d4;
        margin-bottom: 20px;
    }
    .conclusion-row {
        display: flex;
        align-items: baseline;
        gap: 10px;
        margin-bottom: 14px;
    }
    .conclusion-label {
        font-size: 11px;
        font-weight: 700;
        color: #c6a86b;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        white-space: nowrap;
        padding-top: 2px;
        opacity: 0.8;
    }
    .conclusion-text {
        font-size: 16px;
        font-weight: 600;
        color: #ede5d4;
        line-height: 1.5;
    }
    .interpretation-text {
        font-size: 14px;
        color: #8a8a9a;
        line-height: 1.9;
        margin-bottom: 14px;
    }
    .reminder-box {
        background: #0d0f13;
        border-left: 2px solid #c6a86b;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 13px;
        color: #c6a86b;
        font-style: italic;
        line-height: 1.7;
        opacity: 0.9;
    }

    /* ── upsell ── */
    .upsell-card {
        background: linear-gradient(160deg, #13161c 0%, #0f1115 100%);
        border-radius: 16px;
        border: 1px solid #252830;
        padding: 36px 32px;
        margin-top: 8px;
        margin-bottom: 20px;
        text-align: center;
    }
    .upsell-card .upsell-body {
        font-size: 14px;
        color: #5a5a6a;
        line-height: 1.9;
        margin-bottom: 0;
    }
    .upsell-card .upsell-hook {
        font-size: 18px;
        font-weight: 700;
        color: #ede5d4;
        margin-bottom: 14px;
        line-height: 1.5;
    }

    /* ── payment ── */
    .payment-box {
        background: #161920;
        border-radius: 16px;
        border: 1.5px dashed #252830;
        padding: 40px 28px;
        text-align: center;
        margin: 20px 0;
    }

    .section-divider {
        border: none;
        border-top: 1px solid #1e2128;
        margin: 18px 0;
    }
    .page-title { font-size: 28px; font-weight: 700; color: #ede5d4; text-align: center; margin-bottom: 8px; }
    .page-subtitle { font-size: 14px; color: #5a5a6a; text-align: center; margin-bottom: 28px; line-height: 1.8; }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .stButton > button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #c6a86b 0%, #a8864a 100%) !important;
        border: none !important;
        color: #0d0f13 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 20px rgba(198,168,107,0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #d4b87a 0%, #b8965a 100%) !important;
        box-shadow: 0 6px 28px rgba(198,168,107,0.35) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "uploaded_image": None,
        "free_report_ready": False,
        "payment_page": False,
        "paid_unlocked": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------------------------------------------------------------
# Payment helpers (stub — real payment not yet integrated)
# ---------------------------------------------------------------------------

def mock_pay_stub() -> bool:
    return True


def render_header():
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-eyebrow">掌纹解读系统</div>
        <div class="hero-title">你的掌纹，藏着一条<br>尚未被看清的人生路径</div>
        <div class="gold-divider"></div>
        <div class="hero-subtitle">基于掌纹结构与行为模式分析的解读系统<br>解析你的决策方式、关系模式与财富路径</div>
    </div>
    """, unsafe_allow_html=True)


def render_upload_section():
    # 自定义上传区视觉层
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-palm-icon">🤚</div>
        <div class="upload-main-text">上传你的手掌，开始一次关于自我的阅读</div>
        <div class="upload-sub-text">建议自然光拍摄，手掌放松展开（支持 JPG / PNG）</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "upload",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file.read()
        image = Image.open(io.BytesIO(st.session_state.uploaded_image))
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="已上传", use_column_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("开始解读", use_container_width=True, type="primary"):
                st.session_state.free_report_ready = True
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 结果预期区
    st.markdown("""
    <div class="preview-items">
        <div class="preview-label">你将看到的内容</div>
        <div class="preview-item">
            <div class="preview-dot"></div>
            <div>
                <div class="preview-item-title">思考方式</div>
                <div class="preview-item-desc">你如何做出关键决策，以及这种方式带来的优势与盲区</div>
            </div>
        </div>
        <div class="preview-item">
            <div class="preview-dot"></div>
            <div>
                <div class="preview-item-title">关系模式</div>
                <div class="preview-item-desc">你在亲密关系中的行为倾向，以及最容易反复的结构</div>
            </div>
        </div>
        <div class="preview-item">
            <div class="preview-dot"></div>
            <div>
                <div class="preview-item-title">财富路径</div>
                <div class="preview-item-desc">更适合你的积累方式，以及财富真正起势的阶段</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_free_report():
    if st.button("← 重新上传", key="back_upload"):
        st.session_state.free_report_ready = False
        st.session_state.uploaded_image = None
        st.rerun()

    st.markdown('<div class="page-title" style="font-size:28px;">你的掌纹初读</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle" style="margin-bottom:28px;">以下是表层判断，完整解读包含更深层的结构分析</div>', unsafe_allow_html=True)

    if st.session_state.uploaded_image:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            image = Image.open(io.BytesIO(st.session_state.uploaded_image))
            st.image(image, use_column_width=True)

    st.markdown("""
    <div class="card">
        <div class="card-module-label">思考方式</div>
        <div class="conclusion-text" style="margin-bottom:10px;">分析先行，行动在后</div>
        <div class="interpretation-text">
            你倾向于在做决定前反复权衡，对"错误决定"有较高的厌恶感。这让你在复杂局面中比多数人更稳，但在信息不完整时容易陷入迟疑。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="card-module-label">关系模式</div>
        <div class="conclusion-text" style="margin-bottom:10px;">重情但克制，慢热而认真</div>
        <div class="interpretation-text">
            你在关系中不轻易开口，但一旦投入会非常认真。你对安全感和精神连接的需求高于平均水平，承担的往往比说出口的多。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="card-module-label">财富路径</div>
        <div class="conclusion-text" style="margin-bottom:10px;">长期积累型，不适合短期投机</div>
        <div class="interpretation-text">
            你更擅长通过专业能力和系统性方法积累财富，而不是靠时机爆发。前期感觉慢，但一旦形成方法论，会进入稳定上升通道。
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upsell
    st.markdown("""
    <div class="upsell-card">
        <div class="upsell-hook">但以上，只是你掌纹中最表层的信息。</div>
        <div class="upsell-body" style="margin-bottom:16px;">在你的掌纹结构中，还有两条更关键的线：</div>
        <div style="text-align:left;display:inline-block;margin:0 auto 20px;padding:0 8px;">
            <div style="font-size:14px;color:#9a9aaa;line-height:2.2;">
                它们决定了：<br>
                <span style="color:#c6a86b;">·</span>&nbsp; 你财富真正起势的阶段<br>
                <span style="color:#c6a86b;">·</span>&nbsp; 你在关系中最容易反复的模式
            </div>
        </div>
        <div class="upsell-body">这些信息，只在完整解读中呈现。</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("解锁完整解读（9.9元）", use_container_width=True, type="primary", key="goto_payment"):
            st.session_state.payment_page = True
            st.rerun()


def render_payment_section():
    if st.button("← 返回概览", key="back_free"):
        st.session_state.payment_page = False
        st.rerun()

    st.markdown('<div class="page-title" style="font-size:28px;">解锁完整解读</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle" style="margin-bottom:28px;">一次性解锁，永久查看</div>', unsafe_allow_html=True)

    # 解锁后你将看到
    st.markdown("""
    <div class="preview-items" style="margin-bottom:28px;">
        <div class="preview-label">解锁后你将看到</div>
        <div class="preview-item">
            <div class="preview-dot"></div>
            <div>
                <div class="preview-item-title">决策盲区分析</div>
                <div class="preview-item-desc">你在哪类场景下最容易做出让自己后悔的决定，以及背后的结构性原因</div>
            </div>
        </div>
        <div class="preview-item">
            <div class="preview-dot"></div>
            <div>
                <div class="preview-item-title">关系中的反复模式</div>
                <div class="preview-item-desc">你在亲密关系里最容易陷入的循环，以及如何从结构上打破它</div>
            </div>
        </div>
        <div class="preview-item">
            <div class="preview-dot"></div>
            <div>
                <div class="preview-item-title">财富起势的时间窗口</div>
                <div class="preview-item-desc">你的财富积累在哪个阶段会真正加速，以及现在应该做什么准备</div>
            </div>
        </div>
        <div class="preview-item">
            <div class="preview-dot"></div>
            <div>
                <div class="preview-item-title">可执行的调整建议</div>
                <div class="preview-item-desc">不是泛泛而谈，而是针对你的掌纹结构，给出具体的行为调整方向</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    import os
    qr_path = os.path.join(os.path.dirname(__file__), "qrcode.png")
    qr_path1 = os.path.join(os.path.dirname(__file__), "qrcode1.png")

    st.markdown("""
    <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:12px;color:#4a4a5a;line-height:1.8;">当前为测试体验版本，暂未接入自动支付验证。</div>
        <div style="font-size:13px;color:#5a5a6a;margin-top:6px;">扫码支付后，点击下方按钮查看完整内容</div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("测试解锁完整解读", use_container_width=True, type="primary", key="manual_unlock"):
            st.session_state.paid_unlocked = True
            st.rerun()
        st.markdown('<div style="text-align:center;font-size:11px;color:#3a3a4a;margin-top:8px;">正式上线后，将在支付成功后自动解锁完整报告。</div>', unsafe_allow_html=True)

        st.markdown('<div style="text-align:center;font-size:11px;color:#3a3a4a;margin-top:8px;">正式上线后，将在支付成功后自动解锁完整报告。</div>', unsafe_allow_html=True)


def render_full_report():
    if st.button("← 返回概览", key="back_free2"):
        st.session_state.paid_unlocked = False
        st.session_state.payment_page = False
        st.rerun()

    st.markdown('<div class="page-title" style="font-size:28px;">完整掌纹深度报告</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle" style="margin-bottom:28px;">结构性解读 · 共 5 个模块</div>', unsafe_allow_html=True)

    # 模块一：决策结构与盲区
    st.markdown("""
    <div class="card">
        <div class="card-module-label">模块一 · 决策结构</div>
        <div class="card-title">你如何做决定，以及在哪里会卡住</div>
        <div class="conclusion-row">
            <span class="conclusion-label">结论</span>
            <span class="conclusion-text">分析驱动型，对不确定性有较高的心理成本</span>
        </div>
        <div class="interpretation-text">
            你的智慧线走势显示出一种典型的"内部处理优先"模式：在做出判断之前，你需要先在脑子里把信息跑一遍，确认逻辑自洽，才会行动。这在复杂决策中是优势——你不容易被情绪或外部压力带偏。
        </div>
        <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
            <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">盲区：在这些场景下你最容易卡住</div>
            <div style="font-size:13px;color:#8a8a9a;line-height:2;">
                · 信息不完整时，倾向于等待而不是试探性行动<br>
                · 面对"没有标准答案"的选择（比如换城市、换方向），容易陷入反复权衡<br>
                · 当别人催促你做决定时，会产生明显的抵触感，即使你内心已经有了倾向
            </div>
        </div>
        <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
            <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">可执行的调整方向</div>
            <div style="font-size:13px;color:#8a8a9a;line-height:2;">
                · 给自己设定"决策截止时间"，而不是等到完全清晰<br>
                · 把"试一试"和"最终决定"分开——很多事情可以先小规模验证<br>
                · 当你发现自己在同一个问题上想了超过3天，这通常是情绪问题，不是信息问题
            </div>
        </div>
        <div class="reminder-box">你不是缺乏判断力，而是对"错误"的代价估算得太高。</div>
    </div>
    """, unsafe_allow_html=True)

    # 模块二：关系结构与反复模式
    st.markdown("""
    <div class="card">
        <div class="card-module-label">模块二 · 关系结构</div>
        <div class="card-title">你在亲密关系中最容易反复的模式</div>
        <div class="conclusion-row">
            <span class="conclusion-label">结论</span>
            <span class="conclusion-text">高投入、低表达，容易在关系中"消失"</span>
        </div>
        <div class="interpretation-text">
            你的感情线结构显示：你在关系中的情感投入是真实且深度的，但你表达情感的方式是行动而非语言。你倾向于用"做事"来代替"说话"——帮对方解决问题、默默承担、保持稳定，而不是直接说"我需要你"或"我不舒服"。
        </div>
        <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
            <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">最容易反复的循环</div>
            <div style="font-size:13px;color:#8a8a9a;line-height:2;">
                · 你承担得越多，对方越难感知你的真实需求<br>
                · 积累到一定程度，你会突然"冷掉"——不是不在乎，而是消耗完了<br>
                · 对方感到困惑，你感到委屈，但双方都没说清楚发生了什么<br>
                · 这个循环在你的关系史里可能已经出现过不止一次
            </div>
        </div>
        <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
            <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">如何从结构上打破它</div>
            <div style="font-size:13px;color:#8a8a9a;line-height:2;">
                · 在还没有积累到"冷掉"之前，练习说出一件小事："这件事让我有点累"<br>
                · 找一个能接住你"不完美状态"的人，而不是只在你表现好的时候靠近你<br>
                · 你不需要等到"完全确定"才开口，试探性的表达也是表达
            </div>
        </div>
        <div class="reminder-box">你在关系里的问题，不是不够爱，而是爱得太安静。</div>
    </div>
    """, unsafe_allow_html=True)

    # 模块三：财富结构与时间窗口
    st.markdown("""
    <div class="card">
        <div class="card-module-label">模块三 · 财富结构</div>
        <div class="card-title">你的财富起势在哪个阶段，现在该做什么</div>
        <div class="conclusion-row">
            <span class="conclusion-label">结论</span>
            <span class="conclusion-text">方法论驱动型，财富加速发生在"体系成型"之后</span>
        </div>
        <div class="interpretation-text">
            你的命运线走势暗示一种"慢热型"财富结构：前期积累速度不快，但不是因为能力不足，而是因为你需要更长的时间来建立自己的方法论。一旦这套方法论成型，你的财富积累速度会明显快于同龄人。
        </div>
        <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
            <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">财富节奏的三个阶段</div>
            <div style="font-size:13px;color:#8a8a9a;line-height:2;">
                · <span style="color:#c6a86b;">积累期（当下）</span>：专注于建立可复用的能力或资产，不要因为"慢"而焦虑换方向<br>
                · <span style="color:#c6a86b;">加速期（方法论成型后）</span>：你的优势会开始复利，这个阶段适合加大投入<br>
                · <span style="color:#c6a86b;">收获期</span>：更适合资产型收入，而不是继续靠时间换钱
            </div>
        </div>
        <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
            <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">现在最该做的一件事</div>
            <div style="font-size:13px;color:#8a8a9a;line-height:2;">
                不是找更多机会，而是把你已经在做的事情做深——直到它变成别人无法轻易复制的东西。你的财富风险不来自外部，而来自你自己的焦虑和频繁换方向。
            </div>
        </div>
        <div class="reminder-box">你不是走得慢，你是在等一个真正值得加速的方向。</div>
    </div>
    """, unsafe_allow_html=True)

    # 模块四：命运线深度解读
    st.markdown("""
    <div class="card">
        <div class="card-module-label">模块四 · 命运线</div>
        <div class="card-title">你的人生路径结构</div>
        <div class="conclusion-row">
            <span class="conclusion-label">结论</span>
            <span class="conclusion-text">自主驱动型，不依赖外部机遇，靠内部积累成事</span>
        </div>
        <div class="interpretation-text">
            你的命运线从掌心中部延伸，而不是从手腕底部起始——这在掌纹学中意味着你的人生转折点通常来自内部的觉醒或主动选择，而不是外部的机遇或他人的推动。你不是那种"被时代选中"的人，而是"自己选择时代"的人。
        </div>
        <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
            <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">这意味着什么</div>
            <div style="font-size:13px;color:#8a8a9a;line-height:2;">
                · 你的关键转折点，往往发生在你"想清楚了某件事"之后<br>
                · 等待外部机会对你来说效率很低，主动创造条件才是你的节奏<br>
                · 你适合在一个方向上深耕，而不是广撒网
            </div>
        </div>
        <div class="reminder-box">你的路，是自己走出来的，不是等来的。</div>
    </div>
    """, unsafe_allow_html=True)

    # 模块五：综合建议
    st.markdown("""
    <div class="card">
        <div class="card-module-label">模块五 · 综合建议</div>
        <div class="card-title">给你的三条具体建议</div>
        <div style="margin-bottom:18px;">
            <div style="font-size:13px;font-weight:700;color:#c6a86b;margin-bottom:8px;">01 · 关于决策</div>
            <div style="font-size:14px;color:#8a8a9a;line-height:1.9;">给每个悬而未决的问题设一个"到期日"。不是逼自己，而是承认：有些事情等不到完全清晰，行动本身就是获取信息的方式。</div>
        </div>
        <hr class="section-divider">
        <div style="margin:18px 0;">
            <div style="font-size:13px;font-weight:700;color:#c6a86b;margin-bottom:8px;">02 · 关于关系</div>
            <div style="font-size:14px;color:#8a8a9a;line-height:1.9;">在关系里练习"提前说"。不要等到积累到临界点才开口，而是在还有余量的时候，说一件小事。这不是抱怨，是让对方有机会靠近你。</div>
        </div>
        <hr class="section-divider">
        <div style="margin-top:18px;">
            <div style="font-size:13px;font-weight:700;color:#c6a86b;margin-bottom:8px;">03 · 关于财富</div>
            <div style="font-size:14px;color:#8a8a9a;line-height:1.9;">接下来12个月，不要新增方向，而是把你已经在做的事情做到"别人来找你"的程度。你的财富加速，发生在你成为某个领域里不可替代的那一刻。</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="upsell-card">
        <div class="card-module-label" style="text-align:center;margin-bottom:12px;">延伸解读</div>
        <div class="upsell-hook">想进一步了解你的财富路径？</div>
        <div class="upsell-body">如果你希望进一步分析未来3年的事业节奏、财富机会、投资风格与关键选择，可以升级为《人生决策深度报告》。</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.button("升级深度报告（暂未开放）", use_container_width=True, disabled=True, key="upgrade")


def main():
    inject_css()
    init_session_state()

    if st.session_state.paid_unlocked:
        render_full_report()
    elif st.session_state.payment_page:
        render_payment_section()
    elif st.session_state.free_report_ready:
        render_free_report()
    else:
        render_header()
        render_upload_section()


if __name__ == "__main__":
    main()

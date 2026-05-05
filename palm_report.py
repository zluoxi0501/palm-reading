import streamlit as st
from PIL import Image
import io
import base64
import os
import hashlib
import json
import re
import anthropic

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
        "last_image_hash": None,      # 上一次生成报告时的图片 hash
        "free_report_ready": False,
        "payment_page": False,
        "paid_unlocked": False,
        "free_report_data": None,
        "full_report_data": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_anthropic_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("请设置 ANTHROPIC_API_KEY。如果使用中转站，请同时设置 ANTHROPIC_BASE_URL。")
        st.stop()
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    if base_url:
        return anthropic.Anthropic(api_key=api_key, base_url=base_url)
    return anthropic.Anthropic(api_key=api_key)


def image_to_base64(image_bytes: bytes) -> tuple[str, str]:
    """返回 (base64_data, media_type)"""
    img = Image.open(io.BytesIO(image_bytes))
    fmt = img.format or "JPEG"
    media_map = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
    media_type = media_map.get(fmt, "image/jpeg")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return base64.standard_b64encode(buf.getvalue()).decode(), media_type


def extract_json(text: str) -> dict | None:
    """从模型输出中提取 JSON 对象"""
    # 优先从 ```json 代码块提取
    import re
    block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if block:
        try:
            return json.loads(block.group(1))
        except json.JSONDecodeError:
            pass
    # 直接解析整段文本
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # 截取第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
    return None


def verify_vision(client, b64: str, media_type: str) -> dict:
    """让模型详细描述掌纹特征，作为后续报告生成的输入"""
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": b64},
                    },
                    {
                        "type": "text",
                        "text": """请仔细观察这张图片，回答以下问题：

1. 这张图片是手掌吗？（是/否）
2. 如果是手掌，请逐条描述你看到的掌纹特征：
   - 智慧线（头脑线）：走向、长短、深浅、有无分叉、起点与生命线的关系
   - 感情线（心线）：弧度、末端位置、是否分叉、线条深浅
   - 生命线：弧度大小、是否饱满、有无断裂或岛纹
   - 命运线：是否存在、起始位置、清晰程度
   - 其他明显特征

请用具体、客观的语言描述，不要做性格解读，只描述你看到的线条特征。"""
                    },
                ],
            }
        ],
    )
    description = response.content[0].text.strip()
    vision_keywords = ["图片", "图像", "看到", "显示", "手", "掌", "照片", "画面", "颜色", "物体", "人", "背景", "线", "纹"]
    vision_ok = any(kw in description for kw in vision_keywords)
    is_palm = "是" in description[:20] or "手掌" in description[:50]
    return {"description": description, "vision_ok": vision_ok, "is_palm": is_palm}


def generate_free_report(image_bytes: bytes) -> dict:
    try:
        client = get_anthropic_client()
        b64, media_type = image_to_base64(image_bytes)

        # ── Step 1: 获取详细掌纹观察描述 ──
        vision_check = verify_vision(client, b64, media_type)
        if not vision_check["vision_ok"]:
            return {
                "error": True,
                "vision_failed": True,
                "message": f"图片识别未成功，当前接口可能不支持 Vision 图片输入，请检查模型或中转站。\n\n模型返回：{vision_check['description']}",
                "vision_description": vision_check["description"],
            }
        if not vision_check["is_palm"]:
            return {
                "error": True,
                "not_palm": True,
                "message": "上传的图片不是手掌，无法进行掌纹解读，请重新上传手掌照片。",
                "vision_description": vision_check["description"],
            }

        image_description = vision_check["description"]

        # ── Step 2: 把图片观察结果注入正式报告 prompt ──
        prompt = f"""以下是模型基于用户上传图片看到的掌纹信息：

{image_description}

请必须根据这些具体视觉信息生成报告。
不要使用通用模板。
不要生成与图片无关的固定内容。
如果图片描述中没有足够掌纹细节，请在 interpretation 中明确说明"图片细节不足，以下为有限参考"。

你是一位专业的掌纹解读师。基于上方的掌纹观察，输出以下三个模块的解读。
每个模块的 interpretation 必须直接引用上方描述中的具体线条特征，不允许使用"你倾向于""你通常"等泛泛描述。

输出格式（严格按此 JSON 格式）：
{{
  "thinking_style": {{
    "conclusion": "15字以内的核心结论",
    "interpretation": "必须引用上方掌纹描述中的具体特征，2-3句"
  }},
  "relationship_pattern": {{
    "conclusion": "15字以内的核心结论",
    "interpretation": "必须引用上方掌纹描述中的具体特征，2-3句"
  }},
  "wealth_path": {{
    "conclusion": "15字以内的核心结论",
    "interpretation": "必须引用上方掌纹描述中的具体特征，2-3句"
  }}
}}

只输出 JSON，不要有任何前缀说明、后缀解释或 markdown 代码块。"""

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        text = response.content[0].text
        result = extract_json(text)
        if result:
            result["_vision_description"] = image_description
            result["_based_on_image"] = True
            return result
        return {"raw": text, "_vision_description": image_description, "_based_on_image": True}
    except Exception as e:
        return {"error": True, "message": str(e)}


def generate_full_report(image_bytes: bytes) -> dict:
    try:
        client = get_anthropic_client()
        b64, media_type = image_to_base64(image_bytes)

        # ── Step 1: 获取详细掌纹观察描述 ──
        vision_check = verify_vision(client, b64, media_type)
        if not vision_check["vision_ok"]:
            return {
                "error": True,
                "vision_failed": True,
                "message": f"图片识别未成功，当前接口可能不支持 Vision 图片输入，请检查模型或中转站。\n\n模型返回：{vision_check['description']}",
                "vision_description": vision_check["description"],
            }
        if not vision_check["is_palm"]:
            return {
                "error": True,
                "not_palm": True,
                "message": "上传的图片不是手掌，无法进行掌纹解读，请重新上传手掌照片。",
                "vision_description": vision_check["description"],
            }

        image_description = vision_check["description"]

        # ── Step 2: 把图片观察结果注入正式报告 prompt ──
        prompt = f"""以下是模型基于用户上传图片看到的掌纹信息：

{image_description}

请必须根据这些具体视觉信息生成报告。
不要使用通用模板。
不要生成与图片无关的固定内容。
如果图片描述中没有足够掌纹细节，请在 analysis 中明确说明"图片细节不足，以下为有限参考"。

你是一位专业的掌纹解读师。基于上方的掌纹观察，输出五个模块的深度分析。
每个模块的 analysis 必须直接引用上方描述中的具体线条特征，禁止使用"你倾向于""你通常""你可能"等无法从图片验证的泛泛描述。
blind_spots 和 suggestions 每条用 · 分隔。

输出格式（严格按此 JSON 格式）：
{{
  "decision_structure": {{
    "conclusion": "15字以内",
    "analysis": "3-4句，必须引用上方掌纹描述中的具体特征",
    "blind_spots": "条目1 · 条目2 · 条目3",
    "suggestions": "条目1 · 条目2 · 条目3",
    "reminder": "一句金句"
  }},
  "relationship_structure": {{
    "conclusion": "15字以内",
    "analysis": "3-4句，必须引用上方掌纹描述中的具体特征",
    "blind_spots": "条目1 · 条目2 · 条目3",
    "suggestions": "条目1 · 条目2 · 条目3",
    "reminder": "一句金句"
  }},
  "wealth_structure": {{
    "conclusion": "15字以内",
    "analysis": "3-4句，必须引用上方掌纹描述中的具体特征",
    "blind_spots": "条目1 · 条目2 · 条目3",
    "suggestions": "条目1 · 条目2 · 条目3",
    "reminder": "一句金句"
  }},
  "fate_line": {{
    "conclusion": "15字以内",
    "analysis": "3-4句，必须引用上方掌纹描述中的具体特征",
    "blind_spots": "条目1 · 条目2 · 条目3",
    "suggestions": "条目1 · 条目2 · 条目3",
    "reminder": "一句金句"
  }},
  "overall_advice": {{
    "decision": "针对此人掌纹的具体建议",
    "relationship": "针对此人掌纹的具体建议",
    "wealth": "针对此人掌纹的具体建议"
  }}
}}

只输出 JSON，不要有任何前缀说明、后缀解释或 markdown 代码块。"""

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        text = response.content[0].text
        result = extract_json(text)
        if result:
            result["_vision_description"] = image_description
            result["_based_on_image"] = True
            return result
        return {"raw": text, "_vision_description": image_description, "_based_on_image": True}
    except Exception as e:
        return {"error": True, "message": str(e)}



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
        image_bytes = uploaded_file.getvalue()
        image_hash = hashlib.md5(image_bytes).hexdigest()

        # 新图片：清空所有旧结果
        if image_hash != st.session_state.last_image_hash:
            st.session_state.uploaded_image = image_bytes
            st.session_state.last_image_hash = image_hash
            st.session_state.free_report_data = None
            st.session_state.full_report_data = None
            st.session_state.free_report_ready = False
            st.session_state.paid_unlocked = False

        st.caption(f"当前图片ID：{image_hash[:8]}")

        image = Image.open(io.BytesIO(st.session_state.uploaded_image))
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="已上传", use_column_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("开始解读", use_container_width=True, type="primary"):
                # 每次点击强制清空旧报告，确保重新调用 API
                st.session_state.free_report_data = None
                st.session_state.full_report_data = None
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
        st.session_state.last_image_hash = None
        st.session_state.free_report_data = None
        st.rerun()

    st.markdown('<div class="page-title" style="font-size:28px;">你的掌纹初读</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle" style="margin-bottom:28px;">以下是表层判断，完整解读包含更深层的结构分析</div>', unsafe_allow_html=True)

    if st.session_state.uploaded_image:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            image = Image.open(io.BytesIO(st.session_state.uploaded_image))
            st.image(image, use_column_width=True)

    # ── 调用 AI 生成报告：无缓存时生成（换图已在上传时清空缓存）──
    if st.session_state.free_report_data is None:
        with st.spinner("正在解读你的掌纹，请稍候…"):
            st.session_state.free_report_data = generate_free_report(
                st.session_state.uploaded_image
            )

    data = st.session_state.free_report_data

    # 调试信息
    based = "是" if data.get("_based_on_image") else "否"
    desc = data.get("_vision_description", "待获取")
    st.caption(f"图片ID：{st.session_state.last_image_hash[:8] if st.session_state.last_image_hash else '无'} | 图片描述：{desc[:40]} | 报告是否基于图片描述生成：{based}")

    # Vision 失败或 API 错误
    if data.get("error"):
        if data.get("vision_failed"):
            st.error(data.get("message", "图片识别未成功，当前接口可能不支持 Vision 图片输入，请检查模型或中转站。"))
        else:
            st.error(f"图片分析失败，请检查 API Key / Base URL / 模型是否支持图片。\n\n错误详情：{data.get('message', '')}")
        return

    # 非手掌图片
    if data.get("error") == "not_palm" or (isinstance(data.get("message"), str) and "不是手掌" in data.get("message", "")):
        st.warning("上传的图片不是手掌，无法进行掌纹解读，请重新上传。")
        return

    # 兼容解析失败的情况：尝试从 raw 文本中恢复 JSON
    if "raw" in data:
        recovered = extract_json(data["raw"])
        if recovered and isinstance(recovered, dict) and "thinking_style" in recovered:
            recovered["_vision_description"] = data.get("_vision_description", "")
            recovered["_based_on_image"] = data.get("_based_on_image", False)
            data = recovered
            st.session_state.free_report_data = recovered
        else:
            st.error("报告格式解析失败，请重新生成。")
            if st.button("重新生成", key="retry_free"):
                st.session_state.free_report_data = None
                st.rerun()
            return

    ts = data.get("thinking_style", {})
    rp = data.get("relationship_pattern", {})
    wp = data.get("wealth_path", {})

    st.markdown(f"""
    <div class="card">
        <div class="card-module-label">思考方式</div>
        <div class="conclusion-text" style="margin-bottom:10px;">{ts.get("conclusion", "")}</div>
        <div class="interpretation-text">{ts.get("interpretation", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="card-module-label">关系模式</div>
        <div class="conclusion-text" style="margin-bottom:10px;">{rp.get("conclusion", "")}</div>
        <div class="interpretation-text">{rp.get("interpretation", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="card-module-label">财富路径</div>
        <div class="conclusion-text" style="margin-bottom:10px;">{wp.get("conclusion", "")}</div>
        <div class="interpretation-text">{wp.get("interpretation", "")}</div>
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
            st.session_state.full_report_data = None  # 强制重新生成，不复用旧结果
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

    # ── 调用 AI 生成完整报告：hash 变化或无缓存时重新生成 ──
    if st.session_state.full_report_data is None:
        with st.spinner("正在生成完整深度报告，请稍候…"):
            st.session_state.full_report_data = generate_full_report(
                st.session_state.uploaded_image
            )

    data = st.session_state.full_report_data

    # 调试信息
    based = "是" if data.get("_based_on_image") else "否"
    desc = data.get("_vision_description", "待获取")
    st.caption(f"图片ID：{st.session_state.last_image_hash[:8] if st.session_state.last_image_hash else '无'} | 图片描述：{desc[:40]} | 报告是否基于图片描述生成：{based}")

    if data.get("error"):
        if data.get("vision_failed"):
            st.error(data.get("message", "图片识别未成功，当前接口可能不支持 Vision 图片输入，请检查模型或中转站。"))
        else:
            st.error(f"图片分析失败，请检查 API Key / Base URL / 模型是否支持图片。\n\n错误详情：{data.get('message', '')}")
        return

    if data.get("error") == "not_palm" or (isinstance(data.get("message"), str) and "不是手掌" in data.get("message", "")):
        st.warning("上传的图片不是手掌，无法进行掌纹解读，请重新上传。")
        return

    # 如果 extract_json 失败降级到 raw，尝试再解析一次
    if "raw" in data:
        recovered = extract_json(data["raw"])
        if recovered and isinstance(recovered, dict) and "decision_structure" in recovered:
            recovered["_vision_description"] = data.get("_vision_description", "")
            recovered["_based_on_image"] = data.get("_based_on_image", False)
            data = recovered
            st.session_state.full_report_data = recovered
        else:
            st.error("报告格式解析失败，请重新生成。")
            if st.button("重新生成", key="retry_full"):
                st.session_state.full_report_data = None
                st.rerun()
            return

    def render_module(label, title, d):
        blind_spots_html = "".join(
            f'· {line.strip()}<br>' for line in d.get("blind_spots", "").split("·") if line.strip()
        )
        suggestions_html = "".join(
            f'· {line.strip()}<br>' for line in d.get("suggestions", "").split("·") if line.strip()
        )
        st.markdown(f"""
        <div class="card">
            <div class="card-module-label">{label}</div>
            <div class="card-title">{title}</div>
            <div class="conclusion-row">
                <span class="conclusion-label">结论</span>
                <span class="conclusion-text">{d.get("conclusion", "")}</span>
            </div>
            <div class="interpretation-text">{d.get("analysis", "")}</div>
            <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
                <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">盲区 / 风险</div>
                <div style="font-size:13px;color:#8a8a9a;line-height:2;">{blind_spots_html}</div>
            </div>
            <div style="background:#0d0f13;border-radius:10px;padding:18px 20px;margin:14px 0;">
                <div style="font-size:12px;font-weight:700;color:#c6a86b;letter-spacing:0.1em;margin-bottom:10px;">可执行的调整方向</div>
                <div style="font-size:13px;color:#8a8a9a;line-height:2;">{suggestions_html}</div>
            </div>
            <div class="reminder-box">{d.get("reminder", "")}</div>
        </div>
        """, unsafe_allow_html=True)

    render_module("模块一 · 决策结构", "你如何做决定，以及在哪里会卡住",
                  data.get("decision_structure", {}))
    render_module("模块二 · 关系结构", "你在亲密关系中最容易反复的模式",
                  data.get("relationship_structure", {}))
    render_module("模块三 · 财富结构", "你的财富起势在哪个阶段，现在该做什么",
                  data.get("wealth_structure", {}))
    render_module("模块四 · 命运线", "你的人生路径结构",
                  data.get("fate_line", {}))

    # 模块五：综合建议
    oa = data.get("overall_advice", {})
    st.markdown(f"""
    <div class="card">
        <div class="card-module-label">模块五 · 综合建议</div>
        <div class="card-title">给你的三条具体建议</div>
        <div style="margin-bottom:18px;">
            <div style="font-size:13px;font-weight:700;color:#c6a86b;margin-bottom:8px;">01 · 关于决策</div>
            <div style="font-size:14px;color:#8a8a9a;line-height:1.9;">{oa.get("decision", "")}</div>
        </div>
        <hr class="section-divider">
        <div style="margin:18px 0;">
            <div style="font-size:13px;font-weight:700;color:#c6a86b;margin-bottom:8px;">02 · 关于关系</div>
            <div style="font-size:14px;color:#8a8a9a;line-height:1.9;">{oa.get("relationship", "")}</div>
        </div>
        <hr class="section-divider">
        <div style="margin-top:18px;">
            <div style="font-size:13px;font-weight:700;color:#c6a86b;margin-bottom:8px;">03 · 关于财富</div>
            <div style="font-size:14px;color:#8a8a9a;line-height:1.9;">{oa.get("wealth", "")}</div>
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

"""jjellys — 카테고리별 텍스트(체크리스트) · 사진."""

from __future__ import annotations

import html

import streamlit as st

import db

st.set_page_config(
    page_title="jjellys",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&family=Outfit:wght@600;700&display=swap');

      :root {
        --ink: #1a1a1a;
        --muted: #4a4a4a;
        --bg: #f7f4ef;
        --panel: #ffffff;
        --line: #e2dcd3;
        --accent: #1f6b5c;
      }

      html, body, [class*="css"], .stApp, .stMarkdown, p, label, span {
        font-family: 'Noto Sans KR', sans-serif !important;
        color: var(--ink) !important;
      }

      .stApp {
        background: var(--bg) !important;
      }

      /* Force readable text (fixes light-on-light on mobile) */
      .stApp, .stApp p, .stApp label, .stApp span,
      [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
      [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
      [data-testid="stCaption"], .stCaption {
        color: var(--ink) !important;
      }
      .stCaption, [data-testid="stCaption"] {
        color: var(--muted) !important;
        font-size: 0.95rem !important;
      }

      h1, h2, h3 {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif !important;
        letter-spacing: -0.02em;
        color: var(--ink) !important;
        font-weight: 700 !important;
      }
      h1 { font-size: 2rem !important; }
      h2 { font-size: 1.45rem !important; }
      h3 { font-size: 1.2rem !important; }

      .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 720px;
      }

      /* Sidebar: solid, high contrast, large radios */
      section[data-testid="stSidebar"] {
        background: var(--panel) !important;
        border-right: 1px solid var(--line);
      }
      section[data-testid="stSidebar"] * {
        color: var(--ink) !important;
      }
      section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
      section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        font-size: 1.35rem !important;
      }
      section[data-testid="stSidebar"] div[role="radiogroup"] label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 0.65rem 0.4rem !important;
        margin: 0.15rem 0 !important;
        border-radius: 10px !important;
        line-height: 1.4 !important;
      }
      section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: #e8f5f1 !important;
      }
      section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
      }

      /* Tabs larger for thumb taps */
      button[data-baseweb="tab"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.7rem 1rem !important;
      }

      /* Inputs & buttons: larger touch targets */
      .stTextInput input, .stTextArea textarea {
        font-size: 1.1rem !important;
        min-height: 3rem !important;
        color: var(--ink) !important;
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
      }
      .stButton > button {
        font-size: 1.05rem !important;
        min-height: 2.75rem !important;
        font-weight: 600 !important;
      }
      div[data-testid="stCheckbox"] {
        padding: 0.35rem 0 !important;
        transform: scale(1.15);
        transform-origin: left center;
      }

      /* Text rows */
      .jj-item {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.75rem 0.9rem;
        margin: 0.45rem 0;
      }
      .jj-item-text {
        margin: 0;
        font-size: 1.15rem;
        line-height: 1.45;
        color: var(--ink);
        word-break: break-word;
      }
      .jj-item-text.done {
        text-decoration: line-through;
        color: #777 !important;
      }
      .jj-brand {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: var(--ink);
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.03em;
      }
      .jj-sub {
        color: var(--muted) !important;
        font-size: 1rem;
        margin-bottom: 1rem;
      }

      /* Photo: one column feel on narrow screens */
      @media (max-width: 640px) {
        h1 { font-size: 1.75rem !important; }
        .jj-brand { font-size: 1.85rem; }
        section[data-testid="stSidebar"] div[role="radiogroup"] label,
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
          font-size: 1.25rem !important;
        }
        .block-container {
          padding-left: 0.75rem !important;
          padding-right: 0.75rem !important;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def require_login() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown('<p class="jj-brand">jjellys</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="jj-sub">텍스트와 사진을 카테고리별로 나눠 공유합니다.</p>',
        unsafe_allow_html=True,
    )
    password = st.text_input("비밀번호", type="password", placeholder="가족 공통 비밀번호")
    if st.button("들어가기", type="primary", use_container_width=True):
        expected = st.secrets.get("APP_PASSWORD", "")
        if password and password == expected:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    return False


def ensure_secrets() -> bool:
    needed = ("APP_PASSWORD", "SUPABASE_URL", "SUPABASE_KEY")
    missing = [k for k in needed if k not in st.secrets or not str(st.secrets[k]).strip()]
    if missing:
        st.error(
            "설정이 필요합니다. `.streamlit/secrets.toml`에 "
            + ", ".join(missing)
            + " 를 넣어 주세요. (`secrets.toml.example` 참고)"
        )
        return False
    return True


def render_sidebar_categories(categories: list[dict]) -> dict | None:
    st.sidebar.markdown("## 카테고리")
    with st.sidebar.form("add_category_form", clear_on_submit=True):
        new_name = st.text_input("새 카테고리", placeholder="예: 편의점")
        submitted = st.form_submit_button("추가", use_container_width=True)
        if submitted:
            name = (new_name or "").strip()
            if not name:
                st.sidebar.warning("이름을 입력하세요.")
            elif any(c["name"] == name for c in categories):
                st.sidebar.warning("이미 있는 카테고리입니다.")
            else:
                try:
                    db.add_category(name)
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"추가 실패: {e}")

    if not categories:
        st.sidebar.info("카테고리를 추가하면 여기에 목록이 나타납니다.")
        return None

    names = [c["name"] for c in categories]
    if "selected_category_name" not in st.session_state:
        st.session_state.selected_category_name = names[0]
    if st.session_state.selected_category_name not in names:
        st.session_state.selected_category_name = names[0]

    chosen = st.sidebar.radio(
        "카테고리 선택",
        names,
        index=names.index(st.session_state.selected_category_name),
        label_visibility="collapsed",
    )
    st.session_state.selected_category_name = chosen
    return next(c for c in categories if c["name"] == chosen)


def render_text_section(category_id: int) -> None:
    top = st.columns([0.65, 0.35])
    with top[0]:
        st.subheader("텍스트")
    with top[1]:
        editing = st.session_state.get("text_edit_mode", False)
        label = "편집 완료" if editing else "편집"
        if st.button(label, use_container_width=True, key="toggle_text_edit"):
            st.session_state.text_edit_mode = not editing
            st.rerun()

    editing = st.session_state.get("text_edit_mode", False)

    with st.form("add_text_form", clear_on_submit=True):
        line = st.text_input("한 줄 입력", placeholder="할 일이나 메모를 입력")
        add = st.form_submit_button("추가", type="primary", use_container_width=True)
        if add:
            content = (line or "").strip()
            if content:
                try:
                    db.add_text_item(category_id, content)
                    st.rerun()
                except Exception as e:
                    st.error(f"저장 실패: {e}")
            else:
                st.warning("내용을 입력하세요.")

    try:
        items = db.list_text_items(category_id)
    except Exception as e:
        st.error(f"목록을 불러오지 못했습니다: {e}")
        return

    if not items:
        st.caption("아직 텍스트가 없습니다.")
        return

    for item in items:
        if editing:
            edit_cols = st.columns([0.12, 0.88])
            with edit_cols[0]:
                checked = st.checkbox(
                    "완료",
                    value=bool(item["checked"]),
                    key=f"chk_{item['id']}",
                    label_visibility="collapsed",
                )
                if checked != bool(item["checked"]):
                    db.set_text_checked(item["id"], checked)
                    st.rerun()
            with edit_cols[1]:
                new_content = st.text_input(
                    "내용",
                    value=item["content"],
                    key=f"edit_txt_{item['id']}",
                    label_visibility="collapsed",
                )
                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button("저장", key=f"save_txt_{item['id']}", use_container_width=True):
                        content = (new_content or "").strip()
                        if content:
                            db.update_text_item(item["id"], content)
                            st.rerun()
                        else:
                            st.warning("내용을 비울 수 없습니다.")
                with btn_cols[1]:
                    if st.button("삭제", key=f"del_txt_{item['id']}", use_container_width=True):
                        db.delete_text_item(item["id"])
                        st.rerun()
            st.divider()
        else:
            cols = st.columns([0.14, 0.86])
            with cols[0]:
                checked = st.checkbox(
                    "완료",
                    value=bool(item["checked"]),
                    key=f"chk_{item['id']}",
                    label_visibility="collapsed",
                )
                if checked != bool(item["checked"]):
                    db.set_text_checked(item["id"], checked)
                    st.rerun()
            with cols[1]:
                safe = html.escape(item["content"])
                cls = "jj-item-text done" if item["checked"] else "jj-item-text"
                st.markdown(f'<p class="{cls}">{safe}</p>', unsafe_allow_html=True)


def render_photo_section(category_id: int) -> None:
    st.subheader("사진")
    uploaded = st.file_uploader(
        "사진 올리기",
        type=["jpg", "jpeg", "png", "webp", "gif"],
        accept_multiple_files=True,
    )
    if uploaded:
        if st.button("선택한 사진 업로드", type="primary", use_container_width=True):
            ok = 0
            for f in uploaded:
                try:
                    db.upload_photo(
                        category_id,
                        f.name,
                        f.getvalue(),
                        f.type or "image/jpeg",
                    )
                    ok += 1
                except Exception as e:
                    st.error(f"{f.name} 업로드 실패: {e}")
            if ok:
                st.success(f"{ok}장 올렸습니다.")
                st.rerun()

    try:
        photos = db.list_photos(category_id)
    except Exception as e:
        st.error(f"사진을 불러오지 못했습니다: {e}")
        return

    if not photos:
        st.caption("아직 사진이 없습니다.")
        return

    # Single column on phone-friendly layout
    for photo in photos:
        url = db.photo_public_url(photo["storage_path"])
        st.image(url, use_container_width=True)
        if st.button("사진 삭제", key=f"del_photo_{photo['id']}", use_container_width=True):
            db.delete_photo(photo["id"], photo["storage_path"])
            st.rerun()


def main() -> None:
    if not ensure_secrets():
        st.stop()
    if not require_login():
        st.stop()

    try:
        categories = db.list_categories()
    except Exception as e:
        st.error(
            "Supabase에 연결하지 못했습니다. URL/키와 "
            f"`supabase_schema.sql` 실행 여부를 확인하세요.\n\n{e}"
        )
        st.stop()

    selected = render_sidebar_categories(categories)

    st.markdown('<p class="jj-brand">jjellys</p>', unsafe_allow_html=True)
    if st.sidebar.button("로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    if selected is None:
        st.info("왼쪽(☰)에서 카테고리를 추가해 주세요. 예: 편의점, 장보기, 여행")
        st.stop()

    st.header(selected["name"])

    with st.expander("카테고리 관리", expanded=False):
        st.caption("이 카테고리와 안의 텍스트·사진을 모두 삭제합니다.")
        if st.button("카테고리 삭제", use_container_width=True):
            st.session_state[f"confirm_del_cat_{selected['id']}"] = True

    if st.session_state.get(f"confirm_del_cat_{selected['id']}"):
        st.warning(f"'{selected['name']}'을(를) 정말 삭제할까요?")
        c1, c2 = st.columns(2)
        if c1.button("삭제 확정", type="primary", use_container_width=True):
            db.delete_category(selected["id"])
            st.session_state.pop(f"confirm_del_cat_{selected['id']}", None)
            st.session_state.pop("selected_category_name", None)
            st.rerun()
        if c2.button("취소", use_container_width=True):
            st.session_state.pop(f"confirm_del_cat_{selected['id']}", None)
            st.rerun()

    tab_text, tab_photo = st.tabs(["텍스트", "사진"])
    with tab_text:
        render_text_section(selected["id"])
    with tab_photo:
        render_photo_section(selected["id"])


if __name__ == "__main__":
    main()

"""jjellys — 가족 구매 리스트 (물품 = 이름 필수 + 사진 옵션)."""

from __future__ import annotations

import streamlit as st

import db

st.set_page_config(
    page_title="jjellys",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&family=Outfit:wght@600;700&display=swap');

      :root {
        --ink: #1a1a1a;
        --muted: #555;
        --bg: #f7f4ef;
        --panel: #ffffff;
        --accent: #1f6b5c;
      }

      .stApp {
        background: var(--bg) !important;
        font-family: 'Noto Sans KR', sans-serif;
        color: var(--ink);
      }

      [data-testid="stMarkdownContainer"] p,
      [data-testid="stWidgetLabel"] p,
      .stMarkdown p,
      label p {
        font-family: 'Noto Sans KR', sans-serif;
        color: var(--ink);
      }

      h1, h2, h3, .jj-brand {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -0.02em;
        font-weight: 700 !important;
      }

      .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 4rem !important;
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        max-width: 720px;
      }

      .jj-brand { font-size: 1.9rem; margin: 0; }
      .jj-sub {
        color: var(--muted);
        font-size: 0.98rem;
        margin: 0.15rem 0 0.9rem 0;
      }

      div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        padding: 0.75rem 1rem !important;
        color: var(--ink) !important;
      }
      div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.15rem;
        overflow-x: auto;
        flex-wrap: nowrap !important;
      }

      .stTextInput input {
        font-size: 1.08rem !important;
        min-height: 2.85rem !important;
        color: var(--ink) !important;
        background: var(--panel) !important;
      }
      .stButton > button {
        font-size: 1.02rem !important;
        min-height: 2.6rem !important;
        font-weight: 600 !important;
      }

      div[data-testid="stCheckbox"] { padding: 0.35rem 0 !important; }
      div[data-testid="stCheckbox"] label {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 0.65rem !important;
        width: 100%;
      }
      div[data-testid="stCheckbox"] label p {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        line-height: 1.35 !important;
        margin: 0 !important;
        word-break: break-word;
      }
      div[data-testid="stCheckbox"]:has(input:checked) label p {
        text-decoration: line-through;
        color: #888 !important;
      }
      div[data-testid="stCheckbox"] input[type="checkbox"] {
        width: 1.25rem !important;
        height: 1.25rem !important;
        accent-color: var(--accent);
        flex-shrink: 0;
      }

      div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: center !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.dialog("물품 사진")
def show_photo_dialog(url: str, title: str) -> None:
    st.caption(title)
    st.image(url, use_container_width=True)


def require_login() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown('<p class="jj-brand">jjellys</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="jj-sub">가족 구매 리스트 — 편의점·마트 장을 함께 적어요.</p>',
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
        st.error("설정이 필요합니다. `.streamlit/secrets.toml`을 확인해 주세요.")
        return False
    return True


def render_add_category(categories: list[dict]) -> None:
    with st.form("add_category_form", clear_on_submit=True):
        cols = st.columns([0.72, 0.28], vertical_alignment="bottom")
        with cols[0]:
            new_name = st.text_input(
                "장소 추가",
                placeholder="예: 편의점, 마트, 다이소",
                label_visibility="collapsed",
            )
        with cols[1]:
            submitted = st.form_submit_button("추가", use_container_width=True)
        if submitted:
            name = (new_name or "").strip()
            if not name:
                st.warning("이름을 입력하세요.")
            elif any(c["name"] == name for c in categories):
                st.warning("이미 있는 장소입니다.")
            else:
                try:
                    db.add_category(name)
                    st.rerun()
                except Exception as e:
                    st.error(f"추가 실패: {e}")


def render_items(category_id: int) -> None:
    edit_key = f"edit_mode_{category_id}"
    top = st.columns([0.62, 0.38], vertical_alignment="center")
    with top[0]:
        st.markdown("##### 물품")
    with top[1]:
        editing = st.session_state.get(edit_key, False)
        label = "편집 완료" if editing else "편집"
        if st.button(label, use_container_width=True, key=f"toggle_edit_{category_id}"):
            st.session_state[edit_key] = not editing
            st.rerun()

    editing = st.session_state.get(edit_key, False)

    name = st.text_input(
        "물품 이름",
        placeholder="살 물건 이름 (필수)",
        key=f"new_item_name_{category_id}",
    )
    photo_nonce = st.session_state.setdefault(f"photo_nonce_{category_id}", 0)
    photo = st.file_uploader(
        "사진 (선택)",
        type=["jpg", "jpeg", "png", "webp", "gif"],
        key=f"new_item_photo_{category_id}_{photo_nonce}",
    )
    if st.button("물품 추가", type="primary", use_container_width=True, key=f"add_btn_{category_id}"):
        content = (name or "").strip()
        if not content:
            st.warning("물품 이름은 필수입니다.")
        else:
            try:
                if photo is not None:
                    db.add_item(
                        category_id,
                        content,
                        photo.name,
                        photo.getvalue(),
                        photo.type or "image/jpeg",
                    )
                else:
                    db.add_item(category_id, content)
                st.session_state[f"new_item_name_{category_id}"] = ""
                st.session_state[f"photo_nonce_{category_id}"] = photo_nonce + 1
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}")

    try:
        items = db.list_items(category_id)
    except Exception as e:
        st.error(
            f"목록을 불러오지 못했습니다. Supabase에서 "
            f"`alter table text_items add column if not exists storage_path text;` "
            f"를 실행했는지 확인하세요.\n\n{e}"
        )
        return

    if not items:
        st.caption("아직 물품이 없습니다.")
        return

    for item in items:
        path = item.get("storage_path")
        if editing:
            new_content = st.text_input(
                "물품 이름",
                value=item["content"],
                key=f"edit_name_{item['id']}",
            )
            if path:
                st.caption("현재 사진이 있습니다.")
                st.image(db.photo_public_url(path), width=160)
                remove_photo = st.checkbox(
                    "사진 삭제",
                    key=f"rm_photo_{item['id']}",
                )
            else:
                remove_photo = False
                st.caption("사진 없음")

            new_photo = st.file_uploader(
                "사진 변경/추가",
                type=["jpg", "jpeg", "png", "webp", "gif"],
                key=f"edit_photo_{item['id']}",
            )
            btn_cols = st.columns(2)
            with btn_cols[0]:
                if st.button("저장", key=f"save_{item['id']}", use_container_width=True):
                    content = (new_content or "").strip()
                    if not content:
                        st.warning("물품 이름은 필수입니다.")
                    else:
                        try:
                            db.update_item(
                                item["id"],
                                content,
                                new_photo_name=new_photo.name if new_photo else None,
                                new_photo_data=new_photo.getvalue() if new_photo else None,
                                new_photo_type=(new_photo.type if new_photo else None),
                                remove_photo=bool(remove_photo) and new_photo is None,
                                category_id=category_id,
                                old_storage_path=path,
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"저장 실패: {e}")
            with btn_cols[1]:
                if st.button("삭제", key=f"del_{item['id']}", use_container_width=True):
                    db.delete_item(item["id"], path)
                    st.rerun()
            st.divider()
        else:
            row = st.columns([0.82, 0.18], vertical_alignment="center")
            with row[0]:
                checked = st.checkbox(
                    item["content"],
                    value=bool(item["checked"]),
                    key=f"chk_{item['id']}",
                )
                if checked != bool(item["checked"]):
                    db.set_item_checked(item["id"], checked)
                    st.rerun()
            with row[1]:
                if path:
                    if st.button("사진", key=f"view_{item['id']}", use_container_width=True):
                        show_photo_dialog(db.photo_public_url(path), item["content"])
                else:
                    st.caption("—")


def render_category_panel(category: dict) -> None:
    cid = category["id"]
    with st.expander("이 장소 삭제", expanded=False):
        st.caption(f"'{category['name']}' 물품을 모두 지웁니다.")
        if st.button("장소 삭제", use_container_width=True, key=f"del_cat_btn_{cid}"):
            st.session_state[f"confirm_del_cat_{cid}"] = True

    if st.session_state.get(f"confirm_del_cat_{cid}"):
        st.warning(f"'{category['name']}'을(를) 정말 삭제할까요?")
        c1, c2 = st.columns(2)
        if c1.button("삭제 확정", type="primary", use_container_width=True, key=f"del_ok_{cid}"):
            db.delete_category(cid)
            st.session_state.pop(f"confirm_del_cat_{cid}", None)
            st.rerun()
        if c2.button("취소", use_container_width=True, key=f"del_cancel_{cid}"):
            st.session_state.pop(f"confirm_del_cat_{cid}", None)
            st.rerun()

    render_items(cid)


def main() -> None:
    if not ensure_secrets():
        st.stop()
    if not require_login():
        st.stop()

    try:
        categories = db.list_categories()
    except Exception as e:
        st.error(f"Supabase 연결 실패:\n\n{e}")
        st.stop()

    head = st.columns([0.78, 0.22], vertical_alignment="center")
    with head[0]:
        st.markdown('<p class="jj-brand">jjellys</p>', unsafe_allow_html=True)
        st.markdown('<p class="jj-sub">가족 구매 리스트</p>', unsafe_allow_html=True)
    with head[1]:
        if st.button("나가기", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    render_add_category(categories)

    if not categories:
        st.info("위에서 장소를 추가하세요. 예: 편의점 | 마트 | 다이소")
        st.stop()

    cat_tabs = st.tabs([c["name"] for c in categories])
    for tab, category in zip(cat_tabs, categories):
        with tab:
            render_category_panel(category)


if __name__ == "__main__":
    main()

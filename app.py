"""jjellys — 가족 구매 리스트 (모바일 중심)."""

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
        --muted: #5a5a5a;
        --bg: #f7f4ef;
        --panel: #ffffff;
        --line: #e5dfd6;
        --accent: #1f6b5c;
      }

      /* Hide Streamlit chrome on phone */
      #MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }
      [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
      .stDeployButton { display: none !important; }

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

      .block-container {
        padding: 0.6rem 0.75rem 3.5rem 0.75rem !important;
        max-width: 480px;
      }

      .jj-brand {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif !important;
        font-size: 1.65rem;
        font-weight: 700;
        color: var(--ink);
        margin: 0;
        letter-spacing: -0.03em;
      }
      .jj-sub {
        color: var(--muted);
        font-size: 0.9rem;
        margin: 0.1rem 0 0.6rem 0;
      }

      /* iOS: >=16px prevents auto-zoom on focus */
      .stTextInput input,
      .stTextArea textarea {
        font-size: 16px !important;
        min-height: 2.75rem !important;
        color: var(--ink) !important;
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
      }

      .stButton > button {
        font-size: 0.95rem !important;
        min-height: 2.55rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        white-space: nowrap !important;
      }

      /* Pills / category chips */
      div[data-testid="stPills"] button,
      [data-testid="stBaseButton-pills"],
      [data-testid="stBaseButton-pillsActive"] {
        font-size: 1rem !important;
        font-weight: 700 !important;
        min-height: 2.4rem !important;
        padding: 0.35rem 0.85rem !important;
      }

      div[data-testid="stCheckbox"] { padding: 0.35rem 0 !important; }
      div[data-testid="stCheckbox"] label {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 0.55rem !important;
        width: 100%;
        max-width: 100%;
      }
      div[data-testid="stCheckbox"] label p {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        line-height: 1.35 !important;
        margin: 0 !important;
        word-break: break-word;
        overflow-wrap: anywhere;
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
        gap: 0.3rem !important;
        width: 100% !important;
        max-width: 100% !important;
      }
      div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: 0 !important;
      }
      div[data-testid="column"] .stButton,
      div[data-testid="column"] .stButton > button {
        width: 100% !important;
      }

      /* Tighter file uploader on mobile */
      [data-testid="stFileUploader"] section {
        padding: 0.6rem !important;
      }
      [data-testid="stFileUploader"] small,
      [data-testid="stFileUploader"] span {
        font-size: 0.85rem !important;
      }

      div[data-testid="stExpander"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
      }

      .jj-row {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.15rem 0.55rem;
        margin: 0.35rem 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.dialog("사진")
def show_photo_dialog(url: str, title: str) -> None:
    st.caption(title)
    st.image(url, use_container_width=True)


def require_login() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown('<p class="jj-brand">jjellys</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="jj-sub">가족 구매 리스트</p>',
        unsafe_allow_html=True,
    )
    password = st.text_input(
        "비밀번호",
        type="password",
        placeholder="비밀번호",
        label_visibility="collapsed",
    )
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


def sort_shopping_items(items: list[dict]) -> list[dict]:
    # Unchecked first (still need to buy), then checked
    return sorted(items, key=lambda i: (bool(i.get("checked")), i.get("created_at") or ""))


def render_items(category_id: int) -> None:
    edit_key = f"edit_mode_{category_id}"
    editing = st.session_state.get(edit_key, False)
    label = "편집 완료" if editing else "편집"
    if st.button(label, use_container_width=True, key=f"toggle_edit_{category_id}"):
        st.session_state[edit_key] = not editing
        st.rerun()

    editing = st.session_state.get(edit_key, False)

    # Add form only when not editing (less scroll on phone)
    if not editing:
        name = st.text_input(
            "물품",
            placeholder="살 물건 이름",
            key=f"new_item_name_{category_id}",
            label_visibility="collapsed",
        )
        photo_nonce = st.session_state.setdefault(f"photo_nonce_{category_id}", 0)
        photo = st.file_uploader(
            "사진",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            key=f"new_item_photo_{category_id}_{photo_nonce}",
            label_visibility="collapsed",
        )
        if st.button("추가", type="primary", use_container_width=True, key=f"add_btn_{category_id}"):
            content = (name or "").strip()
            if not content:
                st.warning("물품 이름을 입력하세요.")
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
        items = sort_shopping_items(db.list_items(category_id))
    except Exception as e:
        st.error(
            "목록을 불러오지 못했습니다. Supabase에서 "
            "`alter table text_items add column if not exists storage_path text;` "
            f"실행 여부를 확인하세요.\n\n{e}"
        )
        return

    if not items:
        st.caption("목록이 비어 있습니다.")
        return

    for item in items:
        path = item.get("storage_path")
        if editing:
            new_content = st.text_input(
                "이름",
                value=item["content"],
                key=f"edit_name_{item['id']}",
                label_visibility="collapsed",
            )
            if path:
                st.image(db.photo_public_url(path), use_container_width=True)
                remove_photo = st.checkbox("사진 삭제", key=f"rm_photo_{item['id']}")
            else:
                remove_photo = False

            new_photo = st.file_uploader(
                "사진",
                type=["jpg", "jpeg", "png", "webp", "gif"],
                key=f"edit_photo_{item['id']}",
                label_visibility="collapsed",
            )
            btn_cols = st.columns(2, gap="small")
            with btn_cols[0]:
                if st.button("저장", key=f"save_{item['id']}", use_container_width=True, type="primary"):
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
            if path:
                row = st.columns([0.82, 0.18], gap="small", vertical_alignment="center")
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
                    if st.button("📷", key=f"view_{item['id']}", use_container_width=True):
                        show_photo_dialog(db.photo_public_url(path), item["content"])
            else:
                checked = st.checkbox(
                    item["content"],
                    value=bool(item["checked"]),
                    key=f"chk_{item['id']}",
                )
                if checked != bool(item["checked"]):
                    db.set_item_checked(item["id"], checked)
                    st.rerun()


def render_category_tools(category: dict) -> None:
    cid = category["id"]
    with st.expander("장소 삭제", expanded=False):
        st.caption(f"'{category['name']}' 목록을 모두 지웁니다.")
        if st.button("이 장소 삭제", use_container_width=True, key=f"del_cat_btn_{cid}"):
            st.session_state[f"confirm_del_cat_{cid}"] = True

        if st.session_state.get(f"confirm_del_cat_{cid}"):
            st.warning("정말 삭제할까요?")
            c1, c2 = st.columns(2, gap="small")
            if c1.button("삭제", type="primary", use_container_width=True, key=f"del_ok_{cid}"):
                db.delete_category(cid)
                st.session_state.pop(f"confirm_del_cat_{cid}", None)
                st.session_state.pop("selected_category", None)
                st.rerun()
            if c2.button("취소", use_container_width=True, key=f"del_cancel_{cid}"):
                st.session_state.pop(f"confirm_del_cat_{cid}", None)
                st.rerun()


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

    st.markdown('<p class="jj-brand">jjellys</p>', unsafe_allow_html=True)
    st.markdown('<p class="jj-sub">가족 구매 리스트</p>', unsafe_allow_html=True)

    # Secondary actions tucked away (more list space)
    with st.expander("장소 추가 · 설정", expanded=False):
        with st.form("add_category_form", clear_on_submit=True):
            new_name = st.text_input(
                "장소",
                placeholder="예: 편의점, 마트",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("장소 추가", use_container_width=True)
            if submitted:
                name = (new_name or "").strip()
                if not name:
                    st.warning("이름을 입력하세요.")
                elif any(c["name"] == name for c in categories):
                    st.warning("이미 있는 장소입니다.")
                else:
                    try:
                        added = db.add_category(name)
                        if added:
                            st.session_state.selected_category = added["name"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"추가 실패: {e}")
        if st.button("나가기", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    if not categories:
        st.info("위에서 장소를 추가하세요. 예: 편의점, 마트")
        st.stop()

    names = [c["name"] for c in categories]
    if st.session_state.get("selected_category") not in names:
        st.session_state.selected_category = names[0]

    # Only one category rendered → much faster / lighter on phone than st.tabs
    chosen = st.pills(
        "장소",
        names,
        selection_mode="single",
        default=st.session_state.selected_category,
        label_visibility="collapsed",
        key="category_pills",
    )
    if chosen:
        st.session_state.selected_category = chosen
    else:
        chosen = st.session_state.selected_category

    category = next(c for c in categories if c["name"] == chosen)
    render_items(category["id"])
    render_category_tools(category)


if __name__ == "__main__":
    main()

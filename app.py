"""가족 공유 웹앱 — 카테고리별 텍스트(체크리스트) · 사진."""

from __future__ import annotations

import html

import streamlit as st

import db

st.set_page_config(
    page_title="가족 공유",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Warm, simple family look — not purple/dashboard default
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&family=Outfit:wght@600;700&display=swap');

      html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
      }
      .stApp {
        background:
          radial-gradient(ellipse 120% 80% at 10% -10%, #ffe8d6 0%, transparent 55%),
          radial-gradient(ellipse 90% 60% at 100% 0%, #d8f0ea 0%, transparent 50%),
          linear-gradient(180deg, #faf7f2 0%, #f3efe8 100%);
      }
      h1, h2, h3 {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif !important;
        letter-spacing: -0.02em;
      }
      section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff9f3 0%, #f5ebe0 100%);
      }
      .block-container { padding-top: 1.5rem; max-width: 720px; }
      div[data-testid="stCheckbox"] { padding: 0.15rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


def require_login() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.title("가족 공유")
    st.caption("텍스트와 사진을 카테고리별로 나눠 공유합니다.")
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
    st.sidebar.title("카테고리")
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
        "선택",
        names,
        index=names.index(st.session_state.selected_category_name),
        label_visibility="collapsed",
    )
    st.session_state.selected_category_name = chosen
    return next(c for c in categories if c["name"] == chosen)


def render_text_section(category_id: int) -> None:
    st.subheader("텍스트")
    with st.form("add_text_form", clear_on_submit=True):
        line = st.text_input("한 줄 입력", placeholder="할 일이나 메모를 적고 Enter")
        add = st.form_submit_button("추가", type="primary")
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
        cols = st.columns([0.12, 0.73, 0.15])
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
            style = "text-decoration: line-through; opacity: 0.55;" if item["checked"] else ""
            safe = html.escape(item["content"])
            st.markdown(
                f'<p style="margin:0.35rem 0;{style}">{safe}</p>',
                unsafe_allow_html=True,
            )
        with cols[2]:
            if st.button("삭제", key=f"del_txt_{item['id']}", use_container_width=True):
                db.delete_text_item(item["id"])
                st.rerun()


def render_photo_section(category_id: int) -> None:
    st.subheader("사진")
    uploaded = st.file_uploader(
        "사진 올리기",
        type=["jpg", "jpeg", "png", "webp", "gif"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded:
        if st.button("선택한 사진 업로드", type="primary"):
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

    for i in range(0, len(photos), 2):
        row = photos[i : i + 2]
        cols = st.columns(2)
        for col, photo in zip(cols, row):
            with col:
                url = db.photo_public_url(photo["storage_path"])
                st.image(url, use_container_width=True)
                if st.button("삭제", key=f"del_photo_{photo['id']}", use_container_width=True):
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

    st.title("가족 공유")
    if st.sidebar.button("로그아웃"):
        st.session_state.authenticated = False
        st.rerun()

    if selected is None:
        st.info("왼쪽에서 카테고리를 추가해 주세요. 예: 편의점, 장보기, 여행")
        st.stop()

    header_cols = st.columns([0.75, 0.25])
    with header_cols[0]:
        st.header(selected["name"])
    with header_cols[1]:
        if st.button("카테고리 삭제", use_container_width=True):
            st.session_state[f"confirm_del_cat_{selected['id']}"] = True

    if st.session_state.get(f"confirm_del_cat_{selected['id']}"):
        st.warning(f"'{selected['name']}' 카테고리와 안의 텍스트·사진을 모두 삭제할까요?")
        c1, c2 = st.columns(2)
        if c1.button("삭제 확정", type="primary"):
            db.delete_category(selected["id"])
            st.session_state.pop(f"confirm_del_cat_{selected['id']}", None)
            st.session_state.pop("selected_category_name", None)
            st.rerun()
        if c2.button("취소"):
            st.session_state.pop(f"confirm_del_cat_{selected['id']}", None)
            st.rerun()

    tab_text, tab_photo = st.tabs(["텍스트", "사진"])
    with tab_text:
        render_text_section(selected["id"])
    with tab_photo:
        render_photo_section(selected["id"])


if __name__ == "__main__":
    main()

"""jjellys — 가족 구매 리스트 (모바일 중심)."""

from __future__ import annotations

import hashlib
import hmac
import html as html_lib
import time

import streamlit as st
import streamlit.components.v1 as components

import db

st.set_page_config(
    page_title="jjellys",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

AUTH_COOKIE = "jj_auth"
AUTH_DAYS = 30
EXPENSE_TAB = "지출"
EXPENSE_CATEGORIES = ["식당", "카페", "편의점", "쇼핑1", "쇼핑2"]

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
        overflow-x: hidden !important;
      }

      /* Prevent any wide content from sideways scroll on phone */
      .stApp, .main, [data-testid="stAppViewContainer"] {
        overflow-x: hidden !important;
      }

      .jj-calc-item {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.65rem 0.75rem;
        margin: 0.4rem 0;
        word-break: break-word;
        overflow-wrap: anywhere;
      }
      .jj-calc-item .cat {
        font-size: 0.85rem;
        color: var(--muted);
        margin: 0 0 0.15rem 0;
      }
      .jj-calc-item .name {
        font-size: 1.05rem;
        font-weight: 600;
        margin: 0;
        color: var(--ink);
      }
      .jj-calc-item .amt {
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0.2rem 0 0 0;
        color: var(--ink);
      }
      .jj-calc-item.muted .name,
      .jj-calc-item.muted .amt {
        opacity: 0.45;
      }
      .jj-total {
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0.4rem 0 0.8rem 0;
        word-break: break-word;
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

      /* Pills: one horizontal row (place + calc filters) */
      div[data-testid="stPills"] button,
      [data-testid="stBaseButton-pills"],
      [data-testid="stBaseButton-pillsActive"] {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        min-height: 2.1rem !important;
        padding: 0.25rem 0.6rem !important;
        flex-shrink: 0 !important;
      }
      div[data-testid="stPills"] > div,
      div[data-testid="stPills"] [role="group"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 0.25rem !important;
        max-width: 100% !important;
      }

      /* Calculator category chips: keep on one horizontal row */
      .jj-calc-filters {
        max-width: 100%;
        overflow-x: auto;
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
      /* Settings / 계산기 모드 체크에는 취소선 적용 안 함 */
      div[data-testid="stExpander"] div[data-testid="stCheckbox"]:has(input:checked) label p {
        text-decoration: none !important;
        color: var(--ink) !important;
      }
      div[data-testid="stCheckbox"] input[type="checkbox"] {
        width: 1.25rem !important;
        height: 1.25rem !important;
        accent-color: var(--accent);
        flex-shrink: 0;
      }

      /* Calculator category chips: keep on one horizontal row — handled by global pills CSS */

      /* Never force side-by-side — prevents buttons escaping off-screen */
      div[data-testid="stHorizontalBlock"] {
        width: 100% !important;
        max-width: 100% !important;
      }
      div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: 0 !important;
        width: 100% !important;
      }

      /* Compact secondary buttons (photo) */
      .stButton > button[kind="secondary"] {
        min-height: 2.2rem !important;
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


def _auth_secret() -> str:
    return str(st.secrets.get("APP_PASSWORD", "jjellys"))


def make_auth_token(days: int = AUTH_DAYS) -> str:
    """Signed login token that survives Streamlit session reconnects."""
    exp = int(time.time()) + days * 24 * 3600
    payload = f"jjellys:{exp}"
    sig = hmac.new(_auth_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:40]
    return f"{exp}.{sig}"


def verify_auth_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    try:
        exp_s, sig = token.split(".", 1)
        exp = int(exp_s)
        if time.time() > exp:
            return False
        payload = f"jjellys:{exp}"
        expect = hmac.new(
            _auth_secret().encode(), payload.encode(), hashlib.sha256
        ).hexdigest()[:40]
        return hmac.compare_digest(sig, expect)
    except Exception:
        return False


def _token_from_query() -> str | None:
    value = st.query_params.get("auth")
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _token_from_cookie() -> str | None:
    try:
        return st.context.cookies.get(AUTH_COOKIE)
    except Exception:
        return None


def persist_login(token: str) -> None:
    st.query_params["auth"] = token
    # Set on parent page (iframe document.cookie would not stick)
    max_age = AUTH_DAYS * 24 * 3600
    components.html(
        f"""
        <script>
        try {{
          window.parent.document.cookie =
            "{AUTH_COOKIE}={token}; max-age={max_age}; path=/; SameSite=Lax";
        }} catch (e) {{}}
        </script>
        """,
        height=0,
        width=0,
    )


def clear_login() -> None:
    try:
        if "auth" in st.query_params:
            del st.query_params["auth"]
    except Exception:
        pass
    components.html(
        f"""
        <script>
        try {{
          window.parent.document.cookie =
            "{AUTH_COOKIE}=; max-age=0; path=/; SameSite=Lax";
        }} catch (e) {{}}
        </script>
        """,
        height=0,
        width=0,
    )


def restore_login() -> bool:
    """Restore auth after phone background / websocket reconnect."""
    if st.session_state.get("authenticated"):
        # Keep URL token fresh so reconnects stay logged in
        if not _token_from_query() and st.session_state.get("auth_token"):
            st.query_params["auth"] = st.session_state.auth_token
        return True

    token = _token_from_query() or _token_from_cookie()
    if verify_auth_token(token):
        st.session_state.authenticated = True
        st.session_state.auth_token = token
        if _token_from_query() != token:
            st.query_params["auth"] = token
        return True
    return False


def require_login() -> bool:
    if restore_login():
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
            token = make_auth_token()
            st.session_state.authenticated = True
            st.session_state.auth_token = token
            persist_login(token)
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
    reset_key = f"reset_add_{category_id}"

    # Clear add inputs BEFORE widgets are created (avoids Streamlit session_state error)
    if st.session_state.pop(reset_key, False):
        name_nonce = st.session_state.get(f"name_nonce_{category_id}", 0) + 1
        photo_nonce = st.session_state.get(f"photo_nonce_{category_id}", 0) + 1
        st.session_state[f"name_nonce_{category_id}"] = name_nonce
        st.session_state[f"photo_nonce_{category_id}"] = photo_nonce

    editing = st.session_state.get(edit_key, False)
    label = "편집 완료" if editing else "편집"
    if st.button(label, use_container_width=True, key=f"toggle_edit_{category_id}"):
        st.session_state[edit_key] = not editing
        st.rerun()

    editing = st.session_state.get(edit_key, False)

    # Add form only when not editing (less scroll on phone)
    if not editing:
        name_nonce = st.session_state.setdefault(f"name_nonce_{category_id}", 0)
        photo_nonce = st.session_state.setdefault(f"photo_nonce_{category_id}", 0)
        name = st.text_input(
            "물품",
            placeholder="살 물건 이름",
            key=f"new_item_name_{category_id}_{name_nonce}",
            label_visibility="collapsed",
        )
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
                    st.session_state[reset_key] = True
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
            if st.button("삭제", key=f"del_{item['id']}", use_container_width=True):
                db.delete_item(item["id"], path)
                st.rerun()
            st.divider()
        else:
            checked = st.checkbox(
                item["content"],
                value=bool(item["checked"]),
                key=f"chk_{item['id']}",
            )
            if checked != bool(item["checked"]):
                db.set_item_checked(item["id"], checked)
                st.rerun()
            if path:
                if st.button("📷 사진 보기", key=f"view_{item['id']}", use_container_width=True):
                    show_photo_dialog(db.photo_public_url(path), item["content"])


def parse_amount(raw: str) -> int | None:
    """'1200', '1,200', '1200엔' → int. Invalid → None."""
    if raw is None:
        return None
    cleaned = (
        str(raw)
        .strip()
        .replace(",", "")
        .replace("엔", "")
        .replace("円", "")
        .replace("원", "")
        .replace("¥", "")
        .replace(" ", "")
    )
    if not cleaned:
        return None
    try:
        value = int(float(cleaned))
    except ValueError:
        return None
    if value < 0:
        return None
    return value


def format_yen(amount: int | float) -> str:
    return f"{int(amount):,}엔"


def render_calculator() -> None:
    st.caption("합산에 포함할 카테고리 (탭해서 켜고 끄기)")
    st.markdown('<div class="jj-calc-filters">', unsafe_allow_html=True)
    selected = st.pills(
        "합산 카테고리",
        EXPENSE_CATEGORIES,
        selection_mode="multi",
        default=EXPENSE_CATEGORIES,
        label_visibility="collapsed",
        key="calc_sum_pills",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    active = list(selected) if selected else []

    try:
        expenses = db.list_expenses()
    except Exception as e:
        st.error(
            "지출 목록을 불러오지 못했습니다. Supabase SQL Editor에서 "
            "`expenses` 테이블 생성 SQL을 실행했는지 확인하세요.\n\n"
            f"{e}"
        )
        return

    included = [e for e in expenses if e.get("category") in active]
    total = sum(int(e.get("amount") or 0) for e in included)
    st.markdown(
        f'<p class="jj-total">합계 {format_yen(total)}</p>',
        unsafe_allow_html=True,
    )
    if not active:
        st.caption("카테고리를 하나 이상 선택하세요.")

    edit_key = "calc_edit_mode"
    editing = st.session_state.get(edit_key, False)
    label = "편집 완료" if editing else "편집"
    if st.button(label, use_container_width=True, key="calc_toggle_edit"):
        st.session_state[edit_key] = not editing
        st.rerun()
    editing = st.session_state.get(edit_key, False)

    reset_key = "calc_reset_add"
    if st.session_state.pop(reset_key, False):
        st.session_state["calc_name_nonce"] = st.session_state.get("calc_name_nonce", 0) + 1
        st.session_state["calc_price_nonce"] = st.session_state.get("calc_price_nonce", 0) + 1

    if not editing:
        name_nonce = st.session_state.setdefault("calc_name_nonce", 0)
        price_nonce = st.session_state.setdefault("calc_price_nonce", 0)
        title = st.text_input(
            "물건 이름",
            placeholder="물건 이름",
            key=f"calc_title_{name_nonce}",
            label_visibility="collapsed",
        )
        price_raw = st.text_input(
            "가격",
            placeholder="가격 (예: 4500)",
            key=f"calc_price_{price_nonce}",
            label_visibility="collapsed",
        )
        category = st.selectbox(
            "카테고리",
            EXPENSE_CATEGORIES,
            key="calc_category_select",
        )
        if st.button("추가", type="primary", use_container_width=True, key="calc_add_btn"):
            name = (title or "").strip()
            amount = parse_amount(price_raw or "")
            if not name:
                st.warning("물건 이름을 입력하세요.")
            elif amount is None:
                st.warning("가격을 숫자로 입력하세요.")
            else:
                try:
                    db.add_expense(name, amount, category)
                    st.session_state[reset_key] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    if not expenses:
        st.caption("아직 내역이 없습니다.")
        return

    for exp in expenses:
        eid = exp["id"]
        cat = exp.get("category") or ""
        amt = int(exp.get("amount") or 0)
        title = exp.get("title") or ""
        in_sum = cat in active
        safe_title = html_lib.escape(title)
        safe_cat = html_lib.escape(cat)
        muted = "" if in_sum else " muted"
        st.markdown(
            f'<div class="jj-calc-item{muted}">'
            f'<p class="name">[{safe_cat}] {safe_title}</p>'
            f'<p class="amt">{format_yen(amt)}</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
        if editing:
            if st.button("삭제", key=f"calc_del_{eid}", use_container_width=True):
                db.delete_expense(eid)
                st.rerun()


def render_category_tools(category: dict) -> None:
    cid = category["id"]
    with st.expander("장소 삭제", expanded=False):
        st.caption(f"'{category['name']}' 목록을 모두 지웁니다.")
        if st.button("이 장소 삭제", use_container_width=True, key=f"del_cat_btn_{cid}"):
            st.session_state[f"confirm_del_cat_{cid}"] = True

        if st.session_state.get(f"confirm_del_cat_{cid}"):
            st.warning("정말 삭제할까요?")
            if st.button("삭제", type="primary", use_container_width=True, key=f"del_ok_{cid}"):
                db.delete_category(cid)
                st.session_state.pop(f"confirm_del_cat_{cid}", None)
                st.session_state.pop("selected_category", None)
                st.rerun()
            if st.button("취소", use_container_width=True, key=f"del_cancel_{cid}"):
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
                elif name == EXPENSE_TAB:
                    st.warning(f"'{EXPENSE_TAB}'은 예약된 이름입니다.")
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

    # Fixed 지출 tab + user shopping places
    place_names = [c["name"] for c in categories if c["name"] != EXPENSE_TAB]
    tab_names = [EXPENSE_TAB] + place_names

    if st.session_state.get("selected_category") not in tab_names:
        st.session_state.selected_category = place_names[0] if place_names else EXPENSE_TAB

    chosen = st.pills(
        "장소",
        tab_names,
        selection_mode="single",
        default=st.session_state.selected_category,
        label_visibility="collapsed",
        key="category_pills",
    )
    if chosen:
        st.session_state.selected_category = chosen
    else:
        chosen = st.session_state.selected_category

    if chosen == EXPENSE_TAB:
        render_calculator()
        return

    if not place_names:
        st.info("위에서 구매 장소를 추가하세요. 예: 편의점, 마트")
        return

    category = next(c for c in categories if c["name"] == chosen)
    render_items(category["id"])
    render_category_tools(category)


if __name__ == "__main__":
    main()

"""Supabase CRUD — 물품(텍스트 필수 + 사진 옵션)."""

from __future__ import annotations

import uuid
from typing import Any

import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def _upload_file(category_id: int, filename: str, data: bytes, content_type: str) -> str:
    client = get_client()
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    if ext not in {"jpg", "jpeg", "png", "webp", "gif"}:
        ext = "jpg"
    storage_path = f"{category_id}/{uuid.uuid4().hex}.{ext}"
    client.storage.from_("photos").upload(
        path=storage_path,
        file=data,
        file_options={"content-type": content_type or f"image/{ext}", "upsert": "false"},
    )
    return storage_path


def _remove_file(storage_path: str | None) -> None:
    if not storage_path:
        return
    try:
        get_client().storage.from_("photos").remove([storage_path])
    except Exception:
        pass


def list_categories() -> list[dict[str, Any]]:
    client = get_client()
    result = client.table("categories").select("*").order("created_at").execute()
    return result.data or []


def add_category(name: str) -> dict[str, Any] | None:
    client = get_client()
    result = client.table("categories").insert({"name": name.strip()}).execute()
    return (result.data or [None])[0]


def delete_category(category_id: int) -> None:
    client = get_client()
    items = list_items(category_id)
    paths = [i["storage_path"] for i in items if i.get("storage_path")]
    if paths:
        try:
            client.storage.from_("photos").remove(paths)
        except Exception:
            pass
    client.table("categories").delete().eq("id", category_id).execute()


def list_items(category_id: int) -> list[dict[str, Any]]:
    client = get_client()
    result = (
        client.table("text_items")
        .select("*")
        .eq("category_id", category_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


def add_item(
    category_id: int,
    content: str,
    photo_name: str | None = None,
    photo_data: bytes | None = None,
    photo_type: str | None = None,
) -> dict[str, Any] | None:
    storage_path = None
    if photo_data and photo_name:
        storage_path = _upload_file(
            category_id, photo_name, photo_data, photo_type or "image/jpeg"
        )
    client = get_client()
    result = (
        client.table("text_items")
        .insert(
            {
                "category_id": category_id,
                "content": content.strip(),
                "checked": False,
                "storage_path": storage_path,
            }
        )
        .execute()
    )
    return (result.data or [None])[0]


def set_item_checked(item_id: int, checked: bool) -> None:
    get_client().table("text_items").update({"checked": checked}).eq("id", item_id).execute()


def update_item(
    item_id: int,
    content: str,
    *,
    new_photo_name: str | None = None,
    new_photo_data: bytes | None = None,
    new_photo_type: str | None = None,
    remove_photo: bool = False,
    category_id: int | None = None,
    old_storage_path: str | None = None,
) -> None:
    client = get_client()
    payload: dict[str, Any] = {"content": content.strip()}

    if remove_photo:
        _remove_file(old_storage_path)
        payload["storage_path"] = None
    elif new_photo_data and new_photo_name and category_id is not None:
        _remove_file(old_storage_path)
        payload["storage_path"] = _upload_file(
            category_id, new_photo_name, new_photo_data, new_photo_type or "image/jpeg"
        )

    client.table("text_items").update(payload).eq("id", item_id).execute()


def delete_item(item_id: int, storage_path: str | None = None) -> None:
    _remove_file(storage_path)
    get_client().table("text_items").delete().eq("id", item_id).execute()


def photo_public_url(storage_path: str) -> str:
    return get_client().storage.from_("photos").get_public_url(storage_path)


# --- Calculator / expenses ---

def list_expenses() -> list[dict[str, Any]]:
    client = get_client()
    result = (
        client.table("expenses")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def add_expense(title: str, amount: int, category: str) -> dict[str, Any] | None:
    client = get_client()
    result = (
        client.table("expenses")
        .insert(
            {
                "title": title.strip(),
                "amount": int(amount),
                "category": category,
            }
        )
        .execute()
    )
    return (result.data or [None])[0]


def delete_expense(expense_id: int) -> None:
    get_client().table("expenses").delete().eq("id", expense_id).execute()


def update_expense(
    expense_id: int, title: str, amount: int, category: str
) -> None:
    get_client().table("expenses").update(
        {
            "title": title.strip(),
            "amount": int(amount),
            "category": category,
        }
    ).eq("id", expense_id).execute()

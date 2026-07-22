"""Supabase CRUD for the family share app."""

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


def list_categories() -> list[dict[str, Any]]:
    client = get_client()
    result = (
        client.table("categories")
        .select("*")
        .order("created_at")
        .execute()
    )
    return result.data or []


def add_category(name: str) -> dict[str, Any] | None:
    client = get_client()
    result = (
        client.table("categories")
        .insert({"name": name.strip()})
        .execute()
    )
    return (result.data or [None])[0]


def delete_category(category_id: int) -> None:
    client = get_client()
    # Remove storage files for photos in this category first
    photos = list_photos(category_id)
    for photo in photos:
        try:
            client.storage.from_("photos").remove([photo["storage_path"]])
        except Exception:
            pass
    client.table("categories").delete().eq("id", category_id).execute()


def list_text_items(category_id: int) -> list[dict[str, Any]]:
    client = get_client()
    result = (
        client.table("text_items")
        .select("*")
        .eq("category_id", category_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


def add_text_item(category_id: int, content: str) -> dict[str, Any] | None:
    client = get_client()
    result = (
        client.table("text_items")
        .insert(
            {
                "category_id": category_id,
                "content": content.strip(),
                "checked": False,
            }
        )
        .execute()
    )
    return (result.data or [None])[0]


def set_text_checked(item_id: int, checked: bool) -> None:
    client = get_client()
    client.table("text_items").update({"checked": checked}).eq("id", item_id).execute()


def delete_text_item(item_id: int) -> None:
    client = get_client()
    client.table("text_items").delete().eq("id", item_id).execute()


def list_photos(category_id: int) -> list[dict[str, Any]]:
    client = get_client()
    result = (
        client.table("photos")
        .select("*")
        .eq("category_id", category_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def photo_public_url(storage_path: str) -> str:
    client = get_client()
    return client.storage.from_("photos").get_public_url(storage_path)


def upload_photo(category_id: int, filename: str, data: bytes, content_type: str) -> dict[str, Any] | None:
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
    result = (
        client.table("photos")
        .insert({"category_id": category_id, "storage_path": storage_path})
        .execute()
    )
    return (result.data or [None])[0]


def delete_photo(photo_id: int, storage_path: str) -> None:
    client = get_client()
    try:
        client.storage.from_("photos").remove([storage_path])
    except Exception:
        pass
    client.table("photos").delete().eq("id", photo_id).execute()

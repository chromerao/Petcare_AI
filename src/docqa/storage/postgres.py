from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from docqa.core.config import Settings

SCHEMA_SQL = """
create table if not exists pets (
    id text not null,
    user_id text not null,
    name text not null,
    species text not null default '',
    breed text not null default '',
    age text not null default '',
    weight text not null default '',
    status text not null default '',
    vet text not null default '',
    note text not null default '',
    photo_url text not null default '',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table pets drop constraint if exists pets_pkey;
do $$
begin
    if not exists (
        select 1 from pg_constraint where conname = 'pets_user_id_id_key'
    ) then
        alter table pets add constraint pets_user_id_id_key unique (user_id, id);
    end if;
end $$;

create index if not exists pets_user_id_idx on pets(user_id);

create table if not exists chat_sessions (
    id text not null,
    user_id text not null,
    pet_id text,
    title text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (user_id, id)
);

create index if not exists chat_sessions_user_id_updated_idx
    on chat_sessions(user_id, updated_at desc);

create table if not exists chat_messages (
    id text primary key,
    user_id text not null,
    session_id text not null default 'default',
    pet_id text,
    role text not null,
    content text not null,
    response_json jsonb,
    created_at timestamptz not null default now()
);

alter table chat_messages add column if not exists session_id text not null default 'default';

create index if not exists chat_messages_user_id_created_idx
    on chat_messages(user_id, created_at);

create index if not exists chat_messages_user_id_session_created_idx
    on chat_messages(user_id, session_id, created_at);
"""


class UserStore:
    def __init__(self, settings: Settings) -> None:
        if not settings.database_configured or settings.database_url is None:
            raise RuntimeError("DATABASE_URL is not configured.")
        self._database_url = settings.database_url.get_secret_value()

    @contextmanager
    def _connection(self) -> Iterator[psycopg.Connection[dict[str, Any]]]:
        with psycopg.connect(self._database_url, row_factory=dict_row) as connection:
            yield connection

    def ensure_schema(self) -> None:
        with self._connection() as connection:
            connection.execute(SCHEMA_SQL)
            connection.commit()

    def list_pets(self, user_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                select id, name, species, breed, age, weight, status, vet, note,
                       photo_url as "photoUrl"
                from pets
                where user_id = %s
                order by created_at asc
                """,
                (user_id,),
            ).fetchall()
            return list(rows)

    def upsert_pet(self, user_id: str, pet: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self._connection() as connection:
            row = connection.execute(
                """
                insert into pets (
                    id, user_id, name, species, breed, age, weight, status, vet,
                    note, photo_url, created_at, updated_at
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                on conflict (user_id, id) do update set
                    name = excluded.name,
                    species = excluded.species,
                    breed = excluded.breed,
                    age = excluded.age,
                    weight = excluded.weight,
                    status = excluded.status,
                    vet = excluded.vet,
                    note = excluded.note,
                    photo_url = excluded.photo_url,
                    updated_at = excluded.updated_at
                returning id, name, species, breed, age, weight, status, vet, note,
                          photo_url as "photoUrl"
                """,
                (
                    pet["id"],
                    user_id,
                    pet.get("name", ""),
                    pet.get("species", ""),
                    pet.get("breed", ""),
                    pet.get("age", ""),
                    pet.get("weight", ""),
                    pet.get("status", ""),
                    pet.get("vet", ""),
                    pet.get("note", ""),
                    pet.get("photoUrl", ""),
                    now,
                    now,
                ),
            ).fetchone()
            connection.commit()
            if row is None:
                raise PermissionError("Pet does not belong to this user.")
            return dict(row)

    def replace_messages(
        self,
        user_id: str,
        pet_id: str | None,
        messages: list[dict[str, Any]],
        session_id: str = "default",
    ) -> None:
        title = self._session_title_from_messages(messages)
        with self._connection() as connection:
            connection.execute(
                """
                insert into chat_sessions (id, user_id, pet_id, title, created_at, updated_at)
                values (%s, %s, %s, %s, %s, %s)
                on conflict (user_id, id) do update set
                    pet_id = excluded.pet_id,
                    title = excluded.title,
                    updated_at = excluded.updated_at
                """,
                (session_id, user_id, pet_id, title, datetime.now(UTC), datetime.now(UTC)),
            )
            connection.execute(
                "delete from chat_messages where user_id = %s and session_id = %s",
                (user_id, session_id),
            )
            for index, message in enumerate(messages):
                connection.execute(
                    """
                    insert into chat_messages (
                        id, user_id, session_id, pet_id, role, content, response_json, created_at
                    )
                    values (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        message.get("id") or f"message-{index}",
                        user_id,
                        session_id,
                        pet_id,
                        message.get("role", ""),
                        message.get("content", ""),
                        json.dumps(message.get("response")) if message.get("response") else None,
                        datetime.now(UTC),
                    ),
                )
            connection.commit()

    def list_messages(self, user_id: str, session_id: str = "default") -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                select id, role, content, response_json
                from chat_messages
                where user_id = %s and session_id = %s
                order by created_at asc
                """,
                (user_id, session_id),
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "role": row["role"],
                    "content": row["content"],
                    "response": row["response_json"],
                }
                if row["response_json"] is not None
                else {
                    "id": row["id"],
                    "role": row["role"],
                    "content": row["content"],
                }
                for row in rows
            ]

    def list_chat_sessions(self, user_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                select
                    sessions.id,
                    sessions.title,
                    sessions.pet_id,
                    sessions.created_at,
                    sessions.updated_at,
                    count(messages.id)::int as message_count
                from chat_sessions sessions
                left join chat_messages messages
                    on messages.user_id = sessions.user_id
                   and messages.session_id = sessions.id
                where sessions.user_id = %s
                group by sessions.id, sessions.title, sessions.pet_id,
                         sessions.created_at, sessions.updated_at
                order by sessions.updated_at desc
                """,
                (user_id,),
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "pet_id": row["pet_id"],
                    "message_count": row["message_count"],
                    "created_at": row["created_at"].isoformat(),
                    "updated_at": row["updated_at"].isoformat(),
                }
                for row in rows
            ]

    def upsert_chat_session(
        self,
        user_id: str,
        session_id: str,
        title: str,
        pet_id: str | None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self._connection() as connection:
            row = connection.execute(
                """
                insert into chat_sessions (id, user_id, pet_id, title, created_at, updated_at)
                values (%s, %s, %s, %s, %s, %s)
                on conflict (user_id, id) do update set
                    pet_id = excluded.pet_id,
                    title = excluded.title,
                    updated_at = excluded.updated_at
                returning id, title, pet_id, created_at, updated_at
                """,
                (session_id, user_id, pet_id, title, now, now),
            ).fetchone()
            connection.commit()
            if row is None:
                raise PermissionError("Chat session does not belong to this user.")
            return {
                "id": row["id"],
                "title": row["title"],
                "pet_id": row["pet_id"],
                "message_count": 0,
                "created_at": row["created_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat(),
            }

    @staticmethod
    def _session_title_from_messages(messages: list[dict[str, Any]]) -> str:
        for message in messages:
            if message.get("role") == "user" and message.get("content"):
                return str(message["content"]).strip()[:80] or "New consultation"
        return "New consultation"

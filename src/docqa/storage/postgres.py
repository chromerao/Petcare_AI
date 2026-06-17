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
    id text primary key,
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

create index if not exists pets_user_id_idx on pets(user_id);

create table if not exists chat_messages (
    id text primary key,
    user_id text not null,
    pet_id text,
    role text not null,
    content text not null,
    response_json jsonb,
    created_at timestamptz not null default now()
);

create index if not exists chat_messages_user_id_created_idx
    on chat_messages(user_id, created_at);
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
                on conflict (id) do update set
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
                where pets.user_id = excluded.user_id
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
    ) -> None:
        with self._connection() as connection:
            connection.execute("delete from chat_messages where user_id = %s", (user_id,))
            for index, message in enumerate(messages):
                connection.execute(
                    """
                    insert into chat_messages (
                        id, user_id, pet_id, role, content, response_json, created_at
                    )
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        message.get("id") or f"message-{index}",
                        user_id,
                        pet_id,
                        message.get("role", ""),
                        message.get("content", ""),
                        json.dumps(message.get("response")) if message.get("response") else None,
                        datetime.now(UTC),
                    ),
                )
            connection.commit()

    def list_messages(self, user_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                select id, role, content, response_json
                from chat_messages
                where user_id = %s
                order by created_at asc
                """,
                (user_id,),
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

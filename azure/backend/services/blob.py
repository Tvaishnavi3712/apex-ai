"""
Azure Blob Storage adapter — the Azure implementation of Apex's object store.

Implements Apex's object-store port over Azure Blob Storage. A logical
"container" name is passed to the constructor.

Auth is Entra ID via DefaultAzureCredential (the storage account is created with
`allowSharedKeyAccess: false`), and the account is private per the ALZ policy, so
it is reachable only from inside the VNet. Set `USE_LOCAL_MOCK=true` for local
development without VNet connectivity.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class BlobService:
    """Azure Blob implementation of the Apex object-store port."""

    def __init__(self, bucket_name: str):
        # `bucket_name` is retained as an alias for callers that log it.
        self.container_name = bucket_name
        self.bucket_name = bucket_name
        self.account = os.environ.get("AZURE_STORAGE_ACCOUNT", "")
        self._use_mock = os.environ.get("USE_LOCAL_MOCK", "false").lower() == "true"
        self._client = None
        self._local_root = os.environ.get("LOCAL_BLOB_ROOT", "/tmp/apex-blob")

    # ── connection ───────────────────────────────────────────────────────────
    def _container(self):
        if self._client is not None:
            return self._client
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        if not self.account:
            raise RuntimeError(
                "AZURE_STORAGE_ACCOUNT is not set. Set it in backend/.env.azure, "
                "or set USE_LOCAL_MOCK=true for local development."
            )
        svc = BlobServiceClient(
            account_url=f"https://{self.account}.blob.core.windows.net",
            credential=DefaultAzureCredential(),
        )
        self._client = svc.get_container_client(self.container_name)
        return self._client

    def _local_path(self, key: str) -> str:
        path = os.path.join(self._local_root, self.container_name, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def uri(self, key: str) -> str:
        return f"https://{self.account}.blob.core.windows.net/{self.container_name}/{key}"

    # ── core operations ──────────────────────────────────────────────────────
    async def upload_file(
        self,
        content: bytes,
        key: str,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
    ) -> str:
        if self._use_mock:
            with open(self._local_path(key), "wb") as f:
                f.write(content)
            return f"file://{self._local_path(key)}"

        from azure.storage.blob import ContentSettings

        self._container().upload_blob(
            name=key,
            data=content,
            overwrite=True,
            metadata=metadata or None,
            content_settings=ContentSettings(content_type=content_type) if content_type else None,
        )
        return self.uri(key)

    async def download_file(self, key: str) -> bytes:
        if self._use_mock:
            with open(self._local_path(key), "rb") as f:
                return f.read()
        return self._container().download_blob(key).readall()

    async def get_json(self, key: str) -> Dict[str, Any]:
        return json.loads((await self.download_file(key)).decode("utf-8"))

    async def put_json(self, key: str, data: Dict[str, Any]) -> str:
        return await self.upload_file(
            json.dumps(data, indent=2).encode("utf-8"), key, content_type="application/json"
        )

    async def list_files(self, prefix: str = "", limit: int = 1000) -> List[Dict[str, Any]]:
        if self._use_mock:
            root = os.path.join(self._local_root, self.container_name)
            out: List[Dict[str, Any]] = []
            for dirpath, _, names in os.walk(root):
                for n in names:
                    full = os.path.join(dirpath, n)
                    rel = os.path.relpath(full, root)
                    if rel.startswith(prefix):
                        out.append({"key": rel, "size": os.path.getsize(full),
                                    "last_modified": datetime.fromtimestamp(os.path.getmtime(full))})
            return out[:limit]

        out = []
        for i, b in enumerate(self._container().list_blobs(name_starts_with=prefix or None)):
            if i >= limit:
                break
            out.append({"key": b.name, "size": b.size, "last_modified": b.last_modified})
        return out

    async def delete_file(self, key: str) -> None:
        if self._use_mock:
            p = self._local_path(key)
            if os.path.exists(p):
                os.remove(p)
            return
        from azure.core.exceptions import ResourceNotFoundError
        try:
            self._container().delete_blob(key)
        except ResourceNotFoundError:
            pass

    async def delete_prefix(self, prefix: str) -> int:
        items = await self.list_files(prefix=prefix, limit=10_000)
        for it in items:
            await self.delete_file(it["key"])
        return len(items)

    async def get_presigned_url(
        self, key: str, expiration: int = 3600, operation: str = "get_object"
    ) -> str:
        """
        Time-limited URL. Uses a **user-delegation SAS** (Entra ID signed) because
        shared-key access is disabled on the account.
        """
        if self._use_mock:
            return f"file://{self._local_path(key)}"

        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas

        svc = BlobServiceClient(
            account_url=f"https://{self.account}.blob.core.windows.net",
            credential=DefaultAzureCredential(),
        )
        start = datetime.now(timezone.utc)
        expiry = start + timedelta(seconds=expiration)
        udk = svc.get_user_delegation_key(start, expiry)

        perms = BlobSasPermissions(write=True) if operation == "put_object" else BlobSasPermissions(read=True)
        token = generate_blob_sas(
            account_name=self.account,
            container_name=self.container_name,
            blob_name=key,
            user_delegation_key=udk,
            permission=perms,
            expiry=expiry,
            start=start,
        )
        return f"{self.uri(key)}?{token}"

    async def copy_file(self, source_key: str, dest_key: str) -> str:
        data = await self.download_file(source_key)
        return await self.upload_file(data, dest_key)

    async def get_metadata(self, key: str) -> Dict[str, str]:
        if self._use_mock:
            return {}
        return self._container().get_blob_client(key).get_blob_properties().metadata or {}


# Provider-neutral alias.
ObjectStore = BlobService

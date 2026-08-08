"""Client minimale per Cloudflare R2 (API S3-compatibile).

Usato da scripts/import_normative.py per caricare i PDF importati. Non è
collegato al modulo documenti esistente (app/models/documento.py): è un
helper generico, riusabile in futuro da altri moduli che vogliano storage
su R2.
"""
from functools import lru_cache

import boto3
from botocore.client import BaseClient, Config

from app.core.config import settings


class R2NonConfigurato(RuntimeError):
    """Sollevata quando mancano le variabili d'ambiente R2 richieste."""


@lru_cache
def get_r2_client() -> BaseClient:
    if not (
        settings.r2_account_id
        and settings.r2_access_key_id
        and settings.r2_secret_access_key
    ):
        raise R2NonConfigurato(
            "R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY non configurati."
        )
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def get_bucket_normative() -> str:
    if not settings.r2_bucket_normative:
        raise R2NonConfigurato("R2_BUCKET_NORMATIVE non configurato.")
    return settings.r2_bucket_normative


def upload_file(
    client: BaseClient,
    *,
    bucket: str,
    key: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> None:
    client.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)


def object_exists(client: BaseClient, *, bucket: str, key: str) -> bool:
    from botocore.exceptions import ClientError

    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def list_keys(client: BaseClient, *, bucket: str, prefix: str) -> set[str]:
    keys: set[str] = set()
    continuation_token: str | None = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix}
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token
        response = client.list_objects_v2(**kwargs)
        keys.update(obj["Key"] for obj in response.get("Contents", []))
        if not response.get("IsTruncated"):
            break
        continuation_token = response.get("NextContinuationToken")
    return keys

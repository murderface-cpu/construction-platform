"""
AWS S3 storage utilities: presigned URL generation and upload helpers.
"""

from __future__ import annotations

import os
import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def generate_presigned_upload_url(
    folder: str,
    filename: str,
    content_type: str,
    expiry: int = 3600,
) -> dict[str, str]:
    """
    Generate a presigned URL that allows a client to upload directly to S3.

    Args:
        folder: Destination folder within the bucket (e.g. 'portfolio', 'projects').
        filename: Original filename (will be sanitised and prefixed with UUID).
        content_type: MIME type of the file (e.g. 'image/jpeg').
        expiry: URL expiry in seconds (default 1 hour).

    Returns:
        dict with 'upload_url' and 'file_key'.
    """
    _, ext = os.path.splitext(filename)
    safe_ext = ext.lower().lstrip(".")
    file_key = f"{folder}/{uuid.uuid4()}.{safe_ext}"

    s3_client = boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    upload_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": file_key,
            "ContentType": content_type,
        },
        ExpiresIn=expiry,
    )

    return {"upload_url": upload_url, "file_key": file_key}


def generate_presigned_read_url(
    file_key: str,
    expiry: int = 3600,
) -> Optional[str]:
    """
    Generate a presigned URL that allows a client to read a private S3 object.

    Returns None if the key is empty or S3 is not configured.
    """
    if not file_key or not getattr(settings, "USE_S3", False):
        return None

    try:
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        return s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": file_key,
            },
            ExpiresIn=expiry,
        )
    except ClientError:
        return None


def delete_s3_object(file_key: str) -> bool:
    """Delete an object from S3. Returns True on success."""
    if not file_key or not getattr(settings, "USE_S3", False):
        return False
    try:
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_key,
        )
        return True
    except ClientError:
        return False

"""
Módulo de armazenamento S3.

Estrutura de chaves no bucket:
    {nome_usuario}/{slug_pedido}_{timestamp}/solucoes.png
    {nome_usuario}/{slug_pedido}_{timestamp}/metadata.json
"""

import io
import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "db_palete_caixa.env")

BUCKET = os.getenv("S3_BUCKET", "palete-caixa-solucoes")
REGION = os.getenv("REGION", "us-east-1")


def _cliente():
    """Cliente S3 autenticado com as chaves AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY do .env."""
    chave_id = (os.getenv("AWS_ACCESS_KEY_ID") or "").strip()
    chave_secreta = (os.getenv("AWS_SECRET_ACCESS_KEY") or "").strip()
    if not chave_id or not chave_secreta:
        raise RuntimeError(
            "Defina AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY em db_palete_caixa.env."
        )
    return boto3.client(
        "s3",
        region_name=REGION,
        aws_access_key_id=chave_id,
        aws_secret_access_key=chave_secreta,
    )


# ─── Escrita ──────────────────────────────────────────────────────────────────

def salvar_solucao(nome_usuario: str, prefixo: str, img_bytes: bytes, meta: dict) -> str:
    """
    Faz upload da imagem (bytes PNG) e do metadata.json para o S3.

    Retorno
    -------
    Prefixo completo da chave no S3 (sem nome de arquivo).
    """
    s3 = _cliente()
    chave_base = f"{nome_usuario}/{prefixo}"

    s3.put_object(
        Bucket=BUCKET,
        Key=f"{chave_base}/solucoes.png",
        Body=img_bytes,
        ContentType="image/png",
    )
    s3.put_object(
        Bucket=BUCKET,
        Key=f"{chave_base}/metadata.json",
        Body=json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    return chave_base


# ─── Leitura ──────────────────────────────────────────────────────────────────

def listar_solucoes(nome_usuario: str) -> list:
    """Lista prefixos de soluções de um usuário em ordem decrescente."""
    s3 = _cliente()
    resp = s3.list_objects_v2(
        Bucket=BUCKET,
        Prefix=f"{nome_usuario}/",
        Delimiter="/",
    )
    pastas = [
        cp["Prefix"].rstrip("/").split("/", 1)[-1]
        for cp in resp.get("CommonPrefixes", [])
    ]
    return sorted(pastas, reverse=True)


def baixar_imagem(nome_usuario: str, prefixo: str) -> bytes | None:
    """Baixa e retorna os bytes da imagem PNG. Retorna None se não encontrada."""
    s3 = _cliente()
    try:
        resp = s3.get_object(Bucket=BUCKET, Key=f"{nome_usuario}/{prefixo}/solucoes.png")
        return resp["Body"].read()
    except ClientError:
        return None


def baixar_metadata(nome_usuario: str, prefixo: str) -> dict | None:
    """Baixa e retorna o dict de metadados. Retorna None se não encontrado."""
    s3 = _cliente()
    try:
        resp = s3.get_object(Bucket=BUCKET, Key=f"{nome_usuario}/{prefixo}/metadata.json")
        return json.loads(resp["Body"].read().decode("utf-8"))
    except ClientError:
        return None

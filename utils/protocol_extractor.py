# utils/protocol_extractor.py
"""Utilities to extract protocol numbers from Servopa Docparser links/PDFs."""

from __future__ import annotations

import base64
import json
import logging
import re
import tempfile
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple
from urllib.parse import unquote

import pdfplumber
import requests
from selenium.webdriver.remote.webdriver import WebDriver

ProgressCb = Optional[Callable[[str], None]]

LOGGER = logging.getLogger(__name__)


@dataclass
class ProtocolExtractionResult:
    protocol: Optional[str]
    docparser_url: Optional[str] = None
    pdf_url: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict] = None


def _notify(progress_callback: ProgressCb, message: str) -> None:
    if progress_callback:
        try:
            progress_callback(message)
        except Exception:  # pragma: no cover - defensive
            LOGGER.debug("Progress callback failed", exc_info=True)


def _decode_docparser_payload(docparser_url: str) -> Dict:
    base64_chunk = docparser_url.rstrip("/").split("/")[-1]
    base64_chunk = unquote(base64_chunk)
    padding = "=" * (-len(base64_chunk) % 4)
    decoded_bytes = base64.urlsafe_b64decode(base64_chunk + padding)
    decoded_text = decoded_bytes.decode("utf-8", errors="ignore")
    return json.loads(decoded_text)


def _extract_number_from_text(text: str) -> Optional[str]:
    # Prefer patterns explicitly mentioning protocolo
    pattern_with_label = re.search(
        r"protocolo[^\d]*(\d{4,})", text, flags=re.IGNORECASE
    )
    if pattern_with_label:
        return pattern_with_label.group(1)

    # Fallback: pick the longest sequence of >=6 digits
    numbers = re.findall(r"\b\d{6,}\b", text)
    if not numbers:
        return None

    numbers.sort(key=len, reverse=True)
    return numbers[0]


def _download_pdf(driver: WebDriver, pdf_url: str, timeout: int = 15) -> bytes:
    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent")
        if driver
        else "Mozilla/5.0"
    }
    response = requests.get(pdf_url, headers=headers, cookies=cookies, timeout=timeout)
    response.raise_for_status()
    return response.content


def _extract_protocol_from_pdf(driver: WebDriver, pdf_url: str, progress_callback: ProgressCb) -> Tuple[Optional[str], Dict]:
    metadata: Dict = {}
    try:
        pdf_bytes = _download_pdf(driver, pdf_url)
    except Exception as error:  # pragma: no cover - network dependent
        metadata["pdf_download_error"] = str(error)
        _notify(progress_callback, f"⚠️ Falha ao baixar PDF para protocolo: {error}")
        return None, metadata

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_file.flush()

        try:
            with pdfplumber.open(tmp_file.name) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as error:  # pragma: no cover - PDF parsing dependent
            metadata["pdf_parse_error"] = str(error)
            _notify(progress_callback, f"⚠️ Falha ao ler PDF para protocolo: {error}")
            return None, metadata

    protocol = _extract_number_from_text(text)
    metadata["text_length"] = len(text)
    return protocol, metadata


def extract_protocol_from_docparser(
    driver: WebDriver,
    docparser_url: str,
    progress_callback: ProgressCb = None,
) -> ProtocolExtractionResult:
    """Attempts to extract the protocol number from the Docparser URL/PDF."""

    _notify(progress_callback, f"🔍 DEBUG: URL recebida para extração: {docparser_url[:100]}...")

    metadata: Dict = {}
    protocol: Optional[str] = None
    pdf_url: Optional[str] = None
    source: Optional[str] = None

    # Tenta extrair Base64 da URL de diferentes formatos
    base64_chunk = None
    
    if "/view/" in docparser_url:
        # Formato: https://...../view/BASE64
        base64_chunk = docparser_url.split("/view/")[-1]
        _notify(progress_callback, f"🔍 DEBUG: Base64 extraído da URL (/view/): {base64_chunk[:50]}...")
    elif docparser_url.startswith("eyJ"):
        # Já é o Base64 direto
        base64_chunk = docparser_url
        _notify(progress_callback, f"🔍 DEBUG: URL já é Base64: {base64_chunk[:50]}...")
    else:
        _notify(progress_callback, f"⚠️ DEBUG: Formato de URL não reconhecido!")

    if base64_chunk:
        try:
            payload = _decode_docparser_payload(base64_chunk)
            metadata["decoded_payload"] = payload
            _notify(progress_callback, f"✅ DEBUG: Payload decodificado com sucesso!")
        except Exception as error:
            metadata["payload_decode_error"] = str(error)
            _notify(progress_callback, f"⚠️ Não foi possível decodificar Docparser: {error}")
            payload = None
    else:
        _notify(progress_callback, f"⚠️ DEBUG: Não foi possível extrair Base64 da URL")
        payload = None

    if payload:
        data_block = payload.get("data", {}) if isinstance(payload, dict) else {}
        candidate_keys = [
            "num_protocolo_ant",
            "num_protocolo",
            "numero_protocolo",
        ]
        
        _notify(progress_callback, f"🔍 DEBUG: Procurando protocolo em {len(candidate_keys)} campos...")
        
        for key in candidate_keys:
            value = data_block.get(key)
            if value:
                protocol = str(value).strip()
                source = f"json:{key}"
                _notify(progress_callback, f"✅ DEBUG: Protocolo encontrado no campo '{key}': {protocol}")
                break

        if not protocol:
            _notify(progress_callback, f"⚠️ DEBUG: Protocolo não encontrado nos campos esperados")
            maybe_text_field = data_block.get("texto")
            if maybe_text_field:
                protocol = _extract_number_from_text(str(maybe_text_field))
                if protocol:
                    source = "json:texto"
                    _notify(progress_callback, f"✅ DEBUG: Protocolo encontrado no campo 'texto': {protocol}")

        pdf_url = payload.get("url") or payload.get("pdf_url")
        if pdf_url:
            _notify(progress_callback, f"🔍 DEBUG: URL do PDF encontrada: {pdf_url[:50]}...")

    if not protocol and pdf_url:
        _notify(progress_callback, f"🔍 DEBUG: Tentando extrair do PDF...")
        protocol, pdf_meta = _extract_protocol_from_pdf(driver, pdf_url, progress_callback)
        metadata["pdf"] = pdf_meta
        if protocol:
            source = source or "pdf"
            _notify(progress_callback, f"✅ DEBUG: Protocolo extraído do PDF: {protocol}")

    if protocol:
        _notify(progress_callback, f"📑 Protocolo capturado: {protocol}")
    else:
        _notify(progress_callback, "⚠️ Protocolo não encontrado no documento")

    return ProtocolExtractionResult(
        protocol=protocol,
        docparser_url=docparser_url,
        pdf_url=pdf_url,
        source=source,
        metadata=metadata if metadata else None,
    )

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


def _download_pdf(
    driver: Optional[WebDriver], pdf_url: str, timeout: int = 15
) -> Tuple[bytes, Dict[str, Optional[str]]]:
    cookies: Dict[str, str] = {}
    user_agent = "Mozilla/5.0"
    response_info: Dict[str, Optional[str]] = {
        "attempt": "requests",
        "status_code": None,
        "content_type": None,
        "content_disposition": None,
        "url": pdf_url,
    }

    if driver:
        try:
            cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
        except Exception:  # pragma: no cover - defensive around Selenium state
            LOGGER.debug("Failed to read cookies from driver", exc_info=True)
        try:
            user_agent = driver.execute_script("return navigator.userAgent")
        except Exception:  # pragma: no cover - defensive around Selenium state
            LOGGER.debug("Failed to read user agent from driver", exc_info=True)

    headers = {
        "User-Agent": user_agent,
        "Accept": "application/pdf,application/octet-stream,*/*;q=0.8",
        "Referer": "https://www.consorcioservopa.com.br/",
    }

    errors: list[str] = []

    try:
        response = requests.get(pdf_url, headers=headers, cookies=cookies, timeout=timeout)
        response.raise_for_status()

        response_info.update(
            {
                "status_code": str(response.status_code),
                "content_type": response.headers.get("Content-Type"),
                "content_disposition": response.headers.get("Content-Disposition"),
                "url": response.url,
            }
        )

        return response.content, response_info

    except Exception as error:
        response_info["error"] = str(error)
        errors.append(f"requests: {error}")

    if driver:
        try:
            script = """
                const url = arguments[0];
                const callback = arguments[arguments.length - 1];

                fetch(url, { credentials: 'include' })
                    .then(response => {
                        if (!response.ok) {
                            callback({ success: false, status: response.status, statusText: response.statusText });
                            return;
                        }

                        Promise.all([
                            response.arrayBuffer(),
                            response.headers.get('Content-Type'),
                            response.headers.get('Content-Disposition'),
                            response.url,
                            response.status,
                        ])
                        .then(([buffer, contentType, contentDisposition, finalUrl, status]) => {
                            const bytes = new Uint8Array(buffer);
                            const chunkSize = 0x8000;
                            let binary = '';
                            for (let i = 0; i < bytes.length; i += chunkSize) {
                                const chunk = bytes.subarray(i, i + chunkSize);
                                binary += String.fromCharCode.apply(null, chunk);
                            }
                            const base64 = btoa(binary);
                            callback({
                                success: true,
                                base64,
                                contentType,
                                contentDisposition,
                                finalUrl,
                                status,
                            });
                        })
                        .catch(err => callback({ success: false, error: err.message }));
                    })
                    .catch(err => callback({ success: false, error: err.message }));
            """

            result = driver.execute_async_script(script, pdf_url)

            if result and result.get("success") and result.get("base64"):
                response_info.update(
                    {
                        "attempt": "browser-fetch",
                        "status_code": str(result.get("status")) if result.get("status") else response_info.get("status_code"),
                        "content_type": result.get("contentType") or response_info.get("content_type"),
                        "content_disposition": result.get("contentDisposition") or response_info.get("content_disposition"),
                        "url": result.get("finalUrl") or response_info.get("url"),
                    }
                )

                return base64.b64decode(result["base64"]), response_info

            errors.append(f"browser-fetch: {result}")

        except Exception as error:  # pragma: no cover - Selenium/JS dependent
            errors.append(f"browser-fetch: {error}")

    raise RuntimeError("; ".join(errors) if errors else "Unable to download PDF")


def _extract_protocol_from_pdf(
    driver: Optional[WebDriver], pdf_url: str, progress_callback: ProgressCb
) -> Tuple[Optional[str], Dict]:
    metadata: Dict = {}
    try:
        pdf_bytes, response_info = _download_pdf(driver, pdf_url)
        metadata["download"] = response_info
    except Exception as error:  # pragma: no cover - network dependent
        metadata["pdf_download_error"] = str(error)
        _notify(progress_callback, f"⚠️ Falha ao baixar PDF para protocolo: {error}")
        return None, metadata

    if not pdf_bytes.strip().startswith(b"%PDF"):
        metadata["pdf_signature_valid"] = False
        _notify(
            progress_callback,
            "⚠️ Conteúdo baixado não parece ser um PDF (assinatura ausente)",
        )
    else:
        metadata["pdf_signature_valid"] = True

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

        json_protocol: Optional[str] = None
        json_source: Optional[str] = None
        previous_protocol: Optional[str] = None
        previous_source: Optional[str] = None

        for key in candidate_keys:
            value = data_block.get(key)
            if not value:
                continue

            value_str = str(value).strip()
            if not value_str:
                continue

            if "ant" in key.lower():
                if not previous_protocol:
                    previous_protocol = value_str
                    previous_source = f"json:{key}"
                    _notify(
                        progress_callback,
                        f"ℹ️ DEBUG: Protocolo anterior encontrado em '{key}': {previous_protocol}",
                    )
            elif not json_protocol:
                json_protocol = value_str
                json_source = f"json:{key}"
                _notify(
                    progress_callback,
                    f"✅ DEBUG: Protocolo encontrado no campo '{key}': {json_protocol}",
                )

        if not json_protocol:
            _notify(progress_callback, "⚠️ DEBUG: Protocolo não encontrado nos campos esperados")
            maybe_text_field = data_block.get("texto")
            if maybe_text_field:
                extracted = _extract_number_from_text(str(maybe_text_field))
                if extracted:
                    json_protocol = extracted
                    json_source = "json:texto"
                    _notify(progress_callback, f"✅ DEBUG: Protocolo encontrado no campo 'texto': {json_protocol}")

        metadata.setdefault("json_candidates", {})
        if json_protocol:
            metadata["json_candidates"]["primary"] = {
                "value": json_protocol,
                "source": json_source,
            }
        if previous_protocol:
            metadata["json_candidates"]["previous"] = {
                "value": previous_protocol,
                "source": previous_source,
            }

        protocol = json_protocol
        source = json_source

        pdf_url = payload.get("url") or payload.get("pdf_url")
        if pdf_url:
            _notify(progress_callback, f"🔍 DEBUG: URL do PDF encontrada: {pdf_url[:50]}...")

    candidate_pdf_urls = []
    if docparser_url:
        candidate_pdf_urls.append(docparser_url)
    if pdf_url:
        candidate_pdf_urls.append(pdf_url)

    need_pdf_lookup = not protocol or (source and "ant" in source)

    if (need_pdf_lookup or previous_protocol) and candidate_pdf_urls:
        metadata.setdefault("pdf_attempts", [])
        _notify(progress_callback, "🔍 DEBUG: Tentando extrair protocolo a partir do PDF...")

        seen = set()
        for candidate_url in candidate_pdf_urls:
            if not candidate_url or candidate_url in seen:
                continue
            seen.add(candidate_url)

            _notify(progress_callback, f"🔗 DEBUG: Baixando PDF em {candidate_url[:80]}...")
            pdf_protocol, pdf_meta = _extract_protocol_from_pdf(
                driver, candidate_url, progress_callback
            )

            attempt_meta = {
                "url": candidate_url,
                "protocol_found": bool(pdf_protocol),
                "details": pdf_meta,
            }
            metadata["pdf_attempts"].append(attempt_meta)

            if pdf_protocol:
                protocol = pdf_protocol
                pdf_url = candidate_url
                source = source or (
                    "pdf:docparser_view" if candidate_url == docparser_url else "pdf"
                )
                _notify(
                    progress_callback,
                    f"✅ DEBUG: Protocolo extraído do PDF ({candidate_url[:50]}...): {protocol}",
                )
                break
        else:
            _notify(progress_callback, "⚠️ DEBUG: Não foi possível extrair protocolo via PDF")

    if not protocol and previous_protocol:
        protocol = previous_protocol
        source = previous_source
        _notify(
            progress_callback,
            f"ℹ️ DEBUG: Utilizando protocolo anterior como fallback: {protocol}",
        )

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

"""Envia mensagens e fotos para o Telegram.

O token e o ID do chat NUNCA ficam no código: vêm de variáveis de ambiente
(no GitHub, ficam nos 'Secrets').
"""

import os
import time

import requests

PAUSA = 1.0  # segundos entre mensagens (evita bloqueio por excesso de envios)


def _chamar(metodo: str, corpo: dict) -> requests.Response:
    token = os.environ["TELEGRAM_TOKEN"]
    corpo = {"chat_id": os.environ["TELEGRAM_CHAT_ID"], "parse_mode": "HTML", **corpo}
    return requests.post(
        f"https://api.telegram.org/bot{token}/{metodo}", json=corpo, timeout=30
    )


def _erro(resposta: requests.Response) -> str:
    # Não usamos raise_for_status() de propósito: a mensagem de erro dele
    # incluiria a URL com o TOKEN, e o token não pode aparecer em logs.
    try:
        return resposta.json().get("description", "erro desconhecido")
    except ValueError:
        return f"HTTP {resposta.status_code}"


def enviar(texto: str, imagem: str | None = None) -> None:
    """Manda uma foto com legenda; se a foto falhar, manda só o texto."""
    if imagem:
        resposta = _chamar("sendPhoto", {"photo": imagem, "caption": texto})
        if resposta.ok:
            time.sleep(PAUSA)
            return
        print(f"Aviso: não consegui enviar a foto ({_erro(resposta)}). Enviando só texto.")

    resposta = _chamar(
        "sendMessage", {"text": texto, "link_preview_options": {"is_disabled": True}}
    )
    if not resposta.ok:
        raise RuntimeError(f"Telegram recusou a mensagem: {_erro(resposta)}")
    time.sleep(PAUSA)

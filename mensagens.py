"""Transforma os jogos em textos prontos para o Telegram.

Aqui não tem internet nem Telegram: só entra lista de jogos e sai texto.
Por isso é fácil de testar e de mudar o visual das mensagens.
"""

import html
from datetime import datetime, timedelta

from epic import Jogo

LIMITE_DESCRICAO = 220  # caracteres; deixe 0 para NÃO mostrar descrição


def _quando(data: datetime) -> str:
    return data.strftime("%d/%m às %H:%M")


def _descricao(texto: str) -> str:
    texto = " ".join(texto.split())  # tira quebras de linha e espaços repetidos
    if LIMITE_DESCRICAO <= 0:
        return ""
    if len(texto) > LIMITE_DESCRICAO:
        texto = texto[:LIMITE_DESCRICAO].rstrip() + "…"
    return texto


def _cartao(jogo: Jogo, linha_data: str, aviso: str = "") -> str:
    """Monta o texto de um jogo (vai como legenda da imagem)."""
    linhas = [
        f"🎮 <b>{html.escape(jogo.titulo)}</b>",
        f"📦 {html.escape(jogo.tipo)}",
        linha_data,
    ]
    if aviso:
        linhas.append(aviso)
    descricao = _descricao(jogo.descricao)
    if descricao:
        linhas += ["", html.escape(descricao)]
    link = html.escape(jogo.link, quote=True)
    linhas += ["", f'🔗 <a href="{link}">Ver na Epic Games</a>']
    return "\n".join(linhas)


def montar(gratis: list[Jogo], breve: list[Jogo], agora: datetime) -> list[tuple[str, str | None]]:
    """Devolve uma lista de (texto, url_da_imagem) na ordem em que será enviada."""
    saudacao = "☀️ Bom dia!" if agora.hour < 15 else "🌙 Boa noite!"
    mensagens: list[tuple[str, str | None]] = [
        (f"{saudacao} Resumo dos jogos da <b>Epic Games</b>:", None)
    ]

    # --- Grátis agora ---
    if gratis:
        mensagens.append(("🟢 <b>GRÁTIS AGORA</b>", None))
        for jogo in gratis:
            acaba_logo = (jogo.fim - agora) < timedelta(hours=24)
            aviso = "🚨 <b>Acaba em menos de 24h!</b>" if acaba_logo else ""
            data = f"⏳ Grátis até {_quando(jogo.fim)}"
            mensagens.append((_cartao(jogo, data, aviso), jogo.imagem))
    else:
        mensagens.append(("🟢 <b>GRÁTIS AGORA</b>\nNenhum jogo grátis no momento.", None))

    # --- Em breve ---
    if breve:
        mensagens.append(("🔜 <b>EM BREVE</b>", None))
        for jogo in breve:
            data = f"🗓️ Grátis de {_quando(jogo.inicio)} até {_quando(jogo.fim)}"
            mensagens.append((_cartao(jogo, data), jogo.imagem))
    else:
        mensagens.append(("🔜 <b>EM BREVE</b>\nAinda não foi anunciado nada.", None))

    return mensagens

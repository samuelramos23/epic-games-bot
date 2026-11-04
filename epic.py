"""Busca os jogos da Epic e transforma o JSON gigante em objetos simples.

Este arquivo só cuida de UMA coisa: falar com a Epic e entender a resposta.
Se um dia a Epic mudar o formato, é só aqui que você mexe.
"""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

# --- Configurações (mude aqui se quiser) ---------------------------------
URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
LOCALE = "pt-BR"   # idioma das descrições
COUNTRY = "BR"     # país da loja (se vier lista estranha, teste "en-US" e "US")
LOJA = "https://store.epicgames.com/pt-BR"
FUSO = ZoneInfo("America/Sao_Paulo")  # horário de Brasília

# Tradução do campo "offerType" da Epic para algo legível.
TIPOS = {
    "BASE_GAME": "Jogo base",
    "DLC": "DLC (conteúdo extra, precisa do jogo base)",
    "ADD_ON": "Conteúdo adicional (add-on)",
    "EDITION": "Edição do jogo",
    "BUNDLE": "Pacote de jogos",
    "DEMO": "Demo",
    "EDITOR": "Ferramenta / editor",
    "OTHERS": "Outro tipo",
}

# Tipos de imagem que preferimos, em ordem de prioridade.
PREFERENCIA_IMAGEM = [
    "OfferImageWide",
    "DieselStoreFrontWide",
    "Thumbnail",
    "OfferImageTall",
]


@dataclass
class Jogo:
    """Um jogo já 'limpo', com só o que a gente precisa."""

    titulo: str
    tipo: str
    descricao: str
    imagem: str | None
    link: str
    inicio: datetime  # início da promoção (horário de Brasília)
    fim: datetime     # fim da promoção (horário de Brasília)


def buscar() -> dict:
    """Faz o pedido (GET) para a Epic e devolve o JSON como dicionário."""
    parametros = {"locale": LOCALE, "country": COUNTRY, "allowCountries": COUNTRY}
    resposta = requests.get(URL, params=parametros, timeout=30)
    resposta.raise_for_status()  # se der erro (404, 500...), para aqui com a mensagem
    return resposta.json()


def _para_data(texto: str) -> datetime:
    """Converte '2026-10-22T15:00:00.000Z' (UTC) para horário de Brasília."""
    return datetime.fromisoformat(texto.replace("Z", "+00:00")).astimezone(FUSO)


def _janela_gratis(grupos):
    """Procura, dentro das promoções, uma que deixe o jogo 100% grátis.

    Devolve (inicio, fim) ou None se não houver.
    Pegadinha da Epic: 'discountPercentage' == 0 significa que você paga 0%,
    ou seja, é GRÁTIS. (Um desconto de 50% viria como 50.)
    """
    for grupo in grupos or []:
        for oferta in grupo.get("promotionalOffers") or []:
            desconto = (oferta.get("discountSetting") or {}).get("discountPercentage")
            if desconto == 0:
                return _para_data(oferta["startDate"]), _para_data(oferta["endDate"])
    return None


def _imagem(elemento: dict) -> str | None:
    """Escolhe a melhor imagem disponível do jogo."""
    imagens = {i.get("type"): i.get("url") for i in elemento.get("keyImages") or []}
    for tipo in PREFERENCIA_IMAGEM:
        if imagens.get(tipo):
            return imagens[tipo]
    return next((url for url in imagens.values() if url), None)


def _link(elemento: dict) -> str:
    """Monta o link da página do jogo na loja da Epic."""
    candidatos = []
    for mapa in elemento.get("offerMappings") or []:
        candidatos.append(mapa.get("pageSlug"))
    for mapa in (elemento.get("catalogNs") or {}).get("mappings") or []:
        candidatos.append(mapa.get("pageSlug"))
    candidatos.append(elemento.get("productSlug"))

    for slug in candidatos:
        if slug:
            return f"{LOJA}/p/{slug.removesuffix('/home')}"
    # Sem slug (acontece com "jogo misterioso"): manda para a página geral.
    return f"{LOJA}/free-games"


def interpretar(dados: dict) -> tuple[list[Jogo], list[Jogo]]:
    """Separa os jogos em (grátis agora, grátis em breve)."""
    elementos = dados["data"]["Catalog"]["searchStore"]["elements"]

    gratis_agora: list[Jogo] = []
    em_breve: list[Jogo] = []
    vistos: set[str] = set()

    for el in elementos:
        if el.get("id") in vistos:
            continue
        vistos.add(el.get("id"))

        promocoes = el.get("promotions") or {}  # pode vir None
        atual = _janela_gratis(promocoes.get("promotionalOffers"))
        futura = _janela_gratis(promocoes.get("upcomingPromotionalOffers"))
        janela = atual or futura
        if janela is None:
            continue  # nenhum desconto de 100%: ignora

        jogo = Jogo(
            titulo=el.get("title", "Sem título"),
            tipo=TIPOS.get(el.get("offerType"), el.get("offerType") or "Tipo desconhecido"),
            descricao=el.get("description") or "",
            imagem=_imagem(el),
            link=_link(el),
            inicio=janela[0],
            fim=janela[1],
        )
        (gratis_agora if atual else em_breve).append(jogo)

    gratis_agora.sort(key=lambda j: j.fim)    # o que acaba primeiro vem primeiro
    em_breve.sort(key=lambda j: j.inicio)     # o que começa primeiro vem primeiro
    return gratis_agora, em_breve

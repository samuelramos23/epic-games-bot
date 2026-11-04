"""Ponto de entrada: busca os jogos, monta as mensagens e envia.

Uso:
    python main.py            -> envia de verdade para o Telegram
    python main.py --teste    -> só mostra no terminal (não precisa de token)
"""

import sys
from datetime import datetime

import enviar
import epic
import mensagens


def main() -> None:
    modo_teste = "--teste" in sys.argv

    dados = epic.buscar()
    gratis, breve = epic.interpretar(dados)
    agora = datetime.now(epic.FUSO)

    for texto, imagem in mensagens.montar(gratis, breve, agora):
        if modo_teste:
            print(texto)
            print(f"[imagem: {imagem}]")
            print("-" * 40)
        else:
            enviar.enviar(texto, imagem)

    print(f"Pronto: {len(gratis)} grátis agora, {len(breve)} em breve.")


if __name__ == "__main__":
    main()

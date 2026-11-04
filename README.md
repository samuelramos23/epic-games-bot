# Bot da Epic Games no Telegram

Avisa, às 9h e às 21h (Brasília), quais jogos estão grátis na Epic e quais vêm em breve,
com imagem, tipo (jogo base, DLC...), descrição curta e link.

## Arquivos (cada um faz uma coisa só)

| Arquivo | Função |
|---|---|
| `epic.py` | Busca os dados na Epic e separa "grátis agora" e "em breve" |
| `mensagens.py` | Monta os textos (visual das mensagens) |
| `enviar.py` | Envia para o Telegram |
| `main.py` | Junta tudo |
| `.github/workflows/avisar.yml` | Agenda a execução às 9h e 21h no GitHub (grátis) |

## 1. Rodar no seu computador (sem Telegram)

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python main.py --teste

O `--teste` só imprime no terminal. Confira se títulos, tipos, datas, imagens e links fazem sentido.

## 2. Pegar o token e o ID do chat

1. No Telegram, fale com o @BotFather. Para um token novo: `/revoke` e escolha seu bot.
2. Mande qualquer mensagem para o seu bot.
3. Abra no navegador (trocando SEU_TOKEN): `https://api.telegram.org/botSEU_TOKEN/getUpdates`
4. Procure `"chat":{"id":123456789` — esse número é o `TELEGRAM_CHAT_ID`.

Nunca coloque o token no código, em prints ou em conversas.

## 3. Testar o envio real

    export TELEGRAM_TOKEN="8569310351:AAH_S-dS-SoHvSoRWi021TC5TLWrpjwP0Zg"
    export TELEGRAM_CHAT_ID="6986324379"
    python main.py

## 4. Deixar rodando de graça (GitHub Actions)

1. Crie um repositório público no GitHub e suba estes arquivos.
2. Em Settings > Secrets and variables > Actions, crie `TELEGRAM_TOKEN` e `TELEGRAM_CHAT_ID`.
3. Na aba Actions, abra "Avisar jogos grátis da Epic" e clique em "Run workflow" para testar na hora.
4. Pronto: roda sozinho todo dia às ~9h e ~21h (pode atrasar alguns minutos).

## Ajustes rápidos

- Tamanho da descrição: `LIMITE_DESCRICAO` em `mensagens.py` (0 = sem descrição).
- País/idioma: `LOCALE` e `COUNTRY` em `epic.py`.
- Horários: linhas `cron` em `avisar.yml` (em UTC; Brasília = UTC-3).

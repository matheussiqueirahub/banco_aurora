
# Banco Aurora — Sistema de Contas Bancárias (Python, OO, Herança & Polimorfismo)

Projeto didático **portfolio‑ready** demonstrando **herança**, **polimorfismo**, **encapsulamento** e **persistência simples**.
Inclui três tipos de conta com comportamentos distintos aplicados via `end_of_day()` (hook polimórfico).

## Estrutura
```
bank_system/
├─ bank/
│  ├─ __init__.py
│  ├─ accounts.py          # Account (abstrata), CheckingAccount, SavingsAccount, InvestmentAccount, Transaction
│  ├─ bank.py              # Orquestração: abertura de contas, fechamento de dia, persistência JSON
│  ├─ customer.py          # Entidade Customer
│  └─ exceptions.py        # Exceções de domínio
└─ main.py                 # Demo CLI
```

## Conceitos
- **Herança**: `CheckingAccount`, `SavingsAccount`, `InvestmentAccount` herdam de `Account`.
- **Polimorfismo**: cada conta implementa `end_of_day()` com regras próprias (taxa de manutenção, juros diários, yield com fee).
- **Encapsulamento**: `_ledger` e `_record()` controlam os lançamentos; validações de quantia e moeda.
- **Composição**: `Bank` agrega `Account` e `Customer`.
- **Persistência**: `Bank.dump_json()` e `Bank.load_json()`.

## Como rodar
```bash
python3 main.py
```

## Próximos passos (idéias de evolução)
- Estratégias de juros/fee via **Strategy Pattern**.
- Autenticação básica + comandos interativos (CLI/typer).
- Serialização completa do ledger e recálculo determinístico.
- Testes unitários (pytest) e CI (GitHub Actions).


---

## Executar API Flask
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python api.py
```
Endpoints principais:
- `POST /customers` → cria cliente `{name, document_id, email?}`
- `POST /accounts` → abre conta `{owner_id, kind: checking|savings|investment, currency?, balance?, ...}`
- `GET /accounts/<id>` → detalhe
- `POST /accounts/<id>/deposit|withdraw` → movimentações
- `POST /transfer` → `{from_id, to_id, amount, note?}`
- `POST /eod` → aplica regras de cada conta
- `GET /dump` → JSON do banco

## CLI (Typer)
```bash
python cli.py --help
python cli.py add-customer "Alice" 111.222.333-44 --email alice@example.com
python cli.py open-account <CUSTOMER_ID> savings --balance 500
python cli.py deposit <ACCOUNT_ID> 100
python cli.py eod
python cli.py dump
```

## Badges (exemplo para GitHub)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-pytest-brightgreen)
![Style](https://img.shields.io/badge/code_style-PEP8-lightgrey)

## Licença
MIT

## Descrição — Banco Aurora
O **Banco Aurora** é um laboratório de engenharia de software orientado a objetos que foge do trivial.
Aqui, contas **corrente**, **poupança** e **investimento** herdam de uma `Account` abstrata e materializam
**polimorfismo** via `end_of_day()`: cada tipo aplica regras próprias (taxas, juros, yields). O sistema mantém
um **ledger imutável por transação**, valida **regras de domínio** (moeda, saldo, quantia) e oferece uma
**superfície de uso dupla**: **CLI para fluxo de desenvolvedor** e **API Flask** para integrações. É um projeto
enxuto, legível e escalável, pensado para portfólio e entrevistas técnicas.


## Executar com Docker
```bash
docker build -t banco-aurora .
docker run -p 5000:5000 banco-aurora
# ou
docker compose up --build
```

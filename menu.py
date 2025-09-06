#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass


# ===== Modelo OO =====
@dataclass
class Conta:
    numero: str
    titular: str
    saldo: float = 0.0

    def depositar(self, valor: float):
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser positivo.")
        self.saldo += valor

    def sacar(self, valor: float):
        if valor <= 0:
            raise ValueError("O valor do saque deve ser positivo.")
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente.")
        self.saldo -= valor

    def exibir_saldo(self) -> str:
        return f"Conta {self.numero} | Titular: {self.titular} | Saldo: R$ {self.saldo:.2f}"

    # Hook polimórfico: cada conta aplica sua própria regra
    def end_of_day(self):
        pass


class ContaCorrente(Conta):
    def __init__(self, numero: str, titular: str, saldo: float = 0.0, taxa: float = 10.0):
        super().__init__(numero, titular, saldo)
        self.taxa = taxa

    def end_of_day(self):
        # cobra taxa apenas se houver saldo suficiente
        if self.saldo >= self.taxa:
            self.sacar(self.taxa)


class ContaPoupanca(Conta):
    def __init__(self, numero: str, titular: str, saldo: float = 0.0, rendimento: float = 0.02):
        super().__init__(numero, titular, saldo)
        self.rendimento = rendimento  # ex.: 0.02 = 2%

    def end_of_day(self):
        if self.saldo > 0:
            ganho = self.saldo * self.rendimento
            self.depositar(ganho)


class ContaInvestimento(Conta):
    def __init__(
        self,
        numero: str,
        titular: str,
        saldo: float = 0.0,
        taxa_adm: float = 0.01,
        rendimento: float = 0.05,
    ):
        super().__init__(numero, titular, saldo)
        self.taxa_adm = taxa_adm  # ex.: 0.01 = 1% de administração
        self.rendimento = rendimento  # ex.: 0.05 = 5% de rendimento

    def end_of_day(self):
        if self.saldo > 0:
            taxa = self.saldo * self.taxa_adm
            self.sacar(taxa)
            ganho = self.saldo * self.rendimento
            self.depositar(ganho)


# ===== Camada "aplicação" (menu/console) =====
class BancoConsole:
    def __init__(self):
        self.contas: dict[str, Conta] = {}

    def criar_conta(self):
        print("\n== Nova conta ==")
        numero = input("Número da conta: ").strip()
        if numero in self.contas:
            print("Já existe conta com esse número.")
            return
        titular = input("Titular: ").strip()
        tipo = input("Tipo [corrente|poupanca|investimento]: ").strip().lower()
        saldo_inicial = float(input("Saldo inicial (R$): ") or "0")

        if tipo == "corrente":
            taxa = float(input("Taxa de manutenção (R$) [padrão 10]: ") or "10")
            conta = ContaCorrente(numero, titular, saldo_inicial, taxa)
        elif tipo == "poupanca":
            rendimento = float(input("Rendimento (ex.: 0.02 para 2%): ") or "0.02")
            conta = ContaPoupanca(numero, titular, saldo_inicial, rendimento)
        elif tipo == "investimento":
            taxa_adm = float(input("Taxa adm (ex.: 0.01 para 1%): ") or "0.01")
            rendimento = float(input("Rendimento (ex.: 0.05 para 5%): ") or "0.05")
            conta = ContaInvestimento(numero, titular, saldo_inicial, taxa_adm, rendimento)
        else:
            print("Tipo inválido.")
            return

        self.contas[numero] = conta
        print("Conta criada com sucesso.")

    def depositar(self):
        try:
            numero = input("Número da conta: ").strip()
            conta = self.contas[numero]
            valor = float(input("Valor do depósito (R$): "))
            conta.depositar(valor)
            print("Depósito realizado.")
        except KeyError:
            print("Conta não encontrada.")
        except ValueError as e:
            print("Erro:", e)

    def sacar(self):
        try:
            numero = input("Número da conta: ").strip()
            conta = self.contas[numero]
            valor = float(input("Valor do saque (R$): "))
            conta.sacar(valor)
            print("Saque realizado.")
        except KeyError:
            print("Conta não encontrada.")
        except ValueError as e:
            print("Erro:", e)

    def transferir(self):
        try:
            origem = input("Conta origem: ").strip()
            destino = input("Conta destino: ").strip()
            valor = float(input("Valor da transferência (R$): "))
            c_origem = self.contas[origem]
            c_destino = self.contas[destino]
            c_origem.sacar(valor)
            c_destino.depositar(valor)
            print("Transferência concluída.")
        except KeyError:
            print("Conta origem/destino não encontrada.")
        except ValueError as e:
            print("Erro:", e)

    def listar(self):
        if not self.contas:
            print("Nenhuma conta cadastrada.")
            return
        print("\n== Contas ==")
        for c in self.contas.values():
            tipo = c.__class__.__name__
            print(f"[{tipo}] {c.exibir_saldo()}")

    def aplicar_regras(self):
        if not self.contas:
            print("Nenhuma conta cadastrada.")
            return
        for c in self.contas.values():
            c.end_of_day()
        print("Regras de end_of_day() aplicadas (polimorfismo).")

    def menu(self):
        opcoes = {
            "1": ("Criar conta", self.criar_conta),
            "2": ("Depositar", self.depositar),
            "3": ("Sacar", self.sacar),
            "4": ("Transferir", self.transferir),
            "5": ("Listar contas/saldos", self.listar),
            "6": ("Aplicar regras (end_of_day)", self.aplicar_regras),
            "0": ("Sair", None),
        }
        while True:
            print("\n=== Banco Aurora — Menu ===")
            for k, (label, _) in opcoes.items():
                print(f"{k} - {label}")
            escolha = input("> ").strip()
            if escolha == "0":
                print("Até mais!")
                break
            acao = opcoes.get(escolha, (None, None))[1]
            if acao:
                acao()
            else:
                print("Opção inválida.")


if __name__ == "__main__":
    BancoConsole().menu()

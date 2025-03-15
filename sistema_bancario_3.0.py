from abc import ABC, abstractmethod
from datetime import date

# Função para formatação monetária
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "temp").replace(".", ",").replace("temp", ".")

# Interface Transacao
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
    def registrar(self, conta):
        pass

# Classes de Transações
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)
            return True
        return False

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)
            return True
        return False

# Classe Historico
class Historico:
    def __init__(self):
        self._transacoes = []
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append((
            transacao.__class__.__name__,
            transacao.valor,
            date.today().strftime("%d/%m/%Y %H:%M:%S")
        ))
    
    def gerar_relatorio(self):
        return self._transacoes

# Classe Conta
class Conta:
    def __init__(self, cliente, numero, agencia):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = agencia
        self._cliente = cliente
        self._historico = Historico()
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            return True
        return False
    
    def sacar(self, valor):
        if valor > 0 and self._saldo >= valor:
            self._saldo -= valor
            return True
        return False

# Classe ContaCorrente
class ContaCorrente(Conta):
    def __init__(self, cliente, numero, agencia, limite=500, limite_saques=3):
        super().__init__(cliente, numero, agencia)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques_realizados = 0
    
    def sacar(self, valor):
        excedeu_limite = valor > self._limite
        excedeu_saques = self._saques_realizados >= self._limite_saques
        
        if excedeu_limite:
            print("\nErro: Valor excede o limite por saque!")
        elif excedeu_saques:
            print("\nErro: Limite diário de saques atingido!")
        else:
            if super().sacar(valor):
                self._saques_realizados += 1
                return True
        return False

# Classe Cliente
class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self._contas.append(conta)
    
    @property
    def contas(self):
        return self._contas

# Classe PessoaFisica
class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento
    
    @property
    def cpf(self):
        return self._cpf
    
    @property
    def nome(self):
        return self._nome
    
    @property
    def data_nascimento(self):
        return self._data_nascimento

# Funções auxiliares
def buscar_cliente(cpf, clientes):
    for cliente in clientes:
        if isinstance(cliente, PessoaFisica) and cliente.cpf == cpf:
            return cliente
    return None

def buscar_conta(numero_conta, contas):
    for conta in contas:
        if conta.numero == numero_conta:
            return conta
    return None

def criar_usuario(clientes):
    cpf = input("\nCPF (apenas números): ").strip()
    if buscar_cliente(cpf, clientes):
        print("\nErro: CPF já cadastrado!")
        return
    
    nome = input("Nome completo: ").strip()
    data_nasc = input("Data de nascimento (dd/mm/aaaa): ").strip()
    endereco = input("Endereço (logradouro, nº - bairro - cidade/UF): ").strip()
    
    try:
        dia, mes, ano = map(int, data_nasc.split('/'))
        data_nascimento = date(ano, mes, dia)
    except:
        print("\nErro: Formato de data inválido!")
        return
    
    clientes.append(PessoaFisica(cpf, nome, data_nascimento, endereco))
    print("\nUsuário cadastrado com sucesso!")

def criar_conta_corrente(clientes, contas, agencia):
    cpf = input("\nCPF do titular: ").strip()
    cliente = buscar_cliente(cpf, clientes)
    
    if not cliente:
        print("\nErro: Cliente não encontrado!")
        return
    
    numero_conta = len(contas) + 1
    conta = ContaCorrente(cliente, numero_conta, agencia)
    cliente.adicionar_conta(conta)
    contas.append(conta)
    print(f"\nConta {numero_conta} criada com sucesso!")

def listar_contas(contas):
    print("\n======== CONTAS ========")
    if not contas:
        print("Nenhuma conta cadastrada")
    else:
        for conta in contas:
            titular = conta.cliente
            print(
                f"Agência: {conta.agencia}\n"
                f"C/C: {conta.numero}\n"
                f"Titular: {titular.nome}\n"
                f"CPF: {titular.cpf}\n"
                "------------------------"
            )
    print("========================")

def exibir_extrato(conta):
    print("\n======== EXTRATO ========")
    transacoes = conta.historico.gerar_relatorio()
    
    if not transacoes:
        print("Nenhuma movimentação realizada.")
    else:
        for tipo, valor, data in transacoes:
            print(f"{data} - {tipo}: {formatar_valor(valor)}")
    
    print(f"\nSaldo atual: {formatar_valor(conta.saldo)}")
    print("========================")

# Sistema principal
def main():
    AGENCIA = "0001"
    clientes = []
    contas = []
    
    menu = """
======== SISTEMA BANCÁRIO ========
[d] Depositar
[s] Sacar
[e] Extrato
[u] Novo usuário
[c] Nova conta
[l] Listar contas
[q] Sair
==================================
"""
    
    while True:
        print(menu)
        opcao = input("Operação: ").strip().lower()
        
        if opcao == "d":
            numero_conta = int(input("\nNúmero da conta: "))
            conta = buscar_conta(numero_conta, contas)
            
            if not conta:
                print("\nErro: Conta não encontrada!")
                continue
            
            try:
                valor = float(input("Valor do depósito: "))
                transacao = Deposito(valor)
                conta.cliente.realizar_transacao(conta, transacao)
                print("\nDepósito realizado com sucesso!")
            except:
                print("\nErro: Valor inválido!")
        
        elif opcao == "s":
            numero_conta = int(input("\nNúmero da conta: "))
            conta = buscar_conta(numero_conta, contas)
            
            if not conta:
                print("\nErro: Conta não encontrada!")
                continue
            
            try:
                valor = float(input("Valor do saque: "))
                transacao = Saque(valor)
                conta.cliente.realizar_transacao(conta, transacao)
            except:
                print("\nErro: Valor inválido!")
        
        elif opcao == "e":
            numero_conta = int(input("\nNúmero da conta: "))
            conta = buscar_conta(numero_conta, contas)
            
            if not conta:
                print("\nErro: Conta não encontrada!")
                continue
            
            exibir_extrato(conta)
        
        elif opcao == "u":
            criar_usuario(clientes)
        
        elif opcao == "c":
            criar_conta_corrente(clientes, contas, AGENCIA)
        
        elif opcao == "l":
            listar_contas(contas)
        
        elif opcao == "q":
            print("\nEncerrando sistema...")
            break
        
        else:
            print("\nOperação inválida!")

if __name__ == "__main__":
    main()
import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
import hashlib
import random
import string
import threading
import time


class MinerClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.channel = grpc.insecure_channel('localhost:50052')
        self.stub = mine_grpc_pb2_grpc.apiStub(self.channel)


    def get_transaction_id(self):
        try:
            return self.stub.getTransactionId(mine_grpc_pb2.void()).result
        except:
            return -1

    def get_challenge(self, transaction_id):
        try:
            return self.stub.getChallenge(mine_grpc_pb2.transactionId(transactionId=transaction_id)).result
        except:
            return -1

    def get_transaction_status(self, transaction_id):
        try:
            return self.stub.getTransactionStatus(mine_grpc_pb2.transactionId(transactionId=transaction_id)).result
        except:
            return -1

    def get_winner(self, transaction_id):
        try:
            return self.stub.getWinner(mine_grpc_pb2.transactionId(transactionId=transaction_id)).result
        except:
            return -1

    def get_solution(self, transaction_id):
        try:
            return self.stub.getSolution(mine_grpc_pb2.transactionId(transactionId=transaction_id))
        except:
            return None

    def submit_challenge(self, transaction_id, solution):
        try:
            args = mine_grpc_pb2.challengeArgs(transactionId=transaction_id, clientId=self.client_id, solution=solution)
            return self.stub.submitChallenge(args).result
        except:
            return -1

 
    def mine_solution(self, challenge):
        """
        Executa a mineração até encontrar uma solução válida.
        Usa múltiplas threads para acelerar o processo.
        """
        print(f"⏳ Minerando com dificuldade {challenge} ... (sem limite de tempo)")

        found_solution = [None]
        stop_event = threading.Event()
        chars = string.ascii_letters + string.digits

        def worker():
            while not stop_event.is_set():
                candidate = ''.join(random.choices(chars, k=10))
                hash_result = hashlib.sha1(candidate.encode()).hexdigest()
                if hash_result[:challenge] == '0' * challenge:
                    found_solution[0] = candidate
                    stop_event.set()

     
        THREADS = 16
        threads = [threading.Thread(target=worker) for _ in range(THREADS)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()  

        return found_solution[0]



def mostrar_menu():
    print("\n=== MENU CLIENTE RPC ===")
    print("1. getTransactionID")
    print("2. getChallenge")
    print("3. getTransactionStatus")
    print("4. getWinner")
    print("5. getSolution")
    print("6. Mine")
    print("7. Sair")
    return input("Opção: ")



def run():
    try:
        client_id = int(input("Client ID: "))
    except:
        print("❌ ID deve ser numérico.")
        return

    miner = MinerClient(client_id)
    print(f"✅ Conectado ao servidor como Cliente {client_id}")

    while True:
        opcao = mostrar_menu()

        if opcao == '1':
            tid = miner.get_transaction_id()
            print(f"📦 TransactionID atual: {tid}")

        elif opcao == '2':
            tid = int(input("TransactionID: "))
            challenge = miner.get_challenge(tid)
            print(f"🎯 Desafio da transação {tid}: {challenge}")

        elif opcao == '3':
            tid = int(input("TransactionID: "))
            status = miner.get_transaction_status(tid)
            if status == 0:
                print("✅ Desafio já resolvido.")
            elif status == 1:
                print("⏳ Desafio pendente.")
            else:
                print("❌ TransactionID inválido.")

        elif opcao == '4':
            tid = int(input("TransactionID: "))
            winner = miner.get_winner(tid)
            if winner == -1:
                print("❌ TransactionID inválido.")
            elif winner == -1:
                print("⏳ Sem vencedor ainda.")
            else:
                print(f"🏆 Cliente vencedor: {winner}")

        elif opcao == '5':
            tid = int(input("TransactionID: "))
            sol = miner.get_solution(tid)
            if sol and sol.status != -1:
                print(f"📋 Status: {'Resolvido' if sol.status == 0 else 'Pendente'}")
                print(f"🔑 Solução: {sol.solution if sol.solution else '(ainda nenhuma)'}")
                print(f"🎯 Dificuldade: {sol.challenge}")
            else:
                print("❌ TransactionID inválido.")

        elif opcao == '6':
            print("\n🚀 Iniciando mineração...")
            tid = miner.get_transaction_id()
            challenge = miner.get_challenge(tid)
            if tid == -1 or challenge == -1:
                print("❌ Erro ao obter dados do servidor.")
                continue

            print(f"🎯 Transação {tid}, Dificuldade {challenge}")
            solution = miner.mine_solution(challenge)
            if not solution:
                print("⚠️ Nenhuma solução encontrada (algo inesperado).")
                continue

            print(f"💡 Solução encontrada: {solution}")
            result = miner.submit_challenge(tid, solution)

            if result == 1:
                print("🎉 Solução válida! Novo desafio gerado pelo servidor!")
            elif result == 0:
                print("❌ Solução inválida.")
            elif result == 2:
                print("⚠️ Desafio já foi resolvido por outro cliente.")
            else:
                print("❌ Erro na submissão.")

        elif opcao == '7':
            print("👋 Encerrando cliente...")
            break

        else:
            print("❌ Opção inválida.")


if __name__ == '__main__':
    run()

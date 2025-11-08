import grpc
from concurrent import futures
import hashlib
import random
import threading
import mine_grpc_pb2
import mine_grpc_pb2_grpc


class MinerServicer(mine_grpc_pb2_grpc.apiServicer):
    def __init__(self):
        self.transactions = {}
        self.current_transaction_id = -1  
        self.lock = threading.Lock()
        self._generate_new_challenge()


    def _generate_new_challenge(self):
        with self.lock:
            self.current_transaction_id += 1
            challenge = random.randint(1, 20)
            self.transactions[self.current_transaction_id] = {
                'challenge': challenge,
                'solution': '',
                'winner': -1,
                'solved': False
            }
            print(f"🆕 NOVO DESAFIO -> TransactionID={self.current_transaction_id}, Dificuldade={challenge}")

   
    def _verify_solution(self, challenge, solution):
        hash_result = hashlib.sha1(solution.encode()).hexdigest()
        return hash_result[:challenge] == '0' * challenge


    def getTransactionId(self, request, context):
        with self.lock:
            return mine_grpc_pb2.intResult(result=self.current_transaction_id)

    # ======================================================
    # RPC: RETORNA DESAFIO ASSOCIADO AO TRANSACTION ID
    # ======================================================
    def getChallenge(self, request, context):
        tid = request.transactionId
        with self.lock:
            if tid in self.transactions:
                return mine_grpc_pb2.intResult(result=self.transactions[tid]['challenge'])
            return mine_grpc_pb2.intResult(result=-1)

    # ======================================================
    # RPC: RETORNA STATUS DA TRANSAÇÃO (0 resolvido / 1 pendente)
    # ======================================================
    def getTransactionStatus(self, request, context):
        tid = request.transactionId
        with self.lock:
            if tid not in self.transactions:
                return mine_grpc_pb2.intResult(result=-1)
            solved = self.transactions[tid]['solved']
            return mine_grpc_pb2.intResult(result=0 if solved else 1)

    # ======================================================
    # RPC: SUBMISSÃO DE SOLUÇÃO PELO CLIENTE
    # ======================================================
    def submitChallenge(self, request, context):
        tid = request.transactionId
        cid = request.clientId
        sol = request.solution

        with self.lock:
            if tid not in self.transactions:
                return mine_grpc_pb2.intResult(result=-1)

            tx = self.transactions[tid]

            if tx['solved']:
                return mine_grpc_pb2.intResult(result=2)

            if self._verify_solution(tx['challenge'], sol):
                tx['solution'] = sol
                tx['winner'] = cid
                tx['solved'] = True
                print(f"✅ Cliente {cid} resolveu TransactionID={tid} | Solução: {sol}")

                # gera novo desafio em thread separada
                threading.Thread(target=self._generate_new_challenge, daemon=True).start()
                return mine_grpc_pb2.intResult(result=1)
            else:
                print(f"❌ Solução incorreta do cliente {cid} para TransactionID={tid}")
                return mine_grpc_pb2.intResult(result=0)

    # ======================================================
    # RPC: RETORNA CLIENTE VENCEDOR
    # ======================================================
    def getWinner(self, request, context):
        tid = request.transactionId
        with self.lock:
            if tid not in self.transactions:
                return mine_grpc_pb2.intResult(result=-1)
            return mine_grpc_pb2.intResult(result=self.transactions[tid]['winner'])

    # ======================================================
    # RPC: RETORNA STATUS + SOLUÇÃO + DIFICULDADE
    # ======================================================
    def getSolution(self, request, context):
        tid = request.transactionId
        with self.lock:
            if tid not in self.transactions:
                return mine_grpc_pb2.structResult(status=-1, solution="", challenge=0)
            tx = self.transactions[tid]
            return mine_grpc_pb2.structResult(
                status=0 if tx['solved'] else 1,
                solution=tx['solution'],
                challenge=tx['challenge']
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mine_grpc_pb2_grpc.add_apiServicer_to_server(MinerServicer(), server)
    server.add_insecure_port('[::]:50052')
    print("⛏️ Servidor de mineração ativo na porta 50052...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

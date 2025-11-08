import grpc
from concurrent import futures
import grpcCalc_pb2
import grpcCalc_pb2_grpc

class CalculatorServicer(grpcCalc_pb2_grpc.apiServicer):
    
    def add(self, request, context):
        result = request.numOne + request.numTwo
        return grpcCalc_pb2.result(num=result)
    
    def sub(self, request, context):
        result = request.numOne - request.numTwo
        return grpcCalc_pb2.result(num=result)
    
    def mul(self, request, context):
        result = request.numOne * request.numTwo
        return grpcCalc_pb2.result(num=result)
    
    def div(self, request, context):
        if request.numTwo == 0:
            
            return grpcCalc_pb2.result(num=-1)
        result = request.numOne // request.numTwo  
        return grpcCalc_pb2.result(num=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcCalc_pb2_grpc.add_apiServicer_to_server(CalculatorServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Servidor da Calculadora rodando na porta 50051...")
    print("Pressione Ctrl+C para parar o servidor")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
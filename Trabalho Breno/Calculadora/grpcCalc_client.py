import grpc
import grpcCalc_pb2
import grpcCalc_pb2_grpc

def mostrar_menu():
    print("\n=== CALCULADORA RPC ===")
    print("1. Adição (+)")
    print("2. Subtração (-)")
    print("3. Multiplicação (*)")
    print("4. Divisão (/)")
    print("5. Sair")
    return input("Escolha uma operação (1-5): ")

def obter_numeros():
    try:
        num1 = int(input("Digite o primeiro número: "))
        num2 = int(input("Digite o segundo número: "))
        return num1, num2
    except ValueError:
        print("Erro: Por favor, digite números inteiros!")
        return None, None

def executar_operacao(stub, operacao, num1, num2):
    request = grpcCalc_pb2.args(numOne=num1, numTwo=num2)
    
    try:
        if operacao == '1':
            response = stub.add(request)
            operacao_str = "adição"
            simbolo = "+"
        elif operacao == '2':
            response = stub.sub(request)
            operacao_str = "subtração"
            simbolo = "-"
        elif operacao == '3':
            response = stub.mul(request)
            operacao_str = "multiplicação"
            simbolo = "*"
        elif operacao == '4':
            response = stub.div(request)
            operacao_str = "divisão"
            simbolo = "/"
            
            
            if response.num == -1 and num2 == 0:
                print("❌ Erro: Divisão por zero!")
                return
        
        resultado = response.num
        print(f"✅ {num1} {simbolo} {num2} = {resultado}")
            
    except grpc.RpcError as e:
        print(f"❌ Erro de comunicação com o servidor: {e.code()} - {e.details()}")

def run():
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = grpcCalc_pb2_grpc.apiStub(channel)
        
        while True:
            opcao = mostrar_menu()
            
            if opcao == '5':
                print("Saindo da calculadora. Até logo!")
                break
            elif opcao in ['1', '2', '3', '4']:
                num1, num2 = obter_numeros()
                if num1 is not None and num2 is not None:
                    executar_operacao(stub, opcao, num1, num2)
            else:
                print("❌ Opção inválida! Escolha entre 1 e 5.")
                
    except grpc.RpcError as e:
        print(f"❌ Não foi possível conectar ao servidor: {e.details()}")
        print("Certifique-se de que o servidor está rodando na porta 50051")
    except KeyboardInterrupt:
        print("\nSaindo da calculadora. Até logo!")

if __name__ == '__main__':
    run()
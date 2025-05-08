import sys

def metropolis():
    pass
    # input: sInicial, temperatura, qIteracoes, rng
    # output: melhorSolucaoEncontrada
    # s = melhorSolucaoEncontrada = sInicial
    # for qIteracoes
    #   for s' in vizinhos(s, rng)
    #     delta = abs(f(s') - f(s))
    #     if s' > melhorSolucaoEncontrada
    #       melhorSolucaoEncontrada = s'
    #     if s' > s
    #       s = s'
    #     else if rand(rng) <= exp(-delta/temperatura)
    #       s = s'
    # return melhorSolucaoEncontrada

def simulated_annealing():
    pass
    # input: sInicial, temperaturaInicial, temperaturaFinal, m, r, rng
    # output: melhorSolucaoEncontrada
    # t = temperaturaInicial
    # melhorSolucaoEncontrada = s = sInicial
    # while t > temperaturaFinal
    #   algumas iteracoes com t constante
    #   s = metropolis(s, t, m, rng)
    #   if s > melhorSolucaoEncontrada
    #     melhorSolucaoEncontrada = s
    #   t = r*t
    # return melhorSolucaoEncontrada

def main():
    if(len(sys.argv) != 4):
        print("Uso incorreto, deve ser: python3 simulated_annealing.py <caminho_do_arquivo> <iterações> <variação>")
        sys.exit(1)

    filePath = sys.argv[1]
    iterations = sys.argv[2]
    variation = sys.argv[3]

    print(f"Caminho: {filePath}, Iterações: {iterations}, Variação: {variation}")

main()
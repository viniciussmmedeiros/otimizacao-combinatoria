import sys
import random
import math
import time

aliancas = None

def le_instancia(caminho):
    with open(caminho) as f:
        n, m = map(int, f.readline().split())
        aliancas = [tuple(map(int, line.split())) for line in f]
    return n, aliancas

# Função objetivo
def f(solucao):
    penalizacao = 0
    penitenciariasUsadas = len(set(solucao))
    for a, b in aliancas:
        if solucao[a - 1] == solucao[b - 1]:
            penalizacao += 10000
    return penitenciariasUsadas + penalizacao

# Gera os vizinhos
def gera_vizinhos(solucao, rng):
    vizinhos = solucao.copy()
    criminoso = rng.randint(0, len(solucao) - 1)
    penitenciariaAtual = vizinhos[criminoso]
    maiorIndicePenitenciaria = max(vizinhos)
    novaPenitenciaria = rng.choice([p for p in range(1, maiorIndicePenitenciaria + 2) if p != penitenciariaAtual])
    vizinhos[criminoso] = novaPenitenciaria
    return vizinhos

# Metropolis
# sInicial, t, n, r -> melhor solução encontrada
def metropolis(solucaoInicial, temperatura, iteracoes, rng, tempoInicio):
    # s = s* = sInicial
    solucao = solucaoInicial.copy()
    melhorSolucao = solucao.copy()
    melhorValor = f(melhorSolucao)

    # for n iterações do
    for _ in range(iteracoes):
        # for s' E N(s) em ordem aleatória (usa R) do
        solucaoVizinho = gera_vizinhos(solucao, rng)

        valorAtual = f(solucao)
        valorVizinho = f(solucaoVizinho)

        # delta = abs(f(s') - f(s))
        delta = abs(valorVizinho - valorAtual)

        # if s' é melhor que s then
        if valorVizinho < valorAtual:
            solucao = solucaoVizinho.copy()
            # if s' é melhor que s* then
            if valorVizinho < melhorValor:
                melhorSolucao = solucaoVizinho.copy()
                melhorValor = valorVizinho
        # else if rand(R) <= e^(-delta/T) then
        elif rng.random() < math.exp(-delta / temperatura):
            solucao = solucaoVizinho.copy()

    # return s*
    return melhorSolucao

# Simulated Annealing
# sInicial, Ti, Tf, m, r, rng -> melhor solução encontrada na busca
def simulated_annealing(solucaoInicial, temperaturaInicial, temperaturaFinal, iteracoes, taxaResfriamento, rng, tempoInicio):
    # t = Ti
    temperaturaAtual = temperaturaInicial

    # s* = s = sInicial
    melhorSolucao = solucaoAtual = solucaoInicial

    # while t >= Tf
    while temperaturaAtual >= temperaturaFinal:
        # s = metropolis(s,t,m,rng)
        solucaoAtual = metropolis(solucaoAtual, temperaturaAtual, iteracoes, rng, tempoInicio)
        # if s > s*
        if f(solucaoAtual) < f(melhorSolucao):
            # s* = s
            melhorSolucao = solucaoAtual
            tempoTranscorrido = time.time() - tempoInicio
            representacao = [(i + 1, p) for i, p in enumerate(melhorSolucao)]
            print(f"Tempo: {tempoTranscorrido:.2f}s, Melhor solução: {len(set(melhorSolucao))}, Representação: {representacao}")
        # t = r*t
        temperaturaAtual *= taxaResfriamento
    # return s*
    return melhorSolucao

def main():
    global aliancas
    if(len(sys.argv) != 4):
        print("Uso incorreto, deve ser: python3 simulated_annealing.py <caminho_do_arquivo> <iterações> <variação>")
        sys.exit(1)

    caminhoArquivo = sys.argv[1]
    iteracoes = int(sys.argv[2])
    semente = int(sys.argv[3])

    print(f"Caminho: {caminhoArquivo}, Iterações: {iteracoes}, Variação: {semente}")

    quantidadeCriminosos, aliancas = le_instancia(caminhoArquivo)

    tempoInicio = time.time()

    melhorSolucao = simulated_annealing(
        solucaoInicial=list(range(quantidadeCriminosos)), 
        temperaturaInicial=100, 
        temperaturaFinal=0.1, 
        iteracoes=iteracoes, 
        taxaResfriamento=0.99, 
        rng=random.Random(semente),
        tempoInicio=tempoInicio)
        
    tempoTranscorrido = time.time() - tempoInicio
    print(f"Tempo: {tempoTranscorrido:.2f}s, Melhor solução = {len(set(melhorSolucao))}")

main()
import sys
import random
import math
import time


def le_instancia(caminho):
    with open(caminho) as f:
        n, m = map(int, f.readline().split())
        aliancas = [tuple(map(int, line.split())) for line in f]

    # cria uma lista de listas, representando as alianças de cada criminoso para fácil acesso
    aliancasCriminoso = [[] for _ in range(n)]
    for a, b in aliancas:
        aliancasCriminoso[a - 1].append(b - 1)
        aliancasCriminoso[b - 1].append(a - 1)
    print(aliancasCriminoso)
    return n, aliancas, aliancasCriminoso

# Função objetivo
def f(solucao, aliancas):
    penalizacao = 0
    penitenciariasUsadas = len(set(solucao))
    for a, b in aliancas:
        if solucao[a - 1] == solucao[b - 1]:
            penalizacao += 10000
    return penitenciariasUsadas + penalizacao

# função de penaização, para evitar recalcular toda a função objetivo
def delta_f(solucao, criminoso, novaPenitenciaria, aliancasCriminoso):
    penalizacaoAntiga = 0
    penalizacaoNova = 0
    penitenciariaAntiga = solucao[criminoso]
    
    # calculamos a penalização da penitenciária antiga e da nova
    for aliado in aliancasCriminoso[criminoso]:
        if solucao[aliado] == penitenciariaAntiga:
            penalizacaoAntiga += 10000
        if solucao[aliado] == novaPenitenciaria:
            penalizacaoNova += 10000
    
    # calculamos o impacto da realocação do criminoso na quantidade de penitenciárias
    penitenciariasAntes = len(set(solucao))
    solucao_temp = solucao.copy()
    solucao_temp[criminoso] = novaPenitenciaria
    penitenciariasDepois = len(set(solucao_temp))
    deltaPenitenciarias = penitenciariasDepois - penitenciariasAntes
    
    return (penalizacaoNova - penalizacaoAntiga) + deltaPenitenciarias

# Gera os vizinhos
def gera_vizinhos(solucao, rng):
    vizinhos = solucao.copy()
    criminoso = rng.randint(0, len(solucao) - 1)
    penitenciariaAtual = vizinhos[criminoso]
    maiorIndicePenitenciaria = max(vizinhos)
    novaPenitenciaria = rng.choice([p for p in range(1, maiorIndicePenitenciaria + 2) if p != penitenciariaAtual])
    vizinhos[criminoso] = novaPenitenciaria
    return vizinhos, criminoso, novaPenitenciaria

# Metropolis
# sInicial, t, n, r -> melhor solução encontrada
def metropolis(solucaoInicial, temperatura, iteracoes, rng, tempoInicio, aliancas, aliancasCriminoso):
    # s = s* = sInicial
    solucao = solucaoInicial.copy()
    melhorSolucao = solucao.copy()
    valorAtual = f(melhorSolucao, aliancas)
    melhorValor = valorAtual

    # for n iterações do
    for _ in range(iteracoes):
        # for s' E N(s) em ordem aleatória (usa R) do
        solucaoVizinho, criminoso, novaPenitenciaria = gera_vizinhos(solucao, rng)
        
        # delta = abs(f(s') - f(s))
        delta = delta_f(solucao, criminoso, novaPenitenciaria, aliancasCriminoso)
        valorVizinho = valorAtual + delta

        # if s' é melhor que s then
        if valorVizinho < valorAtual:
            solucao = solucaoVizinho.copy()
            valorAtual = valorVizinho
            # if s' é melhor que s* then
            if valorVizinho < melhorValor:
                melhorSolucao = solucaoVizinho.copy()
                melhorValor = valorVizinho
        # else if rand(R) <= e^(-delta/T) then
        elif rng.random() < math.exp(-delta / temperatura):
            solucao = solucaoVizinho.copy()
            valorAtual = valorVizinho

    # return s*
    return melhorSolucao, melhorValor

# Simulated Annealing
# sInicial, Ti, Tf, m, r, rng -> melhor solução encontrada na busca
def simulated_annealing(solucaoInicial, temperaturaInicial, temperaturaFinal, iteracoes, taxaResfriamento, rng, tempoInicio, aliancas, aliancasCriminoso):
    # t = Ti
    temperaturaAtual = temperaturaInicial

    melhorValor = f(solucaoInicial, aliancas)

    # s* = s = sInicial
    melhorSolucao = solucaoAtual = solucaoInicial

    # while t >= Tf
    while temperaturaAtual >= temperaturaFinal:
        # s = metropolis(s,t,m,rng)
        solucaoAtual, valorAtual = metropolis(solucaoAtual, temperaturaAtual, iteracoes, rng, tempoInicio, aliancas, aliancasCriminoso)
        # if s > s*
        if valorAtual < melhorValor:
            # s* = s
            melhorSolucao = solucaoAtual
            melhorValor = valorAtual
            tempoTranscorrido = time.time() - tempoInicio
            representacao = [(i + 1, p) for i, p in enumerate(melhorSolucao)]
            print(f"Tempo: {tempoTranscorrido:.2f}s, Melhor solução: {len(set(melhorSolucao))}, Representação: {representacao}")
        # t = r*t
        temperaturaAtual *= taxaResfriamento
    # return s*
    return melhorSolucao

def main():
    if(len(sys.argv) != 4):
        print("Uso incorreto, deve ser: python3 simulated_annealing.py <caminho_do_arquivo> <iterações> <variação>")
        sys.exit(1)

    caminhoArquivo = sys.argv[1]
    iteracoes = int(sys.argv[2])
    semente = int(sys.argv[3])

    print(f"Caminho: {caminhoArquivo}, Iterações: {iteracoes}, Variação: {semente}")

    quantidadeCriminosos, aliancas, aliancasCriminoso = le_instancia(caminhoArquivo)

    tempoInicio = time.time()

    melhorSolucao = simulated_annealing(
        solucaoInicial=list(range(quantidadeCriminosos)), 
        temperaturaInicial=100, 
        temperaturaFinal=0.1, 
        iteracoes=iteracoes, 
        taxaResfriamento=0.99, 
        rng=random.Random(semente),
        tempoInicio=tempoInicio,
        aliancas=aliancas,
        aliancasCriminoso=aliancasCriminoso)
        
    tempoTranscorrido = time.time() - tempoInicio
    print(f"Tempo: {tempoTranscorrido:.2f}s, Melhor solução = {len(set(melhorSolucao))}")

main()
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

# Função para converter a representação por criminosos para representação por penitenciárias
def converte_representacao(solucao):
    # Identifica todas as penitenciárias usadas
    penitenciarias_usadas = set(solucao)

    # Cria uma lista de listas onde cada lista interna representa uma penitenciária
    representacao_por_penitenciaria = [[] for _ in range(len(penitenciarias_usadas))]

    # Mapeia IDs de penitenciárias para índices sequenciais (0 a N-1)
    mapeamento_penitenciarias = {id_pen: idx for idx, id_pen in enumerate(sorted(penitenciarias_usadas))}

    # Distribui os criminosos nas listas de suas respectivas penitenciárias
    for criminoso, penitenciaria in enumerate(solucao):
        idx_penitenciaria = mapeamento_penitenciarias[penitenciaria]
        representacao_por_penitenciaria[idx_penitenciaria].append(
            criminoso + 1)  # +1 porque os criminosos são numerados a partir de 1

    return representacao_por_penitenciaria

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

            representacao_por_penitenciaria = converte_representacao(melhorSolucao)

            print(f"Tempo: {tempoTranscorrido:.2f}s, Penitenciárias: {len(representacao_por_penitenciaria)}")
            print(f"Representação por penitenciária: {representacao_por_penitenciaria}")

        # t = r*t
        temperaturaAtual *= taxaResfriamento
    # return s*
    return melhorSolucao

def main():
    if len(sys.argv) != 4:
        print("Uso incorreto, deve ser: python3 simulated_annealing.py <caminho_do_arquivo> <iterações> <variação>")
        sys.exit(1)

    caminhoArquivo = sys.argv[1]
    iteracoes = int(sys.argv[2])
    semente = int(sys.argv[3])

    print(f"Caminho: {caminhoArquivo}, Iterações: {iteracoes}, Variação: {semente}")

    quantidadeCriminosos, aliancas, aliancasCriminoso = le_instancia(caminhoArquivo)

    tempoInicio = time.time()

    melhorSolucao = simulated_annealing(
        solucaoInicial=list(range(1, quantidadeCriminosos + 1)),
        # Começamos com cada criminoso em sua própria penitenciária
        temperaturaInicial=100,
        temperaturaFinal=0.1,
        iteracoes=iteracoes,
        taxaResfriamento=0.99,
        rng=random.Random(semente),
        tempoInicio=tempoInicio,
        aliancas=aliancas,
        aliancasCriminoso=aliancasCriminoso)
        
    tempoTranscorrido = time.time() - tempoInicio
    representacao_final = converte_representacao(melhorSolucao)
    print(f"Tempo total: {tempoTranscorrido:.2f}s, Número de penitenciárias: {len(representacao_final)}")
    print(f"Representação final por penitenciária: {representacao_final}")

main()
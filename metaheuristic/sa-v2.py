import sys
import random
import math
import time
from collections import defaultdict, Counter

# Instruções para execução em Linux:
# 1. É preciso ter o Python 3 instalado. Verificar com o comando: python3 --version
# 2. Considerando o arquivo simulated_annealing.py dentro da pasta 'metaheuristics', execute o comando:
#    python3 simulated_annealing.py <caminho_do_arquivo> <iterações> <variação>
#    - <caminho_do_arquivo>: Caminho para o arquivo instância de entrada.
#    - <iterações>: Número de iterações para o algoritmo.
#    - <variação>: Semente para o gerador de números aleatórios.
# Exemplo de execução:
#    python3 simulated_annealing.py instancia.txt 1000 3

# função para ler a instância do problema, criando as estruturas aliancas e aliancasCriminoso
def le_instancia(caminho):
    with open(caminho) as f:
        numeroCriminosos, _ = map(int, f.readline().split())
        # cria a tupla de alianças, ex [(1, 2), (6, 10), ...]
        aliancas = [tuple(map(int, line.split())) for line in f]

    # uma lista de listas, representando as alianças de cada criminoso para fácil acesso
    aliancasCriminoso = [[] for _ in range(numeroCriminosos)]
    for a, b in aliancas:
        aliancasCriminoso[a - 1].append(b - 1) # para o criminoso de índice a-1, adiciona o índice do criminoso b
        aliancasCriminoso[b - 1].append(a - 1) # para o criminoso b faz o inverso, adiciona o criminoso a

    return numeroCriminosos, aliancasCriminoso

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

# sInicial, t, n, r -> melhor solução encontrada
def metropolis(solucaoInicial, temperatura, iteracoes, rng, tempoInicio, aliancasCriminoso, valor_objetivo, prisioneiros_por_prisao, quantidadeCriminosos):
    # s = s* = sInicial
    solucao = solucaoInicial.copy()
    melhorSolucao = solucaoInicial.copy()
    melhorValorObjetivo = valorObjetivoAtual = valor_objetivo

    # for n iterações do
    for _ in range(iteracoes):
        # for s' E N(s) em ordem aleatória (usa R) do

        criminoso = rng.randint(0, len(solucao) - 1) # escolhe um criminoso aleatório, lembrando que len(solucao) é o número de criminosos
        penitenciariaAtual = solucao[criminoso]
        # o código [p for p in penitenciariasPossiveis if p != penitenciariaAtual] cria a lista de penitencárias tirando a que o criminoso está
        # rng choice escolhe aleatoriamente um item dessa lista
        novaPenitenciaria = rng.choice([p for p in range(len(solucao)) if p != penitenciariaAtual])

        # coloca o criminoso na nova penitenciária
        solucao[criminoso] = novaPenitenciaria
        
        novo_valor_objetivo = valorObjetivoAtual

        # decrementa o número de criminosos na penitenciáriaAtual (antiga)
        prisioneiros_por_prisao[penitenciariaAtual] -= 1

        # incrementa o número de criminosos na nova penitenciária
        prisioneiros_por_prisao[novaPenitenciaria] += 1

        # se a penitenciária antiga ficou sem criminosos, então decrementamos o valor objetivo
        if prisioneiros_por_prisao[penitenciariaAtual] == 0:
            novo_valor_objetivo -= 1

        # se a nova penitenciária passou a ter um criminoso, então incrementamos o valor objetivo
        if prisioneiros_por_prisao[novaPenitenciaria] == 1:
            novo_valor_objetivo += 1

        penalizacao = 0
        for aliado in aliancasCriminoso[criminoso]:
            if solucao[aliado] == novaPenitenciaria:
                # a penalização para aliados na mesma penitenciária é o próprio número de criminosos, que representa
                # a solução factível mais trivial possível
                penalizacao += quantidadeCriminosos 
        novo_valor_objetivo += penalizacao

        # se o valor objetivo após a troca de penitenciária é melhor do que o nosso melhor valor, então atualiza a melhor solução e o valor objetivo
        if novo_valor_objetivo < melhorValorObjetivo:
            melhorSolucao = solucao.copy()
            melhorValorObjetivo = novo_valor_objetivo

        # se o valor objetivo após a troca de penitenciária é melhor do que o nosso valor objetivo atual ou a troca foi aceita probabilisticamente
        # então atualizamos o valor objetivo atual e continuamos para a próxima iteração
        if novo_valor_objetivo < valorObjetivoAtual or rng.random() < math.exp(-(novo_valor_objetivo - valorObjetivoAtual) / temperatura):
            valorObjetivoAtual = novo_valor_objetivo
            # solucao já está atualizada
            continue
        else:
            # caso contrário, ou seja: a troca de penitenciária não melhorou o valor objetivo e não foi aceita probabilisticamente, nós revertemos
            # a atualização de penitenciária do criminoso 
            solucao[criminoso] = penitenciariaAtual
            prisioneiros_por_prisao[penitenciariaAtual] += 1
            prisioneiros_por_prisao[novaPenitenciaria] -= 1

    # return s*
    return melhorSolucao, melhorValorObjetivo, prisioneiros_por_prisao

# sInicial, Ti, Tf, m, r, rng -> melhor solução encontrada na busca
def simulated_annealing(solucaoInicial, temperaturaInicial, temperaturaFinal, iteracoes, taxaResfriamento, rng, tempoInicio, aliancasCriminoso, numeroCriminosos):
    # t = Ti
    temperaturaAtual = temperaturaInicial

    # s* = s = sInicial
    melhorSolucao = solucaoInicial.copy()
    solucaoAtual = solucaoInicial.copy()

    # o valor objetivo inicial é o trivial: quantiade de penitenciárias ativas = quantidade de criminosos
    valor_objetivo = len(solucaoInicial)
    
    # valor para fazer avaliação diferencial
    prisioneiros_por_prisao = Counter(solucaoInicial)

    # while t >= Tf
    while temperaturaAtual >= temperaturaFinal:
        # s = metropolis(s,t,m,rng)
        nova_solucao, novo_valor_objetivo, novo_prisioneiros_por_prisao = metropolis(solucaoAtual, temperaturaAtual, iteracoes, rng, tempoInicio, aliancasCriminoso, valor_objetivo, prisioneiros_por_prisao, numeroCriminosos)
        # if s > s* -- no caso <, pois estamos minimizando
        if novo_valor_objetivo < valor_objetivo:
            # s* = s
            melhorSolucao = nova_solucao.copy()
            valor_objetivo = novo_valor_objetivo
            prisioneiros_por_prisao = novo_prisioneiros_por_prisao
        
            tempoTranscorrido = time.time() - tempoInicio
            representacao_por_penitenciaria = converte_representacao(melhorSolucao)
            print(f"Tempo: {tempoTranscorrido:.2f}s, Penitenciárias: {len(representacao_por_penitenciaria)}")
            print(f"Representação por penitenciária: {representacao_por_penitenciaria}")

        # t = r*t
        temperaturaAtual *= taxaResfriamento
    # return s*
    return melhorSolucao

def main():
    caminhoArquivo = sys.argv[1]
    iteracoes = int(sys.argv[2])
    semente = int(sys.argv[3])
    temperaturaInicial = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    taxaResfriamento = float(sys.argv[5]) if len(sys.argv) > 5 else 0.99

    # print(f"Caminho: {caminhoArquivo}, Iterações: {iteracoes}, Variação: {semente}")

    quantidadeCriminosos, aliancasCriminoso = le_instancia(caminhoArquivo)

    tempoInicio = time.time()
    melhorSolucao = simulated_annealing(
        solucaoInicial=list(range(1, quantidadeCriminosos + 1)), # Começamos com cada criminoso em sua própria penitenciária
        temperaturaInicial=temperaturaInicial,
        temperaturaFinal=0.1,
        iteracoes=iteracoes,
        taxaResfriamento=taxaResfriamento,
        rng=random.Random(semente),
        tempoInicio=tempoInicio,
        aliancasCriminoso=aliancasCriminoso,
        numeroCriminosos=quantidadeCriminosos)
        
    tempoTranscorrido = time.time() - tempoInicio
    representacao_final = converte_representacao(melhorSolucao)
    print(f"Tempo total: {tempoTranscorrido:.2f}s, Número de penitenciárias: {len(representacao_final)}")
    print(f"Representação final por penitenciária: {representacao_final}")

main()
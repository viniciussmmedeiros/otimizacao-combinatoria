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
        representacao_por_penitenciaria[idx_penitenciaria].append(criminoso)

    return representacao_por_penitenciaria

# sInicial, t, n, r -> melhor solução encontrada
def metropolis(solucaoInicial, temperatura, iteracoes, rng, aliancasCriminoso, valorObjetivo,
               prisioneirosPorPrisao, quantidadeCriminosos):
    # s = s* = sInicial
    solucao = solucaoInicial.copy()
    melhorSolucao = solucaoInicial.copy()
    prisioneiros_por_prisao_atual = prisioneirosPorPrisao.copy()
    melhorValorObjetivo = valor_objetivo_atual = valorObjetivo

    # for n iterações do
    for _ in range(iteracoes):
        # for s' E N(s) em ordem aleatória (usa R) do

        # escolhe um criminoso aleatório, lembrando que len(solucao) é o número de criminosos
        criminoso = rng.randint(0, len(solucao) - 1)
        penitenciaria_atual = solucao[criminoso]

        # o código [p for p in penitenciariasPossiveis if p != penitenciaria_atual] cria a lista de penitencárias tirando a que o criminoso está
        # rng choice escolhe aleatoriamente um item dessa lista
        nova_penitenciaria = rng.choice([p for p in range(len(solucao)) if p != penitenciaria_atual])

        # salvamos o novo valor objetivo, ainda sem modificar a solução
        novo_valor_objetivo = valor_objetivo_atual

        # calculamos a quantidade de prisioneiros nas penitenciárias após a movimentação
        nova_qtd_penitenciaria_atual = prisioneiros_por_prisao_atual[penitenciaria_atual] - 1
        nova_qtd_penitenciaria_nova = prisioneiros_por_prisao_atual[nova_penitenciaria] + 1

        # se a penitenciária atual ficará vazia, então temos menos uma penitenciária ativa
        if nova_qtd_penitenciaria_atual == 0:
            novo_valor_objetivo -= 1

        # se a nova penitenciária estava vazia, então temos mais uma penitenciária ativa
        if prisioneiros_por_prisao_atual[nova_penitenciaria] == 0:
            novo_valor_objetivo += 1

        # calculamos as penalizações para a penitenciária antiga e para a nova
        penalizacao_nova = 0
        penalizacao_atual = 0
        for aliado in aliancasCriminoso[criminoso]:
            if solucao[aliado] == nova_penitenciaria:
                penalizacao_nova += quantidadeCriminosos
            if solucao[aliado] == penitenciaria_atual:
                penalizacao_atual += quantidadeCriminosos

        novo_valor_objetivo += penalizacao_nova - penalizacao_atual

        # verifica se aceita a mudança (solução melhor ou com rng.random)
        aceita_mudanca = (novo_valor_objetivo < valor_objetivo_atual or
                          rng.random() < math.exp(-(novo_valor_objetivo - valor_objetivo_atual) / temperatura))

        if aceita_mudanca:
            # coloca o criminoso na nova penitenciária
            solucao[criminoso] = nova_penitenciaria
            # atualiza o valor objetivo
            valor_objetivo_atual = novo_valor_objetivo
            # atualiza as quantidades de criminosos para as penitenciárias da movimentação
            prisioneiros_por_prisao_atual[penitenciaria_atual] = nova_qtd_penitenciaria_atual
            prisioneiros_por_prisao_atual[nova_penitenciaria] = nova_qtd_penitenciaria_nova

            # verifica se é a melhor solução encontrada
            if novo_valor_objetivo < melhorValorObjetivo:
                melhorSolucao = solucao.copy()
                melhorValorObjetivo = novo_valor_objetivo

    # return s*
    return solucao, valor_objetivo_atual, prisioneiros_por_prisao_atual

# sInicial, Ti, Tf, m, r, rng -> melhor solução encontrada na busca
def simulated_annealing(solucaoInicial, temperaturaInicial, temperaturaFinal, iteracoes, taxaResfriamento, rng,
                        tempoInicio, aliancasCriminoso, numeroCriminosos):
    # t = Ti
    temperaturaAtual = temperaturaInicial

    # s* = s = sInicial
    melhorSolucao = solucaoInicial.copy()
    solucaoAtual = solucaoInicial.copy()

    # valor objetivo inicial, tanto para o valor global quanto para a solução da iteração
    melhorValorObjetivo = valorObjetivoAtual = len(solucaoInicial)

    # contador para fazer avaliação diferencial
    prisioneiros_por_prisao = Counter(solucaoInicial)

    # while t >= Tf
    while temperaturaAtual >= temperaturaFinal:
        # s = metropolis(s,t,m,rng)
        nova_solucao, novo_valor_objetivo, novo_prisioneiros_por_prisao = metropolis(
            solucaoInicial=solucaoAtual,
            temperatura=temperaturaAtual,
            iteracoes=iteracoes,
            rng=rng,
            aliancasCriminoso=aliancasCriminoso,
            valorObjetivo=valorObjetivoAtual,
            prisioneirosPorPrisao=prisioneiros_por_prisao,
            quantidadeCriminosos=numeroCriminosos
        )

        # atualizamos a solução atual
        solucaoAtual = nova_solucao
        valorObjetivoAtual = novo_valor_objetivo
        prisioneiros_por_prisao = novo_prisioneiros_por_prisao

        # verificamos se encontramos uma melhor solução
        if novo_valor_objetivo < melhorValorObjetivo:
            melhorSolucao = nova_solucao.copy()
            melhorValorObjetivo = novo_valor_objetivo

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
        solucaoInicial=list(range(quantidadeCriminosos)), # Começamos com cada criminoso em sua própria penitenciária
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
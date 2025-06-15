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
            criminoso)

    return representacao_por_penitenciaria

# sInicial, t, n, r -> melhor solução encontrada
def metropolis(solucaoInicial, temperatura, iteracoes, rng, tempoInicio, aliancasCriminoso, valor_objetivo,
               prisioneiros_por_prisao, quantidadeCriminosos):
    # s = s* = sInicial
    solucao = solucaoInicial.copy()
    melhorSolucao = solucaoInicial.copy()
    melhorValorObjetivo = valorObjetivoAtual = valor_objetivo

    # Copia do contador para não modificar o original durante as tentativas
    prisioneiros_por_prisao_atual = prisioneiros_por_prisao.copy()

    # for n iterações do
    for _ in range(iteracoes):
        # Escolhe um criminoso aleatório
        criminoso = rng.randint(0, len(solucao) - 1)
        penitenciariaAtual = solucao[criminoso]

        # Escolhe uma nova penitenciária diferente da atual
        novaPenitenciaria = rng.choice([p for p in range(len(solucao)) if p != penitenciariaAtual])

        # Calcula o novo valor objetivo sem modificar a solução ainda
        novo_valor_objetivo = valorObjetivoAtual

        # Simulação da mudança no contador
        nova_qtd_atual = prisioneiros_por_prisao_atual[penitenciariaAtual] - 1
        nova_qtd_nova = prisioneiros_por_prisao_atual[novaPenitenciaria] + 1

        # Se a penitenciária atual ficará vazia
        if nova_qtd_atual == 0:
            novo_valor_objetivo -= 1

        # Se a nova penitenciária estava vazia
        if prisioneiros_por_prisao_atual[novaPenitenciaria] == 0:
            novo_valor_objetivo += 1

        # Calcula penalizações
        penalizacao_nova = 0
        penalizacao_atual = 0
        for aliado in aliancasCriminoso[criminoso]:
            if solucao[aliado] == novaPenitenciaria:
                penalizacao_nova += quantidadeCriminosos
            if solucao[aliado] == penitenciariaAtual:
                penalizacao_atual += quantidadeCriminosos

        novo_valor_objetivo += penalizacao_nova - penalizacao_atual

        # Verifica se aceita a mudança
        aceita_mudanca = (novo_valor_objetivo < valorObjetivoAtual or
                          rng.random() < math.exp(-(novo_valor_objetivo - valorObjetivoAtual) / temperatura))

        if aceita_mudanca:
            # Aplica a mudança
            solucao[criminoso] = novaPenitenciaria
            valorObjetivoAtual = novo_valor_objetivo
            prisioneiros_por_prisao_atual[penitenciariaAtual] = nova_qtd_atual
            prisioneiros_por_prisao_atual[novaPenitenciaria] = nova_qtd_nova

            # Verifica se é a melhor solução encontrada no Metropolis
            if novo_valor_objetivo < melhorValorObjetivo:
                melhorSolucao = solucao.copy()
                melhorValorObjetivo = novo_valor_objetivo

    # IMPORTANTE: Retorna a solução atual (não necessariamente a melhor do Metropolis)
    # Isso é correto para o Simulated Annealing, pois queremos continuar a partir da última solução aceita
    return solucao, valorObjetivoAtual, prisioneiros_por_prisao_atual


# sInicial, Ti, Tf, m, r, rng -> melhor solução encontrada na busca
def simulated_annealing(solucaoInicial, temperaturaInicial, temperaturaFinal, iteracoes, taxaResfriamento, rng,
                        tempoInicio, aliancasCriminoso, numeroCriminosos):
    # t = Ti
    temperaturaAtual = temperaturaInicial

    # s* = s = sInicial
    melhorSolucao = solucaoInicial.copy()
    solucaoAtual = solucaoInicial.copy()

    # SEPARAR: valor objetivo da melhor solução e da solução atual
    melhorValorObjetivo = len(solucaoInicial)  # Melhor valor objetivo encontrado GLOBALMENTE
    valorObjetivoAtual = len(solucaoInicial)  # Valor objetivo da solução atual

    # valor para fazer avaliação diferencial
    prisioneiros_por_prisao = Counter(solucaoInicial)

    # while t >= Tf
    while temperaturaAtual >= temperaturaFinal:
        # s = metropolis(s,t,m,rng)
        nova_solucao, novo_valor_objetivo, novo_prisioneiros_por_prisao = metropolis(
            solucaoAtual, temperaturaAtual, iteracoes, rng, tempoInicio,
            aliancasCriminoso, valorObjetivoAtual, prisioneiros_por_prisao, numeroCriminosos
        )

        # Atualizar solução atual (sempre, independente de ser melhor)
        solucaoAtual = nova_solucao
        valorObjetivoAtual = novo_valor_objetivo
        prisioneiros_por_prisao = novo_prisioneiros_por_prisao

        # Verificar se encontramos uma nova melhor solução GLOBAL
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
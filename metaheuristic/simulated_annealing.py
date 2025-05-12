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

    return numeroCriminosos, aliancas, aliancasCriminoso

# Função objetivo, com o objetivo de minimizar a quantidade de penitenciárias, considerando as penalizações
def f(solucao, aliancas):
    penalizacao = 0
    # a solução é uma lista contendo a informação de em qual penitenciária cada criminoso está, 
    # logo pegar o length do set disso (os valores distintos da lista) representa
    # quantas penitenciárias estão em uso
    penitenciariasUsadas = len(set(solucao))
    for a, b in aliancas:
        # se dois criminosos aliados estão na mesma penitenciária, adiciona penalização
        if solucao[a - 1] == solucao[b - 1]:
            penalizacao += 10000
    return penitenciariasUsadas + penalizacao

# função de penalização, para evitar recalcular toda a função objetivo
def delta_f(solucao, criminoso, novaPenitenciaria, aliancasCriminoso):
    penalizacaoAntiga = 0
    penalizacaoNova = 0
    penitenciariaAntiga = solucao[criminoso]
    
    # calculamos a penalização da penitenciária antiga e da nova para cada aliado do criminoso usado na movimentação
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
    # o delta então é basicamente o s' - s
    deltaPenitenciarias = penitenciariasDepois - penitenciariasAntes
    
    # retornamos o s'-s + penalização, seguindo a ideia da função objetivo e de factibilização
    return deltaPenitenciarias + (penalizacaoNova - penalizacaoAntiga)

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

def gera_vizinhos(solucao, rng, temperatura):
    vizinhos = []
    deltas = []
    criminososSelecionados = []
    novasPenitenciarias = []
    
    # Usamos a temperatura para ajudar a definir a quantidade de vizinhos, tentando explorar
    # ainda mais o espaço de soluções no início.
    numVizinhos = max(1, int(temperatura / 10)) # garante que pelo menos 1 vizinho seja selecionado quando temperatura estiver muito baixa
    
    maiorIndicePenitenciaria = max(solucao) # pega o maior valor de penitenciária em uso
    penitenciariasPossiveis = list(range(1, maiorIndicePenitenciaria + 2)) # incrementa em 2 para tentar sair de um ótimo local
    
    for _ in range(numVizinhos):
        criminoso = rng.randint(0, len(solucao) - 1) # escolhe um criminoso aleatório, lembrando que len(solucao) é o número de criminosos
        penitenciariaAtual = solucao[criminoso]
        # o código [p for p in penitenciariasPossiveis if p != penitenciariaAtual] cria a lista de penitencárias tirando a que o criminoso está
        # rng choice escolhe aleatoriamente um item dessa lista
        novaPenitenciaria = rng.choice([p for p in penitenciariasPossiveis if p != penitenciariaAtual])
        
        vizinho = solucao.copy()
        vizinho[criminoso] = novaPenitenciaria
        
        # cada vizinho difere da solução atual por uma única movimentação
        vizinhos.append(vizinho)
        criminososSelecionados.append(criminoso)
        novasPenitenciarias.append(novaPenitenciaria)
    
    return vizinhos, criminososSelecionados, novasPenitenciarias

# Utiliza um algoritmo guloso de coloração de grafos para criar uma solução inicial.
# Cada cor representa uma penitenciária.
def solucao_inicial_por_coloracao(quantidadeCriminosos, aliancas):
    # Construir o grafo de adjacência
    grafo = defaultdict(set)
    for a, b in aliancas:
        grafo[a].add(b)
        grafo[b].add(a)

    # Inicializar a solução (cores/penitenciárias)
    solucao = [0] * quantidadeCriminosos

    # Ordem de processamento: começar pelos vértices de maior grau
    criminosos_ordenados = sorted(range(1, quantidadeCriminosos + 1),
                                  key=lambda x: len(grafo[x]),
                                  reverse=True)

    # Coloração gulosa (primeiro encaixe)
    for criminoso in criminosos_ordenados:
        # Cores já usadas pelos vizinhos
        cores_vizinhos = {solucao[vizinho - 1] for vizinho in grafo[criminoso]
                          if solucao[vizinho - 1] != 0}

        # Encontra a primeira cor disponível
        cor = 1
        while cor in cores_vizinhos:
            cor += 1

        solucao[criminoso - 1] = cor

    print("solucao_inicial_por_coloracao", solucao)
    return solucao

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
        vizinhos, criminosos, novasPenitenciarias = gera_vizinhos(solucao, rng, temperatura)
        
        for vizinho, criminoso, novaPenitenciaria in zip(vizinhos, criminosos, novasPenitenciarias):
            # delta = abs(f(s') - f(s))
            delta = delta_f(solucao, criminoso, novaPenitenciaria, aliancasCriminoso)
            # o delta é basicamente a diferença entre a penitenciária antiga e a nova + penalização, então podemos
            # considerar o valor do vizinho como o valor atual + o delta
            valorVizinho = valorAtual + delta

            # if s' é melhor que s then
            if valorVizinho < valorAtual:
                solucao = vizinho.copy()
                valorAtual = valorVizinho
                # if s' é melhor que s* then
                if valorVizinho < melhorValor:
                    melhorSolucao = vizinho.copy()
                    melhorValor = valorVizinho
                # Aceita o primeiro vizinho que melhora, saindo fora do for
                break
            # else if rand(R) <= e^(-delta/T) then
            elif rng.random() < math.exp(-delta / temperatura):
                solucao = vizinho.copy()
                valorAtual = valorVizinho
                # Se aceitou a solução probabilisticamente, então respeitamos a temperatura / rng e também interrompe o for
                break

    # return s*
    return melhorSolucao, melhorValor

# sInicial, Ti, Tf, m, r, rng -> melhor solução encontrada na busca
def simulated_annealing(solucaoInicial, temperaturaInicial, temperaturaFinal, iteracoes, taxaResfriamento, rng, tempoInicio, aliancas, aliancasCriminoso):
    # t = Ti
    temperaturaAtual = temperaturaInicial

    # usamos melhorValor e valorAtual retornado pelo metropolis, evitando recalcular f(s) na condicional if do laço while
    melhorValor = f(solucaoInicial, aliancas)

    # s* = s = sInicial
    melhorSolucao = solucaoAtual = solucaoInicial

    # while t >= Tf
    while temperaturaAtual >= temperaturaFinal:
        # s = metropolis(s,t,m,rng)
        solucaoAtual, valorAtual = metropolis(solucaoAtual, temperaturaAtual, iteracoes, rng, tempoInicio, aliancas, aliancasCriminoso)
        # if s > s* -- no caso <, pois estamos minimizando
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
    if len(sys.argv) != 6:
        print("Uso incorreto, deve ser: python3 simulated_annealing.py <caminho_do_arquivo> <iterações> <variação>")
        sys.exit(1)

    caminhoArquivo = sys.argv[1]
    iteracoes = int(sys.argv[2])
    semente = int(sys.argv[3])
    temperaturaInicial = int(sys.argv[4])
    taxaResfriamento = float(sys.argv[5])

    # print(f"Caminho: {caminhoArquivo}, Iterações: {iteracoes}, Variação: {semente}")

    quantidadeCriminosos, aliancas, aliancasCriminoso = le_instancia(caminhoArquivo)

    tempoInicio = time.time()
    melhorSolucao = simulated_annealing(
        solucaoInicial=solucao_inicial_por_coloracao(quantidadeCriminosos, aliancas),
        temperaturaInicial=temperaturaInicial,
        temperaturaFinal=0.1,
        iteracoes=iteracoes,
        taxaResfriamento=taxaResfriamento,
        rng=random.Random(semente),
        tempoInicio=tempoInicio,
        aliancas=aliancas,
        aliancasCriminoso=aliancasCriminoso)
        
    tempoTranscorrido = time.time() - tempoInicio
    representacao_final = converte_representacao(melhorSolucao)
    print(f"Tempo total: {tempoTranscorrido:.2f}s, Número de penitenciárias: {len(representacao_final)}")
    print(f"Representação final por penitenciária: {representacao_final}")

main()
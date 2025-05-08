import sys
import random
import math
import time

# Função objetivo -- formulação da separação dos comparsas
def f(x):
    return x

# Gera os vizinhos em ordem aleatória
def generate_neighbors(s, rng):
    n = [s + 1, s - 1]
    rng.shuffle(n)
    return n

# Metropolis
# sInicial, t, n, r -> melhor solução encontrada
def metropolis(sInicial, t, n, r, startTime):
    # s = s* = sInicial
    s = best = sInicial
    # for n iterações do
    for _ in range(n):
        # for s' E N(s) em ordem aleatória (usa R) do
        for s_prime in generate_neighbors(s, r):
            # delta = abs(f(s') - f(s))
            delta = abs(f(s_prime) - f(s))
            # if s' é melhor que s* then
            if f(s_prime) > f(best):
                # s* = s'
                best = s_prime
                dTime = time.time() - startTime
                print(f"Tempo: {dTime:.2f}s, Melhor solução: x = {best}")
            # if s' é melhor que s then
            if f(s_prime) > f(s):
                # s = s'
                s = s_prime
            # else if rand(R) <= e^(-delta/T) then
            elif r.random() <= math.exp(-delta / t):
                # s = s'
                s = s_prime
    # return s*
    return best

# Simulated Annealing
# sInicial, Ti, Tf, m, r, rng -> melhor solução encontrada na busca
def simulated_annealing(sInicial, ti, tf, m, r, rng):
    # t = Ti
    t = ti
    # s* = s = sInicial
    best = s = sInicial

    startTime = time.time()

    # while t >= Tf
    while t >= tf:
        # s = metropolis(s,t,m,rng)
        s = metropolis(s, t, m, rng, startTime)
        # if s > s*
        if f(s) > f(best):
            # s* = s
            best = s
            dTime = time.time() - startTime
            print(f"Tempo: {dTime:.2f}s, Melhor solução: x = {best}")
        # t = r*t
        t *= r
    # return s*
    return best

def main():
    if(len(sys.argv) != 4):
        print("Uso incorreto, deve ser: python3 simulated_annealing.py <caminho_do_arquivo> <iterações> <variação>")
        sys.exit(1)

    filePath = sys.argv[1]
    iterations = sys.argv[2]
    variation = sys.argv[3]

    print(f"Caminho: {filePath}, Iterações: {iterations}, Variação: {variation}")


    best = simulated_annealing(0, ti=100, tf=0.1, m=10, r=0.95, rng=random.Random())
    print(f"Melhor solução encontrada: x = {best}")

main()
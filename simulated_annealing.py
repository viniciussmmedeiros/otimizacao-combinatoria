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


simulated_annealing()

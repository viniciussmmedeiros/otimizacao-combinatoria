# Instruções para execução em Linux

1. É preciso ter o Python 3 instalado. Verificar com o comando:
   ```bash
   python3 --version
2. Considerando o arquivo `simulated_annealing.py` dentro do diretório `metaheuristics`, execute o comando:
   ```bash
   python3 simulated_annealing.py <path_to_file> <iterations> <variation>

3. > caminho_do_arquivo: Caminho para o arquivo instância de entrada.
   > iterações: Número de iterações para o algoritmo.
   > variacão: Semente para o gerador de números aleatórios.

  
4. Exemplo de execução: 
   ```bash
   python3 simulated_annealing.py instancia.txt 1000 3
   ```
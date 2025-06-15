# Instruções para execução em Linux

1. É preciso ter a linguagem Julia instalada. Verificar com o comando:
   ```bash
   julia --version
2. Considerando o arquivo `formulation.jl` dentro do diretório `formulation`, execute o comando:
   ```bash
   julia formulation.jl <caminho_do_arquivo> <limite_tempo> <semente>

3. > caminho_do_arquivo: Caminho para o arquivo instância de entrada.
   > limite_tempo: Limite de tempo definido para o solver.
   > semente: Semente para o solver.

4. Exemplo de execução: 
   ```bash
   julia formulation.jl <caminho_do_arquivo>/06.txt 300 1
   ```

https://julialang.org/downloads/
# Para tornar mais rápida a execução:
# * Executar os comandos antes de `m = Model(...)` em um terminal,
#   comentar o `main()` no final do arquivo. Então executar
#   `Revise.includet("q1.jl")`, daí se pode só editar o arquivo e chamar
#   `main()` para executar novamente.
import Pkg
Pkg.activate(@__DIR__)
Pkg.instantiate()

using JuMP
using HiGHS
using Revise

function main()
	m = Model(HiGHS.Optimizer)

	# 10b até 10d
	# 10b: colocar instruções para execução em linux
	# 10c: -
	# 10d: parâmetros por linha de comando:
	#	i - caminho até o arquivo de entrada (incluindo o nome)
	#  ii - valor que controla o critério de parada 
	#		(tempo, usar set_time_limit_sec(model, parse(Int, seconds))
	# iii - semente de aleatoriedade 
	#		(obrigatória, set_attribute(model, "random_seed", seed_parametro))

	caminho_arquivo = ARGS[1]
	criterio_parada = parse(Int, ARGS[2])
	semente = parse(Int, ARGS[3])
	num_criminosos = 0
	aliancas = Tuple{Int, Int}[]

	# 10d: i
	open(caminho_arquivo, "r") do f
		# lendo a primeira linha
		s = split(readline(f))
		num_criminosos = parse(Int, s[1])
		num_aliancas = parse(Int, s[2])
		
		# lendo o restante das linhas
		for _ in 1:num_aliancas
			s = split(readline(f))
			i = parse(Int, s[1])
			j = parse(Int, s[2])
			push!(aliancas, (i, j))
		end
	end

	# 10d: ii
	set_time_limit_sec(m, criterio_parada)
	
	# 10d: iii
	set_attribute(m, "random_seed", semente)

	# consideramos o pior caso onde número de penitenciárias = número de criminosos
	num_penitenciarias = num_criminosos

	# Xij E B para todo i E [n] e para todo j E [n], variável binária representando
	# se um criminoso está ou não em uma penitenciária
	@variable(m, x[1:num_criminosos, 1:num_penitenciarias], Bin)

	# Yj E B para todo j E [n], variável binária representando se uma penitenciária
	# está ou não em uso
	@variable(m, y[1:num_penitenciarias], Bin)

	# Yj deve ser 1 se alguém estiver na penitenciária j
	# Xij <= Yj para todo i E [n] e para todo j E [n]
	for j in 1:num_penitenciarias
		for i in 1:num_criminosos
			@constraint(m, x[i, j] <= y[j])
		end
	end

	# um criminoso deve estar em apenas uma penitenciária
	for i in 1:num_criminosos
		@constraint(m, sum(x[i, j] for j in 1:num_penitenciarias) == 1)
	end

	# dois criminosos da mesma aliança não podem estar na mesma penitenciária
	for k in 1:num_penitenciarias
		for (i, j) in aliancas
			@constraint(m, x[i, k] + x[j, k] <= 1)
		end
	end

	# o objetivo é minimizar o somatório de penitenciárias ativas (uns em y)
	@objective(m, Min, sum(y[j] for j in 1:num_penitenciarias))

	optimize!(m)

	# formulation here

	optimize!(m)
	@show objective_value(m)
	# @show value(single_var)
	# @show value.(vector of variables)
end

main() # comentar aqui se for executar no terminal Julia


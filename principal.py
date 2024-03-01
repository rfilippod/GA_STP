from itertools import groupby
import random
import sys
import numpy as np
import entrada1
import entradas1_semana as semana
import fitness
import copy
import operator
from collections import Counter
import time
from xlwt import Workbook
from datetime import datetime
import csv
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#
tamanho_populacao = int(sys.argv[2])
geracoes = int(sys.argv[3])

seed = 2
cruzamento = int(sys.argv[4])
elitismo = int(sys.argv[5])
# tamanho_populacao = int(10)
# geracoes = int(10)
crossover_rate = 0.2
c = 0
random.seed(seed)
rng = np.random.default_rng(seed) # seed específica numpy
pElite = int((tamanho_populacao / 100) * 10)
sheet = []
wb = Workbook()
coluna_excel = 0
inst = str(sys.argv[1])
sheet1 = wb.add_sheet('Resultados', cell_overwrite_ok=True)


def retorna_matriz():
    matriz_horario = np.full((semana.linha_semana, semana.coluna_semana), 'aaaaaaaa')
    return matriz_horario


def cria_populacao(tamanho_populacao):
    populacao_total = {}

    for i in range(tamanho_populacao):
        z = random.randint(0, 2)
        entrada_shuffle = copy.deepcopy(entrada1.matriz_inicial)
        populacao = {}
        entrada_shuffle[z] = copy.deepcopy(rng.permuted(entrada1.matriz_inicial[z]))
        nota = fitness.Avaliacao(entrada_shuffle)
        populacao[0] = copy.deepcopy(entrada_shuffle)
        populacao[1] = nota.calcula()
        populacao_total[i] = copy.deepcopy(populacao)
    return populacao_total


"""
Função para ordenação do dicionário. A ordenação é feita da menor função objetivo para a maior. 
"""


def ordena_dict(dicionario):
    aux = {}
    dic = {}
    for i in range(len(dicionario)):
        # print(f'\n\n\n\n dic \n{dicionario}\n')
        # print(f'\ni = {i}\n')
        aux[i] = copy.deepcopy(dicionario[i][1])

    sorted_dic = sorted(aux.items(), key=operator.itemgetter(1))

    for i in range(len(dicionario)):
        dic[i] = copy.deepcopy(dicionario[sorted_dic[i][0]])

    return dic


def crossover(parent1, parent2):
    ncover = 7
    if cruzamento == 0:
        return two_point(parent1, parent2, ncover)
    else:
        return custom_crossover(parent1, parent2)


def twopoint(parent1, parent2, ncover = 1):
    for x in range(ncover):
        child = copy.deepcopy(parent1)
        z = random.randint(0, 2)
        parent1_array = list((np.asarray(parent1[z])).flatten())
        del_parent1_array = copy.deepcopy(parent1_array)
        parent2_array = list((np.asarray(parent2[z])).flatten())
        one_point = random.randint(0, len(parent1_array)//2)
        two_point = random.randint(len(parent1_array)//2, len(parent1_array))
        del del_parent1_array[one_point:two_point]
        contagem = Counter(del_parent1_array)

        for i in range(semana.coluna_semana):
            for j, k in zip(range(semana.linha_semana), range(one_point)):
                child[z][i][j] = parent1_array[k]
        for i in range(semana.coluna_semana):
            for j, k in zip(range(semana.linha_semana), range(two_point, len(parent2_array))):
                child[z][i][j] = parent1_array[k]

        for i in range(semana.coluna_semana):
            for j, k in zip(range(semana.linha_semana), range(one_point, two_point)):
                if parent1_array[k] not in contagem:
                    try:
                        child[z][i][j] = parent2_array[k]
                    except ValueError:
                        pass
                else:
                    contagem[parent2_array[k]] -= - 1
                    if contagem[parent2_array[k]] < 0:
                        child[z][i][j] = parent2_array[k]

    return child


def custom_crossover(parent1, parent2, ncover=1):
    child = copy.deepcopy(parent1)
    for x in range(ncover):
        for i in range(len(parent1)):
            if random.random() < crossover_rate:
                crossover_point = random.randint(0, len(parent1) - 1)
                for j in range(len(parent1)):
                    try:
                        if parent1[i][crossover_point][j] not in child[i][:, j]:
                            child[i][crossover_point][j] = parent1[i][crossover_point][j]
                        elif parent2[i][crossover_point][j] not in child[i][:, j]:
                            child[i][crossover_point][j] = parent2[i][crossover_point][j]
                    except:
                        pass
    return child
    

def retorna_elite(dic_ordenado):
    elite = {}
    for i in range(pElite):
        elite[i] = copy.deepcopy(dic_ordenado[i])
    return elite


def mutation(child):
    z = random.randint(0, 2)
    filho = {}
    filhos = {}
    while True:
        rand = float("%.4f" % random.random())
        if rand <= 0.1:
            child[z] = copy.deepcopy(rng.permuted(child[z]))
            filho[0] = copy.deepcopy(child)
            nota = fitness.Avaliacao(child).calcula()
            filho[1] = nota
            filhos[0] = copy.deepcopy(filho)
            # filhos = copy.deepcopy(ordena_dict(filhos))
            return filhos[0]


def cria_mutante(mut):
    mutante = copy.deepcopy(mut)
    for z in range(len(mutante)):
        mutante[(tamanho_populacao) - pElite] = mutation(mutante[z][0])
    # print(f'\n\n\n\n mut {mut}')
    # print(f'\n\n\n\n mut {mutante[9]}')
    # print(f'\n\n\n\n mut {len(mutante)}')
    return mutante



def escreve_excel(t_total, solucao, populacao, geracao, cros, metodo):
    today = datetime.today()
    # dd/mm/YY
    d1 = today.strftime("%d-%m-%Y")
    with open('resultados.csv', 'a', encoding='UTF8') as f:
        f.write(f'\n{sys.argv[1]};')
        f.write(f'{"%.4f" % t_total};')
        f.write(f'{solucao};')
        f.write(f'{populacao};')
        f.write(f'{geracao};')
        f.write(f'{cros};')
        f.write(f'{metodo};')
        f.write(f'{today}')


def cria_geracao(parents):
    filho = {}
    filhos = {}
    for i in range(pElite, (tamanho_populacao - pElite)):
        if elitismo == 0:
            z = random.randint(0, tamanho_populacao - pElite - pElite)
            y = random.randint(0, tamanho_populacao - pElite - pElite)
        else:
            z = random.randint(0, pElite)
            y = random.randint(0, tamanho_populacao - pElite - pElite)
        filho_horario = copy.deepcopy(crossover(parents[z][0], parents[y][0]))
        nota = fitness.Avaliacao(filho_horario)
        # print(f'\n\n\n\n filho {filho}')
        filho[0] = copy.deepcopy(filho_horario)
        filho[1] = nota.calcula()
        filhos[i] = copy.deepcopy(filho)
    return filhos


def codifica(geracao):
    codigo = []
    flat_list = [item for sublist in geracao[geracoes - 1][0][0][0].tolist() for item in sublist] + \
                [item for sublist in geracao[geracoes - 1][0][0][1].tolist() for item in sublist] + \
                [item for sublist in geracao[geracoes - 1][0][0][2].tolist() for item in sublist]
    flat_list.sort()
    for i in range(len(flat_list)):
        codigo.append(float("%.4f" % random.uniform(0, 1)))
    res = {codigo[i]: flat_list[i] for i in range(len(flat_list))}
    return res



def main():
    parent = random.randint(0, tamanho_populacao)
    populacao_total = cria_populacao(tamanho_populacao)
    filho_horario = {}
    teste = {}
    geracao = {}
    filho = {}
    filhos = {}
    geracao_final = {}
    codigo = []
    # for i in populacao_total.values():
    #     print(f'\n{i[0]}')

    dic_ordenado = copy.deepcopy(ordena_dict(populacao_total))
    # dic_ordenado[0][1] = 100
    # print(f'\n\n\n\n\n\n\n dic_ordenado[0][1] {dic_ordenado[0][1]}')
    pop = copy.deepcopy(retorna_elite(dic_ordenado)) # recebe os elites da geração anterior
    pop.update(cria_geracao(dic_ordenado)) # insere após o inicio o restante da geração
    pop_ordenada = copy.deepcopy(ordena_dict(pop))
    for j in range(geracoes):
        pop = copy.deepcopy(retorna_elite(pop_ordenada))  # recebe os elites da geração anterior
        pop.update(cria_geracao(pop_ordenada))
        pop.update(cria_mutante(pop_ordenada))
        pop_ordenada = copy.deepcopy(ordena_dict(pop))
        geracao_final[j] = copy.deepcopy(pop_ordenada)
    # print(f'\n\n\n\n\n\n geracao_final {geracao_final[geracoes-1][0]}\n\n\n\n')
    # antiga criação de gerações aqui
    return geracao_final[geracoes-1][0]


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    start_time = time.time()
    melhor = main()
    total_time = time.time() - start_time
    # print("--- %s seconds ---" % (time.time() - start_time))
    if cruzamento == 0:
        cros = '2point'
    else:
        cros = 'custom'
    if elitismo == 0:
        metodo = 'Sem elitismo'
    else:
        metodo = 'Com elitismo'
    print(f'Fim: {"%.4f" % total_time, melhor[1], tamanho_populacao, geracoes, cros, metodo}')
    escreve_excel(total_time, melhor[1], tamanho_populacao, geracoes, cros, metodo)

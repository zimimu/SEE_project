import random
import numpy as np
from copy import deepcopy


# 遗传算法参数
POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.8


# 计算每个时间点的资源需求
def calculate_resource_profile(schedule, max_time):
    resource_profile = [0] * max_time
    for task in schedule:
        for t in range(task["start_time"], task["end_time"] + 1):
            if t < max_time:
                resource_profile[t] += task["resource_needed"]
    return resource_profile


# 计算资源需求的标准差作为适应度函数
def calculate_fitness(schedule, max_project_duration=None):
    # 最大结束时间
    max_end_time = max(task["end_time"] for task in schedule)
    if max_project_duration is not None and max_end_time >= max_project_duration:
        return 0.001, [], max_end_time

    # 计算每个时刻的资源需求
    resource_profile = calculate_resource_profile(schedule, max_end_time + 1)
    std_dev = np.std(resource_profile) if resource_profile else 0
    total_duration = max_end_time

    # 适应度
    fitness = 1 / (std_dev + 0.1 * total_duration + 0.001)
    return fitness, resource_profile, total_duration


# 初始化种群
def initialize_population(tasks, population_size, max_project_duration=None):
    population = []

    # 计算理论最大工期（所有任务串行）
    theoretical_max_duration = sum(task["duration"] for task in tasks)

    # 如果设置了最大工期约束，使用较小值
    max_duration = min(theoretical_max_duration,
                       max_project_duration) if max_project_duration is not None else theoretical_max_duration

    for _ in range(population_size):
        individual = deepcopy(tasks)
        # 随机分配开始时间
        for task in individual:
            # 允许的最大开始时间
            max_start_time = max_duration - task["duration"]
            task["start_time"] = random.randint(0, max(max_start_time, 0))
            task["end_time"] = task["start_time"] + task["duration"] - 1
        population.append(individual)
    return population


# 选择操作（锦标赛选择）
def tournament_selection(population, fitness_scores, tournament_size=3):
    selected = []
    for item in range(len(population)):
        tournament = random.sample(range(len(population)), tournament_size)

        # 选择适应度最高的个体
        best_idx = max(tournament, key=lambda i: fitness_scores[i])
        selected.append(deepcopy(population[best_idx]))
    return selected


# 交叉操作
def crossover(parent1, parent2):
    if random.random() > CROSSOVER_RATE:
        return deepcopy(parent1), deepcopy(parent2)

    child1 = deepcopy(parent1)
    child2 = deepcopy(parent2)

    # 随机选择交叉点
    crossover_point = random.randint(0, len(parent1) - 1)

    # 交换任务的开始时间
    for i in range(crossover_point, len(parent1)):
        child1[i]["start_time"] = parent2[i]["start_time"]
        child1[i]["end_time"] = child1[i]["start_time"] + child1[i]["duration"] - 1

        child2[i]["start_time"] = parent1[i]["start_time"]
        child2[i]["end_time"] = child2[i]["start_time"] + child2[i]["duration"] - 1

    return child1, child2


# 变异操作
def mutate(individual, max_project_duration=None):
    # 计算理论最大工期
    theoretical_max_duration = sum(task["duration"] for task in individual)
    max_duration = min(theoretical_max_duration,
                       max_project_duration) if max_project_duration is not None else theoretical_max_duration

    for task in individual:
        if random.random() < MUTATION_RATE:
            max_start_time = max_duration - task["duration"]
            task["start_time"] = random.randint(0, max(max_start_time, 0))
            task["end_time"] = task["start_time"] + task["duration"] - 1
    return individual


# 主遗传算法
def genetic_algorithm(tasks, max_project_duration=None):
    # 初始化种群
    population = initialize_population(tasks, POPULATION_SIZE, max_project_duration)

    best_fitness = 0
    best_schedule = None
    best_resource_profile = None
    best_duration = float('inf')

    fitness_history = []

    for generation in range(GENERATIONS):
        # 计算适应度
        fitness_scores = []
        for individual in population:
            fitness, _, _ = calculate_fitness(individual, max_project_duration)
            fitness_scores.append(fitness)

        # 记录最佳解
        best_idx = fitness_scores.index(max(fitness_scores))
        current_best_fitness = fitness_scores[best_idx]
        current_best_schedule = population[best_idx]
        _, current_best_profile, current_duration = calculate_fitness(current_best_schedule, max_project_duration)

        if current_best_fitness > best_fitness or (
                current_best_fitness == best_fitness and current_duration < best_duration):
            best_fitness = current_best_fitness
            best_schedule = deepcopy(current_best_schedule)
            best_resource_profile = current_best_profile
            best_duration = current_duration

        fitness_history.append(best_fitness)

        # 选择
        selected = tournament_selection(population, fitness_scores)

        # 创建新一代
        new_population = []
        while len(new_population) < POPULATION_SIZE:
            # 选择父代
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)

            # 交叉
            child1, child2 = crossover(parent1, parent2)

            # 变异
            child1 = mutate(child1, max_project_duration)
            child2 = mutate(child2, max_project_duration)

            new_population.extend([child1, child2])

        # 确保种群大小不变
        population = new_population[:POPULATION_SIZE]

    return best_schedule


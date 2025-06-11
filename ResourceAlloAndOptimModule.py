

# 准备堆叠柱状图所需的数组
def show_task_bar(tasks):
    # 计算最大结束时间
    max_end_time = max(task["end_time"] for task in tasks)
    data = []

    # 处理每个任务
    for task in tasks:
        task_name = task["task"]
        start_time = task["start_time"]
        end_time = task["end_time"]
        resource_needed = task["resource_needed"]
        task_bar = [0] * (max_end_time + 1)
        for t in range(start_time, end_time + 1):
            task_bar[t] = resource_needed
        data.append({
            "task_name": task_name,
            "task_bar": task_bar
        })
    result = {
        "data": data,
        "xAris": list(range(0, max_end_time + 1))
    }

    return result

def resource_smoothing(activities):
    activity_map = {act["id"]: act for act in activities}

    # ========== 1. 关键路径计算 ==========
    # 正向计算 (最早开始/结束时间)
    for act in activities:
        if not act["predecessors"]:
            act["es"] = 0
        else:
            act["es"] = max(activity_map[pred]["ef"] for pred in act["predecessors"])
        act["ef"] = act["es"] + act["duration"]

    project_duration = max(act["ef"] for act in activities)

    # 反向计算 (最晚开始/结束时间)
    for act in reversed(activities):
        successors = [a for a in activities if act["id"] in a["predecessors"]]
        if not successors:
            act["lf"] = project_duration
        else:
            act["lf"] = min(succ["ls"] for succ in successors)
        act["ls"] = act["lf"] - act["duration"]
        act["tf"] = act["ls"] - act["es"]

    # ========== 2. 初始化资源分布 ==========
    resource_profile = [0] * (project_duration + 1)

    # 初始资源分配（按最早开始时间）
    for act in activities:
        for day in range(act["es"], act["es"] + act["duration"]):
            if day < len(resource_profile):
                resource_profile[day] += act["resource"]

    # ========== 3. 资源平滑核心算法 ==========
    # 按总浮动时间排序（浮动时间小的优先处理）
    non_critical = [act for act in activities if act["tf"] > 0]
    non_critical.sort(key=lambda x: x["tf"])

    # 迭代优化资源分布
    for activity in non_critical:
        best_start = activity["es"]
        best_improvement = float('inf')

        # 在浮动时间内尝试所有可能的开始时间
        for start_time in range(activity["es"], activity["ls"] + 1):
            # 创建临时资源分布副本
            temp_profile = resource_profile.copy()

            # 移除原始资源分配
            for day in range(activity["es"], activity["es"] + activity["duration"]):
                if day < len(temp_profile):
                    temp_profile[day] -= activity["resource"]

            # 添加新时间段的资源
            for day in range(start_time, start_time + activity["duration"]):
                if day < len(temp_profile):
                    temp_profile[day] += activity["resource"]

            # 计算资源波动指标
            max_res = max(temp_profile)
            res_variance = sum((r - sum(temp_profile) / len(temp_profile)) ** 2 for r in temp_profile)

            # 评估改进（优先降低峰值，其次降低方差）
            improvement = max_res * 1000 + res_variance

            # 寻找最佳开始时间
            if improvement < best_improvement:
                best_improvement = improvement
                best_start = start_time

        # 应用最佳方案
        for day in range(activity["es"], activity["es"] + activity["duration"]):
            if day < len(resource_profile):
                resource_profile[day] -= activity["resource"]

        for day in range(best_start, best_start + activity["duration"]):
            if day < len(resource_profile):
                resource_profile[day] += activity["resource"]

        # 更新活动时间
        activity["es"] = best_start
        activity["ef"] = best_start + activity["duration"]

    # ========== 4. 生成结果 ==========
    # 计算最终指标
    max_daily = max(resource_profile)
    min_daily = min(resource_profile)
    avg_daily = sum(resource_profile) / len(resource_profile)
    variance = sum((r - avg_daily) ** 2 for r in resource_profile) / len(resource_profile)

    # 返回结果对象
    return {
        "project_duration": project_duration,
        "resource_profile": resource_profile,
        "max_resource": max_daily,
        "min_resource": min_daily,
        "avg_resource": avg_daily,
        "resource_variance": variance,
        "activities": {act["id"]: {"start": act["es"], "end": act["ef"]} for act in activities}
    }
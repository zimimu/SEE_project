

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

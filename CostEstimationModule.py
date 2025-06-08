def cocomo_basic(KLOC, project_type):
    # COCOMO常数，依项目类型选择
    constants = {
        'Organic': (2.4, 1.05, 2.5, 0.38),
        'Semi-detached': (3.0, 1.12, 2.5, 0.35),
        'Embedded': (3.6, 1.20, 2.5, 0.32)
    }

    # 获取常数
    a, b, c, d = constants[project_type]

    # 基本 COCOMO 计算
    effort = a * (KLOC ** b)
    time = c * (effort ** d)
    personnel = effort / time

    return effort, time, personnel


def cocomo_intermediate(KLOC, project_type, cost_drivers):
    # 获取基本COCOMO的估算
    effort, time, personnel = cocomo_basic(KLOC, project_type)

    # 计算EAF（Effort Adjustment Factor）
    EAF = 1.0
    for driver, factor in cost_drivers.items():
        EAF *= factor

    # 调整后的工作量
    adjusted_effort = effort * EAF
    adjusted_time = time * EAF ** 0.35  # 时间调整因子通常取0.35
    adjusted_personnel = adjusted_effort / adjusted_time

    return adjusted_effort, adjusted_time, adjusted_personnel


def cocomo_detailed(KLOC, project_type, cost_drivers, phase_adjustments):
    # 获取中级COCOMO的估算
    adjusted_effort, adjusted_time, adjusted_personnel = cocomo_intermediate(KLOC, project_type, cost_drivers)

    # 应用开发阶段的调整因子（例如设计、编码、测试阶段）
    total_effort = adjusted_effort
    for phase, adjustment in phase_adjustments.items():
        total_effort *= adjustment

    total_time = adjusted_time * (total_effort ** 0.35)
    total_personnel = total_effort / total_time

    return total_effort, total_time, total_personnel


def cal_kloc(total_fp, total_tcf, programming_language):
    # 编程语言的 SLOC/FP 换算系数
    sloc_per_fp = {
        'Java': 53,
        'C++': 55,
        'Python': 38,
        'JavaScript': 47
    }

    # 检查是否支持的编程语言
    if programming_language not in sloc_per_fp:
        return ValueError("不支持的编程语言，请选择 'Java', 'C++', 'Python' 或 'JavaScript'")

    # 计算调整后的功能点数（Adjusted FP）
    adjusted_fp = total_fp * (0.65 + 0.01 * total_tcf)

    # 计算估算的 KLOC（千行代码）
    sloc_factor = sloc_per_fp[programming_language]
    kloc = (adjusted_fp * sloc_factor) / 1000

    return adjusted_fp, kloc


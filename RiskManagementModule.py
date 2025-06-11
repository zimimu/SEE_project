import numpy as np


# 计算敏感度（保持原版本不变）
def sensitivity_analysis(initial_costs, initial_benefits,
                         change_costs, change_revenue, dev_cost_change=0, revenue_change=0):
    # 调整开发成本（如果有变化）
    development_costs = change_costs * (1 + dev_cost_change)
    total_costs = initial_costs + (development_costs - change_costs)

    # 调整收入（如果有变化）
    revenue = change_revenue * (1 + revenue_change)
    total_benefits = initial_benefits + (revenue - change_revenue)

    # 计算净效益
    net_benefits = total_benefits - total_costs
    initial_net_benefits = initial_benefits - initial_costs

    result = {
        "initial_costs": initial_costs,
        "total_costs": total_costs,
        "initial_benefits": initial_benefits,
        "total_benefits": total_benefits,
        "initial_net_benefits": initial_net_benefits,
        "net_benefits": net_benefits
    }

    return result


# 计算蒙特卡洛模拟（保持原版本不变）
def monte_carlo_simulation(cost_range, revenue_mean, revenue_std, discount_rate_range, duration, num_simulations):
    # 初始投资范围
    cost_distribution = np.random.uniform(cost_range[0], cost_range[1], num_simulations)
    # 年收益范围
    revenue_distribution = np.random.normal(revenue_mean, revenue_std, num_simulations)
    # 折现率范围
    discount_rate_distribution = np.random.uniform(discount_rate_range[0], discount_rate_range[1], num_simulations)

    npv_values = []

    # 模拟
    for i in range(num_simulations):
        cost = cost_distribution[i]
        revenue = revenue_distribution[i]
        discount_rate = discount_rate_distribution[i]
        # 计算项目的净现值（NPV）
        npv = 0
        for t in range(1, duration + 1):
            npv += revenue / (1 + discount_rate) ** t
        npv -= cost
        npv_values.append(npv)

    # 计算均值
    mean_npv = np.mean(npv_values)

    result = {
        'mean_npv': mean_npv,
        'npv_values': npv_values
    }
    return result


# 决策树分析（优化版）
def decision_tree_analysis(risk_scenarios):
    """
    决策树分析 - 优化版

    Args:
        risk_scenarios: 风险场景列表，每个场景包含scenario_name, probability, decisions

    Returns:
        包含最优策略、期望值等信息的分析结果
    """
    if not risk_scenarios or len(risk_scenarios) == 0:
        raise ValueError("必须提供至少一个风险场景")

    # 输入验证
    for i, scenario in enumerate(risk_scenarios):
        if 'probability' not in scenario or scenario['probability'] < 0:
            raise ValueError(f"第{i + 1}个场景缺少合法概率")
        if 'decisions' not in scenario or not scenario['decisions']:
            raise ValueError(f"第{i + 1}个场景必须包含至少一个决策")

    # 概率归一化（如果需要的话）
    total_prob = sum(s['probability'] for s in risk_scenarios)
    if abs(total_prob - 1.0) > 0.01:
        for s in risk_scenarios:
            s['probability'] /= total_prob

    # 计算每个场景的最佳决策
    scenario_results = []
    total_expected_value = 0

    for scenario in risk_scenarios:
        best_decision = max(scenario['decisions'], key=lambda d: d['impact_value'])
        expected_impact = scenario['probability'] * best_decision['impact_value']
        total_expected_value += expected_impact

        scenario_results.append({
            'scenario_name': scenario['scenario_name'],
            'probability': scenario['probability'],
            'best_decision': best_decision['decision_name'],
            'expected_impact': expected_impact,
            'max_impact': best_decision['impact_value']
        })

    # 构建所有可能的路径
    all_paths = []

    def generate_paths(scenario_index, current_path, current_probability, current_value):
        if scenario_index >= len(risk_scenarios):
            all_paths.append({
                'path': current_path.copy(),
                'probability': current_probability,
                'expected_value': current_value
            })
            return

        scenario = risk_scenarios[scenario_index]
        for decision in scenario['decisions']:
            path_element = f"{scenario['scenario_name']}->{decision['decision_name']}"
            generate_paths(
                scenario_index + 1,
                current_path + [path_element],
                current_probability * scenario['probability'],
                current_value + (scenario['probability'] * decision['impact_value'])
            )

    generate_paths(0, [], 1.0, 0.0)

    # 找出最佳路径
    best_path = max(all_paths, key=lambda x: x['expected_value'])

    # 计算统计信息
    all_values = [path['expected_value'] for path in all_paths]
    best_case = max(all_values)
    worst_case = min(all_values)

    # 决策比较分析
    decision_comparison = {}
    for path in all_paths:
        for step in path['path']:
            if step not in decision_comparison:
                decision_comparison[step] = 0
            decision_comparison[step] += path['expected_value'] * path['probability']

    # 排序决策选项
    sorted_decisions = sorted(decision_comparison.items(), key=lambda x: x[1], reverse=True)

    # 风险评估
    std_dev = np.std(all_values) if len(all_values) > 1 else 0
    risk_assessment = _assess_risk_level(best_case, worst_case, std_dev)

    result = {
        'optimal_strategy': ' -> '.join(best_path['path']),
        'expected_value': total_expected_value,
        'all_paths': all_paths,
        'analysis_summary': {
            'best_case_value': best_case,
            'worst_case_value': worst_case,
            'value_range': best_case - worst_case,
            'average_value': np.mean(all_values),
            'std_deviation': std_dev
        },
        'scenario_results': scenario_results,
        'decision_comparison': dict(sorted_decisions),
        'risk_assessment': risk_assessment
    }

    return result


def _assess_risk_level(best_case, worst_case, std_dev):
    """评估风险水平"""
    value_range = best_case - worst_case

    if value_range == 0:
        risk_level = "无风险"
        recommendation = "所有选择结果相同，风险为零"
    elif std_dev < value_range * 0.1:
        risk_level = "低风险"
        recommendation = "风险较低，建议采用期望值最高的策略"
    elif std_dev < value_range * 0.3:
        risk_level = "中等风险"
        recommendation = "存在一定风险，建议平衡收益与风险"
    else:
        risk_level = "高风险"
        recommendation = "风险较高，建议谨慎评估或寻求风险分散策略"

    return {
        'risk_level': risk_level,
        'volatility': std_dev,
        'recommendation': recommendation,
        'confidence_interval': {
            'lower': worst_case,
            'upper': best_case
        }
    }


def _aggregate_decisions(paths):
    """聚合决策选项分析 - 保持原有函数兼容性"""
    from collections import defaultdict
    acc = defaultdict(float)
    for p in paths:
        for (_, d, _, impact) in p['path']:
            acc[d] += p['probability'] * impact
    return dict(sorted(acc.items(), key=lambda x: x[1], reverse=True))
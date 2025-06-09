import numpy as np
# 计算敏感度
# 输入分别为：最初总成本，最初总收益，变更成本项值，变更收益项值，变更成本项变更比率，变更收益项变更比率
def sensitivity_analysis(initial_costs, initial_benefits,
                         change_costs, change_revenue, dev_cost_change=0, revenue_change=0):

    # 调整开发成本（如果有变化）
    development_costs = change_costs * (1 + dev_cost_change)  # 基础开发成本是200,000美元
    total_costs = initial_costs + (development_costs - change_costs)

    # 调整收入（如果有变化）
    revenue = change_revenue * (1 + revenue_change)  # 基础收入是600,000美元
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



# 计算蒙特卡洛模拟
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

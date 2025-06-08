import numpy as np
from scipy.optimize import newton

def budgetingAndCost(return_amount, initial_investment, cash_flows, discount_rate):
    roi = calculate_roi(return_amount, initial_investment)
    npv = calculate_npv(cash_flows, discount_rate, initial_investment)
    irr = calculate_irr(cash_flows, initial_investment)
    period = calculate_payback_period(cash_flows, initial_investment)
    return roi, npv, irr, period

def calculate_roi(return_amount, initial_investment):
    roi = ((return_amount - initial_investment) / initial_investment) * 100
    return roi

def calculate_npv(cash_flows, discount_rate, initial_investment):
    npv = sum([cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows, start=1)]) - initial_investment
    return npv

def calculate_irr(cash_flows, initial_investment):
    def npv_function(r):
        return sum([cf / (1 + r) ** t for t, cf in enumerate(cash_flows, start=1)]) - initial_investment
    irr = newton(npv_function, 0.1)
    return irr * 100  # 返回百分比

def calculate_payback_period(cash_flows, initial_investment):
    cumulative_cash_flow = 0
    for t, cf in enumerate(cash_flows, start=1):
        cumulative_cash_flow += cf
        if cumulative_cash_flow >= initial_investment:
            return t
    # 代表无法回收
    return -1

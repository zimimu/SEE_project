import numpy as np
from scipy.optimize import newton
from model import db, BudgetTrack, Project


def budgeting_and_cost(return_amount, initial_investment, cash_flows, discount_rate):
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


# 创建budget
def create_budget(budget_list,project_id):
    budget_tracks = []
    for budget_data in budget_list:
        budget_track = BudgetTrack(
            project_id=project_id,
            budget_name=budget_data['budget_name'],
            budget_amount=budget_data['budget_amount'],
            budget_period=budget_data['budget_period'],
            cost_amount=budget_data['cost_amount']
        )
        budget_tracks.append(budget_track)

    # 批量添加到数据库
    db.session.bulk_save_objects(budget_tracks)
    db.session.commit()

    return {'message': 'Budget tracks successfully added'}


# 查询budget
def get_budget(project_id):
    # 查询所有与 project_id 相关的预算跟踪记录
    budget_tracks = BudgetTrack.query.filter_by(project_id=project_id).all()

    if not budget_tracks:
        return {'message': 'No budget tracks found for this project'}

    # 返回查询结果
    result = [
        {
            'budget_id': track.budget_id,
            'budget_name': track.budget_name,
            'budget_amount': track.budget_amount,
            'budget_period': track.budget_period,
            'cost_amount': track.cost_amount
        }
        for track in budget_tracks
    ]
    return result


# 组织折线图的结构
def get_linecharts_info(project_id):
    # 查询对应 project_id 的所有预算条目，并按 budget_period 排序
    budget_tracks = BudgetTrack.query.filter_by(project_id=project_id).order_by(BudgetTrack.budget_period.asc()).all()
    # 分别提取 budget_amount 和 cost_amount
    budget_amounts = [track.budget_amount for track in budget_tracks]
    cost_amounts = [track.cost_amount for track in budget_tracks]

    return budget_amounts,cost_amounts


# 编写分析语句
def write_analysis(initial_investment, actual_budget, expected_cost, actual_cost, expected_time, actual_time):
    analysis = ""
    if actual_budget >= initial_investment:
        analysis += "The current budget has been overspent. Pay attention to modifying or applying for more investment\n"
    else:
        analysis += "The current budget has not been overspent\n"
    if actual_cost >= expected_cost:
        analysis += "The current cost exceeds expectations. Pay attention to controlling the cost\n"
    else:
        analysis += "The current cost has not been overspent\n"
    if actual_time >= expected_time:
        analysis += "The current stage number exceeds expectations. Pay attention to adjusting the progress speed of the project\n"
    else:
        analysis += "The current stage number is normal\n"

    if actual_cost >= initial_investment:
        analysis += "The remaining investment amount is 0. Apply for more funds and strictly control expenses"

    return analysis


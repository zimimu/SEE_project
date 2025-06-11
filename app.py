from flask import Flask, request, jsonify
from flask_cors import CORS
import CostEstimationModule
import BudgetingAndCostModule
import ResourceAlloAndOptimModule
import ResourceLeveling
import numpy as np
import RiskManagementModule
from model import db, Project  # 导入数据库和模型

app = Flask(__name__)
# 修改CORS配置，支持credentials
CORS(app)

# 连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:112233@localhost:3306/see_proj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# 用于计算不同形式下的COCOMO值，具体接口接收形式见apifox，下同
@app.route('/costestimation/cocomo', methods=['POST'])
def calculate_cocomo():
    data = request.get_json()
    cocomo_type = data.get('cocomo_type')
    # 判断cocomo类型，调用对应函数解决问题
    if cocomo_type == 'basic':
        effort, time, personnel = CostEstimationModule.cocomo_basic(data.get('kloc'), data.get('project_type'))
        result = {
            'effort': effort,
            'time': time,
            'personnel': personnel
        }
    elif cocomo_type == 'intermediate':
        adjusted_effort, adjusted_time, adjusted_personnel = (
            CostEstimationModule.cocomo_intermediate(data.get('kloc'), data.get('project_type'),
                                                     data.get('cost_drivers')))
        result = {
            'adjusted_effort': adjusted_effort,
            'adjusted_time': adjusted_time,
            'adjusted_personnel': adjusted_personnel
        }
    elif cocomo_type == 'detailed':
        total_effort, total_time, total_personnel = (
            CostEstimationModule.cocomo_detailed(data.get('kloc'), data.get('project_type'),
                                                 data.get('cost_drivers'), data.get('phase_adjustments')))
        result = {
            'total_effort': total_effort,
            'total_time': total_time,
            'total_personnel': total_personnel
        }
    else:
        return jsonify({'error': 'Invalid'})
    return jsonify(result)


# 用于计算对应的调整后FP以及KLOC
@app.route('/costestimation/calkloc', methods=['POST'])
def calculate_fp():
    data = request.get_json()
    adjusted_fp, kloc = CostEstimationModule.cal_kloc(data.get('fp'), data.get('tcf'), data.get('language'))
    result = {
        'adjusted_fp': adjusted_fp,
        'kloc': kloc
    }
    return jsonify(result)


# 计算投资回报率等一系列数值
@app.route('/budgeting/calindicator', methods=['POST'])
def calculate_budget():
    data = request.get_json()
    print(data.get('return_amount'))
    print(data.get('initial_investment'))
    print(data.get('cash_flows'))
    print(data.get('discount_rate'))
    roi, npv, irr, period = (
        BudgetingAndCostModule.budgeting_and_cost(data.get('return_amount'), data.get('initial_investment'),
                                                  data.get('cash_flows'), data.get('discount_rate')))
    result = {
        'roi': roi,
        'npv': npv,
        'irr': irr,
        'period': period
    }
    return jsonify(result)


# 创建项目
@app.route('/budgeting/postProject', methods=['POST'])
def post_project():
    data = request.get_json()
    try:
        # 创建新的项目实例
        new_project = Project(
            initial_investment=data.get('initial_investment'),
            project_name=data.get('project_name'),
            project_description=data.get('project_description'),  # 可为 None
            total_cost=data.get('total_cost'),
            project_period_num=data.get('project_period_num')
        )

        # 添加到数据库并提交
        db.session.add(new_project)
        db.session.commit()

        return jsonify({'message': "succeed to add new project", 'project_id': new_project.project_id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e), 'project_id': None})


# 获取已经创建的项目列表
@app.route('/budgeting/getprojects', methods=['GET'])
def get_projects():
    try:
        # 查询所有项目的 project_id 和 project_name
        projects = Project.query.with_entities(Project.project_id, Project.project_name).all()

        # 格式化成字典列表
        data = [{'project_id': project.project_id, 'project_name': project.project_name} for project in projects]

        result = {
            'message': "the query is successful",
            'data': data
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'message': str(e), 'data': []})


# 获取某个项目下的预算追踪数据
@app.route('/budgeting/getbudgetingtrack', methods=['GET'])
def get_budget_by_project_id():
    try:
        project_id = request.args.get('project_id')

        if not project_id:
            return jsonify({'message': 'project_id is required', 'data': []})

        data = BudgetingAndCostModule.get_budget(project_id)

        result = {
            'message': "the operation is successful",
            'data': data
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'message': str(e), 'data': []})


# 创建追踪数据
@app.route('/budgeting/postBudgeting', methods=['POST'])
def create_budgeting():
    try:
        # 获取数据
        data = request.get_json()
        project_id = data.get('project_id')
        budget_list = data.get('budget_data')

        if not project_id or not budget_list:
            return jsonify({'error': 'Both project_id and budget_data are required'})

        result = BudgetingAndCostModule.create_budget(budget_list, project_id)
        return jsonify(result)

    except Exception as e:
        db.session.rollback()  # 如果发生错误，回滚数据库事务
        return jsonify({'error': str(e)})


# 展示折线图，饼状图以及柱状图
@app.route('/budgeting/showCharts', methods=['get'])
def show_budgeting():
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({'message': 'project_id is required', 'data': []})

        # 查询项目
        project = Project.query.get(project_id)

        if not project:
            return jsonify({'message': 'Project not found', 'data': {}})
        # 折线图数据获取
        budget_amounts, cost_amounts = BudgetingAndCostModule.get_linecharts_info(project_id)

        # 评价
        message = BudgetingAndCostModule.write_analysis(project.initial_investment, sum(budget_amounts),
                                                        project.total_cost, sum(cost_amounts),
                                                        project.project_period_num, len(budget_amounts))

        result = {
            'message': "the operation is successful",
            'data': {
                'project_name': project.project_name,
                'initial_investment': project.initial_investment,
                'total_cost': project.total_cost,
                'project_period_num': project.project_period_num,
                'linecharts': {
                    'linename': ['budget', 'cost'],
                    'xAxis': list(range(1, project.project_period_num + 1)),
                    'budgets': budget_amounts,
                    'costs': cost_amounts
                },
                'barcharts': {
                    'barchart_name': ['name', 'expected', 'actual'],
                    'budgets': ['budget', project.initial_investment, sum(budget_amounts)],
                    'costs': ['cost', project.total_cost, sum(cost_amounts)],
                    'time': ['time', project.project_period_num, len(budget_amounts)]
                },
                'prediction': {
                    'message': message
                }
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e), 'data': {}})


# 敏感度分析
@app.route('/riskmanagement/sensitivity', methods=['POST'])
def sensitivity_calculation():
    data = request.get_json()
    result = RiskManagementModule.sensitivity_analysis(data.get('initial_costs'), data.get('initial_benefits'),
                                                       data.get('change_costs'), data.get('change_revenue'),
                                                       data.get('dev_cost_change'), data.get('revenue_change'))
    return jsonify(result)


# ✅ 决策树可视化辅助函数（优化版）
def build_visual_tree(risk_scenarios):
    """构建决策树可视化结构"""
    root = {
        'name': '开始',
        'children': []
    }

    for scenario in risk_scenarios:
        scenario_node = {
            'name': f"{scenario['scenario_name']} (P={scenario['probability']:.2f})",
            'children': []
        }

        for decision in scenario['decisions']:
            decision_name = decision.get('decision_name')
            impact_value = decision.get('impact_value')
            scenario_node['children'].append({
                'name': f"{decision_name} → {impact_value}"
            })

        root['children'].append(scenario_node)

    return root


# ✅ 决策树分析接口（优化版）
@app.route('/riskmanagement/decisionTree', methods=['POST'])
def decision_tree_calculation():
    """决策树分析接口 - 优化版"""
    try:
        # 获取并验证请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        if 'risk_scenarios' not in data:
            return jsonify({'error': '缺少 risk_scenarios 参数'}), 400

        risk_scenarios = data.get('risk_scenarios')

        # 基本验证
        if not isinstance(risk_scenarios, list) or len(risk_scenarios) == 0:
            return jsonify({'error': '至少需要提供一个风险场景'}), 400

        # 详细验证每个场景
        total_probability = 0
        for i, scenario in enumerate(risk_scenarios):
            if not isinstance(scenario, dict):
                return jsonify({'error': f'第{i + 1}个场景格式错误'}), 400

            # 验证场景名称
            if 'scenario_name' not in scenario or not scenario['scenario_name'].strip():
                return jsonify({'error': f'第{i + 1}个场景缺少场景名称'}), 400

            # 验证概率
            if 'probability' not in scenario:
                return jsonify({'error': f'第{i + 1}个场景缺少概率值'}), 400

            try:
                probability = float(scenario['probability'])
                if probability < 0 or probability > 1:
                    return jsonify({'error': f'第{i + 1}个场景的概率必须在0-1之间'}), 400
                total_probability += probability
            except (ValueError, TypeError):
                return jsonify({'error': f'第{i + 1}个场景的概率格式错误'}), 400

            # 验证决策列表
            if 'decisions' not in scenario or not isinstance(scenario['decisions'], list):
                return jsonify({'error': f'第{i + 1}个场景缺少决策列表'}), 400

            if len(scenario['decisions']) == 0:
                return jsonify({'error': f'第{i + 1}个场景至少需要一个决策'}), 400

            # 验证每个决策
            for j, decision in enumerate(scenario['decisions']):
                if not isinstance(decision, dict):
                    return jsonify({'error': f'第{i + 1}个场景的第{j + 1}个决策格式错误'}), 400

                if 'decision_name' not in decision or not decision['decision_name'].strip():
                    return jsonify({'error': f'第{i + 1}个场景的第{j + 1}个决策缺少名称'}), 400

                if 'impact_value' not in decision:
                    return jsonify({'error': f'第{i + 1}个场景的第{j + 1}个决策缺少影响值'}), 400

                try:
                    float(decision['impact_value'])
                except (ValueError, TypeError):
                    return jsonify({'error': f'第{i + 1}个场景的第{j + 1}个决策的影响值格式错误'}), 400

        # 验证概率总和
        if abs(total_probability - 1.0) > 0.01:
            return jsonify({
                'error': f'所有场景的概率总和必须接近1.0，当前为{total_probability:.3f}'
            }), 400

        # 调用分析模块
        result = RiskManagementModule.decision_tree_analysis(risk_scenarios)

        # 构建可视化结构
        visual_tree = build_visual_tree(risk_scenarios)
        result['tree_chart'] = visual_tree

        return jsonify(result)

    except ValueError as e:
        return jsonify({'error': f'数据验证错误: {str(e)}'}), 400
    except Exception as e:
        # 记录错误日志（在生产环境中）
        app.logger.error(f"决策树分析错误: {str(e)}")
        return jsonify({'error': '服务器内部错误，请稍后重试'}), 500


# 蒙特卡洛模拟
@app.route('/riskmanagement/monteCarlo', methods=['POST'])
def montecarlo_calculation():
    data = request.get_json()
    result = RiskManagementModule.monte_carlo_simulation(data.get('cost_range'), data.get('revenue_mean'),
                                                         data.get('revenue_std'),
                                                         data.get('discount_rate_range'), data.get('duration'),
                                                         data.get('num_simulations'))
    return jsonify(result)


# 资源平衡
@app.route('/resourceallocation/resourceleveling', methods=['POST'])
def resource_leveling():
    data = request.get_json()
    tasks = data.get('tasks')
    # 调用函数处理得到初始数据的柱状图绘制数据
    initial_bar_charts = ResourceAlloAndOptimModule.show_task_bar(tasks)
    best_schedule = (
        ResourceLeveling.genetic_algorithm(tasks, data.get('max_duration')))
    # 调用函数处理得到更改数据的柱状图绘制数据
    changed_bar_charts = ResourceAlloAndOptimModule.show_task_bar(best_schedule)
    result = {'best_schedule': best_schedule,
              'changed_bar_charts': changed_bar_charts,
              'initial_bar_charts': initial_bar_charts
              }
    print(best_schedule[0])
    print(best_schedule[1])
    print(best_schedule[2])
    print(best_schedule[3])
    print(best_schedule[4])
    return jsonify(result)

# 资源平滑
@app.route('/resourceallocation/resourcesmoothing', methods=['POST'])
def resource_smoothing():
    data = request.get_json()
    result = ResourceAlloAndOptimModule.resource_smoothing(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
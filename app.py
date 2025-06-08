from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import CostEstimationModule
import BudgetingAndCostModule
app = Flask(__name__)
CORS(app)


@app.route('/test', methods=['POST'])
def calculate_bmi():
    # 获取前端传递的 JSON 数据
    data = request.get_json()

    # 提取数据
    height = data.get('height')  # 身高（单位：米）
    weight = data.get('weight')  # 体重（单位：公斤）
    gender = data.get('gender')  # 性别
    age = data.get('age')        # 年龄
    # 校验输入数据是否有效
    if height <= 0 or weight <= 0:
        return jsonify({'error': '身高和体重必须大于零'}), 400
    # 计算 BMI
    bmi = weight / (height ** 2)
    # 判断是否肥胖（BMI ≥ 30）
    if bmi >= 30:
        obesity_status = '肥胖'
    else:
        obesity_status = '正常'
    # 返回计算结果
    result = {
        'bmi': round(bmi, 2),
        'obesity_status': obesity_status
    }
    return jsonify(result)


# 用于计算不用形式下的COCOMO值，具体接口接收形式见apifox
@app.route('/costestimation/cocomo', methods=['POST'])
def calculate_cocomo():
    data = request.get_json()
    cocomo_type = data.get('cocomo_type')
    if cocomo_type == 'basic':
        effort, time, personnel = CostEstimationModule.cocomo_basic(data.get('kloc'), data.get('project_type'))
        result = {
            'effort': effort,
            'time': time,
            'personnel': personnel
        }
    elif cocomo_type == 'intermediate':
        adjusted_effort, adjusted_time, adjusted_personnel = (
            CostEstimationModule.cocomo_intermediate(data.get('kloc'), data.get('project_type'), data.get('cost_drivers')))
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

#用于计算对应的调整后FP以及KLOC
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
    roi, npv, irr, period = (
        BudgetingAndCostModule.budgetingAndCost(data.get('return_amount'), data.get('initial_investment'),
                                                data.get('cash_flows'), data.get('discount_rate')))
    result = {
        'roi': roi,
        'npv': npv,
        'irr': irr,
        'period': period
    }
    return jsonify(result)



if __name__ == '__main__':
    app.run()

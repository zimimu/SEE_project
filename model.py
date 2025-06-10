# 数据库文件
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库
db = SQLAlchemy()


# project表
class Project(db.Model):
    __tablename__ = 'project'

    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    initial_investment = db.Column(db.Float, nullable=False)
    project_name = db.Column(db.String(255), nullable=False)
    project_description = db.Column(db.String(255), nullable=True, default=None)
    total_cost = db.Column(db.Float, nullable=False)
    project_period_num = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Project {self.project_name}>"


# budget_tracking表
class BudgetTrack(db.Model):
    __tablename__ = 'budget_track'

    budget_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False)
    budget_name = db.Column(db.String(255), nullable=False)
    budget_amount = db.Column(db.Float, nullable=False)
    budget_period = db.Column(db.Integer, nullable=False)
    cost_amount = db.Column(db.Float, nullable=False)

    # Relationship to the Project table (optional, if you want to access project directly)
    project = db.relationship('Project', backref=db.backref('budget_tracks', lazy=True))

    def __repr__(self):
        return f"<BudgetTrack {self.budget_name} for Project {self.project_id}>"
routes\data_analysis_routes.py
# app/routes/data_analysis_routes.py
from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, Namespace
from app.services.data_analysis_service import DataAnalysisService

data_analysis_bp = Blueprint('data_analysis', __name__, url_prefix='/api')
api = Api(data_analysis_bp, title='Data Analysis API', version='1.0')
data_analysis_ns = Namespace('data-analysis', description='Data analysis operations')
api.add_namespace(data_analysis_ns)

data_analysis_service = DataAnalysisService()

@data_analysis_ns.route('/overview')
class DataAnalysisOverview(Resource):
    def get(self):
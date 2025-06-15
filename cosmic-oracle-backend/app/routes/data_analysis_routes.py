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
        """Get overview data for data analysis dashboard"""
        timeframe = request.args.get('timeframe', '30d')
        category = request.args.get('category', 'all')
        
        # Get real data from your database
        result = data_analysis_service.get_overview_data(timeframe, category)
        return result

@data_analysis_ns.route('/accuracy')
class PredictionAccuracy(Resource):
    def get(self):
        """Get prediction accuracy data"""
        timeframe = request.args.get('timeframe', '30d')
        category = request.args.get('category', 'all')
        
        # Get real data from your database
        result = data_analysis_service.get_accuracy_data(timeframe, category)
        return result

@data_analysis_ns.route('/market-trends')
class MarketTrends(Resource):
    def get(self):
        """Get market trends data"""
        timeframe = request.args.get('timeframe', '30d')
        
        # Get real data from your database
        result = data_analysis_service.get_market_trends(timeframe)
        return result

@data_analysis_ns.route('/data-sources')
class DataSources(Resource):
    def get(self):
        """Get all data sources"""
        result = data_analysis_service.get_data_sources()
        return result

@data_analysis_ns.route('/data-sources/<int:id>')
class DataSourceById(Resource):
    def get(self, id):
        """Get data source by ID"""
        result = data_analysis_service.get_data_source_by_id(id)
        return result
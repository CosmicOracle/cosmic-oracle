# app/services/data_analysis_service.py
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import func, desc
from app import db
from app.models import Prediction, DataSource

logger = logging.getLogger(__name__)

class DataAnalysisService:
    def get_overview_data(self, timeframe: str, category: str) -> Dict[str, Any]:
        """
        Get overview data for the data analysis dashboard
        
        Args:
            timeframe: Time period for analysis (e.g., '7d', '30d', '90d', '1y')
            category: Category filter (e.g., 'all', 'financial', 'political', etc.)
            
        Returns:
            Dict containing overview metrics and data
        """
        try:
            # Convert timeframe to datetime
            end_date = datetime.utcnow()
            if timeframe == '7d':
                start_date = end_date - timedelta(days=7)
            elif timeframe == '30d':
                start_date = end_date - timedelta(days=30)
            elif timeframe == '90d':
                start_date = end_date - timedelta(days=90)
            elif timeframe == '1y':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)  # Default to 30 days
            
            # Get previous period for comparison
            previous_period_length = (end_date - start_date).days
            previous_period_start = start_date - timedelta(days=previous_period_length)
            previous_period_end = start_date
            
            # Query predictions based on filters
            query = Prediction.query.filter(Prediction.createdAt >= start_date)
            previous_query = Prediction.query.filter(
                Prediction.createdAt >= previous_period_start,
                Prediction.createdAt < previous_period_end
            )
            
            if category != 'all':
                query = query.filter(Prediction.category == category)
                previous_query = previous_query.filter(Prediction.category == category)
            
            # Get total predictions
            total_predictions = query.count()
            previous_total = previous_query.count()
            
            # Calculate prediction change percentage
            prediction_change = 0
            if previous_total > 0:
                prediction_change = round(((total_predictions - previous_total) / previous_total) * 100)
            
            # Get accuracy rate
            accurate_predictions = query.filter(Prediction.status == 'Correct').count()
            accuracy_rate = 0
            if total_predictions > 0:
                accuracy_rate = round((accurate_predictions / total_predictions) * 100)
            
            previous_accurate = previous_query.filter(Prediction.status == 'Correct').count()
            previous_accuracy = 0
            if previous_total > 0:
                previous_accuracy = round((previous_accurate / previous_total) * 100)
            
            accuracy_change = accuracy_rate - previous_accuracy
            
            # Get active data sources
            active_sources = DataSource.query.filter(DataSource.status == 'Active').count()
            previous_active_sources = active_sources  # Assuming we don't have historical data for sources
            data_source_change = 0
            
            # Get average confidence
            avg_confidence_result = db.session.query(func.avg(Prediction.confidence)).filter(
                Prediction.createdAt >= start_date
            )
            if category != 'all':
                avg_confidence_result = avg_confidence_result.filter(Prediction.category == category)
            
            avg_confidence = avg_confidence_result.scalar() or 0
            avg_confidence = round(float(avg_confidence))
            
            previous_confidence_result = db.session.query(func.avg(Prediction.confidence)).filter(
                Prediction.createdAt >= previous_period_start,
                Prediction.createdAt < previous_period_end
            )
            if category != 'all':
                previous_confidence_result = previous_confidence_result.filter(Prediction.category == category)
            
            previous_confidence = previous_confidence_result.scalar() or 0
            previous_confidence = round(float(previous_confidence))
            confidence_change = avg_confidence - previous_confidence
            
            # Get category distribution
            category_distribution = []
            if category == 'all':
                categories = db.session.query(
                    Prediction.category, func.count(Prediction.id)
                ).filter(
                    Prediction.createdAt >= start_date
                ).group_by(Prediction.category).all()
                
                for cat, count in categories:
                    category_distribution.append({
                        "name": cat,
                        "value": count
                    })
            
            return {
                "totalPredictions": total_predictions,
                "predictionChange": prediction_change,
                "accuracyRate": accuracy_rate,
                "accuracyChange": accuracy_change,
                "activeDataSources": active_sources,
                "dataSourceChange": data_source_change,
                "avgConfidence": avg_confidence,
                "confidenceChange": confidence_change,
                "categoryDistribution": category_distribution
            }
        
        except Exception as e:
            logger.error(f"Error getting overview data: {str(e)}", exc_info=True)
            return {"error": "Failed to retrieve overview data"}
    
    def get_accuracy_data(self, timeframe: str, category: str) -> Dict[str, Any]:
        """
        Get prediction accuracy data over time
        
        Args:
            timeframe: Time period for analysis
            category: Category filter
            
        Returns:
            Dict containing accuracy metrics and chart data
        """
        try:
            # Convert timeframe to datetime
            end_date = datetime.utcnow()
            if timeframe == '7d':
                start_date = end_date - timedelta(days=7)
                interval = 1  # daily
            elif timeframe == '30d':
                start_date = end_date - timedelta(days=30)
                interval = 3  # every 3 days
            elif timeframe == '90d':
                start_date = end_date - timedelta(days=90)
                interval = 7  # weekly
            elif timeframe == '1y':
                start_date = end_date - timedelta(days=365)
                interval = 30  # monthly
            else:
                start_date = end_date - timedelta(days=30)
                interval = 3
            
            # Generate chart data points
            chart_data = []
            current_date = start_date
            
            while current_date <= end_date:
                next_date = current_date + timedelta(days=interval)
                
                # Query predictions for this interval
                query = Prediction.query.filter(
                    Prediction.createdAt >= current_date,
                    Prediction.createdAt < next_date
                )
                
                if category != 'all':
                    query = query.filter(Prediction.category == category)
                
                total = query.count()
                accurate = query.filter(Prediction.status == 'Correct').count()
                
                accuracy = 0
                if total > 0:
                    accuracy = round((accurate / total) * 100)
                
                chart_data.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "accuracy": accuracy
                })
                
                current_date = next_date
            
            return {
                "chartData": chart_data
            }
        
        except Exception as e:
            logger.error(f"Error getting accuracy data: {str(e)}", exc_info=True)
            return {"error": "Failed to retrieve accuracy data"}
    
    def get_market_trends(self, timeframe: str) -> Dict[str, Any]:
        """
        Get market trends data
        
        Args:
            timeframe: Time period for analysis
            
        Returns:
            Dict containing market trend data
        """
        try:
            # Convert timeframe to datetime
            end_date = datetime.utcnow()
            if timeframe == '7d':
                start_date = end_date - timedelta(days=7)
                interval = 1  # daily
            elif timeframe == '30d':
                start_date = end_date - timedelta(days=30)
                interval = 3  # every 3 days
            elif timeframe == '90d':
                start_date = end_date - timedelta(days=90)
                interval = 7  # weekly
            elif timeframe == '1y':
                start_date = end_date - timedelta(days=365)
                interval = 30  # monthly
            else:
                start_date = end_date - timedelta(days=30)
                interval = 3
            
            # Query financial predictions
            financial_predictions = Prediction.query.filter(
                Prediction.category == 'Financial',
                Prediction.createdAt >= start_date,
                Prediction.createdAt <= end_date
            ).order_by(Prediction.createdAt).all()
            
            # Generate trend data
            trend_data = []
            current_date = start_date
            
            while current_date <= end_date:
                next_date = current_date + timedelta(days=interval)
                
                # Filter predictions for this interval
                interval_predictions = [p for p in financial_predictions if 
                                       current_date <= p.createdAt < next_date]
                
                # Calculate average confidence as a proxy for market trend value
                avg_confidence = 0
                if interval_predictions:
                    avg_confidence = sum(p.confidence for p in interval_predictions) / len(interval_predictions)
                
                trend_data.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "value": round(avg_confidence)
                })
                
                current_date = next_date
            
            return {
                "trendData": trend_data
            }
        
        except Exception as e:
            logger.error(f"Error getting market trends: {str(e)}", exc_info=True)
            return {"error": "Failed to retrieve market trends"}
    
    def get_data_sources(self) -> Dict[str, Any]:
        """
        Get all data sources
        
        Returns:
            List of data sources
        """
        try:
            sources = DataSource.query.all()
            data_sources = []
            
            for source in sources:
                data_sources.append({
                    "id": source.id,
                    "name": source.name,
                    "type": source.type,
                    "status": source.status,
                    "lastUpdated": source.lastUpdated.isoformat() if source.lastUpdated else None,
                    "reliability": source.reliability
                })
            
            return data_sources
        
        except Exception as e:
            logger.error(f"Error getting data sources: {str(e)}", exc_info=True)
            return {"error": "Failed to retrieve data sources"}
    
    def get_data_source_by_id(self, id: int) -> Dict[str, Any]:
        """
        Get data source by ID
        
        Args:
            id: Data source ID
            
        Returns:
            Data source details
        """
        try:
            source = DataSource.query.get(id)
            
            if not source:
                return {"error": "Data source not found"}, 404
            
            return {
                "id": source.id,
                "name": source.name,
                "type": source.type,
                "status": source.status,
                "description": source.description,
                "url": source.url,
                "apiKey": source.apiKey,
                "lastUpdated": source.lastUpdated.isoformat() if source.lastUpdated else None,
                "reliability": source.reliability,
                "config": source.config
            }
        
        except Exception as e:
            logger.error(f"Error getting data source by ID: {str(e)}", exc_info=True)
            return {"error": "Failed to retrieve data source"}
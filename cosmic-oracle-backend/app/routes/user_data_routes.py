from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import JournalEntry, SavedTarotReading, NumerologyReport
from app.services.tarot_service import save_reading
from app import db

user_data_bp = Blueprint('user_data', __name__, url_prefix='/api/user')

@user_data_bp.route('/journal', methods=['POST'])
@jwt_required()
def create_journal_entry():
    """Create a new journal entry for the authenticated user."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
            
        entry = JournalEntry(
            user_id=user_id,
            content=data['content'],
            entry_type=data.get('type', 'general'),
            tags=data.get('tags', []),
            mood=data.get('mood'),
            astrological_context=data.get('astrological_context', {})
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            "message": "Journal entry created successfully",
            "entry_id": entry.id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating journal entry: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_data_bp.route('/journal', methods=['GET'])
@jwt_required()
def get_journal_entries():
    """Get paginated journal entries for the authenticated user."""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        entry_type = request.args.get('type')
        
        query = JournalEntry.query.filter_by(user_id=user_id)
        if entry_type:
            query = query.filter_by(entry_type=entry_type)
            
        entries = query.order_by(JournalEntry.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "entries": [entry.to_dict() for entry in entries.items],
            "total": entries.total,
            "pages": entries.pages,
            "current_page": entries.page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching journal entries: {e}")
        return jsonify({"error": str(e)}), 500

@user_data_bp.route('/journal/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_journal_entry(entry_id):
    """Delete a specific journal entry."""
    try:
        user_id = get_jwt_identity()
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        
        if not entry:
            return jsonify({"error": "Journal entry not found"}), 404
            
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({"message": "Journal entry deleted successfully"}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting journal entry: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_data_bp.route('/tarot/readings', methods=['POST'])
@jwt_required()
def save_tarot_reading():
    """Save a tarot reading for the authenticated user."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['spread_type', 'cards']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
            
        reading = save_reading(user_id, data)
        
        return jsonify({
            "message": "Tarot reading saved successfully",
            "reading_id": reading.id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error saving tarot reading: {e}")
        return jsonify({"error": str(e)}), 500

@user_data_bp.route('/tarot/readings', methods=['GET'])
@jwt_required()
def get_tarot_readings():
    """Get paginated tarot readings for the authenticated user."""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        readings = SavedTarotReading.query.filter_by(user_id=user_id).order_by(
            SavedTarotReading.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "readings": [reading.to_dict() for reading in readings.items],
            "total": readings.total,
            "pages": readings.pages,
            "current_page": readings.page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching tarot readings: {e}")
        return jsonify({"error": str(e)}), 500

@user_data_bp.route('/numerology/reports', methods=['GET'])
@jwt_required()
def get_numerology_reports():
    """Get paginated numerology reports for the authenticated user."""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        reports = NumerologyReport.query.filter_by(user_id=user_id).order_by(
            NumerologyReport.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "reports": [report.to_dict() for report in reports.items],
            "total": reports.total,
            "pages": reports.pages,
            "current_page": reports.page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching numerology reports: {e}")
        return jsonify({"error": str(e)}), 500
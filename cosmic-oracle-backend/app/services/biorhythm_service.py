# app/services/biorhythm_service.py
from datetime import date, datetime, timedelta
import math
from app.utils import parse_date_string # For parsing date strings

BIORHYTHM_CYCLES = {
    "physical": {"length": 23, "label": "Physical", "color": "#2ecc71"},
    "emotional": {"length": 28, "label": "Emotional", "color": "#e74c3c"},
    "intellectual": {"length": 33, "label": "Intellectual", "color": "#3498db"},
    "intuition": {"length": 38, "label": "Intuition", "color": "#9b59b6"}, # Purple
    "aesthetic": {"length": 43, "label": "Aesthetic", "color": "#f1c40f"}, # Yellow
    "awareness": {"length": 48, "label": "Awareness", "color": "#1abc9c"}, # Turquoise
    "spiritual": {"length": 53, "label": "Spiritual", "color": "#e67e22"}  # Orange
}

def _get_biorhythm_value_and_status(percentage):
    """Determines status text based on percentage."""
    if percentage > 90: return "Peak Performance / Very High", percentage
    elif percentage > 70: return "High Energy / Favorable", percentage      
    elif percentage > 55: return "Positive / Above Average", percentage
    elif percentage >= 45 and percentage <= 55: return "Transitional / Critical Day", percentage
    elif percentage > 25: return "Low Energy / Recharge Phase", percentage
    elif percentage > 10: return "Very Low / Rest Recommended", percentage
    else: return "Deep Recharge / Recuperation", percentage

def calculate_all_biorhythms(birth_date_str, analysis_date_str):
    """
    Calculates all defined biorhythm cycles for given dates.
    birth_date_str, analysis_date_str: "YYYY-MM-DD"
    Returns a dictionary of cycle data or an error dictionary.
    """
    birth_date = parse_date_string(birth_date_str)
    analysis_date = parse_date_string(analysis_date_str)

    if not birth_date:
        return {"error": "Invalid birth_date format. Use YYYY-MM-DD."}
    if not analysis_date:
        return {"error": "Invalid analysis_date format. Use YYYY-MM-DD."}

    if analysis_date < birth_date:
        return {"error": "Analysis date cannot be before birth date."}

    days_alive = (analysis_date - birth_date).days
    
    results = {
        "birth_date": birth_date_str,
        "analysis_date": analysis_date_str,
        "days_alive": days_alive,
        "cycles": {}
    }

    for cycle_key, cycle_info in BIORHYTHM_CYCLES.items():
        raw_value = math.sin((2 * math.pi * days_alive) / cycle_info["length"])
        percentage = round((raw_value + 1) / 2 * 100, 2) # As percentage 0-100
        status_text, _ = _get_biorhythm_value_and_status(percentage)
        
        results["cycles"][cycle_key] = {
            "label": cycle_info["label"],
            "length_days": cycle_info["length"],
            "value_sin": round(raw_value, 4), # sin value from -1 to 1
            "percentage": percentage,
            "status": status_text,
            "color": cycle_info["color"]
        }
    return results

def get_biorhythm_chart_data(birth_date_str, analysis_date_str, days_before=15, days_after=15):
    """
    Generates data points for plotting a biorhythm chart.
    days_before/days_after: Number of days to plot around the analysis_date.
    """
    main_calc = calculate_all_biorhythms(birth_date_str, analysis_date_str)
    if "error" in main_calc:
        return main_calc # Propagate error

    analysis_date_obj = parse_date_string(analysis_date_str)
    days_alive_on_analysis = main_calc["days_alive"]
    
    chart_data = {
        "analysis_date": analysis_date_str,
        "plot_range_days": days_before + days_after + 1,
        "series": {} # { "physical": [{date: "YYYY-MM-DD", value_percent: 75.0}, ...], ... }
    }

    for cycle_key, cycle_info in BIORHYTHM_CYCLES.items():
        if cycle_key not in ["physical", "emotional", "intellectual"]: # Only plot main 3 for brevity
            continue
        
        series_points = []
        for day_offset in range(-days_before, days_after + 1):
            current_plot_date = analysis_date_obj + timedelta(days=day_offset)
            days_alive_for_plot_date = days_alive_on_analysis + day_offset
            
            raw_value = math.sin((2 * math.pi * days_alive_for_plot_date) / cycle_info["length"])
            percentage = round((raw_value + 1) / 2 * 100, 2)
            
            series_points.append({
                "date": current_plot_date.strftime("%Y-%m-%d"),
                "value_percent": percentage,
                "value_sin": round(raw_value, 4)
            })
        chart_data["series"][cycle_key] = {
            "label": cycle_info["label"],
            "color": cycle_info["color"],
            "points": series_points
        }
        
    return chart_data

if __name__ == '__main__':
    print("--- Testing Biorhythm Service ---")
    bd_str = "1990-05-15"
    ad_str = "2023-10-27" # datetime.now().strftime("%Y-%m-%d")

    all_rhythms = calculate_all_biorhythms(bd_str, ad_str)
    if "error" not in all_rhythms:
        print(f"\nBiorhythms for DOB {bd_str} on {ad_str} (Days alive: {all_rhythms['days_alive']}):")
        for cycle, data in all_rhythms["cycles"].items():
            print(f"  {data['label']} ({data['length_days']}d): {data['status']} ({data['percentage']}%)")
    else:
        print(f"Error: {all_rhythms['error']}")

    chart_plot_data = get_biorhythm_chart_data(bd_str, ad_str)
    if "error" not in chart_plot_data and "series" in chart_plot_data:
        print(f"\nChart data for {chart_plot_data['analysis_date']} (+/-15 days):")
        for cycle_key, cycle_data in chart_plot_data["series"].items():
            print(f"  Cycle: {cycle_data['label']}, Color: {cycle_data['color']}")
            # print(f"    Points: {cycle_data['points'][:3]}... (first 3)") # Print a few points
    elif "error" in chart_plot_data:
         print(f"Chart data error: {chart_plot_data['error']}")
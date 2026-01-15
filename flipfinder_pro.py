"""
FlipFinder Pro v2.0 - Michigan Fix & Flip Investment Platform
Enhanced with: Mock Data, Advanced Analytics, AI Features, Alert System
Cloud-Ready for Streamlit Cloud Deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import sqlite3
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import random
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="FlipFinder Pro - Michigan Fix & Flip",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    .hot-lead {
        background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Michigan cities with coordinates
MICHIGAN_CITIES = {
    'Detroit': {'lat': 42.3314, 'lng': -83.0458, 'median_price': 85000, 'appreciation': 8.5},
    'Grand Rapids': {'lat': 42.9634, 'lng': -85.6681, 'median_price': 285000, 'appreciation': 12.3},
    'Warren': {'lat': 42.5145, 'lng': -83.0147, 'median_price': 165000, 'appreciation': 9.2},
    'Sterling Heights': {'lat': 42.5803, 'lng': -83.0302, 'median_price': 235000, 'appreciation': 7.8},
    'Ann Arbor': {'lat': 42.2808, 'lng': -83.7430, 'median_price': 425000, 'appreciation': 6.5},
    'Lansing': {'lat': 42.7325, 'lng': -84.5555, 'median_price': 145000, 'appreciation': 11.2},
    'Flint': {'lat': 43.0125, 'lng': -83.6875, 'median_price': 55000, 'appreciation': 15.8},
    'Dearborn': {'lat': 42.3223, 'lng': -83.1763, 'median_price': 175000, 'appreciation': 8.9},
    'Livonia': {'lat': 42.3684, 'lng': -83.3527, 'median_price': 265000, 'appreciation': 7.2},
    'Troy': {'lat': 42.6064, 'lng': -83.1498, 'median_price': 385000, 'appreciation': 5.8},
    'Westland': {'lat': 42.3242, 'lng': -83.4002, 'median_price': 155000, 'appreciation': 10.5},
    'Farmington Hills': {'lat': 42.4989, 'lng': -83.3677, 'median_price': 325000, 'appreciation': 6.9},
    'Kalamazoo': {'lat': 42.2917, 'lng': -85.5872, 'median_price': 175000, 'appreciation': 9.8},
    'Wyoming': {'lat': 42.9134, 'lng': -85.7053, 'median_price': 245000, 'appreciation': 11.5},
    'Southfield': {'lat': 42.4734, 'lng': -83.2219, 'median_price': 125000, 'appreciation': 12.8},
    'Pontiac': {'lat': 42.6389, 'lng': -83.2910, 'median_price': 95000, 'appreciation': 14.2},
    'Taylor': {'lat': 42.2409, 'lng': -83.2697, 'median_price': 125000, 'appreciation': 9.5},
    'Royal Oak': {'lat': 42.4895, 'lng': -83.1446, 'median_price': 315000, 'appreciation': 7.5},
    'Novi': {'lat': 42.4801, 'lng': -83.4755, 'median_price': 445000, 'appreciation': 5.2},
    'Saginaw': {'lat': 43.4195, 'lng': -83.9508, 'median_price': 45000, 'appreciation': 18.5},
}

PROPERTY_TYPES = ['Single Family', 'Multi-Family', 'Condo', 'Townhouse', 'Duplex']

DISTRESS_SIGNALS = [
    'Pre-Foreclosure', 'Foreclosure', 'Auction', 'Tax Lien', 
    'Vacant', 'Absentee Owner', 'Probate/Estate', 'High Equity',
    'Divorce', 'Code Violations', 'Tired Landlord'
]

PIPELINE_STAGES = ['New Lead', 'Contacted', 'Qualified', 'Offer Made', 'Under Contract', 'Closed', 'Dead/Lost']

STREET_NAMES = [
    'Main St', 'Oak Ave', 'Maple Dr', 'Washington Blvd', 'Jefferson Ave',
    'Lincoln Rd', 'Park Place', 'Cedar Lane', 'Elm St', 'Pine Ave',
    'Highland Dr', 'Lake Shore Dr', 'River Rd', 'Forest Ave', 'Sunset Blvd'
]

FIRST_NAMES = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
               'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
              'Rodriguez', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson', 'Martin']

# ============================================================================
# REALESTATEAPI.COM INTEGRATION
# ============================================================================

class RealEstateAPI:
    """Integration with RealEstateAPI.com"""
    
    BASE_URL = "https://api.realestateapi.com/v2"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
    
    def property_search(self, params):
        """Search for properties with given parameters"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/PropertySearch",
                headers=self.headers,
                json=params,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "error": f"API returned status {response.status_code}: {response.text[:500]}",
                    "data": []
                }
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "data": []}
    
    def property_detail(self, property_id):
        """Get detailed info for a specific property"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/PropertyDetail",
                headers=self.headers,
                json={"id": property_id},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return {"error": f"Status {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def skip_trace(self, property_id):
        """Get owner contact information"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/SkipTrace",
                headers=self.headers,
                json={"id": property_id},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return {"error": f"Status {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

# ============================================================================
# DATABASE SETUP
# ============================================================================

def get_db_path():
    return 'flipfinder.db'

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS properties (
        id TEXT PRIMARY KEY,
        address TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        beds INTEGER,
        baths REAL,
        sqft INTEGER,
        year_built INTEGER,
        lot_size REAL,
        property_type TEXT,
        list_price INTEGER,
        estimated_value INTEGER,
        arv INTEGER,
        mortgage_balance INTEGER,
        equity INTEGER,
        equity_percent INTEGER,
        days_on_market INTEGER,
        price_reductions INTEGER,
        ownership_years INTEGER,
        distress_signals TEXT,
        owner_name TEXT,
        owner_phone TEXT,
        owner_email TEXT,
        owner_mailing TEXT,
        lat REAL,
        lng REAL,
        stage TEXT DEFAULT 'New Lead',
        assigned_to TEXT,
        priority_score INTEGER,
        priority_tier TEXT,
        neighborhood_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS followups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id TEXT,
        type TEXT,
        date TEXT,
        time TEXT,
        assignee TEXT,
        status TEXT DEFAULT 'pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id TEXT,
        content TEXT,
        author TEXT DEFAULT 'User',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        property_id TEXT,
        title TEXT,
        message TEXT,
        priority TEXT,
        read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

# ============================================================================
# MOCK DATA GENERATOR
# ============================================================================

def generate_mock_properties(count=50):
    """Generate realistic mock properties for Michigan"""
    properties = []
    
    for i in range(count):
        city = random.choice(list(MICHIGAN_CITIES.keys()))
        city_data = MICHIGAN_CITIES[city]
        
        beds = random.choices([2, 3, 4, 5], weights=[15, 45, 30, 10])[0]
        baths = random.choices([1, 1.5, 2, 2.5, 3], weights=[10, 20, 40, 20, 10])[0]
        sqft = random.randint(800, 3500)
        year_built = random.randint(1920, 2015)
        lot_size = round(random.uniform(0.1, 0.8), 2)
        
        base_price = city_data['median_price']
        price_variance = random.uniform(0.5, 1.5)
        sqft_factor = sqft / 1500
        list_price = int(base_price * price_variance * sqft_factor)
        
        num_signals = random.choices([0, 1, 2, 3, 4, 5], weights=[20, 25, 25, 15, 10, 5])[0]
        signals = random.sample(DISTRESS_SIGNALS, min(num_signals, len(DISTRESS_SIGNALS)))
        
        ownership_years = random.randint(1, 30)
        if ownership_years > 15:
            equity_percent = random.randint(70, 100)
        elif ownership_years > 7:
            equity_percent = random.randint(40, 80)
        else:
            equity_percent = random.randint(10, 50)
        
        if 'Foreclosure' in signals or 'Pre-Foreclosure' in signals:
            days_on_market = random.randint(60, 180)
        else:
            days_on_market = random.randint(5, 120)
        
        price_reductions = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
        
        street_num = random.randint(100, 9999)
        street = random.choice(STREET_NAMES)
        address = f"{street_num} {street}"
        
        owner_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        lat = city_data['lat'] + random.uniform(-0.05, 0.05)
        lng = city_data['lng'] + random.uniform(-0.05, 0.05)
        
        has_phone = random.random() > 0.3
        phone = f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}" if has_phone else ""
        
        has_email = random.random() > 0.5
        email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        email = f"{owner_name.lower().replace(' ', '.')}@{random.choice(email_domains)}" if has_email else ""
        
        prop = {
            'id': f"prop_{i+1:04d}",
            'address': address,
            'city': city,
            'state': 'MI',
            'zip': f"48{random.randint(100, 999)}",
            'beds': beds,
            'baths': baths,
            'sqft': sqft,
            'year_built': year_built,
            'lot_size': lot_size,
            'property_type': random.choice(PROPERTY_TYPES),
            'list_price': list_price,
            'estimated_value': int(list_price * random.uniform(0.95, 1.1)),
            'arv': int(list_price * random.uniform(1.15, 1.4)),
            'equity_percent': equity_percent,
            'mortgage_balance': int(list_price * (100 - equity_percent) / 100),
            'equity': int(list_price * equity_percent / 100),
            'days_on_market': days_on_market,
            'price_reductions': price_reductions,
            'ownership_years': ownership_years,
            'distress_signals': signals,
            'owner_name': owner_name,
            'owner_phone': phone,
            'owner_email': email,
            'owner_mailing': f"{random.randint(100, 9999)} {random.choice(STREET_NAMES)}, {city}, MI",
            'lat': lat,
            'lng': lng,
            'stage': random.choices(PIPELINE_STAGES, weights=[40, 20, 15, 10, 8, 5, 2])[0],
        }
        
        properties.append(prop)
    
    return properties

def load_mock_data():
    """Load mock data into database if empty"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM properties")
    count = c.fetchone()[0]
    conn.close()
    
    if count == 0:
        properties = generate_mock_properties(50)
        for prop in properties:
            priority = calculate_ai_priority_score(prop)
            neighborhood = analyze_neighborhood(prop['city'])
            prop['neighborhood_score'] = neighborhood['score']
            save_property(prop, priority)
        
        generate_mock_alerts()
        return True
    return False

def generate_mock_alerts():
    """Generate mock alerts"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    alerts = [
        ('hot_lead', None, '🔥 New Hot Lead!', 'Property at 1234 Oak Ave in Detroit scored 92/100', 'high'),
        ('price_drop', None, '📉 Price Dropped 15%', '5678 Maple Dr reduced from $150,000 to $127,500', 'high'),
        ('new_listing', None, '🏠 New Pre-Foreclosure', 'Pre-foreclosure property listed in Flint under $50k', 'medium'),
        ('followup', None, '📞 Follow-up Due', 'Call scheduled for John Smith at 2:00 PM today', 'medium'),
        ('market', None, '📈 Market Update', 'Detroit median prices up 8.5% this quarter', 'low'),
    ]
    
    for alert in alerts:
        c.execute('''INSERT INTO alerts (type, property_id, title, message, priority)
                     VALUES (?, ?, ?, ?, ?)''', alert)
    
    conn.commit()
    conn.close()

# ============================================================================
# AI-ENHANCED FEATURES
# ============================================================================

def calculate_ai_priority_score(property_data):
    """AI-Enhanced Priority Scoring System"""
    score = 0
    factors = []
    ai_insights = []
    
    list_price = property_data.get('list_price', 0) or 0
    arv = property_data.get('arv', 0) or int(list_price * 1.2)
    sqft = property_data.get('sqft', 1500)
    beds = property_data.get('beds', 3)
    year_built = property_data.get('year_built', 1970)
    equity_percent = property_data.get('equity_percent', 0)
    ownership_years = property_data.get('ownership_years', 5)
    days_on_market = property_data.get('days_on_market', 0)
    price_reductions = property_data.get('price_reductions', 0)
    distress_signals = property_data.get('distress_signals', [])
    
    if isinstance(distress_signals, str):
        distress_signals = distress_signals.split(',') if distress_signals else []
    
    current_year = datetime.now().year
    age = current_year - year_built if year_built > 1800 else 50
    
    if age > 50:
        repair_per_sqft = 65
        ai_insights.append("🔧 Older home - budget for major systems")
    elif age > 30:
        repair_per_sqft = 45
        ai_insights.append("🔧 Medium-age home - likely needs updates")
    elif age > 15:
        repair_per_sqft = 30
        ai_insights.append("✅ Newer construction - mostly cosmetic")
    else:
        repair_per_sqft = 20
        ai_insights.append("✅ Very new - minimal repairs expected")
    
    estimated_repairs = sqft * repair_per_sqft
    max_offer = (arv * 0.7) - estimated_repairs
    gap = max_offer - list_price
    gap_percent = (gap / arv * 100) if arv > 0 else 0
    
    total_investment = list_price + estimated_repairs + (arv * 0.13)
    net_profit = arv - total_investment
    roi = (net_profit / total_investment * 100) if total_investment > 0 else 0
    
    # PROFIT POTENTIAL (0-40)
    if gap_percent >= 15:
        score += 25
        factors.append({"name": "🎯 Excellent Price Gap (15%+)", "points": 25, "category": "profit"})
        ai_insights.append("💰 SLAM DUNK - Priced below max offer!")
    elif gap_percent >= 10:
        score += 20
        factors.append({"name": "Great Price Gap (10%+)", "points": 20, "category": "profit"})
    elif gap_percent >= 5:
        score += 15
        factors.append({"name": "Good Price Gap (5%+)", "points": 15, "category": "profit"})
    elif gap_percent >= 0:
        score += 10
        factors.append({"name": "At Max Offer", "points": 10, "category": "profit"})
    elif gap_percent >= -10:
        score += 5
        factors.append({"name": "Negotiable", "points": 5, "category": "profit"})
    
    if roi >= 30:
        score += 15
        factors.append({"name": "🚀 Excellent ROI (30%+)", "points": 15, "category": "profit"})
    elif roi >= 20:
        score += 12
        factors.append({"name": "Strong ROI (20%+)", "points": 12, "category": "profit"})
    elif roi >= 15:
        score += 8
        factors.append({"name": "Good ROI (15%+)", "points": 8, "category": "profit"})
    
    # SELLER MOTIVATION (0-35)
    if 'Foreclosure' in distress_signals:
        score += 15
        factors.append({"name": "🚨 Active Foreclosure", "points": 15, "category": "motivation"})
        ai_insights.append("🔥 URGENT - Facing sale deadline!")
    
    if 'Pre-Foreclosure' in distress_signals:
        score += 12
        factors.append({"name": "⚠️ Pre-Foreclosure", "points": 12, "category": "motivation"})
    
    if 'Probate/Estate' in distress_signals:
        score += 12
        factors.append({"name": "📜 Inherited/Estate", "points": 12, "category": "motivation"})
    
    if 'Tax Lien' in distress_signals:
        score += 10
        factors.append({"name": "💸 Tax Lien", "points": 10, "category": "motivation"})
    
    if 'Divorce' in distress_signals:
        score += 10
        factors.append({"name": "💔 Divorce", "points": 10, "category": "motivation"})
    
    if 'Absentee Owner' in distress_signals:
        score += 6
        factors.append({"name": "📍 Absentee Owner", "points": 6, "category": "motivation"})
    
    if 'Vacant' in distress_signals:
        score += 8
        factors.append({"name": "🏚️ Vacant Property", "points": 8, "category": "motivation"})
    
    if 'Tired Landlord' in distress_signals:
        score += 8
        factors.append({"name": "😫 Tired Landlord", "points": 8, "category": "motivation"})
    
    if ownership_years >= 15:
        score += 5
        factors.append({"name": "⏰ Long Ownership (15+ yrs)", "points": 5, "category": "motivation"})
    
    if equity_percent >= 70:
        score += 6
        factors.append({"name": "💎 High Equity (70%+)", "points": 6, "category": "motivation"})
    
    if equity_percent >= 95:
        score += 5
        factors.append({"name": "🆓 Free & Clear", "points": 5, "category": "motivation"})
    
    signal_count = len([s for s in distress_signals if s])
    if signal_count >= 5:
        score += 8
        factors.append({"name": "🔥 5+ Distress Signals", "points": 8, "category": "motivation"})
    elif signal_count >= 3:
        score += 5
        factors.append({"name": "Multiple Signals", "points": 5, "category": "motivation"})
    
    # URGENCY (0-15)
    if days_on_market >= 90:
        score += 8
        factors.append({"name": "📅 Stale Listing (90+ days)", "points": 8, "category": "urgency"})
    elif days_on_market >= 60:
        score += 5
        factors.append({"name": "Getting Stale (60+ days)", "points": 5, "category": "urgency"})
    
    if price_reductions >= 2:
        score += 8
        factors.append({"name": "📉 Multiple Price Drops", "points": 8, "category": "urgency"})
    elif price_reductions >= 1:
        score += 5
        factors.append({"name": "Price Reduced", "points": 5, "category": "urgency"})
    
    current_month = datetime.now().month
    if current_month in [11, 12, 1, 2]:
        score += 3
        factors.append({"name": "❄️ Winter Season", "points": 3, "category": "urgency"})
    
    # CONTACT (0-10)
    if property_data.get('owner_phone'):
        score += 5
        factors.append({"name": "📞 Phone Available", "points": 5, "category": "contact"})
    
    if property_data.get('owner_email'):
        score += 3
        factors.append({"name": "📧 Email Available", "points": 3, "category": "contact"})
    
    if property_data.get('owner_mailing'):
        score += 2
        factors.append({"name": "📬 Mailing Address", "points": 2, "category": "contact"})
    
    score = min(100, score)
    
    if score >= 75:
        tier = "HOT"
        action = "🔥 CALL TODAY - Drop everything!"
    elif score >= 55:
        tier = "WARM"
        action = "🌡️ Contact within 48 hours"
    elif score >= 35:
        tier = "NURTURE"
        action = "💧 Add to drip campaign"
    else:
        tier = "MONITOR"
        action = "👀 Watch for price drops"
    
    if score >= 75 and roi >= 20:
        ai_recommendation = "🎯 STRONG BUY - All signals align for profit"
    elif score >= 55 and roi >= 15:
        ai_recommendation = "✅ GOOD OPPORTUNITY - Worth pursuing"
    elif score >= 35:
        ai_recommendation = "⚠️ NEEDS WORK - Negotiate hard or wait"
    else:
        ai_recommendation = "❌ PASS - Numbers don't work at current price"
    
    return {
        "score": score,
        "tier": tier,
        "action": action,
        "factors": factors,
        "ai_insights": ai_insights,
        "ai_recommendation": ai_recommendation,
        "financials": {
            "max_offer": max_offer,
            "estimated_repairs": estimated_repairs,
            "gap_percent": gap_percent,
            "roi": roi,
            "net_profit": net_profit,
            "total_investment": total_investment
        }
    }

def predict_arv(property_data, city):
    """AI-powered ARV prediction"""
    city_data = MICHIGAN_CITIES.get(city, {'median_price': 150000, 'appreciation': 8.0})
    
    sqft = property_data.get('sqft', 1500)
    beds = property_data.get('beds', 3)
    baths = property_data.get('baths', 2)
    year_built = property_data.get('year_built', 1970)
    list_price = property_data.get('list_price', city_data['median_price'])
    
    price_per_sqft = city_data['median_price'] / 1500
    base_arv = sqft * price_per_sqft
    
    bed_adjustment = (beds - 3) * 10000
    bath_adjustment = max(0, (baths - 1.5)) * 7500
    
    current_year = datetime.now().year
    age = current_year - year_built
    if age <= 10:
        age_multiplier = 1.15
    elif age <= 25:
        age_multiplier = 1.05
    elif age <= 50:
        age_multiplier = 1.0
    else:
        age_multiplier = 0.92
    
    appreciation_factor = 1 + (city_data['appreciation'] / 100)
    predicted_arv = (base_arv + bed_adjustment + bath_adjustment) * age_multiplier * appreciation_factor
    
    confidence = random.randint(75, 95)
    
    return {
        'predicted_arv': int(predicted_arv),
        'low_estimate': int(predicted_arv * 0.9),
        'high_estimate': int(predicted_arv * 1.1),
        'confidence': confidence,
        'price_per_sqft': int(predicted_arv / sqft),
        'appreciation_rate': city_data['appreciation']
    }

def analyze_neighborhood(city):
    """AI neighborhood analysis"""
    city_data = MICHIGAN_CITIES.get(city, {'median_price': 150000, 'appreciation': 8.0})
    
    school_rating = random.randint(4, 10)
    crime_score = random.randint(3, 9)
    walkability = random.randint(20, 85)
    job_growth = round(random.uniform(1.5, 8.5), 1)
    population_trend = random.choice(['Growing', 'Stable', 'Declining'])
    
    score = int(
        (school_rating * 2) +
        (crime_score * 2) +
        (walkability / 10) +
        (job_growth * 2) +
        (city_data['appreciation'] / 2) +
        (10 if population_trend == 'Growing' else 5 if population_trend == 'Stable' else 0)
    )
    score = min(100, score)
    
    if score >= 75:
        grade = 'A'
        investment_outlook = '🌟 Excellent investment area'
    elif score >= 60:
        grade = 'B'
        investment_outlook = '✅ Good investment potential'
    elif score >= 45:
        grade = 'C'
        investment_outlook = '⚠️ Moderate risk/reward'
    else:
        grade = 'D'
        investment_outlook = '❌ Higher risk area'
    
    return {
        'score': score,
        'grade': grade,
        'investment_outlook': investment_outlook,
        'metrics': {
            'school_rating': school_rating,
            'crime_score': crime_score,
            'walkability': walkability,
            'job_growth': job_growth,
            'appreciation': city_data['appreciation'],
            'population_trend': population_trend,
            'median_price': city_data['median_price']
        }
    }

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def save_property(property_data, priority_data):
    """Save property to database"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    prop_id = property_data.get('id', f"prop_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    
    distress_signals = property_data.get('distress_signals', [])
    if isinstance(distress_signals, list):
        distress_signals = ','.join(distress_signals)
    
    c.execute('''INSERT OR REPLACE INTO properties 
        (id, address, city, state, zip, beds, baths, sqft, year_built, lot_size,
         property_type, list_price, estimated_value, arv, mortgage_balance,
         equity, equity_percent, days_on_market, price_reductions, ownership_years,
         distress_signals, owner_name, owner_phone, owner_email, owner_mailing,
         lat, lng, stage, priority_score, priority_tier, neighborhood_score, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        prop_id,
        property_data.get('address', ''),
        property_data.get('city', ''),
        property_data.get('state', 'MI'),
        property_data.get('zip', ''),
        property_data.get('beds', 0),
        property_data.get('baths', 0),
        property_data.get('sqft', 0),
        property_data.get('year_built', 0),
        property_data.get('lot_size', 0),
        property_data.get('property_type', ''),
        property_data.get('list_price', 0),
        property_data.get('estimated_value', 0),
        property_data.get('arv', 0),
        property_data.get('mortgage_balance', 0),
        property_data.get('equity', 0),
        property_data.get('equity_percent', 0),
        property_data.get('days_on_market', 0),
        property_data.get('price_reductions', 0),
        property_data.get('ownership_years', 0),
        distress_signals,
        property_data.get('owner_name', ''),
        property_data.get('owner_phone', ''),
        property_data.get('owner_email', ''),
        property_data.get('owner_mailing', ''),
        property_data.get('lat', 0),
        property_data.get('lng', 0),
        property_data.get('stage', 'New Lead'),
        priority_data.get('score', 0),
        priority_data.get('tier', 'MONITOR'),
        property_data.get('neighborhood_score', 50),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    return prop_id

def get_all_properties():
    """Get all saved properties"""
    conn = sqlite3.connect(get_db_path())
    df = pd.read_sql_query("SELECT * FROM properties ORDER BY priority_score DESC", conn)
    conn.close()
    return df

def get_property_by_id(prop_id):
    """Get single property by ID"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT * FROM properties WHERE id = ?", (prop_id,))
    row = c.fetchone()
    columns = [description[0] for description in c.description]
    conn.close()
    
    if row:
        return dict(zip(columns, row))
    return None

def update_property_stage(prop_id, new_stage):
    """Update property pipeline stage"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("UPDATE properties SET stage = ?, updated_at = ? WHERE id = ?", 
              (new_stage, datetime.now().isoformat(), prop_id))
    conn.commit()
    conn.close()

def get_alerts(unread_only=False):
    """Get alerts"""
    conn = sqlite3.connect(get_db_path())
    query = "SELECT * FROM alerts"
    if unread_only:
        query += " WHERE read = 0"
    query += " ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def mark_alert_read(alert_id):
    """Mark alert as read"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("UPDATE alerts SET read = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def add_note(prop_id, content, author="User"):
    """Add a note"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''INSERT INTO notes (property_id, content, author) VALUES (?, ?, ?)''', 
              (prop_id, content, author))
    conn.commit()
    conn.close()

def get_notes(prop_id):
    """Get notes for property"""
    conn = sqlite3.connect(get_db_path())
    df = pd.read_sql_query(
        "SELECT * FROM notes WHERE property_id = ? ORDER BY created_at DESC", 
        conn, params=(prop_id,)
    )
    conn.close()
    return df

def add_followup(prop_id, followup_type, date, time, assignee, notes=""):
    """Add a follow-up"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''INSERT INTO followups (property_id, type, date, time, assignee, notes)
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (prop_id, followup_type, date, time, assignee, notes))
    conn.commit()
    conn.close()

def get_followups(prop_id):
    """Get follow-ups for property"""
    conn = sqlite3.connect(get_db_path())
    df = pd.read_sql_query(
        "SELECT * FROM followups WHERE property_id = ? ORDER BY date DESC", 
        conn, params=(prop_id,)
    )
    conn.close()
    return df

# ============================================================================
# ANALYTICS
# ============================================================================

def create_analytics_dashboard(properties_df):
    """Create analytics dashboard"""
    if properties_df.empty:
        st.warning("No data available for analytics.")
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        hot_count = len(properties_df[properties_df['priority_tier'] == 'HOT'])
        st.metric("🔥 Hot Leads", hot_count)
    
    with col2:
        total_value = properties_df['list_price'].sum()
        st.metric("💰 Pipeline Value", f"${total_value/1000000:.1f}M")
    
    with col3:
        avg_score = properties_df['priority_score'].mean()
        st.metric("📊 Avg Score", f"{avg_score:.0f}")
    
    with col4:
        closed_count = len(properties_df[properties_df['stage'] == 'Closed'])
        st.metric("✅ Closed Deals", closed_count)
    
    with col5:
        avg_roi = 22.5
        st.metric("📈 Avg ROI", f"{avg_roi}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Properties by Priority Tier")
        tier_counts = properties_df['priority_tier'].value_counts()
        fig = px.pie(
            values=tier_counts.values, 
            names=tier_counts.index,
            color=tier_counts.index,
            color_discrete_map={'HOT': '#ef4444', 'WARM': '#f59e0b', 'NURTURE': '#3b82f6', 'MONITOR': '#6b7280'},
            hole=0.4
        )
        fig.update_layout(showlegend=True, height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📋 Pipeline Distribution")
        stage_counts = properties_df['stage'].value_counts()
        fig = px.bar(
            x=stage_counts.index, 
            y=stage_counts.values,
            color=stage_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False, height=300, xaxis_title="Stage", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏙️ Properties by City")
        city_counts = properties_df['city'].value_counts().head(10)
        fig = px.bar(
            x=city_counts.values, 
            y=city_counts.index,
            orientation='h',
            color=city_counts.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💵 Avg Price by City")
        city_prices = properties_df.groupby('city')['list_price'].mean().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=city_prices.values, 
            y=city_prices.index,
            orientation='h',
            color=city_prices.values,
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MAP
# ============================================================================

def create_property_map(properties_df, selected_property=None):
    """Create interactive map"""
    center_lat = 42.7325
    center_lng = -84.5555
    
    if selected_property:
        center_lat = selected_property.get('lat', center_lat) or center_lat
        center_lng = selected_property.get('lng', center_lng) or center_lng
        zoom = 14
    else:
        zoom = 7
    
    m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom, tiles='cartodbpositron')
    
    tier_colors = {
        'HOT': 'red',
        'WARM': 'orange',
        'NURTURE': 'blue',
        'MONITOR': 'gray'
    }
    
    if not properties_df.empty:
        for _, prop in properties_df.iterrows():
            lat = prop.get('lat', 0)
            lng = prop.get('lng', 0)
            
            if lat and lng and lat != 0 and lng != 0:
                tier = prop.get('priority_tier', 'MONITOR')
                color = tier_colors.get(tier, 'gray')
                
                popup_html = f"""
                <div style="width: 200px;">
                    <h4>{prop.get('address', 'N/A')}</h4>
                    <p>{prop.get('city', '')}, MI</p>
                    <p>💰 ${prop.get('list_price', 0):,}</p>
                    <p>🎯 Score: {prop.get('priority_score', 0)}</p>
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=12 if tier == 'HOT' else 8,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_html, max_width=250)
                ).add_to(m)
    
    return m

# ============================================================================
# PDF REPORT
# ============================================================================

def generate_cma_pdf(property_data, priority_data):
    """Generate CMA PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6366f1'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    story = []
    
    story.append(Paragraph("FlipFinder Pro", title_style))
    story.append(Paragraph("Comparative Market Analysis", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    address = f"{property_data.get('address', 'N/A')}, {property_data.get('city', '')}, MI"
    story.append(Paragraph(f"<b>{address}</b>", styles['Heading1']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    tier = priority_data.get('tier', 'N/A')
    score = priority_data.get('score', 0)
    story.append(Paragraph(f"<b>Priority Score: {score}/100 ({tier})</b>", heading_style))
    story.append(Paragraph(priority_data.get('ai_recommendation', ''), styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Investment Analysis", heading_style))
    financials = priority_data.get('financials', {})
    fin_data = [
        ['List Price', f"${property_data.get('list_price', 0):,}"],
        ['Estimated ARV', f"${property_data.get('arv', 0):,}"],
        ['Max Offer (70% Rule)', f"${financials.get('max_offer', 0):,.0f}"],
        ['Estimated Repairs', f"${financials.get('estimated_repairs', 0):,.0f}"],
        ['Estimated ROI', f"{financials.get('roi', 0):.1f}%"],
    ]
    fin_table = Table(fin_data, colWidths=[3*inch, 2*inch])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(fin_table)
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated by FlipFinder Pro", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    init_database()
    
    if 'mock_loaded' not in st.session_state:
        if load_mock_data():
            st.session_state.mock_loaded = True
            st.toast("✅ Demo data loaded!", icon="🎉")
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'selected_property' not in st.session_state:
        st.session_state.selected_property = None
    if 'use_mock_data' not in st.session_state:
        st.session_state.use_mock_data = True
    if 'api_results' not in st.session_state:
        st.session_state.api_results = []
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🏠 FlipFinder Pro")
        st.caption("Michigan Fix & Flip Platform")
        st.markdown("---")
        
        st.session_state.use_mock_data = st.toggle("🎭 Use Demo Data", value=True)
        
        if not st.session_state.use_mock_data:
            api_key = st.text_input("🔑 RealEstateAPI Key", type="password", value=st.session_state.api_key)
            if api_key:
                st.session_state.api_key = api_key
                st.success("✅ API Key Set")
        
        st.markdown("---")
        
        alerts_df = get_alerts(unread_only=True)
        alert_count = len(alerts_df)
        
        page = st.radio("Navigation", [
            "🏠 Dashboard",
            "🔍 Property Search",
            "🎯 Priority Queue",
            "📋 Pipeline",
            "🗺️ Map View",
            "📊 Analytics",
            f"🔔 Alerts ({alert_count})",
            "🤖 AI Tools",
            "⚙️ Settings"
        ])
    
    st.title("🏠 FlipFinder Pro")
    st.caption("AI-Powered Michigan Fix & Flip Investment Platform")
    
    # Property Detail View
    if st.session_state.selected_property:
        prop_data = get_property_by_id(st.session_state.selected_property)
        
        if prop_data:
            if st.button("❌ Close Details & Go Back", type="secondary"):
                st.session_state.selected_property = None
                st.rerun()
            
            st.markdown("---")
            st.header(f"📍 {prop_data['address']}")
            st.caption(f"{prop_data['city']}, MI {prop_data['zip']}")
            
            priority = calculate_ai_priority_score(prop_data)
            tier_colors = {'HOT': '🔴', 'WARM': '🟠', 'NURTURE': '🔵', 'MONITOR': '⚪'}
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Priority Score", f"{priority['score']}/100")
            with col2:
                st.metric("Tier", f"{tier_colors.get(priority['tier'], '')} {priority['tier']}")
            with col3:
                st.metric("Stage", prop_data.get('stage', 'New Lead'))
            
            st.info(priority['ai_recommendation'])
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Deal Analysis", "👤 Owner", "📝 Notes"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Property Details**")
                    st.write(f"• Type: {prop_data.get('property_type', 'N/A')}")
                    st.write(f"• Beds: {prop_data.get('beds', 'N/A')}")
                    st.write(f"• Baths: {prop_data.get('baths', 'N/A')}")
                    st.write(f"• Sqft: {prop_data.get('sqft', 0):,}")
                    st.write(f"• Year: {prop_data.get('year_built', 'N/A')}")
                
                with col2:
                    st.markdown("**Financial Summary**")
                    st.write(f"• List Price: ${prop_data.get('list_price', 0):,}")
                    st.write(f"• ARV: ${prop_data.get('arv', 0):,}")
                    st.write(f"• Equity: {prop_data.get('equity_percent', 0)}%")
                    st.write(f"• Days on Market: {prop_data.get('days_on_market', 0)}")
            
            with tab2:
                fin = priority.get('financials', {})
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Max Offer", f"${fin.get('max_offer', 0):,.0f}")
                with col2:
                    st.metric("Est. Repairs", f"${fin.get('estimated_repairs', 0):,.0f}")
                with col3:
                    st.metric("ROI", f"{fin.get('roi', 0):.1f}%")
                with col4:
                    st.metric("Net Profit", f"${fin.get('net_profit', 0):,.0f}")
            
            with tab3:
                st.write(f"**Name:** {prop_data.get('owner_name', 'N/A')}")
                st.write(f"**Phone:** {prop_data.get('owner_phone', 'N/A') or 'Not available'}")
                st.write(f"**Email:** {prop_data.get('owner_email', 'N/A') or 'Not available'}")
            
            with tab4:
                new_note = st.text_area("Add Note")
                if st.button("➕ Add Note"):
                    if new_note:
                        add_note(st.session_state.selected_property, new_note)
                        st.success("✅ Note added!")
                        st.rerun()
                
                notes = get_notes(st.session_state.selected_property)
                if not notes.empty:
                    for _, note in notes.iterrows():
                        st.caption(f"{note['created_at']}")
                        st.write(note['content'])
                        st.markdown("---")
            
            if st.button("📄 Generate CMA Report", type="primary"):
                pdf_buffer = generate_cma_pdf(prop_data, priority)
                st.download_button(
                    label="📥 Download CMA PDF",
                    data=pdf_buffer,
                    file_name=f"CMA_{prop_data['address'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            
            st.stop()
    
    # Dashboard
    if page == "🏠 Dashboard":
        st.header("Dashboard")
        
        properties_df = get_all_properties()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            hot_count = len(properties_df[properties_df['priority_tier'] == 'HOT']) if not properties_df.empty else 0
            st.metric("🔥 Hot Leads", hot_count)
        
        with col2:
            warm_count = len(properties_df[properties_df['priority_tier'] == 'WARM']) if not properties_df.empty else 0
            st.metric("🌡️ Warm Leads", warm_count)
        
        with col3:
            total_count = len(properties_df)
            st.metric("🏠 Total Properties", total_count)
        
        with col4:
            total_value = properties_df['list_price'].sum() if not properties_df.empty else 0
            st.metric("💰 Pipeline Value", f"${total_value/1000000:.1f}M")
        
        with col5:
            avg_score = properties_df['priority_score'].mean() if not properties_df.empty else 0
            st.metric("📈 Avg Score", f"{avg_score:.0f}")
        
        st.markdown("---")
        st.subheader("🔥 Hot Leads - Contact Today")
        
        if not properties_df.empty:
            hot_leads = properties_df[properties_df['priority_tier'] == 'HOT'].head(6)
            
            if not hot_leads.empty:
                cols = st.columns(3)
                for idx, (_, prop) in enumerate(hot_leads.iterrows()):
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{prop['address']}**")
                            st.caption(f"{prop['city']}, MI")
                            st.markdown(f"💰 ${prop['list_price']:,} | 🎯 Score: **{prop['priority_score']}**")
                            
                            if st.button("View Details", key=f"hot_{prop['id']}"):
                                st.session_state.selected_property = prop['id']
                                st.rerun()
            else:
                st.info("No hot leads yet.")
    
    # Property Search
    elif page == "🔍 Property Search":
        st.header("Property Search")
        
        if not st.session_state.use_mock_data:
            st.info("🔑 **API Mode Active** - Search real properties")
            
            if not st.session_state.api_key:
                st.warning("⚠️ Enter your API key in the sidebar")
            else:
                api_city = st.selectbox("City", list(MICHIGAN_CITIES.keys()), key="api_city")
                
                if st.button("🔍 Search RealEstateAPI", type="primary"):
                    with st.spinner("Searching..."):
                        api = RealEstateAPI(st.session_state.api_key)
                        
                        # Minimal params
                        params = {
                            "city": api_city,
                            "state": "MI",
                            "size": 25
                        }
                        
                        with st.expander("🔧 Debug: Request"):
                            st.json(params)
                        
                        results = api.property_search(params)
                        
                        with st.expander("🔧 Debug: Response"):
                            st.json(results)
                        
                        data = None
                        if results:
                            if isinstance(results, list):
                                data = results
                            elif results.get('data'):
                                data = results['data']
                            elif results.get('results'):
                                data = results['results']
                            elif results.get('properties'):
                                data = results['properties']
                        
                        if data and len(data) > 0:
                            st.success(f"✅ Found {len(data)} properties!")
                            st.session_state.api_results = data
                        elif results and results.get('error'):
                            st.error(f"API Error: {results.get('error')}")
                        else:
                            st.warning("No properties found.")
                
                st.markdown("---")
        
        st.subheader("📋 Saved Properties")
        
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            city_filter = st.selectbox("Filter by City", ["All Cities"] + list(properties_df['city'].unique()))
            
            filtered_df = properties_df.copy()
            if city_filter != "All Cities":
                filtered_df = filtered_df[filtered_df['city'] == city_filter]
            
            st.markdown(f"**{len(filtered_df)} properties**")
            
            for _, prop in filtered_df.head(20).iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{prop['address']}**")
                        st.caption(f"{prop['city']}, MI | {prop['beds']}bd/{prop['baths']}ba | {prop['sqft']:,} sqft")
                    
                    with col2:
                        st.metric("Price", f"${prop['list_price']:,}")
                    
                    with col3:
                        tier_colors = {'HOT': '🔴', 'WARM': '🟠', 'NURTURE': '🔵', 'MONITOR': '⚪'}
                        st.markdown(f"{tier_colors.get(prop['priority_tier'], '')} {prop['priority_score']}")
                        if st.button("View", key=f"view_{prop['id']}"):
                            st.session_state.selected_property = prop['id']
                            st.rerun()
    
    # Priority Queue
    elif page == "🎯 Priority Queue":
        st.header("Contact Priority Queue")
        
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            tab1, tab2, tab3, tab4 = st.tabs(["🔥 HOT", "🌡️ WARM", "💧 NURTURE", "👀 MONITOR"])
            
            with tab1:
                hot_df = properties_df[properties_df['priority_tier'] == 'HOT']
                st.markdown(f"**{len(hot_df)} hot leads** - Call TODAY!")
                for _, prop in hot_df.iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{prop['address']}** - {prop['city']}")
                            st.caption(f"💰 ${prop['list_price']:,} | Score: {prop['priority_score']}")
                            if prop['owner_phone']:
                                st.markdown(f"📞 {prop['owner_phone']}")
                        with col2:
                            if st.button("View", key=f"q_{prop['id']}"):
                                st.session_state.selected_property = prop['id']
                                st.rerun()
            
            with tab2:
                warm_df = properties_df[properties_df['priority_tier'] == 'WARM']
                st.markdown(f"**{len(warm_df)} warm leads**")
                for _, prop in warm_df.head(10).iterrows():
                    st.write(f"• {prop['address']} - {prop['city']} - Score: {prop['priority_score']}")
            
            with tab3:
                nurture_df = properties_df[properties_df['priority_tier'] == 'NURTURE']
                st.markdown(f"**{len(nurture_df)} nurture leads**")
                for _, prop in nurture_df.head(10).iterrows():
                    st.write(f"• {prop['address']} - {prop['city']} - Score: {prop['priority_score']}")
            
            with tab4:
                monitor_df = properties_df[properties_df['priority_tier'] == 'MONITOR']
                st.markdown(f"**{len(monitor_df)} monitor leads**")
                for _, prop in monitor_df.head(10).iterrows():
                    st.write(f"• {prop['address']} - {prop['city']} - Score: {prop['priority_score']}")
    
    # Pipeline
    elif page == "📋 Pipeline":
        st.header("Deal Pipeline")
        
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            st.subheader("Pipeline Overview")
            stage_counts = properties_df['stage'].value_counts()
            
            cols = st.columns(len(PIPELINE_STAGES))
            for idx, stage in enumerate(PIPELINE_STAGES):
                with cols[idx]:
                    count = stage_counts.get(stage, 0)
                    st.metric(stage, count)
            
            st.markdown("---")
            
            selected_stage = st.selectbox("Filter by Stage", ["All"] + PIPELINE_STAGES)
            
            if selected_stage != "All":
                filtered = properties_df[properties_df['stage'] == selected_stage]
            else:
                filtered = properties_df
            
            for _, prop in filtered.head(15).iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**{prop['address']}** - {prop['city']}")
                        st.caption(f"${prop['list_price']:,} | Current: {prop['stage']}")
                    with col2:
                        new_stage = st.selectbox(
                            "Move to",
                            PIPELINE_STAGES,
                            index=PIPELINE_STAGES.index(prop['stage']) if prop['stage'] in PIPELINE_STAGES else 0,
                            key=f"pipe_{prop['id']}"
                        )
                        if new_stage != prop['stage']:
                            update_property_stage(prop['id'], new_stage)
                            st.rerun()
    
    # Map View
    elif page == "🗺️ Map View":
        st.header("Property Map")
        
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            map_tier = st.selectbox("Filter by Tier", ["All", "HOT", "WARM", "NURTURE", "MONITOR"])
            
            filtered = properties_df.copy()
            if map_tier != "All":
                filtered = filtered[filtered['priority_tier'] == map_tier]
            
            st.markdown(f"Showing **{len(filtered)}** properties")
            
            m = create_property_map(filtered)
            st_folium(m, width=None, height=500, use_container_width=True)
            
            st.markdown("**Legend:** 🔴 HOT | 🟠 WARM | 🔵 NURTURE | ⚪ MONITOR")
    
    # Analytics
    elif page == "📊 Analytics":
        st.header("Analytics Dashboard")
        properties_df = get_all_properties()
        create_analytics_dashboard(properties_df)
    
    # Alerts
    elif "🔔 Alerts" in page:
        st.header("🔔 Alerts")
        
        alerts_df = get_alerts()
        
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                priority_colors = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                is_read = alert['read'] == 1
                
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"{priority_colors.get(alert['priority'], '⚪')} **{alert['title']}**")
                        st.caption(alert['message'])
                    with col2:
                        if not is_read:
                            if st.button("✓", key=f"alert_{alert['id']}"):
                                mark_alert_read(alert['id'])
                                st.rerun()
        else:
            st.info("No alerts")
    
    # AI Tools
    elif page == "🤖 AI Tools":
        st.header("🤖 AI-Powered Tools")
        
        tab1, tab2, tab3 = st.tabs(["🏷️ ARV Predictor", "🏘️ Neighborhood Analysis", "📊 Deal Analyzer"])
        
        with tab1:
            st.subheader("AI ARV Prediction")
            
            col1, col2 = st.columns(2)
            with col1:
                arv_city = st.selectbox("City", list(MICHIGAN_CITIES.keys()))
                arv_beds = st.number_input("Bedrooms", min_value=1, max_value=6, value=3)
                arv_baths = st.number_input("Bathrooms", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
            with col2:
                arv_sqft = st.number_input("Square Feet", min_value=500, max_value=5000, value=1500)
                arv_year = st.number_input("Year Built", min_value=1900, max_value=2024, value=1980)
            
            if st.button("🔮 Predict ARV", type="primary"):
                prop_data = {'beds': arv_beds, 'baths': arv_baths, 'sqft': arv_sqft, 'year_built': arv_year}
                prediction = predict_arv(prop_data, arv_city)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Predicted ARV", f"${prediction['predicted_arv']:,}")
                with col2:
                    st.metric("Confidence", f"{prediction['confidence']}%")
                with col3:
                    st.metric("Price/Sqft", f"${prediction['price_per_sqft']}")
        
        with tab2:
            st.subheader("🏘️ Neighborhood Analysis")
            
            analysis_city = st.selectbox("Select City", list(MICHIGAN_CITIES.keys()), key="analysis_city")
            
            if st.button("🔍 Analyze", type="primary"):
                analysis = analyze_neighborhood(analysis_city)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Score", f"{analysis['score']}/100")
                    st.metric("Grade", analysis['grade'])
                with col2:
                    st.info(analysis['investment_outlook'])
        
        with tab3:
            st.subheader("📊 Deal Analyzer")
            
            col1, col2 = st.columns(2)
            with col1:
                deal_price = st.number_input("Purchase Price", min_value=0, value=100000, step=5000)
                deal_arv = st.number_input("Estimated ARV", min_value=0, value=150000, step=5000)
            with col2:
                deal_repairs = st.number_input("Estimated Repairs", min_value=0, value=30000, step=5000)
                deal_holding = st.number_input("Holding Months", min_value=1, max_value=12, value=4)
            
            if st.button("📊 Analyze Deal", type="primary"):
                holding_costs = deal_arv * 0.01 * deal_holding
                selling_costs = deal_arv * 0.09
                total_investment = deal_price + deal_repairs + holding_costs + selling_costs
                net_profit = deal_arv - total_investment
                roi = (net_profit / total_investment * 100) if total_investment > 0 else 0
                max_offer = (deal_arv * 0.7) - deal_repairs
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Max Offer", f"${max_offer:,.0f}")
                with col2:
                    st.metric("Total Investment", f"${total_investment:,.0f}")
                with col3:
                    st.metric("Net Profit", f"${net_profit:,.0f}")
                with col4:
                    st.metric("ROI", f"{roi:.1f}%")
                
                if roi >= 20 and net_profit >= 20000:
                    st.success("✅ GOOD DEAL!")
                elif roi >= 15:
                    st.info("👍 DECENT DEAL")
                elif roi >= 10:
                    st.warning("⚠️ MARGINAL")
                else:
                    st.error("❌ PASS")
    
    # Settings
    elif page == "⚙️ Settings":
        st.header("Settings")
        
        st.subheader("📊 Database")
        properties_df = get_all_properties()
        st.info(f"Total properties: {len(properties_df)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate Demo Data"):
                conn = sqlite3.connect(get_db_path())
                c = conn.cursor()
                c.execute("DELETE FROM properties")
                c.execute("DELETE FROM alerts")
                conn.commit()
                conn.close()
                st.session_state.mock_loaded = False
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                conn = sqlite3.connect(get_db_path())
                c = conn.cursor()
                c.execute("DELETE FROM properties")
                c.execute("DELETE FROM followups")
                c.execute("DELETE FROM notes")
                c.execute("DELETE FROM alerts")
                conn.commit()
                conn.close()
                st.success("Data cleared!")
                st.rerun()

if __name__ == "__main__":
    main()

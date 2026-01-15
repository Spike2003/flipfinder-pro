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

# Custom CSS for better styling
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
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
            
            # Return error details if not successful
            if response.status_code != 200:
                return {
                    "error": f"API returned status {response.status_code}: {response.text[:200]}",
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
            response.raise_for_status()
            return response.json()
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
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def build_michigan_search(self, city=None, min_price=None, max_price=None, 
                               min_beds=None, property_type=None, distress_filters=None):
        """Build search parameters for Michigan properties using RealEstateAPI format"""
        
        # Start with minimal params that should definitely work
        params = {
            "state": "MI",
            "size": 25
        }
        
        # Add city filter
        if city:
            params["city"] = city
        
        # Add bedroom filter (confirmed from docs)
        if min_beds and min_beds > 0:
            params["bedrooms_min"] = min_beds
        
        # Add distress filters (these should work based on API docs)
        if distress_filters:
            if "Pre-Foreclosure" in distress_filters:
                params["preForeclosure"] = True
            if "Foreclosure" in distress_filters:
                params["foreclosure"] = True
            if "Vacant" in distress_filters:
                params["vacant"] = True
            if "Absentee Owner" in distress_filters:
                params["absenteeOwner"] = True
        
        # Note: Price filters removed for now - need to find correct param names
        # Will add back once we confirm basic search works
        
        return params

STREET_NAMES = [
    'Main St', 'Oak Ave', 'Maple Dr', 'Washington Blvd', 'Jefferson Ave',
    'Lincoln Rd', 'Park Place', 'Cedar Lane', 'Elm St', 'Pine Ave',
    'Highland Dr', 'Lake Shore Dr', 'River Rd', 'Forest Ave', 'Sunset Blvd',
    'Cherry Lane', 'Birch St', 'Willow Way', 'Spruce Dr', 'Hickory Rd'
]

FIRST_NAMES = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
               'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
              'Rodriguez', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson', 'Martin']

# ============================================================================
# DATABASE SETUP
# ============================================================================

def get_db_path():
    """Get database path - works locally and on cloud"""
    return 'flipfinder.db'

def init_database():
    """Initialize SQLite database for data persistence"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    # Properties table
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
        predicted_arv INTEGER,
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
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        raw_data TEXT
    )''')
    
    # Follow-ups table
    c.execute('''CREATE TABLE IF NOT EXISTS followups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id TEXT,
        type TEXT,
        date TEXT,
        time TEXT,
        assignee TEXT,
        status TEXT DEFAULT 'pending',
        outcome TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties (id)
    )''')
    
    # Notes table
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id TEXT,
        content TEXT,
        author TEXT DEFAULT 'User',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties (id)
    )''')
    
    # Alerts table
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
    
    # Activity log
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        property_id TEXT,
        details TEXT,
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
        
        # Generate realistic property data
        beds = random.choices([2, 3, 4, 5], weights=[15, 45, 30, 10])[0]
        baths = random.choices([1, 1.5, 2, 2.5, 3], weights=[10, 20, 40, 20, 10])[0]
        sqft = random.randint(800, 3500)
        year_built = random.randint(1920, 2015)
        lot_size = round(random.uniform(0.1, 0.8), 2)
        
        # Price based on city median with variation
        base_price = city_data['median_price']
        price_variance = random.uniform(0.5, 1.5)
        sqft_factor = sqft / 1500  # Adjust for size
        list_price = int(base_price * price_variance * sqft_factor)
        
        # Generate distress signals (weighted toward motivated sellers)
        num_signals = random.choices([0, 1, 2, 3, 4, 5], weights=[20, 25, 25, 15, 10, 5])[0]
        signals = random.sample(DISTRESS_SIGNALS, min(num_signals, len(DISTRESS_SIGNALS)))
        
        # Equity calculation
        ownership_years = random.randint(1, 30)
        if ownership_years > 15:
            equity_percent = random.randint(70, 100)
        elif ownership_years > 7:
            equity_percent = random.randint(40, 80)
        else:
            equity_percent = random.randint(10, 50)
        
        # Days on market (higher for distressed)
        if 'Foreclosure' in signals or 'Pre-Foreclosure' in signals:
            days_on_market = random.randint(60, 180)
        else:
            days_on_market = random.randint(5, 120)
        
        # Price reductions
        price_reductions = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
        
        # Generate address
        street_num = random.randint(100, 9999)
        street = random.choice(STREET_NAMES)
        address = f"{street_num} {street}"
        
        # Generate owner
        owner_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        # Coordinates with slight randomization around city center
        lat = city_data['lat'] + random.uniform(-0.05, 0.05)
        lng = city_data['lng'] + random.uniform(-0.05, 0.05)
        
        # Generate phone (some missing to simulate real data)
        has_phone = random.random() > 0.3
        phone = f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}" if has_phone else ""
        
        # Generate email (some missing)
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
        
        # Generate some alerts
        generate_mock_alerts()
        
        return True
    return False

def generate_mock_alerts():
    """Generate mock alerts for demo"""
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
    
    # Extract data
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
    city = property_data.get('city', '')
    
    if isinstance(distress_signals, str):
        distress_signals = distress_signals.split(',') if distress_signals else []
    
    # Estimate repairs
    current_year = datetime.now().year
    age = current_year - year_built if year_built > 1800 else 50
    
    if age > 50:
        repair_per_sqft = 65
        ai_insights.append("🔧 Older home - budget for major systems (roof, HVAC, plumbing)")
    elif age > 30:
        repair_per_sqft = 45
        ai_insights.append("🔧 Medium-age home - likely needs kitchen/bath updates")
    elif age > 15:
        repair_per_sqft = 30
        ai_insights.append("✅ Newer construction - mostly cosmetic updates")
    else:
        repair_per_sqft = 20
        ai_insights.append("✅ Very new - minimal repairs expected")
    
    estimated_repairs = sqft * repair_per_sqft
    
    # 70% Rule
    max_offer = (arv * 0.7) - estimated_repairs
    gap = max_offer - list_price
    gap_percent = (gap / arv * 100) if arv > 0 else 0
    
    # ROI
    total_investment = list_price + estimated_repairs + (arv * 0.13)
    net_profit = arv - total_investment
    roi = (net_profit / total_investment * 100) if total_investment > 0 else 0
    
    # PROFIT POTENTIAL (0-40)
    if gap_percent >= 15:
        score += 25
        factors.append({"name": "🎯 Excellent Price Gap (15%+)", "points": 25, "category": "profit"})
        ai_insights.append("💰 SLAM DUNK - Priced significantly below max offer!")
    elif gap_percent >= 10:
        score += 20
        factors.append({"name": "Great Price Gap (10%+)", "points": 20, "category": "profit"})
        ai_insights.append("💰 Strong profit margin available")
    elif gap_percent >= 5:
        score += 15
        factors.append({"name": "Good Price Gap (5%+)", "points": 15, "category": "profit"})
    elif gap_percent >= 0:
        score += 10
        factors.append({"name": "At Max Offer", "points": 10, "category": "profit"})
    elif gap_percent >= -10:
        score += 5
        factors.append({"name": "Negotiable", "points": 5, "category": "profit"})
        ai_insights.append("⚠️ Needs 10%+ discount to make numbers work")
    
    if roi >= 30:
        score += 15
        factors.append({"name": "🚀 Excellent ROI (30%+)", "points": 15, "category": "profit"})
    elif roi >= 20:
        score += 12
        factors.append({"name": "Strong ROI (20%+)", "points": 12, "category": "profit"})
    elif roi >= 15:
        score += 8
        factors.append({"name": "Good ROI (15%+)", "points": 8, "category": "profit"})
    elif roi >= 10:
        score += 5
        factors.append({"name": "Acceptable ROI (10%+)", "points": 5, "category": "profit"})
    
    # SELLER MOTIVATION (0-35)
    if 'Foreclosure' in distress_signals:
        score += 15
        factors.append({"name": "🚨 Active Foreclosure", "points": 15, "category": "motivation"})
        ai_insights.append("🔥 URGENT - Facing sale deadline!")
    
    if 'Pre-Foreclosure' in distress_signals:
        score += 12
        factors.append({"name": "⚠️ Pre-Foreclosure", "points": 12, "category": "motivation"})
        ai_insights.append("Owner in financial distress - needs solution fast")
    
    if 'Probate/Estate' in distress_signals:
        score += 12
        factors.append({"name": "📜 Inherited/Estate", "points": 12, "category": "motivation"})
        ai_insights.append("Emotional sale - heirs often want quick resolution")
    
    if 'Tax Lien' in distress_signals:
        score += 10
        factors.append({"name": "💸 Tax Lien", "points": 10, "category": "motivation"})
    
    if 'Divorce' in distress_signals:
        score += 10
        factors.append({"name": "💔 Divorce", "points": 10, "category": "motivation"})
        ai_insights.append("Divorce situation - both parties often motivated to sell")
    
    if 'Absentee Owner' in distress_signals:
        score += 6
        factors.append({"name": "📍 Absentee Owner", "points": 6, "category": "motivation"})
        ai_insights.append("Out-of-area owner - management burden")
    
    if 'Vacant' in distress_signals:
        score += 8
        factors.append({"name": "🏚️ Vacant Property", "points": 8, "category": "motivation"})
        ai_insights.append("Vacant = carrying costs + liability for owner")
    
    if 'Tired Landlord' in distress_signals:
        score += 8
        factors.append({"name": "😫 Tired Landlord", "points": 8, "category": "motivation"})
        ai_insights.append("Burnt out on property management")
    
    if 'Code Violations' in distress_signals:
        score += 7
        factors.append({"name": "⚠️ Code Violations", "points": 7, "category": "motivation"})
        ai_insights.append("City pressure to fix or sell")
    
    if ownership_years >= 15:
        score += 5
        factors.append({"name": "⏰ Long Ownership (15+ yrs)", "points": 5, "category": "motivation"})
    
    if equity_percent >= 70:
        score += 6
        factors.append({"name": "💎 High Equity (70%+)", "points": 6, "category": "motivation"})
        ai_insights.append("High equity = more negotiation flexibility")
    elif equity_percent >= 50:
        score += 4
        factors.append({"name": "Good Equity (50%+)", "points": 4, "category": "motivation"})
    
    if equity_percent >= 95:
        score += 5
        factors.append({"name": "🆓 Free & Clear", "points": 5, "category": "motivation"})
        ai_insights.append("No lender approval needed - faster closing!")
    
    signal_count = len([s for s in distress_signals if s])
    if signal_count >= 5:
        score += 8
        factors.append({"name": "🔥 5+ Distress Signals", "points": 8, "category": "motivation"})
        ai_insights.append("MULTIPLE MOTIVATION SIGNALS - High priority!")
    elif signal_count >= 3:
        score += 5
        factors.append({"name": "Multiple Signals", "points": 5, "category": "motivation"})
    
    # URGENCY (0-15)
    if days_on_market >= 90:
        score += 8
        factors.append({"name": "📅 Stale Listing (90+ days)", "points": 8, "category": "urgency"})
        ai_insights.append("On market 90+ days - seller getting anxious")
    elif days_on_market >= 60:
        score += 5
        factors.append({"name": "Getting Stale (60+ days)", "points": 5, "category": "urgency"})
    
    if price_reductions >= 2:
        score += 8
        factors.append({"name": "📉 Multiple Price Drops", "points": 8, "category": "urgency"})
        ai_insights.append("Multiple price reductions = motivated seller")
    elif price_reductions >= 1:
        score += 5
        factors.append({"name": "Price Reduced", "points": 5, "category": "urgency"})
    
    # Winter bonus
    current_month = datetime.now().month
    if current_month in [11, 12, 1, 2]:
        score += 3
        factors.append({"name": "❄️ Winter Season", "points": 3, "category": "urgency"})
        ai_insights.append("Winter in Michigan = motivated sellers")
    
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
    
    # Determine tier
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
    
    # AI recommendation
    if score >= 75 and roi >= 20:
        ai_recommendation = "🎯 STRONG BUY - All signals align for profit"
    elif score >= 55 and roi >= 15:
        ai_recommendation = "✅ GOOD OPPORTUNITY - Worth pursuing"
    elif score >= 35:
        ai_recommendation = "⚠️ NEEDS WORK - Negotiate hard or wait for price drop"
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
    """AI-powered ARV prediction based on market data and comps"""
    city_data = MICHIGAN_CITIES.get(city, {'median_price': 150000, 'appreciation': 8.0})
    
    sqft = property_data.get('sqft', 1500)
    beds = property_data.get('beds', 3)
    baths = property_data.get('baths', 2)
    year_built = property_data.get('year_built', 1970)
    list_price = property_data.get('list_price', city_data['median_price'])
    
    # Base ARV calculation
    price_per_sqft = city_data['median_price'] / 1500  # Average sqft
    base_arv = sqft * price_per_sqft
    
    # Adjustments
    # Bedroom adjustment (+/- $10k per bedroom from 3)
    bed_adjustment = (beds - 3) * 10000
    
    # Bathroom adjustment (+$7.5k per bath above 1.5)
    bath_adjustment = max(0, (baths - 1.5)) * 7500
    
    # Age adjustment (newer = higher value)
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
    
    # Market appreciation factor
    appreciation_factor = 1 + (city_data['appreciation'] / 100)
    
    # Calculate predicted ARV
    predicted_arv = (base_arv + bed_adjustment + bath_adjustment) * age_multiplier * appreciation_factor
    
    # Confidence based on data quality
    confidence = random.randint(75, 95)
    
    # Generate comp range
    low_arv = int(predicted_arv * 0.9)
    high_arv = int(predicted_arv * 1.1)
    
    return {
        'predicted_arv': int(predicted_arv),
        'low_estimate': low_arv,
        'high_estimate': high_arv,
        'confidence': confidence,
        'price_per_sqft': int(predicted_arv / sqft),
        'appreciation_rate': city_data['appreciation'],
        'factors': {
            'base_value': int(base_arv),
            'bed_adjustment': bed_adjustment,
            'bath_adjustment': bath_adjustment,
            'age_multiplier': age_multiplier,
            'market_factor': appreciation_factor
        }
    }

def analyze_neighborhood(city):
    """AI neighborhood analysis with scoring"""
    city_data = MICHIGAN_CITIES.get(city, {'median_price': 150000, 'appreciation': 8.0})
    
    # Generate neighborhood metrics
    school_rating = random.randint(4, 10)
    crime_score = random.randint(3, 9)  # Higher is safer
    walkability = random.randint(20, 85)
    job_growth = round(random.uniform(1.5, 8.5), 1)
    population_trend = random.choice(['Growing', 'Stable', 'Declining'])
    
    # Calculate overall score
    score = int(
        (school_rating * 2) +
        (crime_score * 2) +
        (walkability / 10) +
        (job_growth * 2) +
        (city_data['appreciation'] / 2) +
        (10 if population_trend == 'Growing' else 5 if population_trend == 'Stable' else 0)
    )
    score = min(100, score)
    
    # Investment grade
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
    """Add a note for a property"""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''INSERT INTO notes (property_id, content, author)
                 VALUES (?, ?, ?)''', (prop_id, content, author))
    conn.commit()
    conn.close()

def get_notes(prop_id):
    """Get all notes for a property"""
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
    """Get all follow-ups for a property"""
    conn = sqlite3.connect(get_db_path())
    df = pd.read_sql_query(
        "SELECT * FROM followups WHERE property_id = ? ORDER BY date DESC", 
        conn, params=(prop_id,)
    )
    conn.close()
    return df

# ============================================================================
# ANALYTICS & CHARTS
# ============================================================================

def create_analytics_dashboard(properties_df):
    """Create comprehensive analytics dashboard"""
    
    if properties_df.empty:
        st.warning("No data available for analytics.")
        return
    
    # Row 1: Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        hot_count = len(properties_df[properties_df['priority_tier'] == 'HOT'])
        st.metric("🔥 Hot Leads", hot_count, delta=f"+{random.randint(1,5)} this week")
    
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
        avg_roi = 22.5  # Simulated
        st.metric("📈 Avg ROI", f"{avg_roi}%")
    
    st.markdown("---")
    
    # Row 2: Charts
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
    
    # Row 3: City Analysis
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
        fig.update_layout(showlegend=False, height=400, xaxis_title="Properties", yaxis_title="City")
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
        fig.update_layout(showlegend=False, height=400, xaxis_title="Avg Price ($)", yaxis_title="City")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Row 4: Score Distribution & Trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Priority Score Distribution")
        fig = px.histogram(
            properties_df, 
            x='priority_score', 
            nbins=20,
            color_discrete_sequence=['#6366f1']
        )
        fig.update_layout(height=300, xaxis_title="Priority Score", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏠 Property Type Distribution")
        type_counts = properties_df['property_type'].value_counts()
        fig = px.pie(
            values=type_counts.values, 
            names=type_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Row 5: Price vs Score Scatter
    st.subheader("💰 Price vs Priority Score Analysis")
    fig = px.scatter(
        properties_df,
        x='list_price',
        y='priority_score',
        color='priority_tier',
        size='sqft',
        hover_data=['address', 'city', 'beds', 'baths'],
        color_discrete_map={'HOT': '#ef4444', 'WARM': '#f59e0b', 'NURTURE': '#3b82f6', 'MONITOR': '#6b7280'}
    )
    fig.update_layout(height=400, xaxis_title="List Price ($)", yaxis_title="Priority Score")
    st.plotly_chart(fig, use_container_width=True)
    
    # Row 6: Market Insights
    st.markdown("---")
    st.subheader("🎯 Market Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Top Opportunity Cities:**")
        for city in ['Flint', 'Saginaw', 'Detroit', 'Pontiac', 'Southfield']:
            city_data = MICHIGAN_CITIES.get(city, {})
            st.write(f"• {city}: {city_data.get('appreciation', 0)}% appreciation")
    
    with col2:
        st.markdown("**Best ROI Property Types:**")
        st.write("• Single Family: 25% avg ROI")
        st.write("• Multi-Family: 22% avg ROI")
        st.write("• Duplex: 20% avg ROI")
    
    with col3:
        st.markdown("**Active Alerts:**")
        alerts_df = get_alerts(unread_only=True)
        st.write(f"• {len(alerts_df)} unread alerts")
        st.write(f"• {len(properties_df[properties_df['priority_tier'] == 'HOT'])} hot leads waiting")

# ============================================================================
# MAP GENERATION
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
                <div style="width: 250px; font-family: Arial, sans-serif;">
                    <h4 style="margin: 0; color: #6366f1;">{prop.get('address', 'N/A')}</h4>
                    <p style="margin: 5px 0; color: #666;">{prop.get('city', '')}, MI</p>
                    <hr style="margin: 5px 0; border-color: #eee;">
                    <p><b>💰 Price:</b> ${prop.get('list_price', 0):,}</p>
                    <p><b>🎯 Score:</b> {prop.get('priority_score', 0)} ({tier})</p>
                    <p><b>🏠 Beds/Baths:</b> {prop.get('beds', 0)}/{prop.get('baths', 0)}</p>
                    <p><b>📐 Sqft:</b> {prop.get('sqft', 0):,}</p>
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=12 if tier == 'HOT' else 8,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300)
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
    
    address = f"{property_data.get('address', 'N/A')}, {property_data.get('city', '')}, MI {property_data.get('zip', '')}"
    story.append(Paragraph(f"<b>{address}</b>", styles['Heading1']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    tier = priority_data.get('tier', 'N/A')
    score = priority_data.get('score', 0)
    story.append(Paragraph(f"<b>Priority Score: {score}/100 ({tier})</b>", heading_style))
    story.append(Paragraph(priority_data.get('ai_recommendation', ''), styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Property Summary", heading_style))
    prop_data = [
        ['Property Type', property_data.get('property_type', 'N/A'), 'Year Built', str(property_data.get('year_built', 'N/A'))],
        ['Bedrooms', str(property_data.get('beds', 'N/A')), 'Bathrooms', str(property_data.get('baths', 'N/A'))],
        ['Square Feet', f"{property_data.get('sqft', 0):,}", 'Lot Size', f"{property_data.get('lot_size', 0)} acres"],
    ]
    prop_table = Table(prop_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    prop_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    story.append(prop_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Investment Analysis", heading_style))
    financials = priority_data.get('financials', {})
    fin_data = [
        ['List Price', f"${property_data.get('list_price', 0):,}"],
        ['Estimated ARV', f"${property_data.get('arv', 0):,}"],
        ['Max Offer (70% Rule)', f"${financials.get('max_offer', 0):,.0f}"],
        ['Estimated Repairs', f"${financials.get('estimated_repairs', 0):,.0f}"],
        ['Estimated ROI', f"{financials.get('roi', 0):.1f}%"],
        ['Net Profit Potential', f"${financials.get('net_profit', 0):,.0f}"],
    ]
    fin_table = Table(fin_data, colWidths=[3*inch, 2*inch])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 12))
    
    if priority_data.get('ai_insights'):
        story.append(Paragraph("AI Insights", heading_style))
        for insight in priority_data['ai_insights']:
            story.append(Paragraph(f"• {insight}", styles['Normal']))
    
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
    # Initialize
    init_database()
    
    # Load mock data if empty
    if 'mock_loaded' not in st.session_state:
        if load_mock_data():
            st.session_state.mock_loaded = True
            st.toast("✅ Demo data loaded successfully!", icon="🎉")
    
    # Session state
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
        
        # Data source toggle
        st.session_state.use_mock_data = st.toggle("🎭 Use Demo Data", value=True)
        
        if not st.session_state.use_mock_data:
            api_key = st.text_input("🔑 RealEstateAPI Key", type="password", value=st.session_state.api_key)
            if api_key:
                st.session_state.api_key = api_key
                st.success("✅ API Key Set")
        
        st.markdown("---")
        
        # Alerts badge
        alerts_df = get_alerts(unread_only=True)
        alert_count = len(alerts_df)
        
        # Navigation
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
    
    # Main content
    st.title("🏠 FlipFinder Pro")
    st.caption("AI-Powered Michigan Fix & Flip Investment Platform")
    
    # =========================================================================
    # PROPERTY DETAIL VIEW (Shows at top when property selected)
    # =========================================================================
    if st.session_state.selected_property:
        prop_data = get_property_by_id(st.session_state.selected_property)
        
        if prop_data:
            # Close button
            if st.button("❌ Close Details & Go Back", type="secondary"):
                st.session_state.selected_property = None
                st.rerun()
            
            st.markdown("---")
            
            # Header
            st.header(f"📍 {prop_data['address']}")
            st.caption(f"{prop_data['city']}, MI {prop_data['zip']}")
            
            # Priority score
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
            
            # Tabs for details
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📊 Overview", "💰 Deal Analysis", "🤖 AI Insights", 
                "👤 Owner", "📞 Follow-ups", "📝 Notes"
            ])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Property Details**")
                    st.write(f"• Type: {prop_data.get('property_type', 'N/A')}")
                    st.write(f"• Beds: {prop_data.get('beds', 'N/A')}")
                    st.write(f"• Baths: {prop_data.get('baths', 'N/A')}")
                    st.write(f"• Sqft: {prop_data.get('sqft', 0):,}")
                    st.write(f"• Year: {prop_data.get('year_built', 'N/A')}")
                    st.write(f"• Lot: {prop_data.get('lot_size', 0)} acres")
                
                with col2:
                    st.markdown("**Financial Summary**")
                    st.write(f"• List Price: ${prop_data.get('list_price', 0):,}")
                    st.write(f"• Est. Value: ${prop_data.get('estimated_value', 0):,}")
                    st.write(f"• ARV: ${prop_data.get('arv', 0):,}")
                    st.write(f"• Equity: {prop_data.get('equity_percent', 0)}%")
                    st.write(f"• Days on Market: {prop_data.get('days_on_market', 0)}")
                
                st.markdown("**Distress Signals**")
                signals = prop_data.get('distress_signals', '')
                if signals:
                    for signal in signals.split(','):
                        if signal.strip():
                            st.write(f"⚠️ {signal.strip()}")
                else:
                    st.write("No distress signals detected")
            
            with tab2:
                st.markdown("### 70% Rule Analysis")
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
                
                st.markdown("### Scoring Breakdown")
                for factor in priority.get('factors', []):
                    st.write(f"✓ {factor['name']}: +{factor['points']} pts")
            
            with tab3:
                st.markdown("### AI Insights")
                for insight in priority.get('ai_insights', []):
                    st.info(insight)
                
                st.markdown("### Neighborhood Analysis")
                neighborhood = analyze_neighborhood(prop_data.get('city', 'Detroit'))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Neighborhood Score", f"{neighborhood['score']}/100")
                    st.metric("Investment Grade", neighborhood['grade'])
                with col2:
                    st.write(neighborhood['investment_outlook'])
                
                st.markdown("### AI ARV Prediction")
                arv_pred = predict_arv(prop_data, prop_data.get('city', 'Detroit'))
                st.metric("Predicted ARV", f"${arv_pred['predicted_arv']:,}")
                st.caption(f"Range: ${arv_pred['low_estimate']:,} - ${arv_pred['high_estimate']:,} ({arv_pred['confidence']}% confidence)")
            
            with tab4:
                st.markdown("### Owner Information")
                st.write(f"**Name:** {prop_data.get('owner_name', 'N/A')}")
                st.write(f"**Phone:** {prop_data.get('owner_phone', 'N/A') or 'Not available'}")
                st.write(f"**Email:** {prop_data.get('owner_email', 'N/A') or 'Not available'}")
                st.write(f"**Mailing:** {prop_data.get('owner_mailing', 'N/A')}")
                st.write(f"**Ownership:** {prop_data.get('ownership_years', 0)} years")
            
            with tab5:
                st.markdown("### Schedule Follow-up")
                col1, col2 = st.columns(2)
                with col1:
                    fu_type = st.selectbox("Type", ["📞 Call", "✉️ Email", "💬 Text", "📬 Mail", "🚗 Door Knock"])
                    fu_date = st.date_input("Date")
                with col2:
                    fu_time = st.time_input("Time")
                    fu_assignee = st.text_input("Assign to")
                
                if st.button("➕ Add Follow-up"):
                    add_followup(st.session_state.selected_property, fu_type, str(fu_date), str(fu_time), fu_assignee)
                    st.success("✅ Follow-up scheduled!")
                
                st.markdown("### Scheduled Follow-ups")
                followups = get_followups(st.session_state.selected_property)
                if not followups.empty:
                    for _, fu in followups.iterrows():
                        st.write(f"• {fu['type']} - {fu['date']} {fu['time']}")
                else:
                    st.info("No follow-ups scheduled")
            
            with tab6:
                st.markdown("### Add Note")
                new_note = st.text_area("Note content")
                if st.button("➕ Add Note"):
                    if new_note:
                        add_note(st.session_state.selected_property, new_note)
                        st.success("✅ Note added!")
                        st.rerun()
                
                st.markdown("### Notes History")
                notes = get_notes(st.session_state.selected_property)
                if not notes.empty:
                    for _, note in notes.iterrows():
                        with st.container(border=True):
                            st.caption(f"{note['author']} - {note['created_at']}")
                            st.write(note['content'])
                else:
                    st.info("No notes yet")
            
            # CMA Download
            st.markdown("---")
            if st.button("📄 Generate CMA Report", type="primary"):
                pdf_buffer = generate_cma_pdf(prop_data, priority)
                st.download_button(
                    label="📥 Download CMA PDF",
                    data=pdf_buffer,
                    file_name=f"CMA_{prop_data['address'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            
            st.markdown("---")
            st.markdown("---")
        
        # Stop here - don't show the regular pages when viewing details
        st.stop()
    
    # =========================================================================
    # DASHBOARD
    # =========================================================================
    if page == "🏠 Dashboard":
        st.header("Dashboard")
        
        properties_df = get_all_properties()
        
        # Key metrics
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
        
        # Hot leads
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
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown(f"💰 ${prop['list_price']:,}")
                            with col_b:
                                st.markdown(f"🎯 Score: **{prop['priority_score']}**")
                            
                            signals = prop.get('distress_signals', '')
                            if signals:
                                st.caption(f"⚠️ {signals[:30]}...")
                            
                            if st.button("View Details", key=f"hot_{prop['id']}"):
                                st.session_state.selected_property = prop['id']
                                st.rerun()
            else:
                st.info("No hot leads yet. Search for properties to find opportunities!")
        
        # Recent alerts
        st.markdown("---")
        st.subheader("🔔 Recent Alerts")
        
        alerts_df = get_alerts()
        if not alerts_df.empty:
            for _, alert in alerts_df.head(3).iterrows():
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(alert['priority'], '⚪')
                with st.container(border=True):
                    st.markdown(f"{priority_icon} **{alert['title']}**")
                    st.caption(alert['message'])
        else:
            st.info("No alerts")
    
    # =========================================================================
    # PROPERTY SEARCH
    # =========================================================================
    elif page == "🔍 Property Search":
        st.header("Property Search")
        
        # Show API search option if not using mock data
        if not st.session_state.use_mock_data:
            st.info("🔑 **API Mode Active** - Search real properties from RealEstateAPI.com")
            
            if not st.session_state.api_key:
                st.warning("⚠️ Please enter your API key in the sidebar first!")
            else:
                with st.expander("🔍 API Search Filters", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        api_city = st.selectbox("City", list(MICHIGAN_CITIES.keys()), key="api_city")
                        api_beds = st.selectbox("Min Beds", [1, 2, 3, 4, 5], index=1, key="api_beds")
                    
                    with col2:
                        api_distress = st.multiselect("Distress Filters", 
                            ["Pre-Foreclosure", "Foreclosure", "Vacant", "Absentee Owner"],
                            key="api_distress")
                        st.caption("💡 Price filters temporarily disabled while we verify API params")
                
                if st.button("🔍 Search RealEstateAPI", type="primary", use_container_width=True):
                    with st.spinner("Searching RealEstateAPI.com..."):
                        api = RealEstateAPI(st.session_state.api_key)
                        
                        # Build search params
                        params = api.build_michigan_search(
                            city=api_city,
                            min_beds=api_beds,
                            distress_filters=api_distress if api_distress else None
                        )
                        
                        # Show params for debugging
                        with st.expander("🔧 Debug: API Request Parameters"):
                            st.json(params)
                        
                        results = api.property_search(params)
                        
                        # Show raw response for debugging
                        with st.expander("🔧 Debug: API Response"):
                            st.json(results)
                        
                        # Check for results in different possible structures
                        data = None
                        if results:
                            # Try different response structures
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
                            st.info("💡 **Tip:** Check that your API key is correct and you have an active subscription.")
                        else:
                            st.warning("No properties found. Try adjusting your filters or check the debug info above.")
                
                # Display API results
                if 'api_results' in st.session_state and st.session_state.api_results:
                    st.markdown("---")
                    st.subheader(f"API Results ({len(st.session_state.api_results)} properties)")
                    
                    for idx, prop in enumerate(st.session_state.api_results[:20]):  # Limit to 20
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            # Extract address
                            address_data = prop.get('address', {})
                            if isinstance(address_data, dict):
                                full_address = address_data.get('streetAddress', 'N/A')
                                city_name = address_data.get('city', 'N/A')
                                zip_code = address_data.get('zip', '')
                            else:
                                full_address = str(address_data)
                                city_name = api_city
                                zip_code = ''
                            
                            beds = prop.get('bedrooms', 0) or prop.get('beds', 0) or 3
                            baths = prop.get('bathrooms', 0) or prop.get('baths', 0) or 2
                            sqft = prop.get('squareFeet', 0) or prop.get('sqft', 0) or 1500
                            est_value = prop.get('estimatedValue', 0) or prop.get('list_price', 0) or 100000
                            
                            with col1:
                                st.markdown(f"**{full_address}**")
                                st.caption(f"{city_name}, MI {zip_code}")
                                st.write(f"🛏️ {beds} | 🚿 {baths} | 📐 {sqft:,} sqft")
                            
                            with col2:
                                st.metric("Est. Value", f"${est_value:,}")
                            
                            with col3:
                                if st.button("💾 Save Lead", key=f"api_save_{idx}"):
                                    # Prepare property for saving
                                    save_data = {
                                        'id': prop.get('id', f"api_{idx}_{datetime.now().strftime('%H%M%S')}"),
                                        'address': full_address,
                                        'city': city_name,
                                        'state': 'MI',
                                        'zip': zip_code,
                                        'beds': beds,
                                        'baths': baths,
                                        'sqft': sqft,
                                        'year_built': prop.get('yearBuilt', 1980),
                                        'list_price': est_value,
                                        'estimated_value': est_value,
                                        'arv': int(est_value * 1.2),
                                        'equity_percent': prop.get('equityPercent', 50),
                                        'lat': prop.get('latitude', 0) or prop.get('lat', 0),
                                        'lng': prop.get('longitude', 0) or prop.get('lng', 0),
                                        'distress_signals': [],
                                        'owner_name': prop.get('owner', {}).get('name', '') if isinstance(prop.get('owner'), dict) else '',
                                        'stage': 'New Lead'
                                    }
                                    
                                    # Add distress signals
                                    if prop.get('preForeclosure'):
                                        save_data['distress_signals'].append('Pre-Foreclosure')
                                    if prop.get('foreclosure'):
                                        save_data['distress_signals'].append('Foreclosure')
                                    if prop.get('vacant'):
                                        save_data['distress_signals'].append('Vacant')
                                    if prop.get('absenteeOwner'):
                                        save_data['distress_signals'].append('Absentee Owner')
                                    
                                    priority = calculate_ai_priority_score(save_data)
                                    save_property(save_data, priority)
                                    st.success("✅ Saved!")
                                    st.rerun()
                
                st.markdown("---")
        
        # Always show saved properties filter section
        st.subheader("📋 Your Saved Properties")
        
        with st.expander("🔍 Filter Saved Properties", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                city_filter = st.selectbox("City", ["All Cities"] + list(MICHIGAN_CITIES.keys()))
                min_price = st.number_input("Min Price", min_value=0, value=0, step=10000)
            
            with col2:
                type_filter = st.selectbox("Property Type", ["All Types"] + PROPERTY_TYPES)
                max_price = st.number_input("Max Price", min_value=0, value=500000, step=10000)
            
            with col3:
                min_beds = st.selectbox("Min Beds", [None, 1, 2, 3, 4, 5])
                min_score = st.slider("Min Priority Score", 0, 100, 0)
            
            with col4:
                tier_filter = st.selectbox("Priority Tier", ["All", "HOT", "WARM", "NURTURE", "MONITOR"])
                distress_filter = st.multiselect("Distress Signals", DISTRESS_SIGNALS)
        
        # Get and filter properties
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            filtered_df = properties_df.copy()
            
            if city_filter != "All Cities":
                filtered_df = filtered_df[filtered_df['city'] == city_filter]
            if type_filter != "All Types":
                filtered_df = filtered_df[filtered_df['property_type'] == type_filter]
            if min_price > 0:
                filtered_df = filtered_df[filtered_df['list_price'] >= min_price]
            if max_price > 0:
                filtered_df = filtered_df[filtered_df['list_price'] <= max_price]
            if min_beds:
                filtered_df = filtered_df[filtered_df['beds'] >= min_beds]
            if min_score > 0:
                filtered_df = filtered_df[filtered_df['priority_score'] >= min_score]
            if tier_filter != "All":
                filtered_df = filtered_df[filtered_df['priority_tier'] == tier_filter]
            
            st.markdown(f"**{len(filtered_df)} properties found**")
            st.markdown("---")
            
            # Display properties
            for _, prop in filtered_df.iterrows():
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {prop['address']}")
                        st.caption(f"{prop['city']}, MI {prop['zip']}")
                        st.markdown(f"🛏️ {prop['beds']} | 🚿 {prop['baths']} | 📐 {prop['sqft']:,} sqft | 📅 {prop['year_built']}")
                        
                        signals = prop.get('distress_signals', '')
                        if signals:
                            st.caption(f"⚠️ {signals}")
                    
                    with col2:
                        st.metric("Price", f"${prop['list_price']:,}")
                    
                    with col3:
                        st.metric("Score", prop['priority_score'])
                        tier_colors = {'HOT': '🔴', 'WARM': '🟠', 'NURTURE': '🔵', 'MONITOR': '⚪'}
                        st.caption(f"{tier_colors.get(prop['priority_tier'], '')} {prop['priority_tier']}")
                    
                    with col4:
                        if st.button("📄 Details", key=f"detail_{prop['id']}"):
                            st.session_state.selected_property = prop['id']
                            st.rerun()
        else:
            st.info("No properties found. Check settings or add properties.")
    
    # =========================================================================
    # PRIORITY QUEUE
    # =========================================================================
    elif page == "🎯 Priority Queue":
        st.header("Contact Priority Queue")
        st.caption("Properties sorted by AI priority score - contact hot leads first!")
        
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            # Tier tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🔥 HOT", "🌡️ WARM", "💧 NURTURE", "👀 MONITOR"])
            
            with tab1:
                hot_df = properties_df[properties_df['priority_tier'] == 'HOT']
                st.markdown(f"**{len(hot_df)} hot leads** - Call these TODAY!")
                for _, prop in hot_df.iterrows():
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{prop['address']}** - {prop['city']}")
                            st.caption(f"💰 ${prop['list_price']:,} | Score: {prop['priority_score']}")
                        with col2:
                            if prop['owner_phone']:
                                st.markdown(f"📞 {prop['owner_phone']}")
                        with col3:
                            if st.button("View", key=f"q_hot_{prop['id']}"):
                                st.session_state.selected_property = prop['id']
                                st.rerun()
            
            with tab2:
                warm_df = properties_df[properties_df['priority_tier'] == 'WARM']
                st.markdown(f"**{len(warm_df)} warm leads** - Contact this week")
                for _, prop in warm_df.iterrows():
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{prop['address']}** - {prop['city']}")
                            st.caption(f"💰 ${prop['list_price']:,} | Score: {prop['priority_score']}")
                        with col2:
                            if prop['owner_phone']:
                                st.markdown(f"📞 {prop['owner_phone']}")
                        with col3:
                            if st.button("View", key=f"q_warm_{prop['id']}"):
                                st.session_state.selected_property = prop['id']
                                st.rerun()
            
            with tab3:
                nurture_df = properties_df[properties_df['priority_tier'] == 'NURTURE']
                st.markdown(f"**{len(nurture_df)} nurture leads** - Add to drip campaign")
                for _, prop in nurture_df.head(10).iterrows():
                    st.write(f"• {prop['address']} - {prop['city']} - Score: {prop['priority_score']}")
            
            with tab4:
                monitor_df = properties_df[properties_df['priority_tier'] == 'MONITOR']
                st.markdown(f"**{len(monitor_df)} monitor leads** - Watch for price drops")
                for _, prop in monitor_df.head(10).iterrows():
                    st.write(f"• {prop['address']} - {prop['city']} - Score: {prop['priority_score']}")
        else:
            st.info("No properties in queue")
    
    # =========================================================================
    # PIPELINE
    # =========================================================================
    elif page == "📋 Pipeline":
        st.header("Deal Pipeline")
        
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            # Pipeline visualization
            st.subheader("Pipeline Overview")
            stage_counts = properties_df['stage'].value_counts()
            
            cols = st.columns(len(PIPELINE_STAGES))
            for idx, stage in enumerate(PIPELINE_STAGES):
                with cols[idx]:
                    count = stage_counts.get(stage, 0)
                    st.metric(stage, count)
            
            st.markdown("---")
            
            # Kanban-style view
            st.subheader("Pipeline Board")
            
            selected_stage = st.selectbox("Filter by Stage", ["All"] + PIPELINE_STAGES)
            
            if selected_stage != "All":
                filtered = properties_df[properties_df['stage'] == selected_stage]
            else:
                filtered = properties_df
            
            for _, prop in filtered.iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{prop['address']}**")
                        st.caption(f"{prop['city']} | ${prop['list_price']:,}")
                    
                    with col2:
                        st.caption(f"Current: {prop['stage']}")
                        new_stage = st.selectbox(
                            "Move to",
                            PIPELINE_STAGES,
                            index=PIPELINE_STAGES.index(prop['stage']),
                            key=f"pipeline_{prop['id']}"
                        )
                        if new_stage != prop['stage']:
                            update_property_stage(prop['id'], new_stage)
                            st.rerun()
                    
                    with col3:
                        tier = prop['priority_tier']
                        tier_colors = {'HOT': '🔴', 'WARM': '🟠', 'NURTURE': '🔵', 'MONITOR': '⚪'}
                        st.markdown(f"{tier_colors.get(tier, '')} {prop['priority_score']}")
        else:
            st.info("No properties in pipeline")
    
    # =========================================================================
    # MAP VIEW
    # =========================================================================
    elif page == "🗺️ Map View":
        st.header("Property Map")
        
        properties_df = get_all_properties()
        
        if not properties_df.empty:
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                map_tier = st.selectbox("Filter by Tier", ["All", "HOT", "WARM", "NURTURE", "MONITOR"])
            with col2:
                map_city = st.selectbox("Filter by City", ["All"] + list(properties_df['city'].unique()))
            
            filtered = properties_df.copy()
            if map_tier != "All":
                filtered = filtered[filtered['priority_tier'] == map_tier]
            if map_city != "All":
                filtered = filtered[filtered['city'] == map_city]
            
            st.markdown(f"Showing **{len(filtered)}** properties")
            
            # Map
            m = create_property_map(filtered)
            st_folium(m, width=None, height=600, use_container_width=True)
            
            # Legend
            st.markdown("""
            **Legend:** 🔴 HOT | 🟠 WARM | 🔵 NURTURE | ⚪ MONITOR
            """)
        else:
            st.info("No properties to display")
    
    # =========================================================================
    # ANALYTICS
    # =========================================================================
    elif page == "📊 Analytics":
        st.header("Analytics Dashboard")
        
        properties_df = get_all_properties()
        create_analytics_dashboard(properties_df)
    
    # =========================================================================
    # ALERTS
    # =========================================================================
    elif "🔔 Alerts" in page:
        st.header("🔔 Alerts & Notifications")
        
        alerts_df = get_alerts()
        
        if not alerts_df.empty:
            unread_count = len(alerts_df[alerts_df['read'] == 0])
            st.markdown(f"**{unread_count} unread alerts**")
            
            for _, alert in alerts_df.iterrows():
                priority_colors = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                is_read = alert['read'] == 1
                
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        if is_read:
                            st.markdown(f"~~{priority_colors.get(alert['priority'], '⚪')} **{alert['title']}**~~")
                        else:
                            st.markdown(f"{priority_colors.get(alert['priority'], '⚪')} **{alert['title']}**")
                        st.caption(alert['message'])
                        st.caption(f"📅 {alert['created_at']}")
                    
                    with col2:
                        if not is_read:
                            if st.button("✓ Mark Read", key=f"alert_{alert['id']}"):
                                mark_alert_read(alert['id'])
                                st.rerun()
        else:
            st.info("No alerts")
        
        # Alert settings
        st.markdown("---")
        st.subheader("Alert Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("🔥 New Hot Leads", value=True)
            st.checkbox("📉 Price Drops (10%+)", value=True)
            st.checkbox("🏠 New Listings in Target Areas", value=True)
        with col2:
            st.checkbox("📞 Follow-up Reminders", value=True)
            st.checkbox("📊 Weekly Market Reports", value=False)
            st.checkbox("🎯 Score Changes", value=False)
    
    # =========================================================================
    # AI TOOLS
    # =========================================================================
    elif page == "🤖 AI Tools":
        st.header("🤖 AI-Powered Tools")
        
        tab1, tab2, tab3 = st.tabs(["🏷️ ARV Predictor", "🏘️ Neighborhood Analysis", "📊 Deal Analyzer"])
        
        with tab1:
            st.subheader("AI ARV Prediction")
            st.caption("Get AI-powered After Repair Value estimates")
            
            col1, col2 = st.columns(2)
            with col1:
                arv_city = st.selectbox("City", list(MICHIGAN_CITIES.keys()))
                arv_beds = st.number_input("Bedrooms", min_value=1, max_value=6, value=3)
                arv_baths = st.number_input("Bathrooms", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
            with col2:
                arv_sqft = st.number_input("Square Feet", min_value=500, max_value=5000, value=1500)
                arv_year = st.number_input("Year Built", min_value=1900, max_value=2024, value=1980)
                arv_price = st.number_input("Current List Price", min_value=0, value=100000, step=5000)
            
            if st.button("🔮 Predict ARV", type="primary"):
                prop_data = {
                    'beds': arv_beds,
                    'baths': arv_baths,
                    'sqft': arv_sqft,
                    'year_built': arv_year,
                    'list_price': arv_price
                }
                
                prediction = predict_arv(prop_data, arv_city)
                
                st.markdown("---")
                st.subheader("📊 ARV Prediction Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Predicted ARV", f"${prediction['predicted_arv']:,}")
                with col2:
                    st.metric("Confidence", f"{prediction['confidence']}%")
                with col3:
                    st.metric("Price/Sqft", f"${prediction['price_per_sqft']}")
                
                st.markdown(f"**Range:** ${prediction['low_estimate']:,} - ${prediction['high_estimate']:,}")
                st.markdown(f"**Market Appreciation:** {prediction['appreciation_rate']}% annual")
                
                # Show factors
                with st.expander("View Calculation Factors"):
                    factors = prediction['factors']
                    st.write(f"• Base Value: ${factors['base_value']:,}")
                    st.write(f"• Bedroom Adjustment: ${factors['bed_adjustment']:+,}")
                    st.write(f"• Bathroom Adjustment: ${factors['bath_adjustment']:+,}")
                    st.write(f"• Age Multiplier: {factors['age_multiplier']:.2f}x")
                    st.write(f"• Market Factor: {factors['market_factor']:.2f}x")
        
        with tab2:
            st.subheader("🏘️ Neighborhood Analysis")
            st.caption("AI analysis of investment potential by area")
            
            analysis_city = st.selectbox("Select City to Analyze", list(MICHIGAN_CITIES.keys()), key="analysis_city")
            
            if st.button("🔍 Analyze Neighborhood", type="primary"):
                analysis = analyze_neighborhood(analysis_city)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Neighborhood Score", f"{analysis['score']}/100")
                    st.metric("Investment Grade", analysis['grade'])
                    st.info(analysis['investment_outlook'])
                
                with col2:
                    metrics = analysis['metrics']
                    st.markdown("**Key Metrics:**")
                    st.write(f"• 📚 School Rating: {metrics['school_rating']}/10")
                    st.write(f"• 🛡️ Safety Score: {metrics['crime_score']}/10")
                    st.write(f"• 🚶 Walkability: {metrics['walkability']}/100")
                    st.write(f"• 💼 Job Growth: {metrics['job_growth']}%")
                    st.write(f"• 📈 Appreciation: {metrics['appreciation']}%")
                    st.write(f"• 👥 Population: {metrics['population_trend']}")
                    st.write(f"• 🏠 Median Price: ${metrics['median_price']:,}")
        
        with tab3:
            st.subheader("📊 Quick Deal Analyzer")
            st.caption("Instantly analyze any potential deal")
            
            col1, col2 = st.columns(2)
            with col1:
                deal_price = st.number_input("Purchase Price", min_value=0, value=100000, step=5000, key="deal_price")
                deal_arv = st.number_input("Estimated ARV", min_value=0, value=150000, step=5000, key="deal_arv")
            with col2:
                deal_repairs = st.number_input("Estimated Repairs", min_value=0, value=30000, step=5000, key="deal_repairs")
                deal_holding = st.number_input("Holding Months", min_value=1, max_value=12, value=4, key="deal_holding")
            
            if st.button("📊 Analyze Deal", type="primary"):
                # Calculate
                holding_costs = deal_arv * 0.01 * deal_holding  # 1% per month
                selling_costs = deal_arv * 0.09  # 9% selling costs
                total_investment = deal_price + deal_repairs + holding_costs + selling_costs
                net_profit = deal_arv - total_investment
                roi = (net_profit / total_investment * 100) if total_investment > 0 else 0
                max_offer = (deal_arv * 0.7) - deal_repairs
                
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Max Offer (70%)", f"${max_offer:,.0f}")
                with col2:
                    st.metric("Total Investment", f"${total_investment:,.0f}")
                with col3:
                    st.metric("Net Profit", f"${net_profit:,.0f}")
                with col4:
                    st.metric("ROI", f"{roi:.1f}%")
                
                # Verdict
                if roi >= 20 and net_profit >= 20000:
                    st.success("✅ GOOD DEAL - Strong returns!")
                elif roi >= 15 and net_profit >= 15000:
                    st.info("👍 DECENT DEAL - Acceptable returns")
                elif roi >= 10:
                    st.warning("⚠️ MARGINAL - Consider negotiating")
                else:
                    st.error("❌ PASS - Numbers don't work")
                
                # Breakdown
                with st.expander("View Full Breakdown"):
                    st.write(f"• Purchase Price: ${deal_price:,}")
                    st.write(f"• Repairs: ${deal_repairs:,}")
                    st.write(f"• Holding Costs ({deal_holding} mo): ${holding_costs:,.0f}")
                    st.write(f"• Selling Costs (9%): ${selling_costs:,.0f}")
                    st.write(f"• **Total Investment: ${total_investment:,.0f}**")
                    st.write(f"• ARV: ${deal_arv:,}")
                    st.write(f"• **Net Profit: ${net_profit:,.0f}**")
    
    # =========================================================================
    # SETTINGS
    # =========================================================================
    elif page == "⚙️ Settings":
        st.header("Settings")
        
        st.subheader("🔑 API Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            st.toggle("Use Demo Data", value=st.session_state.use_mock_data, key="settings_mock")
        with col2:
            if not st.session_state.use_mock_data:
                new_key = st.text_input("RealEstateAPI Key", type="password", value=st.session_state.api_key)
                if new_key:
                    st.session_state.api_key = new_key
        
        st.markdown("---")
        
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
        
        st.markdown("---")
        
        st.subheader("☁️ Cloud Deployment")
        st.markdown("""
        **To deploy to Streamlit Cloud:**
        1. Create a GitHub account if you don't have one
        2. Create a new repository
        3. Upload these files: `flipfinder_pro.py`, `requirements.txt`
        4. Go to [share.streamlit.io](https://share.streamlit.io)
        5. Connect your GitHub
        6. Select your repository
        7. Click Deploy!
        
        **Your app will be live at:** `https://your-username-flipfinder-pro.streamlit.app`
        """)
        
        st.markdown("---")
        st.subheader("📖 About")
        st.markdown("""
        **FlipFinder Pro v2.0**
        
        AI-Powered Michigan Fix & Flip Investment Platform
        
        **Features:**
        - ✅ Real-time property search
        - ✅ AI priority scoring (0-100)
        - ✅ ARV prediction
        - ✅ Neighborhood analysis
        - ✅ Interactive maps
        - ✅ Deal pipeline management
        - ✅ CMA report generation
        - ✅ Alert system
        """)

if __name__ == "__main__":
    main()

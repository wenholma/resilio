import streamlit as st
from logic import calculate_water_needs, calculate_power_needs, calculate_sanitation_needs
from pdf_gen import generate_calmera_pdf

st.set_page_config(
    page_title="Calmera | Household Resilience Audit",
    page_icon="🛡️",
    layout="centered"
)

# ---------------------------------------------------------
# SESSION STATE SETUP
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "otp" not in st.session_state:
    st.session_state.otp = None

if "email" not in st.session_state:
    st.session_state.email = None

if "paid" not in st.session_state:
    st.session_state.paid = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

# ---------------------------------------------------------
# LANDING PAGE (VISIBLE TO ALL - NO LOGIN REQUIRED)
# ---------------------------------------------------------
if not st.session_state.logged_in and not st.session_state.show_login:
    st.title("🛡️ Calmera — Household Resilience Audit")

    st.subheader(
        "A calm, practical way to understand how prepared your household is for short‑term disruptions."
    )

    st.markdown(
        """
    Most households want to feel prepared for disruptions like power outages, water interruptions, or severe weather — but it's hard to know where to start.

    Calmera gives you a **clear, personalised snapshot** of your household's readiness, based on public‑health and civil‑defence guidance.

    You'll complete a short audit (about **5 minutes**) and see your results instantly.  
    You can also choose to download a **personalised 6‑page PDF blueprint** to keep.
    """
    )

    st.markdown("---")

    st.markdown(
        """
    ### What you'll get

    - **Water plan** — how much you need, how to store it safely  
    - **Essential power plan** — phones, lighting, and critical devices  
    - **Sanitation setup** — simple, short‑term guidance  
    - **Communications checklist** — staying informed when networks are slow  
    - **30‑day maintenance routine** — a calm monthly check-in  
    - **Personalised next steps** — small improvements that make a big difference  

    All in a clear, printable 6‑page blueprint.
    """
    )

    st.markdown("---")

    st.markdown("### Ready to begin?")
    st.markdown("No account needed — just an email to save your results.")

    if st.button("✨ Start Your Free Audit", type="primary", use_container_width=True):
        st.session_state.show_login = True
        st.rerun()

    st.divider()
    st.caption(
        """
    This tool provides general household preparedness information only.
    It does not provide medical, engineering, or emergency‑response advice.
    Always follow official guidance during emergencies.
    """
    )
    st.stop()

# ---------------------------------------------------------
# LOGIN SYSTEM (EMAIL + OTP)
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.header("🔐 Login to Begin Your Audit")
    st.caption("Enter your email to receive a one‑time login code.")

    email = st.text_input("Email address", placeholder="you@example.com")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("📧 Send Login Code", use_container_width=True):
            if email:
                import random
                st.session_state.otp = str(random.randint(100000, 999999))
                st.session_state.email = email
                st.success(f"Your one-time login code is: **{st.session_state.otp}**")
                st.info("📬 In production, this would be emailed to you.")
            else:
                st.warning("Please enter your email address.")

    if st.session_state.otp:
        st.markdown("---")
        entered_code = st.text_input("Enter the 6-digit code", placeholder="123456", max_chars=6)

        if st.button("✓ Verify Code", use_container_width=True):
            if entered_code == st.session_state.otp:
                st.session_state.logged_in = True
                st.session_state.show_login = False
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("Incorrect code. Please try again.")

    # Back button to landing page
    if st.button("← Back to Home"):
        st.session_state.show_login = False
        st.rerun()

    st.stop()

# ---------------------------------------------------------
# INTRO SECTION (POST-LOGIN)
# ---------------------------------------------------------
st.title("🛡️ Calmera — Household Resilience Audit")

st.markdown(
    """
Welcome! Use the sidebar to enter your household details.  
Your results will update automatically as you make changes.
"""
)

st.divider()

# ---------------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------------
with st.sidebar:
    st.header("🏠 Household Profile")
    st.caption("These details help tailor the plan to your household.")

    people = st.number_input(
        "People in household",
        min_value=1,
        value=2,
        help="Count everyone who will rely on your supplies."
    )

    temp_unit = st.radio(
        "Temperature unit",
        ["°C", "°F"],
        horizontal=True,
        help="Used to estimate water needs in warmer conditions."
    )

    temperature = st.number_input(
        f"Typical warm‑day temperature ({temp_unit})",
        value=28.0,
        help="An estimate of a warm daytime temperature where you live. If unsure, use today's warm average."
    )

    days = st.slider(
        "How many days should this plan cover?",
        3,
        30,
        7,
        help="Common choices: 3 days (short outages), 7 days (major disruption), 14 days (extended)."
    )

    st.divider()
    st.header("🐾 Life & Comfort")
    st.caption("These choices affect water and hygiene needs.")

    cats = st.number_input(
        "Cats in your care",
        0, 10, 0,
        help="Include pets you would keep supplied at home."
    )
    dogs = st.number_input(
        "Dogs in your care",
        0, 10, 0,
        help="Include pets you would keep supplied at home."
    )

    hygiene_plus = st.checkbox(
        "Include water for basic hygiene and dishwashing",
        value=True,
        help="Adds water for handwashing, minimal bathing, and cleaning dishes."
    )

    st.divider()
    st.header("🔌 Essential Power")
    st.caption("This estimates power for essential needs only — not normal household use.")

    fridge = st.toggle(
        "Backup the fridge?",
        value=True,
        help="This estimates the power needed to keep your fridge cold during an outage. It assumes short, infrequent door openings and typical household fridge efficiency."
    )

    phones = st.number_input("Phones (daily charging)", 0, 10, 2)
    laptops = st.number_input("Laptops (essential use)", 0, 10, 1)

    led_lights = st.number_input(
        "LED lights (battery-powered)",
        0, 20, 3,
        help="Enter the number of LED lights you plan to use during an outage."
    )

    hours_of_light = st.slider("Hours of lighting each night", 1, 12, 5)

    st.divider()
    st.header("🚽 Sanitation & Hygiene")
    st.caption("Planning ahead reduces illness risk if services are disrupted.")

    has_toilet_plan = st.checkbox("I have a backup toilet plan.", value=False)
    has_cover_material = st.checkbox("I have cover material.", value=False)

    st.divider()
    st.header("📡 Communications")
    st.caption("Reliable information helps you make good decisions during disruptions.")

    has_radio = st.checkbox("Battery-powered or wind-up radio.", value=False)
    has_contacts = st.checkbox("Printed emergency contacts.", value=False)
    has_map = st.checkbox("Local paper map.", value=False)

# ---------------------------------------------------------
# CLIMATE LOGIC
# ---------------------------------------------------------
def classify_climate(temp_value, unit):
    if unit == "°F":
        temp_c = (temp_value - 32) * 5.0 / 9.0
    else:
        temp_c = temp_value

    if temp_c >= 35:
        return "Extreme Heat"
    elif temp_c >= 28:
        return "High Heat"
    else:
        return "Standard"

climate_class = classify_climate(temperature, temp_unit)
climate_for_engine = "Arid/Hot" if climate_class in ["High Heat", "Extreme Heat"] else "Temperate"

# ---------------------------------------------------------
# CORE CALCULATIONS
# ---------------------------------------------------------
water_results = calculate_water_needs(
    people=people,
    days=days,
    climate=climate_for_engine,
    cats=cats,
    dogs=dogs,
    hygiene_plus=hygiene_plus
)

power_results = calculate_power_needs(
    fridge=fridge,
    phones=phones,
    laptops=laptops,
    led_lights=led_lights,
    hours_of_light=hours_of_light
)

sanitation_results = calculate_sanitation_needs(people, days)

# ---------------------------------------------------------
# CALMERA SCORE
# ---------------------------------------------------------
water_score = min(1.0, water_results["total_liters"] / (people * days * 3.0))
power_score = 1.0 if power_results["recommended_battery_size"] >= 500 else 0.5
sanitation_score = 1.0 if (has_toilet_plan and has_cover_material) else 0.3
comms_score = sum([has_radio, has_contacts, has_map]) / 3.0

overall_score = (water_score + power_score + sanitation_score + comms_score) / 4.0

def score_to_grade(score):
    if score >= 0.85:
        return "A"
    elif score >= 0.7:
        return "B"
    elif score >= 0.55:
        return "C"
    elif score >= 0.4:
        return "D"
    else:
        return "E"

grade = score_to_grade(overall_score)

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
st.header("📊 Your Resilience Snapshot")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Water", f"{water_results['total_liters']} L")
with col2:
    st.metric("Battery Capacity", f"{power_results['recommended_battery_size']} Wh")
with col3:
    st.metric("Calmera Score", grade)

st.caption(
    "This score is a planning snapshot, not a guarantee of safety. "
    "It highlights where small improvements could make a big difference."
)

# ---------------------------------------------------------
# DETAILED BREAKDOWN
# ---------------------------------------------------------
st.header("🔍 Detailed Breakdown")

# Water
st.subheader("💧 Water details")
st.markdown(
    "**What this means:** This is the minimum water needed to keep your household safe and functional "
    "for the selected number of days."
)
st.markdown(
    f"""
- **Daily requirement:** {water_results['daily_requirement']} L  
- **Total water needed:** {water_results['total_liters']} L  
- **20L containers needed:** {water_results['containers_needed_20L']:.1f}  
- **Total weight:** {water_results['weight_kg']} kg  
"""
)
st.caption("This does not include water for gardens, washing clothes, or firefighting.")

# Power
st.subheader("🔌 Power details")
st.markdown(
    "**What this means:** This is the minimum power needed to keep your household connected, "
    "informed, and safely lit during an outage."
)
st.markdown(
    f"""
- **Daily energy required:** {power_results['daily_wh_required']} Wh  
- **Recommended battery size:** {power_results['recommended_battery_size']} Wh  
- **Estimated solar panel output:** {power_results['solar_panel_est']} Wh/day  
"""
)
st.caption("Solar output varies by season, weather, and panel size.")

# Sanitation
st.subheader("🚽 Sanitation & Hygiene")
st.markdown(
    "**What this means:** These supplies support a temporary household sanitation setup "
    "if normal toilets are unavailable."
)
st.markdown(
    f"""
- **Buckets needed:** {sanitation_results['buckets_needed']}  
- **Cover material:** {sanitation_results['cover_material_kg']} kg  
- **Sanitizer:** {sanitation_results['sanitizer_liters']} L  
"""
)

# Communications
st.subheader("📡 Communications")
st.markdown(
    "**What this means:** Radios and printed information are often the most reliable way "
    "to receive updates when networks are overloaded."
)
st.markdown(
    f"""
- **Radio available:** {"Yes" if has_radio else "No"}  
- **Printed contacts:** {"Yes" if has_contacts else "No"}  
- **Local map:** {"Yes" if has_map else "No"}  
"""
)

# ---------------------------------------------------------
# PAYWALL — Unlock PDF Blueprint (6 pages)
# ---------------------------------------------------------

st.markdown("---")
st.subheader("🔓 Unlock Your Personalised PDF Blueprint")

st.markdown(
    """
### **NZD 9.99 — one‑time, lifetime access**

Your personalised **6‑page Household Resilience Blueprint** includes:

- **Clear explanations** of how every number is calculated  
- **What each number means** for your household  
- **Actionable suggestions** based on your specific answers  
- Water, power, sanitation, and communications targets  
- A simple emergency sanitation setup guide  
- A 30‑day maintenance routine  
- A tear‑out shopping list with specific products and stores  
- Practical tips based on public‑health and civil‑defence guidance  

This is a **one‑off payment**.  
**No subscription. No recurring fees.**
"""
)

# Stripe payment button (replace YOUR_NEW_LINK with your actual Stripe payment link)
st.markdown(
    """
    <a href="https://buy.stripe.com/YOUR_NEW_LINK" target="_blank">
        <button style="
            background-color:#1a73e8;
            color:white;
            padding:12px 22px;
            border:none;
            border-radius:6px;
            font-size:16px;
            cursor:pointer;
            margin-top:10px;
        ">
            Pay NZD 9.99
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

st.markdown(" ")

# Confirmation button
if st.button("I have completed payment"):
    st.session_state.paid = True
    st.success("Payment confirmed. Your personalised PDF is now ready to download.")

if st.session_state.paid:
    # ---------------------------------------------------------
    # PREPARE DATA FOR 6-PAGE PDF (enhanced)
    # ---------------------------------------------------------
    next_steps = []

    if not has_radio:
        next_steps.append("Add a battery or wind-up radio for reliable updates.")
    elif not has_contacts:
        next_steps.append("Print a list of emergency contacts and keep it accessible.")
    elif not has_map:
        next_steps.append("Keep a local paper map in case digital navigation fails.")
    elif water_results["total_liters"] < people * days * 3:
        next_steps.append("Increase stored water to meet minimum daily needs.")
    elif power_results["recommended_battery_size"] < 500:
        next_steps.append("Consider a small battery or power bank for essential devices.")

    general_tips = [
        "Review and refresh your household emergency supplies.",
        "Label water containers with fill dates and store away from sunlight.",
        "Test your battery-powered lights and charge devices monthly.",
        "Keep important documents in a waterproof, grab-and-go folder."
    ]

    for tip in general_tips:
        if len(next_steps) < 3:
            next_steps.append(tip)

    # Additional suggestions for PDF
    water_suggestions = []
    if water_results["total_liters"] < people * days * 3:
        water_suggestions.append("Your water storage is below the recommended minimum. Aim to store at least 3 litres per person per day.")
    if water_results["weight_kg"] > 100:
        water_suggestions.append("Water is heavy. Store containers on the floor, not on high shelves, to avoid injury.")
    if climate_class in ["High Heat", "Extreme Heat"]:
        water_suggestions.append("In hot climates, water needs increase. Consider adding 1-2 extra litres per person per day.")

    power_suggestions = []
    if power_results["recommended_battery_size"] < 300:
        power_suggestions.append("A small power bank (200-300 Wh) can keep phones and lights running for a few days.")
    elif power_results["recommended_battery_size"] > 2000:
        power_suggestions.append("Consider a solar panel to recharge your battery during longer outages.")
    if not fridge:
        power_suggestions.append("Without fridge backup, plan to consume perishable foods first or use a cooler with ice.")

    pdf_data = {
        "people": people,
        "days": days,
        "temperature": temperature,
        "unit": temp_unit,
        "cats": cats,
        "dogs": dogs,
        "hygiene_plus": hygiene_plus,
        "climate_class": climate_class,
        "has_toilet_plan": has_toilet_plan,
        "has_cover_material": has_cover_material,

        "water_total": water_results["total_liters"],
        "water_daily": water_results["daily_requirement"],
        "water_containers": round(water_results["containers_needed_20L"], 1),
        "water_weight": water_results["weight_kg"],
        "water_suggestions": water_suggestions,

        "power_daily_wh": power_results["daily_wh_required"],
        "power_battery_wh": power_results["recommended_battery_size"],
        "power_solar_wh": power_results["solar_panel_est"],
        "power_suggestions": power_suggestions,

        "sanitation_buckets": sanitation_results["buckets_needed"],
        "sanitation_cover_kg": sanitation_results["cover_material_kg"],
        "sanitation_sanitizer_l": sanitation_results["sanitizer_liters"],

        "has_radio": has_radio,
        "has_contacts": has_contacts,
        "has_map": has_map,

        "grade": grade,
        "next_steps": next_steps[:3],

        "water_breakdown": {
            "drinking": people * days * 2.0,
            "food_prep": people * days * 1.0,
            "hygiene": (people * days * 2.0) if hygiene_plus else 0,
            "pets": (cats * 0.2 + dogs * 1.0) * days,
            "climate_factor": 1.2 if climate_class in ["High Heat", "Extreme Heat"] else 1.0
        },
        "power_breakdown": {
            "fridge_wh": 1200 if fridge else 0,
            "phone_wh": phones * 15,
            "laptop_wh": laptops * 60,
            "light_wh": led_lights * 5 * hours_of_light
        }
    }

    pdf_bytes = generate_calmera_pdf(pdf_data)

    st.download_button(
        label="📄 Download My Calmera Blueprint (PDF)",
        data=pdf_bytes,
        file_name="Calmera_Blueprint.pdf",
        mime="application/pdf"
    )

# ---------------------------------------------------------
# DISCLAIMER
# ---------------------------------------------------------
st.divider()
st.caption(
    """
    This tool provides general household preparedness information only.
    It does not provide medical, engineering, or emergency‑response advice.
    Always follow official guidance during emergencies.
    """
)

# Legal expanders (Terms & Privacy)
with st.expander("📜 Terms of Service"):
    st.markdown("""
    **Terms of Service**  
    Calmera provides general household preparedness guidance based on publicly available civil-defence and public-health recommendations. It is intended as a planning aid only.  
    Calmera does not predict, prevent, or guarantee protection from any emergency, disaster, or disruption. Results are estimates based on user-provided inputs.  
    Calmera is not a substitute for official emergency management guidance. Always follow official instructions.  
    Use of this tool is at your own risk.
    """)

with st.expander("🔒 Privacy Policy"):
    st.markdown("""
    **Privacy Policy**  
    Calmera collects your email address solely to send you a one‑time login code and to deliver your PDF blueprint. We do not share, sell, or rent your email address.  
    We retain email addresses for 90 days after your last login. Payments are processed by Stripe; we do not store credit card details.
    """)
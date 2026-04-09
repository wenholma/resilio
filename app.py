import streamlit as st
from logic import calculate_water_needs, calculate_power_needs, calculate_sanitation_needs
from pdf_gen import generate_resilience_pdf

st.set_page_config(
    page_title="Resilio | Household Resilience Audit",
    page_icon="🛡️",
    layout="centered"
)

# ---------------------------------------------------------
# LOGIN SYSTEM (EMAIL + OTP)
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "otp" not in st.session_state:
    st.session_state.otp = None

if "email" not in st.session_state:
    st.session_state.email = None

if "paid" not in st.session_state:
    st.session_state.paid = False

if not st.session_state.logged_in:
    st.header("🔐 Login to Begin Your Audit")

    email = st.text_input("Enter your email address")

    if st.button("Send Login Code"):
        import random
        st.session_state.otp = str(random.randint(100000, 999999))
        st.session_state.email = email
        st.success(f"Your one-time login code is: {st.session_state.otp}")
        st.info("In production, this would be emailed to you.")

    if st.session_state.otp:
        entered_code = st.text_input("Enter the 6-digit code")

        if st.button("Verify Code"):
            if entered_code == st.session_state.otp:
                st.session_state.logged_in = True
                st.success("Login successful!")
            else:
                st.error("Incorrect code. Please try again.")

    if not st.session_state.logged_in:
        st.stop()

# ---------------------------------------------------------
# LANDING PAGE CONTENT
# ---------------------------------------------------------
st.title("🛡️ Resilio — Household Resilience Audit")

st.subheader(
    "A calm, practical way to understand how prepared your household is for short‑term disruptions."
)

st.markdown(
    """
Most households want to feel prepared for disruptions like power outages, water interruptions, or severe weather — but it's hard to know where to start.

Resilio gives you a **clear, personalised snapshot** of your household's readiness, based on public‑health and civil‑defence guidance.

You'll complete a short audit (about **5 minutes**) and see your results instantly.  
You can also choose to download a **personalised 3‑page PDF blueprint** to keep.
"""
)

st.markdown(
    """
### What you'll get

- **Water plan** — how much you need, how to store it safely  
- **Essential power plan** — phones, lighting, and critical devices  
- **Sanitation setup** — simple, short‑term guidance  
- **Communications checklist** — staying informed when networks are slow  
- **30‑day maintenance routine** — a calm monthly check-in  
- **Personalised next steps** — small improvements that make a big difference  

All in a clear, printable 3‑page blueprint.
"""
)

st.markdown("### Ready to begin?")
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
        help="This estimates the power needed to keep your fridge cold during an outage. It assumes short, infrequent door openings and typical household fridge efficiency. Optional — include only if keeping food cold is important for your household."
    )

    phones = st.number_input("Phones (daily charging)", 0, 10, 2)
    laptops = st.number_input("Laptops (essential use)", 0, 10, 1)

    led_lights = st.number_input(
        "LED lights (battery-powered)",
        0, 20, 3,
        help="Enter the number of LED lights you plan to use during an outage. This helps estimate how much battery power you'll need for safe lighting at night."
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
# RESILIO SCORE
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
    st.metric("Resilio Score", grade)

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
# PAYWALL
# ---------------------------------------------------------
st.divider()
st.header("🔓 Unlock Your Personalised PDF Blueprint (NZD 9.99)")

st.markdown(
    """
Download a **3‑page Household Resilience Blueprint** tailored to your inputs.

It includes:
- Exact water and power targets
- Storage and weight‑distribution guidance
- A simple sanitation plan
- A communications checklist
- A 30‑day maintenance routine
- Personalised next steps

Complete it once. Save it. Revisit when your household changes.
"""
)
st.caption("No subscription. One‑time download.")

STRIPE_LINK = "https://buy.stripe.com/9B64gA6Gm6FicsGbQ80sU01"

st.link_button("Pay NZD 9.99 via Stripe", STRIPE_LINK)

st.info("After completing payment, click below:")

if st.button("I have completed payment"):
    st.session_state.paid = True
    st.success("Payment confirmed!")

if st.session_state.paid:
    # ---------------------------------------------------------
    # PREPARE DATA FOR 3-PAGE PDF (FIXED DUPLICATE LOGIC)
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

    # Fill remaining slots with general preparedness tips (no duplicates)
    general_tips = [
        "Review and refresh your household emergency supplies.",
        "Label water containers with fill dates and store away from sunlight.",
        "Test your battery-powered lights and charge devices monthly.",
        "Keep important documents in a waterproof, grab-and-go folder."
    ]

    for tip in general_tips:
        if len(next_steps) < 3:
            next_steps.append(tip)

    pdf_data = {
        "people": people,
        "days": days,
        "temperature": temperature,
        "unit": temp_unit,
        "cats": cats,
        "dogs": dogs,

        "water_total": water_results["total_liters"],
        "power_daily": power_results["daily_wh_required"],
        "buckets": sanitation_results["buckets_needed"],

        "radio": "Yes" if has_radio else "No",
        "contacts": "Yes" if has_contacts else "No",
        "map": "Yes" if has_map else "No",

        "grade": grade,
        "next_steps": next_steps[:3],

        "water": {
            "daily": water_results["daily_requirement"],
            "total": water_results["total_liters"],
            "containers": round(water_results["containers_needed_20L"], 1),
            "weight": water_results["weight_kg"]
        },

        "power": {
            "daily_wh": power_results["daily_wh_required"],
            "battery_wh": power_results["recommended_battery_size"],
            "solar_wh": power_results["solar_panel_est"]
        },

        "sanitation": {
            "buckets": sanitation_results["buckets_needed"],
            "cover_kg": sanitation_results["cover_material_kg"],
            "sanitizer_l": sanitation_results["sanitizer_liters"]
        },

        "comms": {
            "radio": "Yes" if has_radio else "No",
            "contacts": "Yes" if has_contacts else "No",
            "map": "Yes" if has_map else "No"
        }
    }

    pdf_bytes = generate_resilience_pdf(pdf_data)

    st.download_button(
        label="📄 Download My Resilience Blueprint (PDF)",
        data=pdf_bytes,
        file_name="Resilio_Blueprint.pdf",
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
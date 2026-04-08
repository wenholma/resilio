import streamlit as st
from logic import calculate_water_needs, calculate_power_needs, calculate_sanitation_needs
from pdf_gen import generate_resilience_pdf

st.set_page_config(
    page_title="Resilio | Home Resilience Audit",
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

    # STOP ONLY IF NOT LOGGED IN
    if not st.session_state.logged_in:
    	st.stop()

# ---------------------------------------------------------
# INTRO SECTION
# ---------------------------------------------------------
st.title("🛡️ Resilio — Home Resilience Audit")
st.subheader("A once-off, evidence-based blueprint for your household’s emergency readiness.")

st.markdown(
    """
Most households think they’re prepared. Very few actually are.

This audit gives you a **science-based snapshot** of your home’s ability to cope during:

- Power outages  
- Water disruptions  
- Storms and earthquakes  
- Civil emergencies  

**Free on-screen:**  
- Water readiness  
- Power readiness  
- Sanitation & communications check  
- Your overall **Resilio Score (A–F)**  

**Paid upgrade (NZD 9.99):**  
A personalised **5‑page PDF Blueprint** with:

- Exact water & power requirements  
- Storage and weight‑distribution guidance  
- Two‑bucket sanitation protocol  
- Communications plan  
- Tailored shopping list  
- Printable emergency card  
- 30‑day maintenance schedule  

This is a **once-off household audit** — complete it once, save your blueprint, and you’re done.
"""
)

st.divider()

# ---------------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------------
with st.sidebar:
    st.header("🏠 Household Profile")

    people = st.number_input(
        "People in Household",
        min_value=1,
        value=2
    )

    temp_unit = st.radio(
        "Temperature Unit",
        ["°C", "°F"],
        horizontal=True
    )

    temperature = st.number_input(
        f"Average Summer Temperature ({temp_unit})",
        value=28.0
    )

    days = st.slider(
        "Resilience Target (Days)",
        3, 30, 14
    )

    st.divider()
    st.header("🐾 Life & Comfort")

    cats = st.number_input("Number of Cats", 0, 10, 0)
    dogs = st.number_input("Number of Dogs", 0, 10, 0)

    hygiene_plus = st.checkbox(
        "Include 'Dignity' Water (Hygiene & Dishes)",
        value=True
    )

    st.divider()
    st.header("🔌 Critical Power")

    fridge = st.toggle("Backup the Fridge?", value=True)
    phones = st.number_input("Phones to Charge", 0, 10, 2)
    laptops = st.number_input("Laptops to Run", 0, 10, 1)
    led_lights = st.number_input("LED Lights to Use", 0, 20, 3)
    hours_of_light = st.slider("Hours of Light per Day", 1, 12, 5)

    st.divider()
    st.header("🚽 Sanitation Check")

    has_toilet_plan = st.checkbox("I have a backup toilet plan.", value=False)
    has_cover_material = st.checkbox("I have cover material.", value=False)

    st.divider()
    st.header("📡 Communications Check")

    has_radio = st.checkbox("Battery-powered or wind-up radio", value=False)
    has_contacts = st.checkbox("Printed emergency contacts", value=False)
    has_map = st.checkbox("Local paper map", value=False)

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

# ---------------------------------------------------------
# DETAILED BREAKDOWN
# ---------------------------------------------------------
st.header("🔍 Detailed Breakdown")

st.subheader("💧 Water Details")
st.write(water_results)

st.subheader("🔌 Power Details")
st.write(power_results)

st.subheader("🚽 Sanitation Overview")
st.write(sanitation_results)

st.subheader("📡 Communications Overview")
st.write({
    "radio": has_radio,
    "contacts": has_contacts,
    "map": has_map
})

# ---------------------------------------------------------
# PAYWALL
# ---------------------------------------------------------
st.divider()
st.header("🔓 Unlock Your Full PDF Blueprint (NZD 9.99)")

STRIPE_LINK = "https://buy.stripe.com/your_resilio_link_here"

st.link_button("Pay NZD 9.99 via Stripe", STRIPE_LINK)

st.info("After completing payment, click below:")

if st.button("I have completed payment"):
    st.session_state.paid = True
    st.success("Payment confirmed!")

if st.session_state.paid:
    user_profile = {
        "email": st.session_state.email,
        "days": days
    }

    pdf_bytes = generate_resilience_pdf(
        water_results,
        power_results,
        sanitation_results,
        {
            "radio": has_radio,
            "contacts": has_contacts,
            "map": has_map
        },
        user_profile
    )

    st.download_button(
        label="📄 Download My Resilience Blueprint (PDF)",
        data=pdf_bytes,
        file_name="Resilio_Blueprint.pdf",
        mime="application/pdf"
    )

# ---------------------------------------------------------
# DISCLAIMERS
# ---------------------------------------------------------
st.divider()
st.caption(
    """
This tool provides general household preparedness guidance only.
It is not medical, engineering, or emergency-response advice.
"""
)

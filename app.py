import streamlit as st
from logic import calculate_water_needs, calculate_power_needs, calculate_sanitation_needs
from pdf_gen import generate_calmera_pdf
import math

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
# LANDING PAGE
# ---------------------------------------------------------
if not st.session_state.logged_in and not st.session_state.show_login:
    st.title("🛡️ Calmera — Household Resilience Audit")
    st.subheader("A calm, practical way to understand how prepared your household is for short‑term disruptions.")
    st.markdown("""
    Most households want to feel prepared for disruptions like power outages, water interruptions, or severe weather — but it's hard to know where to start.

    Calmera gives you a **clear, personalised snapshot** of your household's readiness, based on public‑health and civil‑defence guidance.

    You'll complete a short audit (about **5 minutes**) and see your results instantly.  
    You can also choose to download a **personalised 7‑page PDF blueprint** to keep.
    """)
    st.markdown("---")
    st.markdown("""
    ### What you'll get
    - **Water plan** — how much you need, how to store it safely  
    - **Essential power plan** — phones, lighting, and critical devices  
    - **Sanitation setup** — simple, short‑term guidance  
    - **Communications checklist** — staying informed when networks are slow  
    - **30‑day maintenance routine** — a calm monthly check-in  
    - **Personalised next steps** — small improvements that make a big difference  
    - **Full transparency** – exactly how every number is calculated  

    All in a clear, printable 7‑page blueprint.
    """)
    st.markdown("---")
    st.markdown("### Ready to begin?")
    st.markdown("No account needed — just an email to save your results.")
    if st.button("✨ Start Your Free Audit", type="primary", use_container_width=True):
        st.session_state.show_login = True
        st.rerun()
    st.divider()
    st.caption("This tool provides general household preparedness information only. It does not provide medical, engineering, or emergency‑response advice. Always follow official guidance during emergencies.")
    st.stop()

# ---------------------------------------------------------
# LOGIN SYSTEM
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
    if st.button("← Back to Home"):
        st.session_state.show_login = False
        st.rerun()
    st.stop()

# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------
st.title("🛡️ Calmera — Household Resilience Audit")
st.markdown("Welcome! Use the sidebar to enter your household details. Your results will update automatically as you make changes.")
st.divider()

# SIDEBAR INPUTS (all start at zero)
with st.sidebar:
    st.header("🏠 Household Profile")
    people = st.number_input("People in household", min_value=0, value=0, help="Count everyone who will rely on your supplies.")
    temp_unit = st.radio("Temperature unit", ["°C", "°F"], horizontal=True)
    # Integer temperature only
    temperature = st.number_input(f"Typical warm‑day temperature ({temp_unit})", value=0, step=1, help="An estimate of a warm daytime temperature where you live. Use whole number.")
    days = st.slider("How many days should this plan cover?", 3, 30, 3)
    st.divider()
    st.header("🐾 Life & Comfort")
    cats = st.number_input("Cats in your care", 0, 10, 0)
    dogs = st.number_input("Dogs in your care", 0, 10, 0)
    hygiene_plus = st.checkbox("Include water for basic hygiene and dishwashing", value=False)
    st.divider()
    st.header("🔌 Essential Power")
    fridge = st.toggle("Backup the fridge?", value=False)
    phones = st.number_input("Phones (daily charging)", 0, 10, 0)
    laptops = st.number_input("Laptops (essential use)", 0, 10, 0)
    led_lights = st.number_input("LED lights (battery-powered)", 0, 20, 0)
    hours_of_light = st.slider("Hours of lighting each night", 1, 12, 1)
    st.divider()
    st.header("🚽 Sanitation & Hygiene")
    has_toilet_plan = st.checkbox("I have a backup toilet plan.", value=False)
    has_cover_material = st.checkbox("I have cover material.", value=False)
    st.divider()
    st.header("📡 Communications")
    has_radio = st.checkbox("Battery-powered or wind-up radio.", value=False)
    has_contacts = st.checkbox("Printed emergency contacts.", value=False)
    has_map = st.checkbox("Local paper map.", value=False)
    st.divider()
    st.header("💰 Quick Start under $100")
    st.markdown("""
    - **2 x 20L water containers** – $50–60  
    - **2 x 20,000mAh power banks** – $60–80  
    - **1 x bucket + bag of kitty litter** – $20  
    - **Battery‑powered radio** – $30  
    **Total ≈ $100–120** – covers water, basic power, sanitation, comms.
    """)

# Climate classification
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

if people > 0:
    climate_class = classify_climate(temperature, temp_unit)
    climate_for_engine = "Arid/Hot" if climate_class in ["High Heat", "Extreme Heat"] else "Temperate"

    water_results = calculate_water_needs(
        people=people, days=days, climate=climate_for_engine,
        cats=cats, dogs=dogs, hygiene_plus=hygiene_plus
    )
    power_results = calculate_power_needs(
        fridge=fridge, phones=phones, laptops=laptops,
        led_lights=led_lights, hours_of_light=hours_of_light
    )
    sanitation_results = calculate_sanitation_needs(people, days)

    # Fix sanitation buckets
    sanitation_results['buckets_needed'] = max(1, (people + 1) // 2)
    sanitation_results['cover_material_kg'] = round(people * days * 0.1, 1)
    sanitation_results['sanitizer_liters'] = round(people * days * 0.02, 1)

    # Score calculation
    water_score = min(1.0, water_results["total_liters"] / (people * days * 3.0))
    power_score = 1.0 if power_results["recommended_battery_size"] >= 500 else 0.5
    sanitation_score = 1.0 if (has_toilet_plan and has_cover_material) else 0.3
    comms_score = sum([has_radio, has_contacts, has_map]) / 3.0
    overall_score = (water_score + power_score + sanitation_score + comms_score) / 4.0

    def score_to_grade(score):
        if score >= 0.85: return "A"
        elif score >= 0.7: return "B"
        elif score >= 0.55: return "C"
        elif score >= 0.4: return "D"
        else: return "E"
    grade = score_to_grade(overall_score)

    # Dashboard
    st.header("📊 Your Resilience Snapshot")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Water", f"{water_results['total_liters']:.1f} L", help=f"Minimum water needed for {days} days")
    with col2:
        st.metric("Battery Capacity", f"{power_results['recommended_battery_size']:.0f} Wh", help="Watt-hours (Wh) measure energy. A 500Wh battery can run a 50W light for 10 hours.")
    with col3:
        st.metric("Calmera Score", grade, help="A=Excellent, B=Good, C=Needs work, D/E=Significant gaps")
    st.caption("This score is a planning snapshot, not a guarantee of safety. It highlights where small improvements could make a big difference.")

    # Detailed breakdown (shortened – no calculations)
    st.header("🔍 Detailed Breakdown")
    st.subheader("💧 Water details")
    containers_needed = math.ceil(water_results['total_liters'] / 20)
    st.markdown(f"""
    - **Daily requirement:** {water_results['daily_requirement']:.1f} L  
    - **Total water needed:** {water_results['total_liters']:.1f} L  
    - **20L containers needed:** {containers_needed}  
    - **Total weight:** {water_results['weight_kg']:.1f} kg  
    """)
    st.caption("This does not include water for gardens, washing clothes, or firefighting.")

    st.subheader("🔌 Power details")
    st.markdown(f"""
    - **Daily energy required:** {power_results['daily_wh_required']:.0f} Wh  
    - **Recommended battery size:** {power_results['recommended_battery_size']:.0f} Wh  
    - **Estimated solar panel output:** {power_results['solar_panel_est']:.0f} Wh/day  
    """)
    st.caption("Solar output varies by season, weather, and panel size.")

    st.subheader("🚽 Sanitation & Hygiene")
    st.markdown(f"""
    - **Buckets needed:** {sanitation_results['buckets_needed']}  
    - **Cover material:** {sanitation_results['cover_material_kg']:.1f} kg  
    - **Sanitizer:** {sanitation_results['sanitizer_liters']:.1f} L  
    """)

    st.subheader("📡 Communications")
    st.markdown(f"""
    - **Radio available:** {"Yes" if has_radio else "No"}  
    - **Printed contacts:** {"Yes" if has_contacts else "No"}  
    - **Local map:** {"Yes" if has_map else "No"}  
    """)

    # Paywall
    st.markdown("---")
    st.subheader("🔓 Unlock Your Personalised PDF Blueprint")
    st.markdown("""
    ### **NZD 9.99 — one‑time, lifetime access**

    Your personalised **7‑page Household Resilience Blueprint** includes:

    - **Clear explanations** of how every number is calculated.  
    - **What each number means** for your household.  
    - **Actionable suggestions** based on your specific answers.  
    - Water, power, sanitation, and communications targets.  
    - A simple emergency sanitation setup guide.  
    - A 30‑day maintenance routine.  
    - A tear‑out shopping list with specific products and stores.  
    - Practical tips based on public‑health and civil‑defence guidance.  

    This is a **one‑off payment**.  
    **No subscription. No recurring fees.**
    """)
    # Stripe payment button (replace YOUR_NEW_LINK with your actual Stripe payment link)
    st.markdown("""
    <a href="https://buy.stripe.com/YOUR_NEW_LINK" target="_blank">
        <button style="background-color:#1a73e8;color:white;padding:12px 22px;border:none;border-radius:6px;font-size:16px;cursor:pointer;">
            Pay NZD 9.99
        </button>
    </a>
    """, unsafe_allow_html=True)
    st.markdown(" ")
    if st.button("I have completed payment"):
        st.session_state.paid = True
        st.success("Payment confirmed. Your personalised PDF is now ready to download.")

    if st.session_state.paid:
        # Prepare PDF data
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
            "Test your battery-powered lights and charge devices monthly."
        ]
        for tip in general_tips:
            if len(next_steps) < 3:
                next_steps.append(tip)

        pdf_data = {
            "people": people, "days": days, "temperature": temperature, "unit": temp_unit,
            "cats": cats, "dogs": dogs, "hygiene_plus": hygiene_plus, "climate_class": climate_class,
            "has_toilet_plan": has_toilet_plan, "has_cover_material": has_cover_material,
            "water_total": water_results["total_liters"], "water_daily": water_results["daily_requirement"],
            "water_containers": containers_needed, "water_weight": water_results["weight_kg"],
            "power_daily_wh": power_results["daily_wh_required"],
            "power_battery_wh": power_results["recommended_battery_size"],
            "power_solar_wh": power_results["solar_panel_est"],
            "sanitation_buckets": sanitation_results["buckets_needed"],
            "sanitation_cover_kg": sanitation_results["cover_material_kg"],
            "sanitation_sanitizer_l": sanitation_results["sanitizer_liters"],
            "has_radio": has_radio, "has_contacts": has_contacts, "has_map": has_map,
            "grade": grade, "next_steps": next_steps[:3],
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
        st.download_button("📄 Download My Calmera Blueprint (PDF)", data=pdf_bytes, file_name="Calmera_Blueprint.pdf", mime="application/pdf")
else:
    st.info("👈 Please enter your household details in the sidebar to see your resilience plan.")

# ---------------------------------------------------------
# DISCLAIMER & LEGAL
# ---------------------------------------------------------
st.divider()
st.caption("This tool provides general household preparedness information only. It does not provide medical, engineering, or emergency‑response advice. Always follow official guidance during emergencies.")

with st.expander("📜 Terms of Service"):
    st.markdown("""
    **Terms of Service**  
    Last updated: April 2026  

    **1. Acceptance of Terms**  
    By using Calmera ("the Service"), you agree to these Terms of Service. If you do not agree, do not use the Service.  

    **2. Description of Service**  
    Calmera provides general household preparedness guidance based on publicly available civil-defence and public-health recommendations. It is intended as a planning aid only.  

    **3. No Guarantee of Safety**  
    Calmera does not predict, prevent, or guarantee protection from any emergency, disaster, or disruption. Results are estimates based on user-provided inputs. Actual household needs may vary.  

    **4. Not Official Advice**  
    Calmera is not a substitute for official emergency management guidance. During any emergency, always follow instructions from civil defence, emergency services, and local authorities.  

    **5. Limitation of Liability**  
    Calmera makes no warranties, express or implied, about the accuracy, completeness, or fitness for purpose of the information provided. Use of this tool is at your own risk.  

    **6. Changes to Terms**  
    We may update these Terms from time to time. Continued use constitutes acceptance of the updated Terms.  

    **7. Contact**  
    For questions, contact [your email address].  
    """)

with st.expander("🔒 Privacy Policy"):
    st.markdown("""
    **Privacy Policy**  
    Last updated: April 2026  

    **1. Data We Collect**  
    Calmera collects your email address solely to send you a one‑time login code and to deliver your PDF blueprint. We do not share, sell, or rent your email address to any third party.  

    **2. How We Use Data**  
    - To authenticate your login via OTP.  
    - To deliver your purchased PDF.  
    - To improve the Service (aggregated, anonymised).  

    **3. Data Retention**  
    We retain email addresses for 90 days after your last login, after which they are permanently deleted.  

    **4. Payment Processing**  
    Payments are processed by Stripe. We do not store credit card details. Stripe's privacy policy applies to payment information.  

    **5. Your Rights**  
    You may request deletion of your email address by contacting us.  

    **6. Changes to This Policy**  
    We may update this policy. Continued use indicates acceptance.  
    """)
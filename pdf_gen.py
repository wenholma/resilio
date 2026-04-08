from fpdf import FPDF

def generate_resilience_pdf(water_data, power_data, sanitation_data, comms_data, user_profile):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "RESILIO — HOME RESILIENCE BLUEPRINT", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Prepared for: {user_profile['email']}", ln=True, align='C')
    pdf.cell(0, 10, f"Duration: {user_profile['days']} Days", ln=True, align='C')
    pdf.ln(10)

    # Water
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. WATER SECURITY", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8,
        f"Total required: {water_data['total_liters']}L.\n"
        f"Store {water_data['containers_needed_20L']} x 20L containers.\n"
        "Rotate water every 6–12 months."
    )
    pdf.ln(5)

    # Power
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. ENERGY & COMMUNICATIONS", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8,
        f"Battery needed: {power_data['recommended_battery_size']}Wh.\n"
        f"Solar panel estimate: {power_data['solar_panel_est']}W.\n"
        "Run fridge in cycles to extend battery life."
    )
    pdf.ln(5)

    # Sanitation
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. SANITATION", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8,
        f"Buckets needed: {sanitation_data['buckets_needed']}.\n"
        f"Cover material: {sanitation_data['cover_material_kg']}kg.\n"
        f"Hand sanitizer: {sanitation_data['sanitizer_liters']}L."
    )
    pdf.ln(5)

    # Comms
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "4. COMMUNICATIONS", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8,
        f"Radio: {'Yes' if comms_data['radio'] else 'No'}\n"
        f"Printed contacts: {'Yes' if comms_data['contacts'] else 'No'}\n"
        f"Local map: {'Yes' if comms_data['map'] else 'No'}"
    )

    return pdf.output(dest='S').encode('latin-1')

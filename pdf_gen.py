from fpdf import FPDF


# ---------------------------------------------------------
# PDF SETUP & SHARED HELPERS
# ---------------------------------------------------------

class ResilioPDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "Resilio — Household Resilience Blueprint", ln=True)
        self.ln(2)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()} of 3", align="R")


def section_title(pdf, text):
    pdf.set_font("DejaVu", "B", 13)
    pdf.ln(4)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, text, ln=True)
    pdf.ln(2)


def subsection_title(pdf, text):
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, text, ln=True)
    pdf.ln(1)


def body_text(pdf, text):
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 6, text)
    pdf.ln(2)


def bullet_item(pdf, text):
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.set_x(15)  # Indent for bullet
    pdf.cell(5, 6, "•", ln=0)
    pdf.set_x(22)  # Position for text after bullet
    pdf.multi_cell(170, 6, text)  # Fixed width to prevent overflow


def info_box(pdf, text):
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, text, fill=True)
    pdf.ln(3)


def divider_line(pdf):
    pdf.set_draw_color(220, 220, 220)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)


# ---------------------------------------------------------
# PAGE 1 — HOUSEHOLD SNAPSHOT
# ---------------------------------------------------------

def render_page_1_snapshot(pdf, data):
    pdf.add_page()

    # Intro paragraph
    pdf.set_x(10)
    body_text(
        pdf,
        "This blueprint gives you a calm, practical overview of how your household "
        "can cope with short‑term disruptions such as power outages, water "
        "interruptions, or severe weather."
    )
    pdf.ln(4)

    # Household Profile
    subsection_title(pdf, "Household Profile")
    bullet_item(pdf, f"People: {data['people']}")
    bullet_item(pdf, f"Plan duration: {data['days']} days")
    bullet_item(pdf, f"Warm‑day temperature: {data['temperature']} {data['unit']}")
    bullet_item(pdf, f"Pets: {data['cats']} cats, {data['dogs']} dogs")
    pdf.ln(4)

    divider_line(pdf)

    # Your Key Targets
    subsection_title(pdf, "Your Key Targets")
    bullet_item(pdf, f"Water: {data['water_total']} L needed for drinking, food prep, and basic hygiene.")
    bullet_item(pdf, f"Power: {data['power_daily']} Wh/day for essential devices.")
    bullet_item(pdf, f"Sanitation: {data['buckets']}-bucket setup recommended.")
    bullet_item(pdf, f"Communications: Radio {data['radio']}. Contacts {data['contacts']}. Map {data['map']}.")
    pdf.ln(4)

    divider_line(pdf)

    # Resilio Score
    subsection_title(pdf, f"Your Resilio Score: {data['grade']}")
    pdf.set_x(10)
    info_box(
        pdf,
        "This score is a planning snapshot, not a prediction or guarantee. "
        "It highlights where small, practical improvements can make a meaningful difference."
    )
    pdf.ln(4)

    # Top 3 Next Steps
    subsection_title(pdf, "Top 3 Next Steps")
    steps = data["next_steps"]
    bullet_item(pdf, steps[0])
    bullet_item(pdf, steps[1])
    bullet_item(pdf, steps[2])


# ---------------------------------------------------------
# PAGE 2 — WATER & POWER ESSENTIALS
# ---------------------------------------------------------

def render_page_2_water_power(pdf, data):
    pdf.add_page()

    # Water Plan
    section_title(pdf, "Water Plan")
    pdf.set_x(10)
    body_text(
        pdf,
        "Water is the most important resource during any disruption. This plan shows "
        "the minimum amount your household needs to stay safe and functional."
    )
    pdf.ln(2)

    water = data["water"]
    bullet_item(pdf, f"Daily minimum: {water['daily']} L")
    bullet_item(pdf, f"Total for {data['days']} days: {water['total']} L")
    bullet_item(pdf, f"20 L containers needed: {water['containers']}")
    bullet_item(pdf, f"Total weight: {water['weight']} kg")
    pdf.ln(2)

    pdf.set_x(10)
    body_text(
        pdf,
        "Storage guidance: Spread containers across low, stable areas such as garage "
        "floors or under benches. Avoid high shelving."
    )
    pdf.ln(2)

    subsection_title(pdf, "Tips:")
    bullet_item(pdf, "Label containers with fill dates")
    bullet_item(pdf, "Store away from sunlight")
    bullet_item(pdf, "Refresh every 6-12 months")
    pdf.ln(6)

    divider_line(pdf)

    # Essential Power Plan
    section_title(pdf, "Essential Power Plan")
    pdf.set_x(10)
    body_text(
        pdf,
        "This plan focuses on essential electricity needs only — staying connected, "
        "informed, and safely lit."
    )
    pdf.ln(2)

    power = data["power"]
    bullet_item(pdf, f"Daily energy required: {power['daily_wh']} Wh")
    bullet_item(pdf, f"Recommended battery size: {power['battery_wh']} Wh")
    bullet_item(pdf, f"Estimated solar input: {power['solar_wh']} Wh/day")
    pdf.ln(2)

    pdf.set_x(10)
    info_box(
        pdf,
        "What this means: A mid‑sized battery or power bank will support phones, "
        "lighting, and limited laptop use. Solar can extend battery life but varies "
        "with weather and season."
    )


# ---------------------------------------------------------
# PAGE 3 — SANITATION, COMMUNICATIONS & MAINTENANCE
# ---------------------------------------------------------

def render_page_3_sanitation_comms_maintenance(pdf, data):
    pdf.add_page()

    # Sanitation & Hygiene
    section_title(pdf, "Sanitation & Hygiene")
    pdf.set_x(10)
    body_text(
        pdf,
        "If water or sewer services are disrupted, a simple sanitation setup helps "
        "maintain comfort and reduces illness risk."
    )
    pdf.ln(2)

    sanitation = data["sanitation"]
    bullet_item(pdf, f"Buckets: {sanitation['buckets']}")
    bullet_item(pdf, f"Cover material: {sanitation['cover_kg']} kg")
    bullet_item(pdf, f"Hand hygiene: {sanitation['sanitizer_l']} L")
    pdf.ln(2)

    subsection_title(pdf, "Short‑term method:")
    bullet_item(pdf, "One bucket is used as the toilet.")
    bullet_item(pdf, "Cover material is added after each use.")
    bullet_item(pdf, "A second bucket stores supplies.")
    bullet_item(pdf, "Hands are cleaned after every use.")
    pdf.ln(6)

    divider_line(pdf)

    # Communications Checklist
    section_title(pdf, "Communications Checklist")
    comms = data["comms"]
    bullet_item(pdf, f"Radio: {comms['radio']}.")
    bullet_item(pdf, f"Printed contacts: {comms['contacts']}.")
    bullet_item(pdf, f"Local map: {comms['map']}.")
    pdf.ln(2)

    pdf.set_x(10)
    body_text(
        pdf,
        "These items help you stay informed if mobile networks are slow or unavailable."
    )
    pdf.ln(6)

    divider_line(pdf)

    # 30-Day Maintenance Routine
    section_title(pdf, "30‑Day Maintenance Routine")
    bullet_item(pdf, "Week 1: Check water containers and labels.")
    bullet_item(pdf, "Week 2: Test lights and charge batteries.")
    bullet_item(pdf, "Week 3: Review hygiene and pantry supplies.")
    bullet_item(pdf, "Week 4: Update contacts and reprint your emergency card.")
    pdf.ln(6)

    # Important Note
    pdf.set_x(10)
    info_box(
        pdf,
        "Important Note: This blueprint provides general household preparedness "
        "guidance only. It does not replace official instructions from emergency "
        "authorities."
    )


# ---------------------------------------------------------
# MAIN PDF GENERATOR
# ---------------------------------------------------------

def generate_resilience_pdf(data):
    pdf = ResilioPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(left=15, top=20, right=15)

    # Add DejaVu fonts (Unicode support)
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)

    render_page_1_snapshot(pdf, data)
    render_page_2_water_power(pdf, data)
    render_page_3_sanitation_comms_maintenance(pdf, data)

    return bytes(pdf.output())
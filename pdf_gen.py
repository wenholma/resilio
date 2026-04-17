from fpdf import FPDF
from datetime import datetime
import textwrap
import re

class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=12)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 5, "Calmera - Household Resilience Blueprint", 0, 0, "L")
            self.cell(0, 5, f"Page {self.page_no()}", 0, 0, "R")
            self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, "General guidance only. Always follow official emergency advice.", 0, 0, "C")

    def _clean_text(self, text):
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        # Replace special characters
        replacements = {
            "—": "-", "–": "-", "•": "-", "’": "'", "‘": "'",
            "“": '"', "”": '"', "…": "...", "✓": "[X]", "✗": "[ ]",
            "≥": ">=", "≤": "<=", "→": "->", "←": "<-",
            "°": " deg", "×": "x", "±": "+/-", "█": "#", "░": "."
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Also replace Unicode checkmark and cross if any remain
        text = text.replace("✅", "[OK]").replace("❌", "[NO]")
        return text

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, self._clean_text(title), 0, 1, "L")
        self.ln(2)

    def subsection_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 51, 102)
        self.cell(0, 7, self._clean_text(title), 0, 1, "L")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        text = self._clean_text(text)
        for line in textwrap.wrap(text, 120):
            self.cell(0, 4, line, 0, 1)
        self.ln(1)

    def bullet_point(self, text):
        self.set_font("Helvetica", "", 9)
        text = self._clean_text(text)
        self.cell(5, 4, "-", 0, 0)
        for line in textwrap.wrap(text, 115):
            self.cell(0, 4, line, 0, 1)
            if line != textwrap.wrap(text, 115)[-1]:
                self.cell(5, 4, " ", 0, 0)
        self.ln(1)

    def draw_table(self, headers, rows, col_widths=None):
        """Draw a simple table with borders"""
        if col_widths is None:
            col_widths = [40, 40, 40]
        self.set_font("Helvetica", "B", 9)
        # Header row
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, self._clean_text(header), 1, 0, "C")
        self.ln()
        # Data rows
        self.set_font("Helvetica", "", 9)
        for row in rows:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6, self._clean_text(str(cell)), 1, 0, "L")
            self.ln()
        self.ln(2)

    def progress_bar_ascii(self, percentage, width_chars=30):
        """Return a string of # and . for visual progress"""
        filled = int(round(width_chars * percentage / 100))
        return "#" * filled + "." * (width_chars - filled)

def generate_calmera_pdf(data):
    pdf = PDF()
    pdf.add_page()

    # ----- PAGE 1 -----
    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, "Calmera Household Resilience Dashboard", 0, 1, "C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, "Your Readiness at a Glance", 0, 1, "C")
    pdf.ln(6)

    # Metrics table
    water_percent = min(100, (data['water_total'] / (data['people'] * data['days'] * 3)) * 100)
    power_percent = 100 if data['power_battery_wh'] >= 500 else 50
    sanitation_percent = 100 if data['has_toilet_plan'] and data['has_cover_material'] else 30
    comms_percent = (sum([data['has_radio'], data['has_contacts'], data['has_map']]) / 3) * 100
    overall_score_val = (water_percent + power_percent + sanitation_percent + comms_percent) / 4
    grade = data['grade']
    grade_text = f"{grade} — {'Well Prepared' if grade in ['A','B'] else 'Action Needed' if grade == 'C' else 'Significant Gaps'}"
    # Map grade to status emoji replacement
    if grade in ['A','B']:
        status_symbol = "[OK]"
    elif grade == 'C':
        status_symbol = "[!]"
    else:
        status_symbol = "[!!]"

    headers = ["Metric", "Status", "Score"]
    rows = [
        [f"Overall Grade", f"{status_symbol} {grade_text}", f"{overall_score_val:.0f}%"],
        ["Water Readiness", f"{'[OK] Fully covered' if water_percent >= 80 else '[!] Partial'}", f"{water_percent:.0f}%"],
        ["Power Backup", f"{'[OK] Full backup' if power_percent >= 80 else '[!] Partial coverage'}", f"{power_percent:.0f}%"],
        ["Sanitation Plan", f"{'[OK] System in place' if sanitation_percent >= 80 else '[!] Missing'}", f"{sanitation_percent:.0f}%"],
        ["Communications", f"{'[OK] Complete' if comms_percent >= 80 else '[!] Gaps to address'}", f"{comms_percent:.0f}%"]
    ]
    pdf.draw_table(headers, rows, col_widths=[45, 70, 30])

    # Household info line
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Household: {data['people']} adult(s), {data['cats']+data['dogs']} pets · Planning horizon: {data['days']} days · Generated: {datetime.now().strftime('%d %B %Y')}", 0, 1, "C")
    pdf.ln(4)

    # The Bottom Line
    pdf.section_title("The Bottom Line")
    if overall_score_val >= 70:
        pdf.body_text("Your household can handle short disruptions, but you're vulnerable beyond 48 hours. The good news: a single weekend of targeted action closes the gaps.")
    else:
        pdf.body_text("Your household has significant gaps. The good news: a single weekend of targeted action can dramatically improve your readiness.")
    pdf.body_text(f"Your water storage is {'solid' if water_percent >= 80 else 'below target'}. Your sanitation plan {'works' if sanitation_percent >= 80 else 'needs setup'}. What's missing is backup power capacity and a printed communications kit—both fixable for under $150.")

    # Water section
    pdf.section_title("Water — Your Critical Asset")
    daily_water = data['water_daily']
    total_water = data['water_total']
    pdf.body_text(f"{data['days']}-Day Requirement: {total_water:.0f} litres total ({daily_water:.1f} L/day)")
    pdf.ln(2)

    # Daily breakdown with ASCII progress bar
    breakdown = data['water_breakdown']
    drinking = breakdown.get('drinking', 0) / data['days']
    cooking = breakdown.get('food_prep', 0) / data['days']
    hygiene = breakdown.get('hygiene', 0) / data['days']
    pets = breakdown.get('pets', 0) / data['days']
    total_daily = drinking + cooking + hygiene + pets

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, "Daily Breakdown", 0, 1)
    pdf.set_font("Courier", "", 8)
    # Use monospace for alignment
    bar_width = 30
    for label, value in [("Drinking & Hydration", drinking), ("Cooking & Food Prep", cooking), ("Basic Hygiene", hygiene), ("Pets", pets)]:
        percent = (value / total_daily) * 100 if total_daily > 0 else 0
        bar = pdf.progress_bar_ascii(percent, bar_width)
        pdf.cell(45, 5, label, 0, 0)
        pdf.cell(bar_width*0.8*2, 5, bar, 0, 0)
        pdf.cell(20, 5, f"{value:.0f} L", 0, 1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(45, 5, "Total", 0, 0)
    pdf.cell(0, 5, f"{total_daily:.0f} L/day", 0, 1)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 9)
    containers_needed = data['water_containers']
    pdf.body_text(f"What you need: {containers_needed} x 20L food-grade jerry cans (~$25-35 each at Bunnings or Mitre 10)")
    pdf.body_text("Storage rules:")
    pdf.bullet_point("Floor level only — total water weighs nearly {:.0f}kg".format(data['water_weight']))
    pdf.bullet_point("Away from direct sunlight")
    pdf.bullet_point("Label with fill date; refresh annually")

    # Power section (starts on page 1, continues to page 2 if needed)
    pdf.ln(4)
    pdf.section_title("Power & Communications")
    pdf.body_text(f"Daily Energy Target: {data['power_daily_wh']:.0f} Wh")

    # Device table
    device_headers = ["Device", "Daily Draw"]
    device_rows = []
    if data['power_breakdown']['phone_wh'] > 0:
        device_rows.append([f"Phones", f"{data['power_breakdown']['phone_wh']:.0f} Wh"])
    if data['power_breakdown']['laptop_wh'] > 0:
        device_rows.append([f"Laptop", f"{data['power_breakdown']['laptop_wh']:.0f} Wh"])
    if data['power_breakdown']['light_wh'] > 0:
        device_rows.append([f"LED Lighting", f"{data['power_breakdown']['light_wh']:.0f} Wh"])
    if data['power_breakdown']['fridge_wh'] > 0:
        device_rows.append([f"Fridge", f"{data['power_breakdown']['fridge_wh']:.0f} Wh"])
    else:
        device_rows.append([f"Fridge", "0 Wh (not currently backed up)"])
    pdf.draw_table(device_headers, device_rows, col_widths=[60, 60])

    pdf.subsection_title("Two Paths Forward")
    options_headers = ["Option", "What It Covers", "Cost"]
    options_rows = [
        ["Budget Lifeline", "Phones, lights, radio", "~$150"],
        ["Full Backup", "Add fridge + devices", "$2,000+"]
    ]
    pdf.draw_table(options_headers, options_rows, col_widths=[40, 70, 40])
    pdf.body_text("For most households, the budget option—two 20,000mAh power banks plus a battery radio—keeps you connected when it matters most.")

    # Communications checklist table
    pdf.subsection_title("Communications Checklist")
    comms_headers = ["Item", "Status", "Why It Matters"]
    comms_rows = [
        ["AM/FM Emergency Radio", "[X]" if data['has_radio'] else "[ ]", "Civil Defence updates when towers fail"],
        ["Printed Contact List", "[X]" if data['has_contacts'] else "[ ]", "Doctor, school, family—write them down"],
        ["Local Paper Map", "[X]" if data['has_map'] else "[ ]", "Navigate when GPS is offline"]
    ]
    pdf.draw_table(comms_headers, comms_rows, col_widths=[50, 30, 70])

    # If space allows, start sanitation on page 1; otherwise it will flow to page 2
    # We'll let auto page break handle it.

    # ----- PAGE 2 (or continue on same page if space) -----
    # Sanitation section
    pdf.section_title("Sanitation — The Two-Bucket System")
    pdf.body_text("When water mains break, this cheap setup prevents the illness outbreaks that follow disasters.")
    pdf.body_text(f"Your kit:")
    pdf.bullet_point(f"{data['sanitation_buckets']} heavy-duty bucket with lid (the toilet)")
    pdf.bullet_point("Cover material: sawdust, peat moss, or clay litter")
    pdf.bullet_point("Compostable bin liners")
    pdf.bullet_point(f"{data['sanitation_sanitizer_l']:.1f} L hand sanitiser")
    pdf.body_text("The process: Line bucket -> use -> cover waste completely -> seal and store when full.")

    # Shopping list
    pdf.section_title("Weekend Shopping List")
    pdf.subsection_title("Quick-Start Bundle (under $100)")
    pdf.body_text("Start here if budget is tight—these four items cover the essentials:")
    pdf.bullet_point("2 x 20L water containers")
    pdf.bullet_point("2 x 20,000mAh power banks")
    pdf.bullet_point("1 bucket + 1 bag kitty litter")
    pdf.bullet_point("1 battery AM/FM radio")

    pdf.subsection_title("Full List by Store")
    pdf.body_text("Hardware (Bunnings / Mitre 10)")
    pdf.bullet_point(f"{containers_needed} x 20L food-grade water containers")
    pdf.bullet_point("2 x heavy-duty buckets with lids")
    pdf.bullet_point("Sawdust or kitty litter")
    pdf.bullet_point("Heavy-duty rubbish bags")
    pdf.bullet_point("Masking tape + permanent marker")
    pdf.body_text("Electronics (PB Tech / Noel Leeming)")
    pdf.bullet_point("2 x 20,000mAh power banks")
    pdf.bullet_point("Battery-powered radio + spare batteries")
    pdf.bullet_point("Extra phone charging cables")
    pdf.body_text("Supermarket / Pharmacy")
    pdf.bullet_point("Hand sanitiser (2 large pump bottles)")
    pdf.bullet_point("Basic first aid: Panadol, plasters, antiseptic")
    pdf.bullet_point("7 days non-perishable food you'll actually eat")

    # 30-Day plan table
    pdf.section_title("30-Day Implementation Plan")
    plan_headers = ["Weekend", "Focus", "Actions"]
    plan_rows = [
        ["1", "Hydration", "Buy containers, wash, fill, label, store"],
        ["2", "Sanitation", "Buckets, bags, cover material -> garage or laundry"],
        ["3", "Power & Comms", "Order power banks, buy radio, print contacts"],
        ["4", "Food & First Aid", "Stock canned goods, pasta, first aid kit"]
    ]
    pdf.draw_table(plan_headers, plan_rows, col_widths=[20, 40, 90])
    pdf.body_text("After Weekend 1, you're better prepared than 80% of households.")

    # Top 3 actions
    pdf.section_title("Your Top 3 Actions This Week")
    for step in data['next_steps'][:3]:
        pdf.bullet_point(step)

    # Legal disclaimer
    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "This blueprint is general guidance, not official emergency advice. Always follow local Civil Defence instructions during an actual event.", 0, 0, "C")
    pdf.set_y(-12)
    pdf.cell(0, 4, f"Generated by Calmera on {datetime.now().strftime('%d %B %Y')}. All rights reserved.", 0, 0, "C")

    return bytes(pdf.output(dest="S"))
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
        self.cell(0, 5, "For personal use only. Not official emergency advice.", 0, 0, "C")

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
        replacements = {
            "—": "-", "–": "-", "•": "-", "’": "'", "‘": "'",
            "“": '"', "”": '"', "…": "...", "✓": "√", "✗": "x",
            "≥": ">=", "≤": "<=", "→": "->", "←": "<-",
            "°": " deg", "×": "x", "±": "+/-"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 51, 102)
        self.cell(0, 7, self._clean_text(title), 0, 1, "L")
        self.ln(1)

    def subsection_title(self, title):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 6, self._clean_text(title), 0, 1, "L")
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

    def metric_card(self, x, y, label, value, unit, bg_color=(240, 240, 240)):
        self.set_fill_color(*bg_color)
        self.rect(x, y, 55, 22, 'F')
        self.set_xy(x+3, y+3)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, self._clean_text(label), 0, 1)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.set_xy(x+3, y+10)
        self.cell(0, 6, f"{value} {unit}", 0, 1)

    def progress_bar(self, x, y, width, percentage, label=""):
        self.set_fill_color(230, 230, 230)
        self.rect(x, y, width, 4, 'F')
        fill_width = width * min(1.0, percentage / 100)
        self.set_fill_color(0, 150, 100)
        self.rect(x, y, fill_width, 4, 'F')
        if label:
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(80, 80, 80)
            self.set_xy(x, y-3)
            self.cell(0, 3, self._clean_text(label), 0, 1)

def generate_calmera_pdf(data):
    pdf = PDF()
    pdf.add_page()

    # ----- PAGE 1 -----
    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, "Calmera: Household Resilience Blueprint", 0, 1, "C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, "Your personalised dashboard for short-term disruptions", 0, 1, "C")
    pdf.ln(4)

    # Household profile
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(45, 6, f"Adults: {data['people']}", 0, 0)
    pdf.cell(45, 6, f"Pets: {data['cats']+data['dogs']}", 0, 0)
    pdf.cell(45, 6, f"Plan: {data['days']} days", 0, 0)
    pdf.cell(60, 6, f"Climate: {data['climate_class']} ({data['temperature']:.0f}{data['unit']})", 0, 1)
    pdf.ln(4)

    # Metrics row
    y_start = pdf.get_y()
    pdf.metric_card(10, y_start, "Total Water", f"{data['water_total']:.0f}", "L")
    pdf.metric_card(75, y_start, "Battery Capacity", f"{data['power_battery_wh']:.0f}", "Wh")
    pdf.metric_card(140, y_start, "Calmera Score", data['grade'], "")
    pdf.set_y(y_start + 26)

    # Score interpretation
    pdf.section_title("What Your Score Means")
    score = data['grade']
    if score == 'A':
        pdf.body_text("Excellent! Your household is well prepared. Maintain your supplies and review monthly.")
    elif score == 'B':
        pdf.body_text("Good foundation. A few small investments will make a big difference.")
    elif score == 'C':
        pdf.body_text("Action required. Focus on the top priorities below to improve your resilience.")
    else:
        pdf.body_text("Significant gaps. Start with the Quick Start bundle and the top 3 priorities.")

    # Top 3 priorities
    pdf.section_title("Your Top 3 Priorities")
    for step in data['next_steps']:
        pdf.bullet_point(step)

    # Progress bars
    pdf.ln(2)
    pdf.section_title("Readiness Breakdown")
    water_percent = min(100, (data['water_total'] / (data['people'] * data['days'] * 3)) * 100)
    power_percent = 100 if data['power_battery_wh'] >= 500 else 50
    sanitation_percent = 100 if data['has_toilet_plan'] and data['has_cover_material'] else 30
    comms_percent = (sum([data['has_radio'], data['has_contacts'], data['has_map']]) / 3) * 100

    pdf.body_text("Water Storage")
    pdf.progress_bar(10, pdf.get_y(), 180, water_percent, f"{water_percent:.0f}% of target")
    pdf.ln(7)
    pdf.body_text("Power Backup")
    pdf.progress_bar(10, pdf.get_y(), 180, power_percent, f"{power_percent:.0f}% of recommended")
    pdf.ln(7)
    pdf.body_text("Sanitation Plan")
    pdf.progress_bar(10, pdf.get_y(), 180, sanitation_percent, f"{sanitation_percent:.0f}% ready")
    pdf.ln(7)
    pdf.body_text("Communications")
    pdf.progress_bar(10, pdf.get_y(), 180, comms_percent, f"{comms_percent:.0f}% complete")
    pdf.ln(10)

    # Quick start note
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 6, "Quick Start under $100", 0, 1)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.body_text("2 x 20L water containers, 2 x 20,000mAh power banks, 1 bucket + kitty litter, 1 battery radio")

    # ----- PAGE 2 -----
    pdf.add_page()

    # Water explanation
    pdf.section_title("Water Plan")
    pdf.body_text(f"You need {data['water_total']:.0f} litres for {data['days']} days. That's {data['water_daily']:.1f} litres per day.")
    pdf.body_text(f"Store {data['water_containers']} x 20L containers (Bunnings/Mitre 10). Total weight: {data['water_weight']:.1f} kg – keep on floor level.")
    if data['water_total'] < data['people'] * data['days'] * 3:
        pdf.body_text("Your water storage is below the recommended minimum. Aim for at least 3 litres per person per day.")
    else:
        pdf.body_text("Your water target is met. Great work!")

    # Power explanation with Wh clarity
    pdf.section_title("Power Plan")
    pdf.body_text(f"Daily energy need: {data['power_daily_wh']:.0f} Wh (Watt-hours). Recommended battery: {data['power_battery_wh']:.0f} Wh.")
    pdf.body_text("A Watt-hour (Wh) measures energy. For example, a 500Wh battery can run a 50W phone charger for 10 hours. A 2000Wh battery can run a fridge for most of a day.")
    if data['power_battery_wh'] < 500:
        pdf.body_text("A small power bank (200-500 Wh) can keep phones and lights running. For fridge backup, consider a larger power station like EcoFlow or Jackery.")
    else:
        pdf.body_text("Your battery target is sufficient for essential devices. Add a solar panel for longer outages.")

    # Sanitation explanation with cover material vs sanitizer
    pdf.section_title("Sanitation Setup")
    pdf.body_text(f"You need {data['sanitation_buckets']} bucket(s), {data['sanitation_cover_kg']:.0f} kg cover material, and {data['sanitation_sanitizer_l']:.1f} L hand sanitiser.")
    pdf.body_text("Cover material (e.g., sawdust, kitty litter) is used to cover waste after each toilet use – it controls odour and flies. Hand sanitiser is for cleaning your hands after contact.")
    if not (data['has_toilet_plan'] and data['has_cover_material']):
        pdf.body_text("You don't yet have a backup toilet plan or cover material. A simple bucket, heavy-duty bags, and kitty litter works well.")
    else:
        pdf.body_text("You have a plan – good. Remember: after each use, add a scoop of cover material before sealing the bag.")

    # Communications
    pdf.section_title("Communications")
    missing = []
    if not data['has_radio']: missing.append("radio")
    if not data['has_contacts']: missing.append("printed contacts")
    if not data['has_map']: missing.append("paper map")
    if missing:
        pdf.body_text(f"Missing: {', '.join(missing)}. Add these to stay informed when networks fail.")
    else:
        pdf.body_text("You have all three communication tools. Well done!")

    # Shopping list (condensed)
    pdf.section_title("Weekend Shopping List")
    pdf.body_text(f"• {data['water_containers']} x 20L water containers (Mitre 10/Bunnings)")
    pdf.body_text("• 2 x heavy-duty buckets, 1 bag kitty litter, rubbish bags, masking tape")
    pdf.body_text("• 2 x 20,000mAh power banks or portable power station (PB Tech/Noel Leeming)")
    pdf.body_text("• Battery-powered radio, spare batteries, charging cables")
    pdf.body_text("• Hand sanitiser, first aid supplies, 7 days non-perishable food")

    # 30-day plan
    pdf.section_title("30-Day Implementation Plan")
    pdf.body_text("Week 1: Buy and fill water containers. Week 2: Assemble sanitation bucket. Week 3: Get power banks and radio. Week 4: Stock food and first aid.")

    # Legal (condensed)
    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "This blueprint provides general guidance only. Always follow official emergency advice.", 0, 0, "C")
    pdf.set_y(-12)
    pdf.cell(0, 4, f"Generated by Calmera on {datetime.now().strftime('%d %B %Y')}. All rights reserved.", 0, 0, "C")

    return bytes(pdf.output(dest="S"))
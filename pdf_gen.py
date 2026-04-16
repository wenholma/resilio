from fpdf import FPDF
from datetime import datetime
import textwrap
import math

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 6, "Calmera - Household Resilience Blueprint", 0, 0, "L")
            self.cell(0, 6, f"Page {self.page_no()}", 0, 0, "R")
            self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, "For personal use only. Not official emergency advice.", 0, 0, "C")

    def _clean_text(self, text):
        # Remove all emojis and special characters
        import re
        # Remove emoji patterns
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        # Replace other punctuation
        replacements = {
            "—": "-", "–": "-", "•": "-", "’": "'", "‘": "'",
            "“": '"', "”": '"', "…": "...", "✓": "√", "✗": "x"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
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
        for line in textwrap.wrap(text, 95):
            self.cell(0, 4, line, 0, 1)
        self.ln(1)

    def bullet_point(self, text):
        self.set_font("Helvetica", "", 9)
        text = self._clean_text(text)
        self.cell(5, 4, "-", 0, 0)
        for line in textwrap.wrap(text, 90):
            self.cell(0, 4, line, 0, 1)
            if line != textwrap.wrap(text, 90)[-1]:
                self.cell(5, 4, " ", 0, 0)
        self.ln(1)

def generate_calmera_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # PAGE 1: Cover
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, "Calmera: Your Household Resilience Blueprint", 0, 1, "C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, "A calm, practical guide to keeping your household safe, powered, and hydrated", 0, 1, "C")
    pdf.cell(0, 5, "during short-term disruptions.", 0, 1, "C")
    pdf.ln(6)

    pdf.section_title("Prepared For:")
    pdf.body_text(f"{data['people']} Adults | {data['cats']+data['dogs']} Pets | {data['days']} Days")
    pdf.body_text(f"Climate Profile: {data['climate_class']} ({data['temperature']}{data['unit']}) - Requires elevated water planning.")

    score = data['grade']
    if score in ['A', 'B']:
        score_msg = f"Your Calmera Readiness Score: {score} (Well Prepared)"
    elif score == 'C':
        score_msg = f"Your Calmera Readiness Score: {score} (Action Required)"
    else:
        score_msg = f"Your Calmera Readiness Score: {score} (Significant Gaps)"
    pdf.section_title(score_msg)
    pdf.body_text("This score is based on your water storage, power backup, sanitation plan, and communication tools. A or B means you're in good shape. C means you have some gaps. D or E means immediate action is recommended.")
    pdf.body_text("Your household has a solid foundation but is currently vulnerable to disruptions lasting longer than 48 hours. Small, targeted investments this weekend will significantly boost your family's resilience.")

    pdf.section_title("Your Top 3 Immediate Priorities:")
    next_steps = data.get('next_steps', [])
    for step in next_steps[:3]:
        pdf.bullet_point(step)

    # PAGE 2: Water Strategy
    pdf.add_page()
    pdf.section_title("Water Strategy - Your Most Critical Asset")
    pdf.body_text("Water is heavy, takes up space, and is the first thing to disappear during an emergency. Public health guidelines recommend at least 3 litres per person per day for drinking, cooking, and basic hygiene.")
    
    total_water = data['water_total']
    daily_water = data['water_daily']
    pdf.body_text(f"Your {data['days']}-Day Household Requirement: {total_water:.0f} Litres total")
    pdf.body_text(f"(Based on a daily target of {daily_water:.1f} Litres/day for {data['people']} adults, including a climate adjustment if applicable).")
    
    pdf.subsection_title("Your Daily Breakdown:")
    # Use the breakdown from data
    breakdown = data.get('water_breakdown', {})
    pdf.body_text(f"- Drinking & Hydration: {breakdown.get('drinking', 0):.0f} L / day")
    pdf.body_text(f"- Cooking & Food Prep: {breakdown.get('food_prep', 0):.0f} L / day")
    if breakdown.get('hygiene', 0) > 0:
        pdf.body_text(f"- Basic Hygiene: {breakdown['hygiene']:.0f} L / day")
    pdf.body_text(f"- Pets: {breakdown.get('pets', 0):.0f} L / day")
    if breakdown.get('climate_factor', 1.0) > 1.0:
        pdf.body_text(f"- Climate adjustment: +{(breakdown['climate_factor']-1)*100:.0f}%")

    containers = math.ceil(data['water_total'] / 20)  # round up
    weight = data['water_weight']
    pdf.subsection_title("How to Actually Store This:")
    pdf.body_text("You don't need expensive water tanks. The easiest way to store this much water is using standard, heavy-duty 20-litre jerry cans.")
    pdf.body_text(f"- You need: {containers} x 20L Food-Grade Water Containers.")
    pdf.body_text("- Where to buy: Bunnings, Mitre 10, or local camping stores (approx. NZD 25-35 each). Make sure they are stamped 'Food Grade'.")
    pdf.body_text(f"- Storage Rules: Store them on the floor (never on high shelves; {total_water:.0f}L weighs {weight:.1f}kg). Keep out of direct sunlight.")
    pdf.body_text("- Maintenance: Add a piece of masking tape with today's date. Empty and refill once a year (or every 6 months if using tap water).")

    # PAGE 3: Power & Communications
    pdf.add_page()
    pdf.section_title("Power & Communications Plan")
    pdf.body_text("When the grid goes down, you need to keep phones charged for emergency alerts, run basic lighting, and potentially save your fridge food.")
    pdf.body_text(f"Your Daily Energy Target: {data['power_daily_wh']:.0f} Watt-hours (Wh)")
    pdf.body_text("(This covers an energy-efficient fridge, phone charges, a laptop, and basic LED lighting).")
    pdf.body_text("Note: A Watt-hour (Wh) is a unit of energy. For example, a 100Wh battery can run a 10W LED light for 10 hours.")

    pdf.subsection_title("Your Purchase Options:")
    pdf.body_text("Option 1: The Full Backup (Run the Fridge + Devices)")
    pdf.body_text("- What you need: A Portable Power Station rated at 2000W or higher.")
    pdf.body_text("- Brands: EcoFlow Delta Max, Jackery Explorer 2000, or Bluetti.")
    pdf.body_text("- Add-on: A 200W folding solar panel to recharge during the day.")
    pdf.body_text("Option 2: The Budget Lifeline (Keep Phones & Lights Alive)")
    pdf.body_text("- If running a fridge is too expensive, focus on communication.")
    pdf.body_text("- What you need: Two 20,000mAh Power Banks (approx. NZD 60-100 each from PB Tech or Noel Leeming) and a pack of battery-powered lights or headlamps.")

    pdf.subsection_title("Communications Checklist:")
    radio_status = "Yes" if data['has_radio'] else "No"
    contacts_status = "Yes" if data['has_contacts'] else "No"
    map_status = "Yes" if data['has_map'] else "No"
    pdf.body_text(f"- [ ] AM/FM Emergency Radio: {radio_status}. Crucial for Civil Defence updates when mobile towers fail.")
    pdf.body_text(f"- [ ] Printed Contact List: {contacts_status}. Write down doctor, school, and out-of-town family numbers.")
    pdf.body_text(f"- [ ] Local Paper Map: {map_status}. Helps you navigate if GPS fails.")

    # PAGE 4: Sanitation System
    pdf.add_page()
    pdf.section_title("Sanitation System")
    pdf.body_text("If water mains break or sewer lines are damaged, flushing the toilet becomes impossible. This is a primary cause of illness following disasters. The 'Two-Bucket System' is cheap, sanitary, and highly effective.")
    pdf.body_text("We recommend 1 bucket for every 2 people. For a household of 1-2 people, 1 bucket is sufficient. For 3-4 people, 2 buckets, etc.")

    pdf.subsection_title("Your Household Needs:")
    buckets = data['sanitation_buckets']
    pdf.body_text(f"- {buckets} x Heavy Duty Buckets (with tight-fitting lids)")
    pdf.body_text(f"- {data['sanitation_cover_kg']:.0f} kg of 'Cover Material' (Sawdust, peat moss, or cheap clay kitty litter)")
    pdf.body_text("- Heavy-duty compostable bin liners")
    pdf.body_text(f"- {data['sanitation_sanitizer_l']:.1f} L of hand sanitiser")

    pdf.subsection_title("How the System Works:")
    pdf.body_text("1. Bucket 1 (The Toilet): Line this bucket with a heavy-duty bag.")
    pdf.body_text("2. The Golden Rule: After every use, cover waste completely with a generous scoop of Cover Material. This suffocates odors and repels flies.")
    pdf.body_text("3. Bucket 2 (The Storage): Store clean cover material, spare bags, toilet paper, and sanitiser.")
    pdf.body_text("4. Disposal: When bag is full, tie it off and store in a sealed wheelie bin until local authorities advise on safe disposal.")

    # PAGE 5: Shopping List + Low-Cost Bundle
    pdf.add_page()
    pdf.section_title("Your 'Grab-and-Go' Weekend Shopping List")
    pdf.body_text("Tear this page out and take it to the store.")

    pdf.subsection_title("Hardware Store (Mitre 10 / Bunnings)")
    pdf.body_text(f"[ ] {containers} x 20L Food-Grade Water Containers")
    pdf.body_text("[ ] 2 x 20L Heavy Duty Buckets with lids")
    pdf.body_text("[ ] 1 x Bag of Sawdust / Wood Shavings (or kitty litter from supermarket)")
    pdf.body_text("[ ] Heavy-duty rubbish bags")
    pdf.body_text("[ ] Masking tape and a permanent marker (for dating water)")

    pdf.subsection_title("Electronics / Online (PB Tech / Noel Leeming)")
    pdf.body_text("[ ] 2 x 20,000mAh Power Banks (or Portable Power Station if budget allows)")
    pdf.body_text("[ ] Battery-powered radio & spare batteries")
    pdf.body_text("[ ] Extra charging cables for your specific phones")

    pdf.subsection_title("Supermarket / Pharmacy")
    pdf.body_text("[ ] 2 x Large pump bottles of hand sanitiser")
    pdf.body_text("[ ] Basic First Aid supplies (Panadol, plasters, antiseptic cream)")
    pdf.body_text("[ ] 7 days of non-perishable food (canned goods, rice, oats - buy what you actually eat)")

    pdf.subsection_title("Quick Start Bundle (under $100)")
    pdf.body_text("If you can only spend $100 this weekend, start here:")
    pdf.body_text("- 2 x 20L water containers (Bunnings/Mitre 10)")
    pdf.body_text("- 2 x 20,000mAh power banks (PB Tech/Noel Leeming)")
    pdf.body_text("- 1 x bucket + 1 bag of kitty litter")
    pdf.body_text("- 1 x battery-powered AM/FM radio")
    pdf.body_text("These four items give you water for 2-3 days, phone charging, a toilet backup, and emergency broadcasts.")

    # PAGE 6: 30-Day Plan & Legal
    pdf.add_page()
    pdf.section_title("30-Day Implementation Plan")
    pdf.body_text("Don't try to do this all in one day. Spread the cost and effort over four weekends.")
    pdf.body_text("- Weekend 1: Hydration. Buy water containers, wash, fill, label, store. You are now safer than 80% of households.")
    pdf.body_text("- Weekend 2: Sanitation. Buy buckets, bags, and kitty litter/sawdust. Store in garage or laundry.")
    pdf.body_text("- Weekend 3: Power & Comms. Order power banks, buy emergency radio, print emergency contacts.")
    pdf.body_text("- Weekend 4: Food & First Aid. Do larger supermarket shop for canned goods, pasta, first aid.")

    pdf.section_title("Important Legal & Safety Information")
    pdf.subsection_title("Not Official Advice")
    pdf.body_text("This blueprint provides general household preparedness guidance only. It does not replace official instructions from emergency authorities, first responders, or medical professionals. Always follow local Civil Defence and government advice during an actual emergency.")
    
    pdf.subsection_title("Limitation of Liability")
    pdf.body_text("Calmera is a planning aid and does not predict, prevent, or guarantee protection from any emergency. Results are estimates based on user-provided inputs. Calmera makes no warranties regarding accuracy or completeness. Use at your own risk.")

    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Generated by Calmera on {datetime.now().strftime('%d %B %Y')}. All rights reserved.", 0, 0, "C")

    return bytes(pdf.output(dest="S"))
def calculate_water_needs(people, days, climate, cats=0, dogs=0, hygiene_plus=True):
    """
    Calculates total water requirements based on household size, climate, pets, and hygiene needs.
    """

    # Base human requirement (liters per person per day)
    base_per_person = 3.0  # drinking + minimal cooking

    # Climate adjustment
    if climate == "Arid/Hot":
        base_per_person *= 1.3  # 30% more water in high heat

    # Pets
    cat_water = cats * 0.25  # 250ml per cat per day
    dog_water = dogs * 1.0   # 1L per dog per day

    # Hygiene / dignity water
    hygiene_water = 2.0 if hygiene_plus else 0.5

    daily_requirement = (people * base_per_person) + cat_water + dog_water + hygiene_water
    total_liters = daily_requirement * days

    containers_needed_20L = total_liters / 20.0
    weight_kg = total_liters  # 1L = 1kg

    return {
        "daily_requirement": round(daily_requirement, 1),
        "total_liters": round(total_liters, 1),
        "containers_needed_20L": round(containers_needed_20L, 1),
        "weight_kg": round(weight_kg, 1)
    }


def calculate_power_needs(fridge=True, phones=0, laptops=0, led_lights=0, hours_of_light=5):
    """
    Calculates daily watt-hour requirements and recommended battery size.
    """

    total_wh = 0

    # Fridge consumption (approx)
    if fridge:
        total_wh += 600  # Wh/day for efficient cycling

    # Phones
    total_wh += phones * 15  # 15Wh per phone per day

    # Laptops
    total_wh += laptops * 60  # 60Wh per laptop per day

    # LED lights
    total_wh += led_lights * 5 * hours_of_light  # 5W bulbs

    # Safety margin
    recommended_battery = total_wh * 1.2

    # Solar estimate (assuming 4 hours peak sun)
    solar_panel_est = recommended_battery / 4.0

    return {
        "daily_wh_required": round(total_wh, 1),
        "recommended_battery_size": round(recommended_battery, 1),
        "solar_panel_est": round(solar_panel_est, 1)
    }


def calculate_sanitation_needs(people, days):
    """
    Calculates essential waste management needs.
    """

    # 1kg of cover material per person per week
    cover_material_kg = (people * (days / 7)) * 1.0

    return {
        "buckets_needed": 2,  # Standard two-bucket system
        "cover_material_kg": round(cover_material_kg, 1),
        "sanitizer_liters": round(people * 0.5, 1)  # 500ml per person
    }

def calculate_water_needs(people, days, climate, cats=0, dogs=0, hygiene_plus=True):
    """
    Calculate water needs based on NZ Civil Defence guidelines.
    
    Base: 3L per person/day (drinking + basic hygiene)
    Heat multiplier: +33% for High Heat / Extreme Heat
    Dignity water: 20L per person/day if hygiene_plus is True
    Pets: 1.5L per dog, 0.3L per cat per day
    
    Returns dictionary with daily requirement, total liters,
    containers needed (20L), and total weight in kg.
    """
    # Base requirement per person per day (drinking + basic hygiene)
    base_liters_per_person = 3.0

    # Climate adjustment (hot climate increases needs by ~33%)
    if climate in ["High Heat", "Extreme Heat", "Arid/Hot"]:
        base_liters_per_person = base_liters_per_person * 1.33

    # If hygiene_plus is selected, use comprehensive 20L per person standard
    if hygiene_plus:
        base_liters_per_person = 20.0

    # Pet water requirements
    pet_water_daily = (dogs * 1.5) + (cats * 0.3)

    # Daily total for all people + pets
    daily_requirement = (people * base_liters_per_person) + pet_water_daily

    # Total for the planned duration
    total_liters = daily_requirement * days

    # Number of 20L containers needed
    containers_needed = total_liters / 20.0

    # Weight in kg (1 liter of water = 1 kg)
    weight_kg = total_liters

    return {
        "daily_requirement": round(daily_requirement, 1),
        "total_liters": round(total_liters, 1),
        "containers_needed_20L": containers_needed,
        "weight_kg": weight_kg
    }


def calculate_power_needs(fridge=True, phones=2, laptops=1, led_lights=3, hours_of_light=5):
    """
    Estimate daily watt-hours based on typical device usage.
    
    Assumptions:
    - Fridge: 200W running, cycles ~8 hours/day = 1600 Wh/day
    - Phone charger: 10W, 2 hours to charge = 20 Wh per phone
    - Laptop: 50W, assume 2 hours of use = 100 Wh per laptop
    - LED light: 10W each, used for specified hours
    
    Returns dictionary with daily Wh required, recommended battery size
    (daily need + 20% buffer), and rough solar estimate.
    """
    daily_wh = 0

    # Fridge: 200W running, cycles ~8 hours/day = 1600 Wh/day
    if fridge:
        daily_wh += 1600

    # Phones: 10W charger, 2 hours to charge = 20 Wh per phone
    daily_wh += phones * 20

    # Laptops: 50W, assume 2 hours of use = 100 Wh per laptop
    daily_wh += laptops * 100

    # LED lights: 10W each, used for specified hours
    daily_wh += led_lights * 10 * hours_of_light

    # Recommended battery size: daily need + 20% buffer
    recommended_battery = daily_wh * 1.2

    # Solar estimate: ~30% of daily need as a rough average (assumes 100W panel)
    solar_est = daily_wh * 0.3

    return {
        "daily_wh_required": round(daily_wh, 0),
        "recommended_battery_size": round(recommended_battery, 0),
        "solar_panel_est": round(solar_est, 1)
    }


def calculate_sanitation_needs(people, days):
    """
    Calculate emergency sanitation supplies using the two-bucket system.
    
    Assumptions:
    - 2 buckets total (one for waste, one for cover material/supplies)
    - 0.5 kg cover material per person per day (sawdust, dry leaves, etc.)
    - 0.1 L hand sanitizer per person per day
    
    Returns dictionary with buckets needed, cover material in kg, and sanitizer in liters.
    """
    buckets_needed = 2
    
    cover_material_kg = round(people * days * 0.5, 1)
    
    sanitizer_liters = round(people * days * 0.1, 1)
    
    return {
        "buckets_needed": buckets_needed,
        "cover_material_kg": cover_material_kg,
        "sanitizer_liters": sanitizer_liters
    }
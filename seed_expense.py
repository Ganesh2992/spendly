"""Seed <count> realistic dummy expenses for user_id across past <months> months."""
import random
import sys
from datetime import date, timedelta

from database.db import get_db

# Force UTF-8 on Windows so the rupee sign (₹) prints cleanly.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Weighted categories — Food appears most, Health/Entertainment least.
CATEGORY_POOL = [
    ("Food",          50,   800,  [
                              "Chai and samosa", "Lunch at office canteen", "Dinner at Haldiram's",
                              "Weekly groceries from D-Mart", "Swiggy order", "Zomato dinner",
                              "Cold coffee at CCD", "Street food - pani puri", "Idli sambar breakfast",
                              "Subway meal", "Domino's pizza night", "Milk and bread",
                          ], 18),
    ("Transport",     20,   500,  [
                              "Uber to airport", "Auto rickshaw to station", "Metro card recharge",
                              "Petrol refill", "Ola ride to office", "Rapido bike trip",
                              "Bus pass top-up", "Diesel for car", "Cab to friend's place",
                          ], 14),
    ("Bills",         200,  3000, [
                              "Electricity bill - BESCOM", "Broadband recharge - Jio Fiber",
                              "Mobile postpaid - Airtel", "Gas cylinder refill",
                              "Water bill - BWSSB", "DTH recharge - Tata Play",
                              "Credit card bill payment", "WiFi monthly plan",
                          ], 14),
    ("Health",        100,  2000, [
                              "Pharmacy - Apollo", "Doctor consultation",
                              "Blood test at Thyrocare", "Vitamins and supplements",
                              "Dental cleaning", "Eye checkup at Lenskart",
                          ], 8),
    ("Entertainment", 100,  1500, [
                              "PVR movie tickets", "Netflix monthly plan",
                              "Spotify Premium", "Book from Crossword",
                              "Concert ticket", "Disney+ Hotstar subscription",
                          ], 8),
    ("Shopping",      200,  5000, [
                              "T-shirt from H&M", "Groceries from BigBasket",
                              "Headphones from Amazon", "Shoes from Nike",
                              "Smartphone accessories", "Kitchen appliances",
                              "Books from Amazon", "Festival shopping",
                          ], 14),
    ("Other",         50,   1000, [
                              "Household supplies", "Gift for friend's birthday",
                              "Donation to temple", "Courier charges",
                              "Repair work", "Miscellaneous expense",
                          ], 9),
]

# Build weighted flat list of (category, min, max, descriptions).
WEIGHTED = []
for cat, lo, hi, descs, weight in CATEGORY_POOL:
    for _ in range(weight):
        WEIGHTED.append((cat, lo, hi, descs))


def main(user_id: int, count: int, months: int) -> None:
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user is None:
            print(f"No user found with id {user_id}.")
            sys.exit(1)

        today = date.today()
        start = today - timedelta(days=months * 30)
        total_days = (today - start).days

        rows = []
        for _ in range(count):
            cat, lo, hi, descs = random.choice(WEIGHTED)
            amount = round(random.uniform(lo, hi), 2)
            offset = random.randint(0, total_days)
            d = start + timedelta(days=offset)
            description = random.choice(descs)
            rows.append((user_id, amount, cat, d.isoformat(), description))

        try:
            conn.executemany(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        dates = [r[3] for r in rows]
        print(f"Inserted {len(rows)} expenses for user_id={user_id}.")
        print(f"Date range: {min(dates)} to {max(dates)}")
        print("Sample of 5 inserted records:")
        for r in rows[:5]:
            print(f"  {r[3]}  ₹{r[1]:>8.2f}  [{r[2]:<13}]  {r[4]}")
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python seed_expense.py <user_id> <count> <months>")
        sys.exit(1)
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
from decouple import config
from celery import shared_task
from .models import NAV, Scheme, Portfolio
import requests
from datetime import datetime
import traceback

# RapidAPI endpoint
API_URL = f"https://{config('RAPID_API_HOST')}/latest"

# Headers with API Key and Host from .env
HEADERS = {
    "X-RapidAPI-Key": config("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": config("RAPID_API_HOST")
}

# --- Celery Task ---
@shared_task
def update_nav_and_portfolio():
    print(">>> Running NAV update task...")
    try:
        print(">>> Sending request to:", API_URL)
        response = requests.get(API_URL, headers=HEADERS, timeout=60)

        print(">>> Status code:", response.status_code)
        if response.status_code != 200:
            print(">>> Failed to fetch NAVs. Response:", response.text)
            return

        data = response.json()
        print(f">>> Received {len(data)} NAV records")

        today = datetime.today().date()
        updated = 0
        skipped = 0

        for item in data:
            scheme_code = item.get("Scheme_Code")
            nav_value = item.get("Net_Asset_Value")
            date_str = item.get("Date")

            if not (scheme_code and nav_value and date_str):
                skipped += 1
                continue

            try:
                nav_date = datetime.strptime(date_str, "%d-%b-%Y").date()
                scheme = Scheme.objects.get(scheme_code=scheme_code)

                # Update or create NAV entry
                NAV.objects.update_or_create(
                    scheme=scheme,
                    date=nav_date,
                    defaults={"nav": nav_value}
                )

                # Update all portfolios linked to this scheme
                portfolios = Portfolio.objects.filter(scheme=scheme)
                for p in portfolios:
                    p.current_nav = nav_value
                    p.current_value = round(p.units * nav_value, 2)
                    p.save()

                updated += 1

            except Scheme.DoesNotExist:
                skipped += 1
                continue
            except Exception as inner_e:
                print(">>> Error processing scheme:", scheme_code, str(inner_e))
                skipped += 1

        print(f">>> NAV updated: {updated}, Skipped: {skipped}")
        print(">>> NAV and Portfolio update task completed.")

    except Exception as e:
        print(">>> Top-level error in task:")
        print(traceback.format_exc())

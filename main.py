from playwright.sync_api import sync_playwright
import time


def wait_for_available_slot_and_click(page):
    print("Waiting for standard appointment slot...")

    while True:
        try:
            slot_buttons = page.locator("button[data-testid='btn-available-slot']:visible")
            count = slot_buttons.count()

            if count > 0:
                for i in range(count):
                    button = slot_buttons.nth(i)
                    label_span = button.locator("span.sr-only")

                    if label_span.count() > 0:
                        label_text = label_span.inner_text().strip().lower()

                        if "standard appointment" in label_text:
                            button.wait_for(state="visible", timeout=3000)
                            time_text = button.inner_text().strip()
                            button.click()
                            print(f"Clicked standard appointment slot: {time_text}")
                            return

                print("No standard appointment slots available right now.")
            else:
                print("No available slot buttons found.")
        except Exception as e:
            print(f"Error checking for standard slot: {e}")

        print("Retrying in 15s...")
        time.sleep(15)
        page.reload()
        page.wait_for_load_state("networkidle")


def login_and_book():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Login
        page.goto(
            "https://auth.visas-de.tlscontact.com/auth/realms/atlas/protocol/openid-connect/auth?"
            "client_id=tlscitizen&redirect_uri=https%3A%2F%2Fvisas-de.tlscontact.com%2Fen-us%2Fauth-callback"
            "&response_mode=query&response_type=code&scope=openid"
        )
        page.fill("input[name='username']", "muhammadanas1586@gmail.com")
        page.fill("input[name='password']", "Anas@9090")
        page.click("button:has-text('Login')")
        page.wait_for_load_state("networkidle")
        print("Logged in")

        try:
            print("Waiting for country selection...")

            target_p = page.locator("p.whitespace-nowrap", has_text="United Kingdom")
            target_p.wait_for(state="visible", timeout=15000)
            clickable_card = target_p.locator("..").locator("..")
            clickable_card.click()
            print("Clicked card containing 'United Kingdom'")
            page.wait_for_timeout(3000)
        except Exception as e:
            print("Failed to click country card:", e)

        # Step 2: Click "Select"
        select_btn = page.locator("button:has-text('Select')").nth(1)
        select_btn.wait_for(state="visible", timeout=10000)
        select_btn.click()
        page.wait_for_load_state("networkidle")

        # Optional: Try clicking "Continue" link if it appears
        for _ in range(5):  # Retry 5 times
            try:
                continue_btn = page.locator("a:has-text('Continue')")
                if continue_btn.count() > 0 and continue_btn.first.is_visible():
                    continue_btn.first.click()
                    page.wait_for_load_state("networkidle")
                    print("Clicked 'Continue' and moved to next step")
                    break
                else:
                    print("'Continue' button not visible yet. Waiting...")
                    time.sleep(2)
            except Exception as e:
                print("Retry error while looking for 'Continue':", e)

        # Step 3: Wait for and click appointment slot
        wait_for_available_slot_and_click(page)

        # Step 4: Click "Book your appointment"
        try:
            book_btn = page.locator("button:has-text('Book your appointment')")
            book_btn.wait_for(state="visible", timeout=10000)

            while book_btn.is_disabled():
                print("Waiting for 'Book your appointment' button to enable...")
                time.sleep(1)

            book_btn.click()
            print("Clicked 'Book your appointment'")

        except Exception as e:
            print("Could not click 'Book your appointment':", e)

        # Step 5: Detect booking confirmation (redirect or success message)
        print("Waiting for final confirmation or redirects...")
        time.sleep(5)

        try:
            if page.url.endswith("/confirmation") or "/confirmation" in page.url:
                print("Reached confirmation page.")
            elif page.locator("text=Your appointment has been booked").count() > 0:
                print("Appointment confirmed via message.")
            else:
                print("No clear confirmation detected.")
        except Exception as e:
            print("Could not verify confirmation:", e)

        # Step 6: Exit
        time.sleep(5)
        browser.close()
        print("Booking complete. Browser closed. Exiting script.")


# Run it
login_and_book()

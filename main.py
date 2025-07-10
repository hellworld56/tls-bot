from playwright.sync_api import sync_playwright
import time


def wait_for_available_slot_and_click(page):
    print("⏳ Waiting for available slot...")

    while True:
        try:
            # Look for visible buttons with class including 'available'
            slot_btns = page.locator("button[class*='available']:visible")
            if slot_btns.count() > 0:
                slot_btn = slot_btns.first
                slot_btn.wait_for(state="visible", timeout=5000)
                slot_text = slot_btn.inner_text().strip()
                slot_btn.click()
                print(f"✅ Clicked available slot: {slot_text}")
                return
            else:
                print("❌ No available slots found.")
        except Exception as e:
            print("⚠️ Error while checking slots:", e)

        print("🔁 Retrying in 15s...")
        time.sleep(15)
        page.reload()
        page.wait_for_load_state("networkidle")


def click_confirmation_button(page):
    try:
        page.wait_for_timeout(2000)  # allow any modal to appear

        visible_buttons = page.locator("button:visible")
        count = visible_buttons.count()
        print(f"🔍 Found {count} visible button(s).")

        for i in range(count):
            btn = visible_buttons.nth(i)
            try:
                text = btn.inner_text().strip().lower()
                if any(word in text for word in ["confirm", "continue", "ok", "yes", "submit", "accept", "book"]):
                    if not btn.is_disabled():
                        btn.click()
                        print(f"✅ Clicked confirmation button: '{text}'")
                        return
            except:
                continue

        if count >= 2:
            fallback_btn = visible_buttons.nth(1)
            if not fallback_btn.is_disabled():
                fallback_btn.click()
                print("⚠️ Fallback: Clicked second visible button.")
            else:
                print("⚠️ Fallback button was disabled.")
        else:
            print("❌ Not enough buttons found in modal.")
    except Exception as e:
        print("❌ Error during popup confirmation:", e)


def login_and_book():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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
        print("✅ Logged in")

        # Step 2: Click "Select"
        select_btn = page.locator("button:has-text('Select')").nth(1)
        select_btn.wait_for(state="visible", timeout=10000)
        select_btn.click()
        page.wait_for_load_state("networkidle")

        # Step 3: Click "Continue"
        page.locator("a:has-text('Continue')").click()
        page.wait_for_load_state("networkidle")
        print("➡️ Reached appointment calendar page")

        # Step 4: Wait for and click available slot
        wait_for_available_slot_and_click(page)

        # Step 5: Click "Book your appointment"
        try:
            book_btn = page.locator("button:has-text('Book your appointment')")
            book_btn.wait_for(state="visible", timeout=10000)

            while book_btn.is_disabled():
                print("⏳ Waiting for 'Book your appointment' button to enable...")
                time.sleep(1)

            book_btn.click()
            print("🎯 Clicked 'Book your appointment'")

            # Step 6: Handle confirmation popup
            click_confirmation_button(page)

        except Exception as e:
            print("❌ Could not click 'Book your appointment':", e)

        
        # Optional: Wait a few seconds before closing (to allow any final steps to complete)
        print("⏳ Waiting for final confirmation or redirects...")
        time.sleep(10)

        # Then close the browser and exit
        browser.close()
        print("✅ Booking complete. Browser closed. Exiting script.")

        # page.pause()
    

# Run it
# login_and_book()

if __name__ == "__main__":
    login_and_book()

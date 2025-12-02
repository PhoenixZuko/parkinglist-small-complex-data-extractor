import os
import subprocess

def finalize_progress(airport_file="core/airports.txt", log_file="progress.log"):
    # Verifică dacă lista de aeroporturi este goală
    airports_empty = not os.path.exists(airport_file) or os.stat(airport_file).st_size == 0
    log_exists = os.path.exists(log_file) and os.stat(log_file).st_size > 0

    if airports_empty:
        if log_exists:
            print("[✓] All airports processed. Clearing progress log...")
            # Golește logul
            open(log_file, "w", encoding="utf-8").close()

            # Rulează extract_parking_data.py
            print("[⋅] Running extract_parking_data.py ...")
            try:
                subprocess.run(["python", "extract_parking_data.py"], check=True)
                print("[✓] extract_parking_data.py finished successfully.")
            except subprocess.CalledProcessError as e:
                print(f"[❌] Failed to run extract_parking_data.py: {e}")
        else:
            print("[⋅] Log is already empty or doesn't exist. Nothing to clear.")
    else:
        print("[!] Airports still remain. Progress log not cleared.")

if __name__ == "__main__":
    finalize_progress()

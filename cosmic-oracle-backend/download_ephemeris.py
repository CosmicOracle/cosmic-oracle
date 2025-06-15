import os
import urllib.request
from pathlib import Path

def download_ephemeris():
    """Download the Skyfield ephemeris file if it doesn't exist."""
    # Create the directory if it doesn't exist
    data_dir = Path("instance/skyfield-data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Define the URL and local path
    url = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp"
    local_path = data_dir / "de440.bsp"
    
    # Download the file if it doesn't exist
    if not local_path.exists():
        print(f"Downloading ephemeris file to {local_path}...")
        try:
            urllib.request.urlretrieve(url, local_path)
            print("Download completed successfully!")
        except Exception as e:
            print(f"Error downloading ephemeris file: {e}")
    else:
        print(f"Ephemeris file already exists at {local_path}")

if __name__ == "__main__":
    download_ephemeris()

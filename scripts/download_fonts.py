import os
import requests

os.makedirs("fonts", exist_ok=True)

fonts = {
    "Poppins-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",

    "Montserrat-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf",
    "Montserrat-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf",

    "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
    "Roboto-Bold.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf",

    "OpenSans-Regular.ttf": "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf",
    "OpenSans-Bold.ttf": "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Bold.ttf",

    "Lato-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf",
    "Lato-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Bold.ttf",

    "Inter-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/inter/Inter-Regular.ttf",
    "Inter-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/inter/Inter-Bold.ttf",

    "Oswald-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald-Regular.ttf",

    "PlayfairDisplay-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf",

    "Raleway-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/raleway/Raleway-Regular.ttf",

    "Nunito-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/nunito/Nunito-Regular.ttf",

    "Merriweather-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather-Regular.ttf",

    "BebasNeue-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",

    "Anton-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",

    "SourceSansPro-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/sourcesanspro/SourceSansPro-Regular.ttf",
}

for filename, url in fonts.items():
    print(f"Downloading {filename}...")

    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        with open(os.path.join("fonts", filename), "wb") as f:
            f.write(response.content)
        print(f"✓ Saved {filename}")
    else:
        print(f"✗ Failed {filename}")

print("\nAll downloads complete.")
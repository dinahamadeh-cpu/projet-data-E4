import os
import requests


def fetch_data(
    url: str = "https://www.data.gouv.fr/api/1/datasets/r/5f71ba43-afc8-43a0-b306-dafe29940f9c",
    output_path: str = "C:\\Users\\achve\\OneDrive - ESIEE Paris\\Documents\\projet_data\\data\\raw\\effectifs.csv"
) -> None:

    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    headers = {"User-Agent": "Mozilla/5.0 (compatible; DataProjectBot/1.0)"}
    
    print(f"Téléchargement des données depuis : {url}")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"✅ Données enregistrées dans : {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")


if __name__ == "__main__":
    fetch_data()

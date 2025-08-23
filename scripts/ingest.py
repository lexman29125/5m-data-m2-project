import requests, zipfile, os

url = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"
save_path = "/Users/alexfoo/Documents/NTU_DSAI/5m-data-m2-project/assets/"
zip_file = os.path.join(save_path, "brazilian-ecommerce.zip")

# Download file
response = requests.get(url, stream=True)
if response.status_code == 200:
    with open(zip_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded zip to: {zip_file}")
else:
    print("Download failed:", response.status_code)

# Unzip
with zipfile.ZipFile(zip_file, "r") as zip_ref:
    zip_ref.extractall(save_path)

print(f"Files extracted to: {save_path}")
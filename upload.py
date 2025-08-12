"""Gets a video from the internet and uploads it"""

import urllib.request

# from tiktok_uploader.upload import upload_video
from src.tiktok_uploader.upload import upload_video
# URL = "https://raw.githubusercontent.com/wkaisertexas/wkaisertexas.github.io/main/upload.mp4"
FILENAME = "/Users/loctruong/API_tiktok/splits/Construye para SOBREVIVIR a los BRAINROTS OP en Minecraft/Construye para SOBREVIVIR a los BRAINROTS OP en Minecraft_008.mp4"

if __name__ == "__main__":
    # download random video
    # urllib.request.urlretrieve(URL, FILENAME)

    # upload video to TikTok
    upload_video(
        FILENAME,
        description="This is a #xuhuong video I just downloade check it out on @tiktok",
        cookies="cookies.txt",
        # product_id="YOUR_PRODUCT_ID_HERE",
    )
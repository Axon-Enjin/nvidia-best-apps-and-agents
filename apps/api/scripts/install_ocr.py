"""Install pinned Windows OCR binaries by extraction into private development data/. No admin or PATH edits."""
import hashlib
import subprocess
import urllib.request

from sentinel.config import workspace_root
from sentinel.ocr import ENGLISH_SHA256

ROOT = workspace_root() / "data" / "tools"
FILES = {
    "7zr.exe": ("https://github.com/ip7z/7zip/releases/download/26.05/7zr.exe", "9bf582b894dfa665f852d7e9112b02290a1c303c2d95a21fcdc41ffcb03143b7"),
    "7z2605-x64.exe": ("https://github.com/ip7z/7zip/releases/download/26.05/7z2605-x64.exe", "fd99e86f57d8f429ef5ed045bf98315af962e2309b0f1ba87a147a44c71647d0"),
    "tesseract-setup.exe": ("https://github.com/tesseract-ocr/tesseract/releases/download/5.5.3/tesseract-ocr-w64-setup-5.5.3.20260724.exe", "bee9e3434bd94fd65387d9be28cd467a41f61b1275383b55b0f59a1331270ae4"),
}


def verified_download(url, target, digest):
    if not target.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            content = response.read(40*1024*1024+1)
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("Download checksum mismatch; nothing executed.")
        target.write_bytes(content)
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise ValueError("Cached download checksum mismatch.")


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    for name,(url,digest) in FILES.items():
        verified_download(url,ROOT/name,digest)
    subprocess.run([str(ROOT/"7zr.exe"),"x",str(ROOT/"7z2605-x64.exe"),f"-o{ROOT/'sevenzip'}","-y"],check=True,stdout=subprocess.DEVNULL)
    subprocess.run([str(ROOT/"sevenzip/7z.exe"),"x",str(ROOT/"tesseract-setup.exe"),f"-o{ROOT/'tesseract'}","-y"],check=True,stdout=subprocess.DEVNULL)
    verified_download("https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/eng.traineddata",
                      ROOT/"tesseract/tessdata/eng.traineddata",ENGLISH_SHA256)
    subprocess.run([str(ROOT/"tesseract/tesseract.exe"),"--version"],check=True)


if __name__ == "__main__":
    main()

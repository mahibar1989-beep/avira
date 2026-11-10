# Avira Image Studio

A free Streamlit web app for preparing Meesho product photos.

## Features
- Multiple image uploads
- Before/after preview
- EXIF orientation correction
- Conservative brightness, contrast and sharpness controls
- Keep aspect ratio, square-fit or square-center-crop framing
- Resize and export as JPEG or PNG
- Batch ZIP download
- Basic EXIF and possible C2PA-marker inspection

## Important limitations
- This app does **not** remove or conceal C2PA provenance or SynthID.
- The basic C2PA marker scan is not a standards-compliant C2PA verifier.
- SynthID status cannot be determined by this app.
- Re-exporting an image may change file metadata. Do not treat this as a provenance-removal feature.
- Always compare colour, pattern, fabric texture and product details against the actual item before listing.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Free deployment on Streamlit Community Cloud
1. Create a GitHub account and a new **public** repository named `avira-image-studio`.
2. Upload `app.py` and `requirements.txt` to the repository root.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Choose **Create app**, select the repository, branch `main`, and file `app.py`.
5. Deploy. Streamlit will provide a `*.streamlit.app` URL.
6. Open that URL on iPhone Safari and use Share → Add to Home Screen.

Do not upload customer personal information or confidential files. The free host may sleep when unused and has resource limits.

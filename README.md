# Mandate Allocation Calculator

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)

Application for calculating mandate distribution between parties using different methods (Hare, Droop, Saint-Laguë, D'Hondt, Imperiali) with Russian and English language support.

---

## 🚀 Quick Start (Streamlit Cloud)

1. **Fork or clone this repository on GitHub.**
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and log in with GitHub.
3. Click **"New app"** and select your repository.
4. Set the main file: `app.py` and branch (usually `main`).
5. Click **"Deploy"**.
6. In a minute, your app will be available at a public link!

---

## 📦 Repository Contents

- `app.py` — main application code
- `requirements.txt` — dependencies
- `README.md` — this documentation
- `parties.json` — (optional) example data file

---

## 📝 Features

- Russian and English language support (switch in sidebar)
- Results visualization and method explanations
- Export results to Excel
- Input data validation

---

## 🛠️ Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Available Methods

The calculator supports the following mandate allocation methods:
- **Hare Quota** - Simple quota method
- **Droop Quota** - Modified quota method
- **Saint-Laguë** - Divisor method with odd divisors
- **D'Hondt** - Divisor method with natural divisors
- **Imperiali** - Quota method with Imperiali divisor

## Usage

1. Select your preferred language in the sidebar
2. Enter party names and vote counts
3. Specify total number of mandates to distribute
4. Choose allocation method
5. View results with detailed explanations
6. Export results to Excel if needed

---

**Enjoy using the calculator!** 
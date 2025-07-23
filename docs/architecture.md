# System Architecture

## Frontend
- Built with **Streamlit**
- Modular pages: teacher, admin, parent, student, sync
- Uses dynamic layout via `base_ui.py`

## Backend
- Python modules in `/utils/`
- `sheets_api.py` for Google Sheets
- `moodle_api.py` for Moodle sync

## Storage
- Google Sheets (per term or class)
- Moodle DB or REST API (official source)

## Auth
- Role-based logic (teacher, admin, etc.)
- Email/role input (future: OAuth or login system)

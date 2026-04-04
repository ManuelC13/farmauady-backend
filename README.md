## Instalación y configuración

```bash
git clone https://github.com/ManuelC13/farmauady-backend
cd farmauady-backend

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload

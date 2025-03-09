# Air Quality Dataset Dashboard

## Setup Environment - Anaconda
conda create --name main-ds python=3.9 <br>
conda activate main-ds <br>
pip install -r requirements.txt <br>

## Setup Environment - Terminal
mkdir proyek_analisis_data <br>
cd proyek_analisis_data <br>
pipenv install <br>
pipenv shell <br>
pip install -r requirements.txt <br>

## Run Streamlit app
streamlit run dashboard.py <br>

## Notes
Pada script dashboard, apabila ingin menjalankan secara lokal ganti path menjadi nama data saja, tidak perlu folder dashboard. Pada repo ini, diperlukan folder dashboard agar bisa dibaca oleh streamlit.

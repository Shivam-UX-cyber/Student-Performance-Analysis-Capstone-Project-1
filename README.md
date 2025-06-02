# Student-Performance-Analysis-Capstone-Project-1

# Student-Performance-Analysis-Capstone-Project-1

A web application for analyzing student performance using data-driven strategies. Built with Flask, it provides dashboards, visualizations, and insights to help students and educators track academic progress and improve outcomes.

## Features

- User authentication (sign in/out)
- Dashboard with personalized greeting
- Data analysis and summary statistics
- Marks distribution and top students visualization
- Responsive web UI with multiple pages (About, Docs, Support, Learn More)
- Built with Flask, Pandas, Matplotlib, Seaborn

## Project Structure

- `app.py` – Main Flask application with routes and session management
- `analysis.py` – Data loading, summary, and plotting functions
- `templates/` – HTML templates (Jinja2)
- `static/` – Static files (CSS, images)
- `requirements.txt` – Python dependencies

## Getting Started

1. **Clone the repository**
2. **Create a virtual environment**
   ```sh
   python -m venv env
   source env/bin/activate  # or .\env\Scripts\activate on Windows
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the app**
   ```sh
   python app.py
   ```
5. **Open** [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Requirements

See [requirements.txt](requirements.txt) for all dependencies.

## License

MIT License (add your license here)
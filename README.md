# Django Farm Management System

## Overview
This is a Django-based Farm Management System that helps users manage various aspects of an ostrich farm, including families, eggs, sales, expenses, and insights.

## Features
- **Farm Settings:** Manage farm configurations, families, and ostriches.
- **Egg Management:** Track egg production, create batches, and monitor egg status.
- **Chick Management:** Record chick growth and history.
- **Sales Module:** Sell ostriches, chicks, and eggs with invoice generation.
- **Expense Tracking:** Manage food, medical, salary, and other costs.
- **Reporting & Insights:** Generate detailed reports and graphical insights.
- **AI Chat & Feedback:** Use AI to provide recommendations and answer system-related questions.

## Installation
### Prerequisites
Ensure you have Python installed (recommended: Python 3.8 or later).

### Steps
1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd <project-folder>
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the application:**
   Open `http://127.0.0.1:8000/` in your browser.

## Project Structure
```
project-folder/
│── manage.py
│── Track/  # Main Django app
│── templates/  # HTML templates
│── static/  # Static files (CSS, JS, images)
│── requirements.txt  # Dependencies
│── README.md  # Documentation
```

## Requirements
### Dependencies
Below are the main dependencies used in this project:
```
django
numpy
pandas
matplotlib
seaborn
reportlab
llama-cpp-python
```
For a full list, see `requirements.txt`.

## License
MIT License (or any license you choose).

## Contact
For inquiries, reach out at [muhap.ayman0@gmail.com](mailto:muhap.ayman0@gmail.com).

# Graphs

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An end-to-end machine learning workbench for exploring datasets and training classification or regression models with no code.

**[View Live Demo →](https://sankalpvaish.github.io/Django_Graphs/)**

## What it does

1. **Upload a dataset** — CSV files with numeric and categorical columns
2. **Explore visually** — histograms, pie charts, boxplots, correlation matrix
3. **Handle outliers** — click any boxplot to clip extreme values to the mean
4. **Configure preprocessing** — adjust train/test split and choose a feature scaler
5. **Train models** — one click to fit Logistic Regression, Random Forest, SVM, Decision Trees, Naive Bayes or KNN
6. **Compare results** — review metrics, feature importance and run history

## Requirements

- Python 3.8+
- Django 4.1+
- pandas, plotly, scikit-learn, kaleido

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SankalpVaish/Django.git
   cd Django
   ```

2. **Install dependencies**
   ```bash
   pip install django django-bootstrap5 pandas plotly scikit-learn kaleido
   ```

3. **Run migrations**
   ```bash
   cd Graphs
   python manage.py migrate
   ```

4. **Create a user account**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the server**
   ```bash
   python manage.py runserver
   ```

6. **Open your browser** at `http://127.0.0.1:8000`

## Usage

### Getting started

1. Sign in with the account you created
2. Click **Upload CSV** on the Analysis page
3. Choose a file with numeric and categorical columns (e.g., a loan applications dataset with Age, Income, Employment status)

### Exploring your data

1. After upload, select two columns and a chart type to plot them
2. Click **Data Understanding** in the nav to see the full profile
3. Choose your target variable and problem type (Classification or Regression)

### Training a model

1. On the profile page, adjust the **test set size** slider (5–50%)
2. Pick a **feature scaling** method (Min-Max, Standard, Robust, or None)
3. Click any model card at the bottom — training happens instantly
4. Review accuracy/MSE, insights and run history on the results page

### Handling outliers

1. The profile page shows boxplots for every numeric column
2. Click a boxplot to open its outlier analysis page
3. The app clips values beyond 1.5× IQR to the column mean automatically

### Setting preferences

Your preprocessing defaults can be saved in **Preferences** (nav dropdown) so new runs start with your chosen split and scaler.

## Regenerating the demo site

The static snapshot in `docs/` is built with:

```bash
cd Graphs
python build_demo.py
```

This renders every page with a sample dataset and rewrites URLs for GitHub Pages.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Copyright

Copyright © 2026 Sankalp Vaish. All rights reserved.

## Credits

Built by [Sankalp Vaish]

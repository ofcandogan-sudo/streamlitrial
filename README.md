# 📊 Statistics App

A web-based statistical analysis application built with Python and Streamlit.

## Features

- **Data Upload**: Drag-and-drop Excel (.xlsx) or CSV files
- **Data Preview**: View first 5 rows of your dataset
- **Missing Data Handling**: Drop rows or fill with mean/median
- **Statistical Analysis**:
  - Descriptive Statistics (Mean, Median, Mode, Variance, Std Dev)
  - Comparative Analysis (Independent T-test, ANOVA)
  - Correlation Matrix (Pearson, Spearman, Kendall)
- **Interactive Visualizations**: Plotly-powered charts
- **Export Results**: Download as CSV or Excel

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install streamlit pandas numpy scipy plotly openpyxl
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at: **http://localhost:8501**

## Usage

1. **Upload Data**: Use the sidebar to upload an Excel or CSV file
2. **Handle Missing Data**: Choose how to handle missing values
3. **Select Analysis**: Choose from:
   - Descriptive Statistics
   - Comparative Analysis (T-test)
   - Comparative Analysis (ANOVA)
   - Correlation Matrix
4. **Visualize**: View interactive Plotly charts
5. **Export**: Download results as CSV or Excel

## Supported Data Types

- Genomic sequencing results
- Microbiota abundance metrics
- Marketing campaign data
- Any tabular data with samples in rows and features in columns

## Example

```bash
# Clone or navigate to the project
cd statistics-app

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py --server.port 8501
```

## Configuration

You can customize the Streamlit server:

```bash
streamlit run app.py --server.port 8501 --server.address localhost
```

## Project Structure

```
statistics-app/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## License

MIT

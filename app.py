"""
Statistics App - Automated Statistical Analysis Tool
===================================================
A web-based application for uploading Excel/CSV files and performing
statistical analyses with interactive visualizations.

Author: Orchestrator
Created: 2026-03-03
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="Statistics App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0f0f23;
    }
    .stApp {
        background-color: #0f0f23;
    }
    h1, h2, h3 {
        color: #7c3aed !important;
    }
    .stButton>button {
        background-color: #7c3aed;
        color: white;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #6d28d9;
    }
    .stSelectbox, .stMultiSelect {
        background-color: #1e1e3f;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def load_data(uploaded_file):
    """Load data from uploaded Excel or CSV file."""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload .csv or .xlsx files.")
            return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def handle_missing_data(df, method, fill_value=None):
    """Handle missing data based on selected method."""
    if method == "Drop missing values":
        return df.dropna()
    elif method == "Fill with mean":
        return df.fillna(df.mean(numeric_only=True))
    elif method == "Fill with median":
        return df.fillna(df.median(numeric_only=True))
    elif method == "Fill with custom value":
        return df.fillna(fill_value) if fill_value is not None else df
    return df


def calculate_descriptive_stats(df, columns):
    """Calculate descriptive statistics for selected numeric columns."""
    results = {}
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            data = df[col].dropna()
            results[col] = {
                'Count': len(data),
                'Mean': data.mean(),
                'Median': data.median(),
                'Mode': data.mode().iloc[0] if len(data.mode()) > 0 else np.nan,
                'Variance': data.var(),
                'Std Dev': data.std(),
                'Min': data.min(),
                'Max': data.max(),
                'Range': data.max() - data.min(),
                'Skewness': data.skew(),
                'Kurtosis': data.kurtosis()
            }
    return pd.DataFrame(results).T


def perform_ttest(df, group1_col, group2_col):
    """Perform independent t-test between two groups."""
    try:
        group1 = df[group1_col].dropna()
        group2 = df[group2_col].dropna()
        
        if len(group1) < 2 or len(group2) < 2:
            return None, "Insufficient data for t-test (need at least 2 values per group)"
        
        t_stat, p_value = stats.ttest_ind(group1, group2)
        
        result = {
            'T-Statistic': t_stat,
            'P-Value': p_value,
            'Group 1 Mean': group1.mean(),
            'Group 1 Std': group1.std(),
            'Group 2 Mean': group2.mean(),
            'Group 2 Std': group2.std(),
            'Significant (p<0.05)': 'Yes' if p_value < 0.05 else 'No'
        }
        return result, None
    except Exception as e:
        return None, f"Error performing t-test: {str(e)}"


def perform_anova(df, group_col, value_col):
    """Perform one-way ANOVA."""
    try:
        groups = df[group_col].unique()
        group_data = [df[df[group_col] == g][value_col].dropna() for g in groups]
        
        # Filter out empty groups
        group_data = [g for g in group_data if len(g) >= 2]
        
        if len(group_data) < 2:
            return None, "Need at least 2 groups with data for ANOVA"
        
        f_stat, p_value = stats.f_oneway(*group_data)
        
        # Calculate group means
        group_means = df.groupby(group_col)[value_col].agg(['mean', 'std', 'count'])
        
        result = {
            'F-Statistic': f_stat,
            'P-Value': p_value,
            'Significant (p<0.05)': 'Yes' if p_value < 0.05 else 'No',
            'Number of Groups': len(groups)
        }
        
        return result, group_means, None
    except Exception as e:
        return None, None, f"Error performing ANOVA: {str(e)}"


def calculate_correlation(df, columns, method='pearson'):
    """Calculate correlation matrix for selected columns."""
    try:
        numeric_df = df[columns].select_dtypes(include=[np.number])
        if method == 'pearson':
            return numeric_df.corr(method='pearson')
        elif method == 'spearman':
            return numeric_df.corr(method='spearman')
        else:
            return numeric_df.corr(method='kendall')
    except Exception as e:
        st.error(f"Error calculating correlation: {str(e)}")
        return None


def export_to_excel(df):
    """Export dataframe to Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='Results')
    return output.getvalue()


def export_to_csv(df):
    """Export dataframe to CSV bytes."""
    return df.to_csv(index=True).encode('utf-8')


def main():
    """Main application logic."""
    
    # Header
    st.title("📊 Statistics App")
    st.markdown("### Automated Statistical Analysis Tool")
    st.markdown("---")
    
    # Sidebar - File Upload and Settings
    st.sidebar.header("1. Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel or CSV file",
        type=['csv', 'xlsx', 'xls'],
        help="Drag and drop your file here"
    )
    
    # Main content
    if uploaded_file is not None:
        # Load data
        df = load_data(uploaded_file)
        
        if df is not None:
            # Data Preview
            st.sidebar.header("2. Missing Data")
            
            # Show data info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
                st.metric("Missing %", f"{missing_pct:.2f}%")
            
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Handle missing data
            missing_method = st.sidebar.selectbox(
                "Handle Missing Data",
                ["Drop missing values", "Fill with mean", "Fill with median", "Fill with custom value", "Keep as is"],
                index=0
            )
            
            custom_fill = None
            if missing_method == "Fill with custom value":
                custom_fill = st.sidebar.number_input("Custom fill value", value=0)
            
            if missing_method != "Keep as is":
                df = handle_missing_data(df, missing_method, custom_fill)
                st.success(f"Missing data handled: {missing_method}")
            
            # Analysis Section
            st.markdown("---")
            st.subheader("🔬 Statistical Analysis")
            
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Descriptive Statistics", "Comparative Analysis (T-test)", "Comparative Analysis (ANOVA)", "Correlation Matrix"]
            )
            
            # Descriptive Statistics
            if analysis_type == "Descriptive Statistics":
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if numeric_cols:
                    selected_cols = st.multiselect(
                        "Select numeric columns",
                        numeric_cols,
                        default=numeric_cols[:3]
                    )
                    
                    if st.button("Calculate Descriptive Statistics"):
                        with st.spinner("Calculating..."):
                            results = calculate_descriptive_stats(df, selected_cols)
                            
                            st.markdown("#### Results")
                            st.dataframe(results, use_container_width=True)
                            
                            # Visualizations
                            st.markdown("#### Visualizations")
                            
                            # Histograms
                            selected_hist = st.selectbox("Select column for histogram", selected_cols)
                            if selected_hist:
                                fig = px.histogram(
                                    df, 
                                    x=selected_hist,
                                    nbins=30,
                                    title=f"Distribution of {selected_hist}",
                                    color_discrete_sequence=['#7c3aed']
                                )
                                fig.update_layout(
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font_color='white'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Export
                            if st.button("Export Results"):
                                export_format = st.radio("Export format", ["CSV", "Excel"], horizontal=True)
                                if export_format == "CSV":
                                    csv = export_to_csv(results)
                                    st.download_button(
                                        "Download CSV",
                                        csv,
                                        "descriptive_stats.csv",
                                        "text/csv"
                                    )
                                else:
                                    excel = export_to_excel(results)
                                    st.download_button(
                                        "Download Excel",
                                        excel,
                                        "descriptive_stats.xlsx",
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                else:
                    st.warning("No numeric columns found in the data.")
            
            # T-Test
            elif analysis_type == "Comparative Analysis (T-test)":
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if numeric_cols:
                    col1, col2 = st.columns(2)
                    with col1:
                        group1_col = st.selectbox("Select Group 1", numeric_cols, key="g1")
                    with col2:
                        group2_col = st.selectbox("Select Group 2", numeric_cols, key="g2")
                    
                    if st.button("Perform T-Test"):
                        with st.spinner("Performing t-test..."):
                            result, error = perform_ttest(df, group1_col, group2_col)
                            
                            if error:
                                st.error(error)
                            else:
                                st.markdown("#### T-Test Results")
                                
                                # Display results
                                res_df = pd.DataFrame([result])
                                st.dataframe(res_df, use_container_width=True)
                                
                                # Visualization - Box plot
                                combined_df = pd.DataFrame({
                                    'Group 1': df[group1_col],
                                    'Group 2': df[group2_col]
                                })
                                
                                melted = combined_df.melt(var_name='Group', value_name='Value')
                                fig = px.box(
                                    melted,
                                    x='Group',
                                    y='Value',
                                    title=f"Comparison: {group1_col} vs {group2_col}",
                                    color='Group',
                                    color_discrete_sequence=['#7c3aed', '#f59e0b']
                                )
                                fig.update_layout(
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font_color='white'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Interpretation
                                if result['P-Value'] < 0.05:
                                    st.success("✅ Statistically Significant: The difference between groups is significant (p < 0.05)")
                                else:
                                    st.info("ℹ️ Not Significant: No statistically significant difference detected (p ≥ 0.05)")
                                
                                # Export
                                if st.button("Export T-Test Results"):
                                    csv = export_to_csv(res_df)
                                    st.download_button(
                                        "Download CSV",
                                        csv,
                                        "ttest_results.csv",
                                        "text/csv"
                                    )
                else:
                    st.warning("No numeric columns found.")
            
            # ANOVA
            elif analysis_type == "Comparative Analysis (ANOVA)":
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                
                if numeric_cols and categorical_cols:
                    col1, col2 = st.columns(2)
                    with col1:
                        group_col = st.selectbox("Select Grouping Variable (categorical)", categorical_cols)
                    with col2:
                        value_col = st.selectbox("Select Value Variable (numeric)", numeric_cols)
                    
                    if st.button("Perform ANOVA"):
                        with st.spinner("Performing ANOVA..."):
                            result, group_means, error = perform_anova(df, group_col, value_col)
                            
                            if error:
                                st.error(error)
                            else:
                                st.markdown("#### ANOVA Results")
                                
                                res_df = pd.DataFrame([result])
                                st.dataframe(res_df, use_container_width=True)
                                
                                # Group means table
                                st.markdown("#### Group Statistics")
                                st.dataframe(group_means, use_container_width=True)
                                
                                # Visualization - Box plot
                                fig = px.box(
                                    df,
                                    x=group_col,
                                    y=value_col,
                                    title=f"ANOVA: {value_col} by {group_col}",
                                    color=group_col,
                                    color_discrete_sequence=px.colors.qualitative.Set2
                                )
                                fig.update_layout(
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font_color='white'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Interpretation
                                if result['P-Value'] < 0.05:
                                    st.success("✅ Statistically Significant: At least one group differs significantly (p < 0.05)")
                                else:
                                    st.info("ℹ️ Not Significant: No significant difference between groups (p ≥ 0.05)")
                                
                                # Export
                                if st.button("Export ANOVA Results"):
                                    csv = export_to_csv(res_df)
                                    st.download_button(
                                        "Download CSV",
                                        csv,
                                        "anova_results.csv",
                                        "text/csv"
                                    )
                else:
                    st.warning("Need at least one numeric and one categorical column.")
            
            # Correlation
            elif analysis_type == "Correlation Matrix":
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if numeric_cols:
                    selected_corr = st.multiselect(
                        "Select columns for correlation",
                        numeric_cols,
                        default=numeric_cols[:5]
                    )
                    
                    corr_method = st.radio(
                        "Correlation Method",
                        ["Pearson", "Spearman", "Kendall"],
                        horizontal=True
                    )
                    
                    if st.button("Calculate Correlation"):
                        with st.spinner("Calculating correlation..."):
                            corr_matrix = calculate_correlation(df, selected_corr, corr_method.lower())
                            
                            if corr_matrix is not None:
                                st.markdown("#### Correlation Matrix")
                                st.dataframe(corr_matrix.style.background_gradient(cmap='purple', axis=None), use_container_width=True)
                                
                                # Heatmap
                                fig = px.imshow(
                                    corr_matrix,
                                    text_auto='.2f',
                                    title=f"{corr_method} Correlation Matrix",
                                    color_continuous_scale='RdBu_r',
                                    zmin=-1,
                                    zmax=1
                                )
                                fig.update_layout(
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    font_color='white'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Scatter matrix
                                if len(selected_corr) <= 4:
                                    st.markdown("#### Scatter Plot Matrix")
                                    fig2 = px.scatter_matrix(
                                        df[selected_corr],
                                        title="Scatter Plot Matrix",
                                        color_discrete_sequence=['#7c3aed']
                                    )
                                    fig2.update_layout(
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        font_color='white'
                                    )
                                    st.plotly_chart(fig2, use_container_width=True)
                                
                                # Export
                                if st.button("Export Correlation"):
                                    csv = export_to_csv(corr_matrix)
                                    st.download_button(
                                        "Download CSV",
                                        csv,
                                        "correlation_matrix.csv",
                                        "text/csv"
                                    )
                else:
                    st.warning("No numeric columns found.")
    
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        ### Welcome to Statistics App! 👋
        
        **Get started:**
        1. Upload an Excel (.xlsx) or CSV file using the sidebar
        2. Choose how to handle missing data
        3. Select your analysis type
        
        **Supported data types:**
        - Genomic sequencing results
        - Microbiota abundance metrics  
        - Marketing campaign data
        - Any tabular data with samples in rows and features in columns
        
        **Analysis Features:**
        - 📈 Descriptive Statistics (Mean, Median, Mode, Std Dev, Variance)
        - 🔬 Comparative Analysis (T-test, ANOVA)
        - 🔗 Correlation Matrix (Pearson, Spearman, Kendall)
        - 📊 Interactive Visualizations (Box plots, Scatter plots, Histograms)
        - 💾 Export Results to CSV or Excel
        """)
        
        # Sample data option
        if st.button("Load Sample Data"):
            # Create sample marketing data
            np.random.seed(42)
            n = 100
            sample_data = pd.DataFrame({
                'Customer_Age': np.random.randint(18, 70, n),
                'Annual_Income': np.random.normal(50000, 15000, n),
                'Purchase_Frequency': np.random.poisson(5, n),
                'Customer_Segment': np.random.choice(['Premium', 'Standard', 'Basic'], n),
                'Region': np.random.choice(['North', 'South', 'East', 'West'], n),
                'Satisfaction_Score': np.random.uniform(1, 10, n)
            })
            # Add some missing values
            sample_data.loc[np.random.choice(n, 5), 'Annual_Income'] = np.nan
            sample_data.loc[np.random.choice(n, 3), 'Satisfaction_Score'] = np.nan
            
            csv = sample_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Sample Data",
                csv,
                "sample_data.csv",
                "text/csv",
                key="sample-download"
            )
            st.success("Sample data created! Download and upload to test.")


if __name__ == "__main__":
    main()

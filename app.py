import streamlit as st
import pandas as pd
from io import BytesIO

# Set Streamlit page configuration
st.set_page_config(page_title="File Converter & Cleaner")

st.title("File Converter & Cleaner")
st.write("Upload CSV or Excel files, clean data, and convert formats.")

# File uploader for CSV and Excel files
files = st.file_uploader("Upload CSV or Excel Files:", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        file.seek(0)  # Reset file pointer
        ext = file.name.split(".")[-1].lower()  # Extract file extension
        
        # Read file with caching to improve performance
        @st.cache_data
        def load_file(file, ext):
            return pd.read_csv(file) if ext == "csv" else pd.read_excel(file)

        df = load_file(file, ext)

        st.subheader(f"{file.name} - Preview")
        st.dataframe(df.head())

        # Remove Duplicates
        if st.checkbox(f"Remove Duplicates - {file.name}"):
            df = df.drop_duplicates()
            st.success("Duplicates Removed")
            st.dataframe(df.head())

        # Handle Missing Values
        fill_option = st.selectbox(
            f"Handle Missing Values - {file.name}", ["Do Nothing", "Fill with Mean", "Fill with Median", "Fill with Mode"]
        )
        if fill_option != "Do Nothing":
            for col in df.select_dtypes(include=["number"]).columns:
                if fill_option == "Fill with Mean":
                    df[col].fillna(df[col].mean(), inplace=True)
                elif fill_option == "Fill with Median":
                    df[col].fillna(df[col].median(), inplace=True)
                elif fill_option == "Fill with Mode":
                    df[col].fillna(df[col].mode()[0], inplace=True)
            st.success(f"Missing values filled with {fill_option.lower()}")
            st.dataframe(df.head())

        # Select Columns
        selected_columns = st.multiselect(f"Select Columns - {file.name}", df.columns, default=list(df.columns))
        df = df[selected_columns]
        st.dataframe(df.head())

        # Show Chart with Column Selection
        if st.checkbox(f"Show Chart - {file.name}"):
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if numeric_cols:
                chart_cols = st.multiselect(f"Select Numeric Columns for Chart - {file.name}", numeric_cols, default=numeric_cols[:2])
                if chart_cols:
                    st.bar_chart(df[chart_cols])
                else:
                    st.warning("No columns selected for chart.")
            else:
                st.warning("No numeric columns available for chart.")

        # Convert and Download File
        format_choice = st.radio(f"Convert {file.name} to:", ["csv", "excel"], key=file.name)
        
        if st.button(f"Download {file.name} as {format_choice}"):
            output = BytesIO()
            if format_choice == "csv":
                df.to_csv(output, index=False)
                mime = "text/csv"
                new_name = file.name.replace(ext, "csv")
            else:
                df.to_excel(output, index=False, engine="openpyxl")
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file.name.replace(ext, "xlsx")

            output.seek(0)  # Ensure file is read from the beginning
            st.download_button(label=f"Download {new_name}", data=output, file_name=new_name, mime=mime)

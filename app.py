import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Title
st.title("Data Sweeper")

st.write("Transform your files between CSV and Excel with built-in data cleaning and visualization!")

# File Uploader
uploaded_files = st.file_uploader("Upload Files", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[1].lower()

        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                 df = pd.read_excel(file, engine="openpyxl")  # ✅ FIXED ENGINE
            else:
                st.error(f"File type not supported: {file_ext}")
                continue

            # Display file info
            st.write(f"**File Name:** {file.name}")
            st.write(f"**File Type:** {file.type}")
            st.write(f"**File Size:** {file.size / 1024:.2f} KB")

            # Display first 5 rows of the dataframe
            st.write("**Preview of the DataFrame:**")
            st.write(df.head())

            # Data Cleaning Options
            st.subheader(f"Data Cleaning Options for {file.name}:")
            if st.checkbox(f"Clean data for {file.name}"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Remove duplicates from {file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.success("✅ Duplicates removed!")

                with col2:
                    if st.button(f"Remove missing values from {file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns  # ✅ Fixed dtype
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✅ Missing values replaced with column mean.")

            # Choose specific columns to convert
            st.subheader("**Select Columns to Convert:**")
            selected_columns = st.multiselect("Choose columns:", df.columns)

            # Data Visualization
            st.subheader("**Data Visualization:**")
            if st.checkbox(f"Show data visualization for {file.name}"):
                st.bar_chart(df.select_dtypes(include=['number']).iloc[:, :2])  # ✅ Fixed method name

            # Convert file between CSV and Excel
            st.subheader("**Conversion Options:**")
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()

                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    new_filename = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"

                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")  # ✅ Added engine
                    new_filename = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)  # ✅ Ensure correct file download

                st.download_button(
                    label=f"Click here to download {new_filename}",
                    data=buffer,
                    file_name=new_filename,
                    mime=mime_type,
                )

                st.success(f"✅ {file.name} converted to {conversion_type} successfully!")

        except Exception as e:
            st.error(f"⚠️ Error processing {file.name}: {e}")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Histogram + CDF + Probability Plot", layout="centered")
st.title("Histogram + Cumulative Distribution + Probability Plot")

uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx","xls","csv"])

if uploaded_file is not None:
    # Load data
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Preview Data:")
    st.dataframe(df.head())

    # ======================
    # ✅ FILTER (OPSIONAL)
    # ======================
    st.subheader("Filter Data (Opsional)")
    filter_column = st.selectbox("Pilih kolom untuk filter:", ["None"] + list(df.columns))

    df_filtered = df.copy()

    if filter_column != "None":
        unique_vals = sorted(df[filter_column].dropna().unique(), key=lambda x: str(x))
        filter_value = st.selectbox(f"Pilih nilai untuk kolom **{filter_column}**:", unique_vals)
        df_filtered = df[df[filter_column] == filter_value]

    st.write(f"Jumlah data setelah filter: **{len(df_filtered)} baris**")

    # ======================
    # LANJUT KE ANALISIS
    # ======================

    # Column selection
    numeric_cols = df_filtered.select_dtypes(include=["float","int"]).columns
    if len(numeric_cols) == 0:
        st.error("Tidak ada kolom numerik di data (setelah filter).")
    else:
        selected_column = st.selectbox("Select column to analyze", numeric_cols)

        # Bin size
        bins = st.slider("Number of bins", min_value=5, max_value=100, value=30)

        # Log scale option for X-axis
        log_x = st.checkbox("Use logarithmic X-scale (grade)", value=False)

        data = df_filtered[selected_column].dropna()

        # If log X requested, filter non-positive values
        if log_x:
            data_pos = data[data > 0]
            if data_pos.empty:
                st.error("Data tidak memiliki nilai > 0. Tidak bisa memakai skala logaritmik pada sumbu X.")
                st.stop()
            data_for_hist = data_pos
            data_min = data_pos.min()
            data_max = data_pos.max()
            if data_min == data_max:
                bins_array = bins
            else:
                bins_array = np.logspace(np.log10(data_min), np.log10(data_max), bins)
        else:
            data_for_hist = data
            bins_array = bins

        # Histogram + CDF
        st.subheader("Histogram + Cumulative Frequency")
        fig1, ax1 = plt.subplots(figsize=(8,5))
        counts, bin_edges, patches = ax1.hist(data_for_hist, bins=bins_array, alpha=0.6)

        if log_x:
            ax1.set_xscale('log')

        ax1.set_xlabel(selected_column)
        ax1.set_ylabel("Frequency")

        cdf = np.cumsum(counts) / np.sum(counts)
        ax2 = ax1.twinx()
        ax2.plot(bin_edges[1:], cdf * 100, marker='o', linewidth=1)
        ax2.set_ylabel("Cumulative Frequency (%)")
        ax2.grid(False)

        st.pyplot(fig1)

        # Probability Plot
        st.subheader("Probability Plot (Cumulative Probability vs Grade)")
        if log_x:
            x = np.sort(data[data > 0])
        else:
            x = np.sort(data)
        y = np.arange(1, len(x)+1) / len(x) * 100

        fig2, ax3 = plt.subplots(figsize=(7,4))
        ax3.plot(x, y, marker='.', linestyle='-', linewidth=1)
        ax3.set_xlabel(selected_column)
        ax3.set_ylabel("Cumulative Probability (%)")
        ax3.grid(True)

        if log_x:
            ax3.set_xscale('log')

        st.pyplot(fig2)

        st.markdown("**Notes:** Jika memilih skala logaritmik X, semua nilai ≤ 0 akan diabaikan. Bins dibuat secara logaritmik agar histogram merepresentasikan distribusi pada skala log.")

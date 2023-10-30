import streamlit as st
import pandas as pd
from datetime import datetime

# Create DataFrames for raw material data, production tracking, stock-to-product mapping,
# product verification, and work orders
raw_material_data = pd.DataFrame()
production_tracking_data = pd.DataFrame(columns=['Bulk Material Barcode', 'Processed Material', 'Waste Factor'])
stock_to_product_mapping = pd.DataFrame(columns=['Stock Code', 'Product'])
product_verification_data = pd.DataFrame(columns=['Product', 'Associated Raw Material'])
work_orders = pd.DataFrame(columns=['Order ID', 'Product', 'Operator', 'Start Time', 'End Time'])

def main():
    st.title("Production and Work Order Management App")

    # File uploader to allow the user to upload the supplier's spreadsheet
    uploaded_file = st.file_uploader("Upload CSV or XLSX File", type=["csv", "xlsx"])

    global raw_material_data, production_tracking_data, stock_to_product_mapping, product_verification_data, work_orders

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            raw_material_data = pd.read_csv(uploaded_file)
        else:
            raw_material_data = pd.read_excel(uploaded_file, engine="openpyxl")

    st.subheader("Raw Material Data")
    st.dataframe(raw_material_data)

    # Data verification and input form
    st.subheader("Data Verification and Entry")

    barcode = st.text_input("Enter Barcode:")
    manual_entry = st.text_input("Manual Data Entry:")
    product_association = st.text_input("Product Associated:")

    if st.button("Verify and Add Data"):
        # Perform verification logic (e.g., check against existing data, validate format)
        if barcode or manual_entry:
            new_data = pd.DataFrame({'Barcode': [barcode], 'Manual_Entry': [manual_entry]})
            raw_material_data = raw_material_data.append(new_data, ignore_index=True)
            st.success("Data added successfully!")

            if product_association:
                mapping_data = pd.DataFrame({'Stock Code': [barcode], 'Product': [product_association]})
                stock_to_product_mapping = stock_to_product_mapping.append(mapping_data, ignore_index=True)
                st.success("Product association added successfully!")

        else:
            st.warning("Please provide either Barcode or Manual Data Entry.")

    # Production tracking (Stage 1)
    st.subheader("Production Tracking (Stage 1)")

    bulk_material = st.text_input("Bulk Material Barcode:")
    waste_factor = st.number_input("Waste Factor:", min_value=0.0)

    if st.button("Track Production (Stage 1)"):
        # Perform production tracking logic (e.g., calculate processed material and waste)
        if bulk_material and waste_factor is not None:
            processed_material = bulk_material  # Modify this based on your actual logic
            production_tracking_data = production_tracking_data.append({'Bulk Material Barcode': bulk_material, 'Processed Material': processed_material, 'Waste Factor': waste_factor}, ignore_index=True)
            st.success(f"Processed Material: {processed_material}, Waste: {waste_factor}")

    # Display the stock-to-product mapping
    st.subheader("Stock to Product Mapping")
    st.dataframe(stock_to_product_mapping)

    # Manual entry and verification of products
    st.subheader("Product Entry and Verification")

    product_name = st.text_input("Enter Product Name:")
    associated_raw_material = st.text_input("Associated Raw Material Barcode:")

    if st.button("Verify and Add Product"):
        if product_name and associated_raw_material:
            product_verification_data = product_verification_data.append({'Product': product_name, 'Associated Raw Material': associated_raw_material}, ignore_index=True)
            st.success("Product added successfully!")

            # Calculate and check yield
            yield_threshold = 0.8  # Adjust this threshold as needed
            raw_materials_used = raw_material_data[raw_material_data['Barcode'] == associated_raw_material]
            if not raw_materials_used.empty:
                yield_percentage = len(raw_materials_used) / len(production_tracking_data)
                if yield_percentage >= yield_threshold:
                    st.success(f"Yield is within acceptable range: {yield_percentage * 100:.2f}%")
                else:
                    st.error(f"Yield is below the specified threshold: {yield_percentage * 100:.2f}%")
            else:
                st.warning("No matching raw material found for the associated product.")

    # Work order management
    st.subheader("Work Order Management")

    order_id = st.text_input("Order ID:")
    product_for_order = st.text_input("Product for the Order:")
    operator_name = st.text_input("Operator Name:")
    start_time = st.time_input("Start Time:")
    end_time = st.time_input("End Time:")

    if st.button("Issue Work Order"):
        if order_id and product_for_order and operator_name and start_time and end_time:
            # Perform data verification and calculations, update work orders
            if not product_verification_data[
                (product_verification_data['Product'] == product_for_order) &
                (product_verification_data['Associated Raw Material'] == raw_material_data.loc[0, 'Barcode'])
            ].empty:
                work_orders = work_orders.append({'Order ID': order_id, 'Product': product_for_order, 'Operator': operator_name,
                                                  'Start Time': start_time, 'End Time': end_time}, ignore_index=True)
                st.success("Work order issued successfully!")

                # Calculate productivity
                start_datetime = datetime.combine(datetime.today(), start_time)
                end_datetime = datetime.combine(datetime.today(), end_time)
                time_diff = (end_datetime - start_datetime).total_seconds()
                productivity = len(raw_material_data[raw_material_data['Barcode'] == raw_material_data.loc[0, 'Barcode']]) / time_diff
                st.info(f"Productivity: {productivity:.2f} units/second")

            else:
                st.warning("Product not associated with the provided raw material.")

if __name__ == "__main__":
    main()

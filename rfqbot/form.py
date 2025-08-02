# form_component.py
import streamlit as st
import re

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    return re.match(r"^\d{10}$", phone)

def reset_form():
    st.session_state.email_fields = []
    st.session_state.phone_fields = []
    st.rerun()

def contact_form():
    st.subheader("Register Your RFQ Here.")
    
    col1,col2 = st.columns([0.5,0.5])
    with col1: 
        name = st.text_input("Full Name")
    with col2:
        company = st.text_input("Company")

    # Initialize dynamic fields in session state
    if "email_fields" not in st.session_state:
        st.session_state.email_fields = ['']
    if "phone_fields" not in st.session_state:
        st.session_state.phone_fields = ['']

    # # Add buttons to add more fields
    # col1, col2 = st.columns([1, 1])
    # with col1:
    #     if st.button("➕ Add Email"):
    #         st.session_state.email_fields.append("")
    # with col2:
    #     if st.button("➕ Add Phone Number"):
    #         st.session_state.phone_fields.append("")

    # Dynamic Email Inputs
    st.markdown("#### Email Addresses")
    emails = []

    if st.button("➕ Add Email"):
            st.session_state.email_fields.append("")

    for i in range(len(st.session_state.email_fields)):
        email = st.text_input(f"Email {i+1}", key=f"email_{i}")
        emails.append(email)

    # Dynamic Phone Inputs
    st.markdown("#### Phone Numbers")
    phones = []

    if st.button("➕ Add Phone"):
        st.session_state.phone_fields.append("")

    for i in range(len(st.session_state.phone_fields)):
        phone = st.text_input(f"Phone {i+1}", key=f"phone_{i}")
        phones.append(phone)



    uploaded_file = st.file_uploader(
        "Upload a file (PDF, DOCX, Image, etc.)", 
        type=["pdf", "docx", "png", "jpg", "jpeg","csv","xlsx"]
    )

    submitted = st.button("📤 Submit Form")

    if st.button("🔄 Reset Form"):
        reset_form()

    # Validate & return
    if submitted:
        errors = []

        if not name.strip():
            errors.append("❌ Name is required.")
        if not company.strip():
            errors.append("❌ Company cannot be empty.")

        # for i, email in enumerate(emails):
        #     if not is_valid_email(email):
        #         errors.append(f"❌ Email {i+1} is invalid.")
        # for i, phone in enumerate(phones):
        #     if not is_valid_phone(phone):
        #         errors.append(f"❌ Phone {i+1} must be 10 digits.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("✅ Form submitted successfully!")
            st.write("### Form Data")
            st.write(f"**Name:** {name}")
            st.write(f"**Company:** {company}")
            st.write("**Emails:**")
            st.write(emails)
            st.write("**Phones:**")
            st.write(phones)
            if uploaded_file:
                st.write(f"**Uploaded File:** {uploaded_file.name}")
            else:
                st.warning("⚠️ No file uploaded.")
 
        reset_form()
        return {
            "submitted": submitted,
            "name": name,
            "emails": emails,
            "phones": phones,
            "Company": company,
            "file": uploaded_file
        }

form = contact_form()


# if __name__ == 'main':
#     form = contact_form()
    
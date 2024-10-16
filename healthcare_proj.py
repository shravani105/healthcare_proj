import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Healthcare Management System", page_icon=":hospital:", layout="wide")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB connection string
db = client['health_db']
patients_collection = db['patients']

# Apply custom CSS for beige background and other styling
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #f5f5dc;  /* Beige color */
    }
    .css-1v3fvcr {
        background-color: #f5f5dc;
    }
    .css-1d391kg {
        text-align: center;
    }
    .nav-buttons {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    }
    .nav-buttons button {
        margin: 0 10px;
    }
    .centered-heading {
        text-align: center;
        margin-top: 50px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Function to check if a patient exists by both name and contact
def patient_exists(name, contact):
    return patients_collection.find_one({'name': name, 'contact': contact})

# Function to count appointments for a specific date
def count_appointments(date):
    return patients_collection.count_documents({'appointment': str(date)})

# Helper function to add a new patient
def add_patient(name, age, gender, contact, medical_history):
    if not name:
        st.error("Name cannot be empty!")
        return
    if len(contact) != 10 or not contact.isdigit():
        st.error("Contact number must be a valid 10-digit Indian mobile number!")
        return
    if patient_exists(name, contact):
        st.error(f"Record for {name} with contact {contact} already exists!")
    else:
        patient_data = {
            'name': name,
            'age': age,
            'gender': gender,
            'contact': contact,
            'medical_history': medical_history,
            'appointment': None  # Initialize appointment as None
        }
        patients_collection.insert_one(patient_data)
        st.success(f"Patient {name} added successfully!")

# Helper function to view patient records, including appointment details
def view_patients():
    patients = list(patients_collection.find())
    if patients:
        for patient in patients:
            st.write(f"**Name**: {patient['name']}")
            st.write(f"**Age**: {patient['age']}")
            st.write(f"**Gender**: {patient['gender']}")
            st.write(f"**Contact**: {patient['contact']}")
            st.write(f"**Medical History**: {patient['medical_history']}")
            if patient.get('appointment'):
                st.write(f"**Appointment**: {patient['appointment']}")
            else:
                st.write("**Appointment**: No appointment scheduled")
            st.write("---")
    else:
        st.info("No patients found.")

# Helper function to schedule an appointment
def schedule_appointment(name, contact, appointment_date):
    if patient_exists(name, contact):
        if appointment_date < datetime.now().date():
            st.error("Appointment date cannot be in the past.")
            return
        
        if count_appointments(appointment_date) >= 20:
            st.error("Appointment slots for this date are fully booked. Please select another date.")
            return

        patients_collection.update_one(
            {'name': name, 'contact': contact}, 
            {"$set": {'appointment': str(appointment_date)}}
        )
        st.success(f"Appointment scheduled for {name} on {appointment_date}!")
    else:
        st.warning(f"Patient with name {name} and contact {contact} not found!")

# Streamlit UI

# Home page with heading and navigation buttons
def home():
    st.markdown('<h1 class="centered-heading">Healthcare Management System</h1>', unsafe_allow_html=True)
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Add Patient", key='add_patient_btn'):
            st.session_state['page'] = 'add_patient'
    with col2:
        if st.button("Schedule Appointment", key='schedule_appointment_btn'):
            st.session_state['page'] = 'schedule_appointment'
    with col3:
        if st.button("View Patients", key='view_patients_btn'):
            st.session_state['page'] = 'view_patients'

    st.markdown('</div>', unsafe_allow_html=True)

# Add Patient page
def add_patient_page():
    st.subheader("Add New Patient")
    
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact = st.text_input("Contact Information")
    medical_history = st.text_area("Medical History")
    
    if st.button("Add Patient"):
        add_patient(name, age, gender, contact, medical_history)

# View Patients page
def view_patients_page():
    st.subheader("View All Patients")
    view_patients()

# Schedule Appointment page
def schedule_appointment_page():
    st.subheader("Schedule Appointment for Patient")
    
    name = st.text_input("Enter Patient Name")
    contact = st.text_input("Enter Patient Contact Number")
    appointment_date = st.date_input("Select Appointment Date", min_value=datetime.now().date())
    
    if st.button("Schedule Appointment"):
        schedule_appointment(name, contact, appointment_date)

# Determine which page to show
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

if st.session_state['page'] == 'home':
    home()
elif st.session_state['page'] == 'add_patient':
    add_patient_page()
elif st.session_state['page'] == 'view_patients':
    view_patients_page()
elif st.session_state['page'] == 'schedule_appointment':
    schedule_appointment_page()

# Add a "Back to Home" button on other pages
if st.session_state['page'] != 'home':
    if st.button("Back to Home", key='back_home_btn'):
        st.session_state['page'] = 'home'

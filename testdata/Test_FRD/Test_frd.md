
# Hospital Management System
## Functional Requirements Document (FRD)

**Version:** 1.0  
**Date:** 18 November 2026  
**Status:** Draft for Review

---

# 1. Document Control

## 1.1 Purpose
This Functional Requirements Document defines the functional scope, workflows, business rules, actors, data requirements, and acceptance criteria for a Hospital Management System (HMS).

## 1.2 Document Status
Draft baseline for requirements review. Hospital-specific policies, regulatory requirements, integrations, and workflows must be confirmed before implementation.

## 1.3 Assumptions
- The system is a web-based hospital management application.
- The system supports administrative and operational workflows.
- Different users have different access permissions.
- Clinical decisions remain the responsibility of qualified healthcare professionals.
- The system does not independently diagnose patients or prescribe medicines.

# 2. Project Overview

## 2.1 Background
Hospitals manage patient registration, appointments, admissions, clinical records, laboratory tests, pharmacy, billing, and discharge processes.

Many hospitals use separate systems or manual processes, which can result in:
- Duplicate patient records.
- Appointment scheduling conflicts.
- Delayed patient services.
- Incorrect billing.
- Difficulty tracking hospital resources.
- Limited visibility into hospital operations.

The Hospital Management System will provide a unified platform to manage these activities.

## 2.2 Business Objectives
1. Simplify patient registration.
2. Improve appointment scheduling.
3. Manage inpatient and outpatient workflows.
4. Maintain centralized patient records.
5. Improve bed and ward management.
6. Automate billing and payment tracking.
7. Manage pharmacy inventory.
8. Generate operational reports.
9. Improve security and auditability.

## 2.3 Project Scope

### In Scope
- Patient registration and management.
- Appointment scheduling.
- Doctor and department management.
- OPD management.
- IPD management.
- Bed and ward management.
- Clinical documentation.
- Laboratory management.
- Radiology order tracking.
- Pharmacy inventory.
- Billing and invoicing.
- Payment management.
- Patient discharge.
- User and role management.
- Reports and dashboards.

### Out of Scope
- AI-based medical diagnosis.
- Automated treatment recommendations.
- Ambulance fleet management.
- Telemedicine.
- Payroll management.
- Advanced accounting.
- Medical device integrations in the initial release.

# 3. Stakeholders and User Roles

## 3.1 Stakeholders
- Hospital Administrator.
- Doctors.
- Nurses.
- Receptionists.
- Laboratory Technicians.
- Pharmacists.
- Billing Executives.
- Ward Coordinators.
- Patients.
- IT Administrators.

## 3.2 User Roles

### System Administrator
- Manage users.
- Configure roles and permissions.
- Manage hospital settings.
- Manage departments and master data.

### Receptionist
- Register patients.
- Search existing patients.
- Schedule appointments.
- Manage patient check-ins.

### Doctor
- View assigned patient records.
- Record consultation details.
- Add diagnoses.
- Create investigation orders.
- Document treatment and follow-up instructions.

### Nurse
- Record patient observations.
- Update nursing notes.
- Manage assigned ward activities.

### Laboratory Technician
- View investigation orders.
- Update test status.
- Enter laboratory results.

### Pharmacist
- Manage medicine inventory.
- Update medicine stock.
- Dispense medicines.
- Monitor expiry dates.

### Billing Executive
- Generate invoices.
- Record payments.
- Process authorized refunds.
- Generate receipts.

### Patient
- View appointments.
- View permitted medical reports.
- View invoices and payment history.

# 4. High-Level Business Workflow

## 4.1 Patient Journey

1. Patient visits the hospital.
2. Receptionist searches for an existing patient.
3. If the patient is new, a registration record is created.
4. Patient books an appointment or registers as a walk-in.
5. Patient checks in.
6. Doctor performs consultation.
7. Doctor records clinical information.
8. Doctor orders laboratory tests if required.
9. Laboratory technician performs tests and uploads results.
10. Doctor reviews the results.
11. Pharmacy dispenses prescribed medicines where applicable.
12. Billing department generates the invoice.
13. Patient completes payment.
14. Visit is closed.
15. Follow-up appointment is scheduled if required.

## 4.2 Inpatient Workflow

1. Doctor recommends hospital admission.
2. Admission request is created.
3. Ward coordinator checks bed availability.
4. Patient is assigned a bed.
5. Nursing team records observations.
6. Doctor documents treatment and progress.
7. Laboratory and pharmacy services are provided.
8. Billing department tracks hospital charges.
9. Doctor initiates discharge.
10. Final bill is generated.
11. Discharge summary is prepared and authenticated.
12. Bed is marked for cleaning and subsequently made available.

# 5. Functional Requirements

## FR-001: Patient Registration and Management

**Description:**  
The system shall allow authorized users to register and manage patient information.

**Requirements:**
- Generate a unique patient ID.
- Capture patient full name.
- Capture date of birth.
- Capture contact number.
- Capture email address.
- Capture residential address.
- Capture emergency contact details.
- Support patient search.
- Detect potential duplicate patient records.
- Allow authorized users to update patient information.
- Maintain patient history.

**Expected Result:**  
A successfully registered patient receives a unique patient ID.

## FR-002: Appointment Management

**Description:**  
The system shall allow users to schedule and manage appointments.

**Requirements:**
- Search doctors by specialization.
- View doctor availability.
- Book appointments.
- Reschedule appointments.
- Cancel appointments.
- Check in patients.
- Prevent unauthorized double-booking.
- Send appointment notifications.
- Maintain appointment history.

**Appointment Status:**
- Booked
- Confirmed
- Checked-in
- In Consultation
- Completed
- Cancelled
- No-show

## FR-003: Doctor and Department Management

**Requirements:**
- Create doctor profiles.
- Update doctor information.
- Assign doctors to departments.
- Configure consultation schedules.
- Manage doctor availability.
- Maintain doctor specialization.
- Activate or deactivate doctor profiles.

## FR-004: Outpatient Department (OPD)

**Requirements:**
- Create outpatient encounters.
- Link appointments with patient records.
- Record presenting complaints.
- Record medical history.
- Record examination notes.
- Record diagnoses.
- Create investigation orders.
- Record treatment plans.
- Schedule follow-up appointments.
- Maintain consultation history.

## FR-005: Inpatient Department (IPD)

**Requirements:**
- Create admission requests.
- Record admission date and time.
- Assign attending doctors.
- Allocate beds.
- Manage patient transfers.
- Record admission status.
- Maintain inpatient history.
- Track discharge status.

## FR-006: Ward and Bed Management

**Requirements:**
- Create hospital wards.
- Create rooms.
- Register beds.
- Track bed availability.
- Assign beds to admitted patients.
- Transfer patients between beds.
- Block unavailable beds.
- Track bed occupancy.

**Bed Status:**
- Available
- Reserved
- Occupied
- Cleaning
- Blocked
- Out of Service

**Business Rule:**  
The system shall not allocate an occupied or blocked bed to another patient.

## FR-007: Nursing Management

**Requirements:**
- Record patient vital signs.
- Record nursing observations.
- Maintain nursing notes.
- View assigned patients.
- Track nursing activities.
- Maintain observation history.

## FR-008: Laboratory Management

**Requirements:**
- Create laboratory test orders.
- View pending test requests.
- Assign tests to laboratory staff.
- Update test status.
- Enter test results.
- Upload laboratory reports.
- Link reports with patient records.
- Maintain test history.

**Test Status:**
- Ordered
- Sample Collected
- In Progress
- Completed
- Cancelled

## FR-009: Radiology Management

**Requirements:**
- Create radiology orders.
- Record requested imaging procedures.
- Track order status.
- Upload radiology reports.
- Link reports to patient encounters.
- Maintain investigation history.

## FR-010: Pharmacy and Inventory Management

**Requirements:**
- Add medicines to the catalogue.
- Update medicine details.
- Manage medicine stock.
- Record batch numbers.
- Record manufacturing dates.
- Record expiry dates.
- Receive new stock.
- Dispense medicines.
- Track stock transactions.
- Generate low-stock alerts.
- Generate expiry alerts.

**Business Rules:**
- Expired medicines must not be dispensed through normal workflows.
- Stock quantity must be updated after dispensing.
- Stock adjustments must have an audit record.

## FR-011: Billing and Invoice Management

**Requirements:**
- Generate patient invoices.
- Add consultation charges.
- Add laboratory charges.
- Add pharmacy charges.
- Add room and bed charges.
- Add procedure charges.
- Apply authorized discounts.
- Calculate taxes according to configured rules.
- Generate invoice numbers.
- View billing history.

## FR-012: Payment Management

**Requirements:**
- Record cash payments.
- Record card payments.
- Record bank transfers.
- Support approved online payment gateways.
- Support partial payments.
- Track outstanding balances.
- Generate payment receipts.
- Process authorized refunds.
- Maintain payment history.

## FR-013: Patient Discharge Management

**Requirements:**
- Initiate discharge requests.
- Record discharge date and time.
- Prepare discharge summaries.
- Record follow-up instructions.
- Verify mandatory clearance steps.
- Generate final invoices.
- Update admission status.
- Release beds according to hospital cleaning policy.

## FR-014: Patient Portal

**Requirements:**
- Patient login.
- View personal profile.
- View upcoming appointments.
- View permitted medical reports.
- View invoices.
- View payment history.
- Download permitted documents.

## FR-015: Notification Management

**Requirements:**
- Send appointment confirmation.
- Send appointment reminders.
- Send cancellation notifications.
- Send payment receipts.
- Notify patients when reports are available.
- Maintain notification delivery logs.

**Supported Channels:**
- Email
- SMS
- In-app notifications

## FR-016: User and Role Management

**Requirements:**
- Create user accounts.
- Update user information.
- Assign roles.
- Configure permissions.
- Activate and deactivate accounts.
- Reset passwords.
- Maintain user activity history.
- Enforce role-based access control.

## FR-017: Audit Trail Management

**Requirements:**
- Record user login activity.
- Record patient record modifications.
- Record billing changes.
- Record payment changes.
- Record medicine stock changes.
- Record bed allocation changes.
- Record permission changes.
- Store timestamps and user information.

## FR-018: Dashboard and Reports

**Requirements:**
- Display total registered patients.
- Display daily appointments.
- Display total admissions.
- Display available beds.
- Display occupied beds.
- Display completed consultations.
- Display pending laboratory tests.
- Display pharmacy stock.
- Display daily revenue.
- Display outstanding payments.
- Generate date-wise reports.
- Export authorized reports.

# 6. Business Rules

| Rule ID | Business Rule |
|---|---|
| BR-001 | Every patient must have a unique patient ID. |
| BR-002 | A patient can have multiple appointments. |
| BR-003 | A doctor cannot have conflicting appointments unless an authorized override is used. |
| BR-004 | A bed cannot be allocated to multiple active admissions. |
| BR-005 | Only authorized doctors can authenticate clinical documentation. |
| BR-006 | Financial adjustments require authorization. |
| BR-007 | Discharge requires mandatory clearances. |
| BR-008 | Expired medicine cannot be routinely dispensed. |
| BR-009 | All critical user activities must be auditable. |
| BR-010 | Users can access only authorized modules and records. |

# 7. Data Requirements

## 7.1 Patient Table
- patient_id
- first_name
- last_name
- date_of_birth
- contact_number
- email
- address
- emergency_contact
- created_at
- updated_at

## 7.2 Doctor Table
- doctor_id
- doctor_name
- specialization
- department_id
- contact_number
- consultation_fee
- availability_status

## 7.3 Appointment Table
- appointment_id
- patient_id
- doctor_id
- appointment_date
- appointment_time
- appointment_status

## 7.4 Admission Table
- admission_id
- patient_id
- doctor_id
- ward_id
- bed_id
- admission_date
- discharge_date
- admission_status

## 7.5 Medicine Table
- medicine_id
- medicine_name
- batch_number
- quantity
- expiry_date
- unit_price

## 7.6 Invoice Table
- invoice_id
- patient_id
- total_amount
- discount
- tax
- payable_amount
- payment_status
- invoice_date

## 7.7 Payment Table
- payment_id
- invoice_id
- payment_mode
- payment_amount
- transaction_reference
- payment_date
- payment_status

# 8. Non-Functional Requirements

## NFR-001: Security
- Secure authentication.
- Role-based authorization.
- Encrypted network communication.
- Secure password storage.
- Session management.
- Protection against common web vulnerabilities.

## NFR-002: Performance
- Common read operations should complete within 3 seconds under agreed normal load.
- Appointment search should complete within 3 seconds.
- Standard reports should complete within 10 seconds for agreed data volumes.

## NFR-003: Availability
- The application should support agreed business-hour availability.
- Backup and recovery procedures must be implemented.
- Recovery time and recovery point objectives must be defined.

## NFR-004: Scalability
- Support increasing patient records.
- Support additional hospital departments.
- Support increasing concurrent users.

## NFR-005: Usability
- Simple user interface.
- Responsive design.
- Clear error messages.
- Consistent navigation.
- Accessible form controls.

## NFR-006: Data Privacy
- Protect patient information.
- Restrict access to sensitive records.
- Maintain audit logs.
- Follow applicable healthcare privacy regulations.

## NFR-007: Maintainability
- Structured application logs.
- Documented APIs.
- Health checks.
- Automated regression tests.
- Environment-based configuration.

# 9. External Integrations

The system may integrate with:

1. SMS Gateway.
2. Email Service.
3. Payment Gateway.
4. Laboratory Information System (LIS).
5. Picture Archiving and Communication System (PACS).
6. Accounting Software.
7. Identity Provider / SSO.

Each integration must define authentication, data formats, error handling, retries and reconciliation.

# 10. Error Handling and Validation

| Scenario | Expected Behavior |
|---|---|
| Duplicate patient registration | Show potential duplicate warning. |
| Invalid phone number | Display validation message. |
| Appointment slot unavailable | Prevent booking. |
| Bed already occupied | Prevent bed allocation. |
| Insufficient medicine stock | Prevent normal dispensing. |
| Expired medicine | Block routine dispensing. |
| Payment failure | Show failure or pending status. |
| Unauthorized access | Deny access and log event. |
| Missing mandatory fields | Display field-level errors. |
| Database unavailable | Show a meaningful error without exposing internal details. |

# 11. Acceptance Criteria

## AC-001: Patient Registration
Given an authorized receptionist, when valid patient information is submitted, then the system should create a patient record with a unique patient ID.

## AC-002: Appointment Booking
Given an available doctor slot, when a receptionist books an appointment, then the system should create the appointment successfully.

## AC-003: Duplicate Appointment Prevention
Given an already-booked doctor slot, when another user attempts to book the same slot, then the system should prevent double-booking unless an authorized override applies.

## AC-004: Bed Allocation
Given an available bed, when a patient admission is created, then the system should allocate the bed and update its status to Occupied.

## AC-005: Laboratory Management
Given a valid laboratory order, when an authorized technician enters the result, then the result should be linked to the correct patient and encounter.

## AC-006: Pharmacy Management
Given available medicine stock, when a pharmacist dispenses medicine, then the system should update the stock quantity correctly.

## AC-007: Billing
Given configured billable services, when an invoice is generated, then the system should calculate the correct total amount.

## AC-008: Payment
Given a valid invoice, when a successful payment is recorded, then the system should update the outstanding balance and generate a receipt.

## AC-009: Discharge
Given all mandatory discharge clearances are complete, when an authorized clinician finalizes discharge, then the system should save discharge documentation and update the bed status according to policy.

## AC-010: Authorization
Given a user without the required permission, when the user accesses a restricted module, then the system should deny access and record the security event.

# 12. QA and Testing Considerations

## 12.1 Testing Types
- Functional Testing.
- UI Testing.
- API Testing.
- Database Testing.
- Integration Testing.
- Security Testing.
- Performance Testing.
- Regression Testing.
- User Acceptance Testing.

## 12.2 High-Priority End-to-End Scenarios

### Scenario 1: Complete OPD Workflow
1. Register a new patient.
2. Book a doctor appointment.
3. Check in the patient.
4. Complete consultation.
5. Create laboratory order.
6. Enter investigation result.
7. Generate invoice.
8. Record payment.
9. Close the visit.

### Scenario 2: Complete IPD Workflow
1. Register a patient.
2. Create admission request.
3. Allocate bed.
4. Record nursing observations.
5. Transfer patient to another ward.
6. Generate service charges.
7. Complete discharge.
8. Generate final bill.
9. Release bed according to policy.

### Scenario 3: Pharmacy Workflow
1. Add medicine to inventory.
2. Receive stock.
3. Record batch and expiry date.
4. Dispense medicine.
5. Verify stock decrement.
6. Verify low-stock alert.

### Scenario 4: Security Workflow
1. Login as receptionist.
2. Attempt to access administrator functionality.
3. Verify access is denied.
4. Verify security audit entry.

## 12.3 Test Data Requirements
- New patient records.
- Existing patient records.
- Duplicate patient details.
- Multiple doctor profiles.
- Available and unavailable appointment slots.
- Available and occupied beds.
- Valid and expired medicines.
- Successful and failed payments.
- Users with different roles.

Use synthetic patient data in testing environments.

# 13. Risks and Dependencies

## 13.1 Risks
- Duplicate patient records.
- Unauthorized access to medical records.
- Incorrect billing calculations.
- Bed allocation conflicts.
- External integration failures.
- Incomplete migration data.
- Incorrect inventory updates.

## 13.2 Dependencies
- Approved hospital workflows.
- Doctor and department master data.
- Medicine catalogue.
- Hospital tariff configuration.
- Payment gateway configuration.
- SMS and email gateway access.
- Security and privacy policies.

# 14. Open Questions

1. Is this application for a single hospital or a hospital chain?
2. Which country and regulatory framework will apply?
3. Is a patient mobile application required?
4. Which payment gateways should be integrated?
5. Is insurance claim management required?
6. Should the system support multiple languages?
7. What is the expected number of concurrent users?
8. Which external laboratory systems need integration?
9. Is online appointment booking required?
10. What are the hospital's backup and recovery requirements?

# 15. Approval and Sign-Off

The FRD must be reviewed and approved by:

| Role | Approval Status |
|---|---|
| Product Owner | Pending |
| Hospital Administrator | Pending |
| Clinical Representative | Pending |
| IT/Security Representative | Pending |
| QA Lead | Pending |

**End of Document**

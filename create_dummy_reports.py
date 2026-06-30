#!/usr/bin/env python3
"""
Create dummy dormitory assessment and academic report for testing
"""

import frappe
from frappe.utils import today, add_days

def create_dummy_data():
    frappe.connect(site='erp.gcihs.local')
    frappe.flags.in_test = False
    
    # Use existing student
    student_id = "12108-002"  # Miriam Victoria ADAMS-MILWOOD
    student_name = "Miriam Victoria ADAMS-MILWOOD"
    
    # Check if student exists
    if not frappe.db.exists("Student", student_id):
        print(f"❌ Student {student_id} not found")
        return
    
    print(f"✓ Using student: {student_name} ({student_id})")
    
    # Use current academic year and term
    academic_year = "2024-25"
    term = "2024-25 (TERM 2)"
    
    # Create or get house
    house_name = "Victoria House"
    if not frappe.db.exists("House", house_name):
        house_doc = frappe.get_doc({
            "doctype": "House",
            "house": house_name
        })
        house_doc.insert()
        frappe.db.commit()
        print(f"✓ Created house: {house_name}")
    else:
        print(f"✓ Using existing house: {house_name}")
    
    # Create or get class
    class_name = "Form 9S"
    if not frappe.db.exists("Student Group", class_name):
        class_doc = frappe.get_doc({
            "doctype": "Student Group",
            "student_group_name": class_name,
            "group_based_on": "Batch"
        })
        class_doc.insert()
        frappe.db.commit()
        print(f"✓ Created class: {class_name}")
    else:
        print(f"✓ Using existing class: {class_name}")
    
    # Check if dormitory assessment already exists
    existing_dorm = frappe.db.exists({
        "doctype": "Dormitory Assessment",
        "student": student_id,
        "academic_year": academic_year,
        "term": term
    })
    
    if existing_dorm:
        print(f"⚠ Dormitory Assessment already exists: {existing_dorm}")
        dorm_doc = frappe.get_doc("Dormitory Assessment", existing_dorm)
    else:
        # Create Dormitory Assessment
        dorm_doc = frappe.get_doc({
            "doctype": "Dormitory Assessment",
            "student": student_id,
            "student_name": student_name,
            "academic_year": academic_year,
            "term": term,
            "class_section": class_name,
            "programme": "SCIENCE",
            "house": house_name,
            "responsible": "5",
            "reliable": "4",
            "cooperation": "5",
            "concern": "4",
            "obedience": "5",
            "tidiness": "3",
            "timeliness": "4",
            "relation": "5",
            "maturity": "4",
            "respectful": "5",
            "character": "5",
            "house_staff_remarks": "Miriam is an excellent student who demonstrates strong leadership qualities and maintains high standards of conduct. She is reliable, responsible, and always willing to help her peers. Her Christian character is exemplary and serves as a positive influence in the dormitory.",
            "principal_comments": "Outstanding performance in dormitory life. Miriam exhibits maturity beyond her years and is a role model for other students. Keep up the excellent work!"
        })
        dorm_doc.insert()
        print(f"✓ Created Dormitory Assessment: {dorm_doc.name}")
        
        # Submit the assessment
        dorm_doc.submit()
        frappe.db.commit()
        print(f"✓ Submitted Dormitory Assessment")
    
    # Check if academic report already exists
    existing_report = frappe.db.exists({
        "doctype": "GCIHS Academic Reports",
        "admission_no": student_id,
        "academic_year": academic_year,
        "term": term,
        "report_mode": "Individual Report"
    })
    
    if existing_report:
        print(f"⚠ Academic Report already exists: {existing_report}")
        report_doc = frappe.get_doc("GCIHS Academic Reports", existing_report)
    else:
        # Create Academic Report
        report_doc = frappe.get_doc({
            "doctype": "GCIHS Academic Reports",
            "report_mode": "Individual Report",
            "select_school": "WASSCE",
            "admission_no": student_id,
            "student_name": student_name,
            "academic_year": academic_year,
            "term": term,
            "class_name": class_name,
            "house": house_name,
            "include_dormitory_assessment": 1,
            "next_term_begins": add_days(today(), 30),
            "vacation_date": add_days(today(), 7),
            "class_avg_mark": "75.5",
            "promoted_to": "Form 10",
            "gpa": "3.5"
        })
        
        # Add sample conduct assessments
        conduct_items = [
            {"consideration": "Punctuality", "score": "5", "interpretation": "Excellent"},
            {"consideration": "Honesty", "score": "5", "interpretation": "Excellent"},
            {"consideration": "Cooperation", "score": "4", "interpretation": "Very Good"},
            {"consideration": "Respect for Authority", "score": "5", "interpretation": "Excellent"},
            {"consideration": "Initiative", "score": "4", "interpretation": "Very Good"}
        ]
        
        for item in conduct_items:
            report_doc.append("conduct_assessments", item)
        
        # Add sample subject assessments
        subjects = [
            {"subject_name": "Mathematics", "class_score": "38", "exam_score": "52", "total_score": "90", "grade": "A*"},
            {"subject_name": "English Language", "class_score": "35", "exam_score": "48", "total_score": "83", "grade": "A"},
            {"subject_name": "Integrated Science", "class_score": "37", "exam_score": "50", "total_score": "87", "grade": "A"},
            {"subject_name": "Social Studies", "class_score": "36", "exam_score": "45", "total_score": "81", "grade": "A"},
            {"subject_name": "Religious & Moral Education", "class_score": "39", "exam_score": "53", "total_score": "92", "grade": "A*"},
            {"subject_name": "French", "class_score": "33", "exam_score": "42", "total_score": "75", "grade": "B+"},
            {"subject_name": "Information Technology", "class_score": "38", "exam_score": "50", "total_score": "88", "grade": "A"}
        ]
        
        for subject in subjects:
            report_doc.append("assessments_table", subject)
        
        report_doc.insert()
        frappe.db.commit()
        print(f"✓ Created Academic Report: {report_doc.name}")
        
        # The dormitory assessment should be auto-linked
        if report_doc.dormitory_assessment_link:
            print(f"✓ Dormitory Assessment auto-linked: {report_doc.dormitory_assessment_link}")
        else:
            print(f"⚠ Dormitory Assessment not auto-linked, linking manually...")
            report_doc.dormitory_assessment_link = dorm_doc.name
            report_doc.save()
            frappe.db.commit()
            print(f"✓ Manually linked Dormitory Assessment")
    
    print("\n" + "="*60)
    print("✅ DUMMY DATA CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📋 Student: {student_name} ({student_id})")
    print(f"📚 Class: {class_name}")
    print(f"🏠 House: {house_name}")
    print(f"📅 Academic Year: {academic_year}")
    print(f"📆 Term: {term}")
    print(f"\n🔗 Dormitory Assessment: {dorm_doc.name}")
    print(f"🔗 Academic Report: {report_doc.name}")
    print("\n📄 To view the report with dormitory assessment:")
    print(f"   Navigate to: GCIHS > GCIHS Academic Reports > {report_doc.name}")
    print(f"   Click: Menu > Print > GCIHS Academic Report Card")
    print("\n" + "="*60)
    
    frappe.db.commit()
    frappe.destroy()

if __name__ == "__main__":
    create_dummy_data()

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from students.models import StudentProfile
from courses.models import Course
from admissions.models import AdmissionApplication, ApplicationTimeline
from documents.models import Document
from enrollments.models import Enrollment
from notifications.models import Notification
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial demo data for College Admission and Student Enrollment Management System'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting database seed...'))

        # 1. Create or update Admin User
        admin, created = User.objects.get_or_create(
            email='admin@college.edu',
            defaults={
                'username': 'admin',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '9876543200'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin created: admin@college.edu / admin123'))
        else:
            admin.role = 'ADMIN'
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password('admin123')
            admin.save()

        # 2. Courses
        courses_data = [
            {
                'course_name': 'BCA',
                'course_code': 'BCA',
                'department': 'Computer Applications',
                'description': 'Bachelor of Computer Applications - Comprehensive 3-year program focusing on software development, web systems, database design, and cloud applications.',
                'duration': '3 Years',
                'total_seats': 60,
                'available_seats': 42,
                'eligibility': '10+2 with Mathematics/Computer Science/Information Technology with minimum 50% aggregate marks.',
                'fees': 45000.00,
                'status': 'Active',
            },
            {
                'course_name': 'B.Sc Computer Science',
                'course_code': 'BSC-CS',
                'department': 'Computer Science',
                'description': 'Bachelor of Science in Computer Science - Strong foundation in computer algorithms, data structures, AI/ML, and computational theory.',
                'duration': '3 Years',
                'total_seats': 60,
                'available_seats': 38,
                'eligibility': '10+2 with Physics, Chemistry, and Mathematics with minimum 55% aggregate marks.',
                'fees': 50000.00,
                'status': 'Active',
            },
            {
                'course_name': 'B.Com',
                'course_code': 'BCOM',
                'department': 'Commerce',
                'description': 'Bachelor of Commerce - In-depth coverage of accounting, taxation, financial management, auditing, and corporate governance.',
                'duration': '3 Years',
                'total_seats': 60,
                'available_seats': 45,
                'eligibility': '10+2 Commerce/Science/Arts with minimum 45% aggregate marks.',
                'fees': 35000.00,
                'status': 'Active',
            },
            {
                'course_name': 'BBA',
                'course_code': 'BBA',
                'department': 'Business Administration',
                'description': 'Bachelor of Business Administration - Focus on modern management, marketing strategies, human resource leadership, and business analytics.',
                'duration': '3 Years',
                'total_seats': 60,
                'available_seats': 48,
                'eligibility': '10+2 in any stream with minimum 50% aggregate marks.',
                'fees': 40000.00,
                'status': 'Active',
            },
            {
                'course_name': 'B.Sc Mathematics',
                'course_code': 'BSC-MATH',
                'department': 'Mathematics',
                'description': 'Bachelor of Science in Mathematics - Rigorous mathematical analysis, abstract algebra, differential equations, and statistics.',
                'duration': '3 Years',
                'total_seats': 50,
                'available_seats': 35,
                'eligibility': '10+2 with Mathematics with minimum 55% aggregate marks.',
                'fees': 30000.00,
                'status': 'Active',
            },
            {
                'course_name': 'B.A English',
                'course_code': 'BA-ENG',
                'department': 'Arts',
                'description': 'Bachelor of Arts in English - British, American, and World Literature, creative writing, linguistics, and communicative journalism.',
                'duration': '3 Years',
                'total_seats': 50,
                'available_seats': 40,
                'eligibility': '10+2 in any stream with minimum 45% marks in English.',
                'fees': 25000.00,
                'status': 'Active',
            },
        ]

        course_objects = {}
        for cdata in courses_data:
            course, _ = Course.objects.update_or_create(
                course_code=cdata['course_code'],
                defaults=cdata
            )
            course_objects[course.course_code] = course
        self.stdout.write(self.style.SUCCESS(f'Created/Updated {len(course_objects)} courses.'))

        # 3. Create Primary Demo Student: Rahul Sharma
        rahul, r_created = User.objects.get_or_create(
            email='rahul@gmail.com',
            defaults={
                'username': 'rahul_sharma',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'role': 'STUDENT',
                'phone_number': '9876543210'
            }
        )
        rahul.set_password('student123')
        rahul.save()

        rahul_profile, _ = StudentProfile.objects.get_or_create(
            user=rahul,
            defaults={
                'date_of_birth': datetime.date(2005, 6, 15),
                'gender': 'Male',
                'address': '123, Green Park, New Delhi',
                'city': 'New Delhi',
                'state': 'Delhi',
                'pincode': '110016',
                'father_name': 'Amit Sharma',
                'mother_name': 'Neha Sharma',
                'guardian_contact': '9876543299',
                'previous_institution': 'Delhi Public School, R.K. Puram',
                'qualification': '12th Standard / CBSE',
                'board_university': 'CBSE',
                'passing_year': 2024,
                'percentage_cgpa': 88.50,
            }
        )

        # 4. Rahul's Applications
        # Application 1: Enrolled in BCA (CAE202500123)
        app_bca, _ = AdmissionApplication.objects.update_or_create(
            application_id='CAE202500123',
            defaults={
                'student': rahul,
                'course': course_objects['BCA'],
                'status': 'Enrolled',
                'current_step': 5,
                'full_name': 'Rahul Sharma',
                'email': 'rahul@gmail.com',
                'phone_number': '9876543210',
                'date_of_birth': datetime.date(2005, 6, 15),
                'gender': 'Male',
                'address': '123, Green Park, New Delhi',
                'father_name': 'Amit Sharma',
                'mother_name': 'Neha Sharma',
                'guardian_contact': '9876543299',
                'previous_institution': 'Delhi Public School, R.K. Puram',
                'qualification': '12th Standard / CBSE',
                'board_university': 'CBSE',
                'passing_year': 2024,
                'percentage_cgpa': 88.50,
                'admin_remarks': 'Excellent academic record. Verified original documents and confirmed enrollment.',
                'reviewed_by': admin,
                'reviewed_at': timezone.now() - datetime.timedelta(days=2),
                'submitted_at': timezone.now() - datetime.timedelta(days=8),
            }
        )

        # Timelines for App 1
        ApplicationTimeline.objects.get_or_create(
            application=app_bca,
            status='Submitted',
            defaults={
                'title': 'Application Submitted',
                'description': 'Student submitted application form online.',
                'performed_by': rahul
            }
        )
        ApplicationTimeline.objects.get_or_create(
            application=app_bca,
            status='Document Verification',
            defaults={
                'title': 'Document Verification',
                'description': 'Academic certificates and ID proofs verified by admissions team.',
                'performed_by': admin
            }
        )
        ApplicationTimeline.objects.get_or_create(
            application=app_bca,
            status='Approved',
            defaults={
                'title': 'Admission Approved',
                'description': 'Admission committee granted approval for BCA program.',
                'performed_by': admin
            }
        )
        ApplicationTimeline.objects.get_or_create(
            application=app_bca,
            status='Enrolled',
            defaults={
                'title': 'Enrollment Completed',
                'description': 'Student confirmed enrollment and roll number was allocated.',
                'performed_by': rahul
            }
        )

        # Enrollment for App 1
        enr_rahul, _ = Enrollment.objects.update_or_create(
            enrollment_id='ENR202500123',
            defaults={
                'student': rahul,
                'application': app_bca,
                'course': course_objects['BCA'],
                'academic_year': '2025-2026',
                'status': 'Confirmed',
                'roll_number': 'BCA-2025-001',
                'remarks': 'Seat allocated under General Merit list.'
            }
        )

        # Application 2 for Rahul: Rejected application for B.Sc Computer Science
        app_bsc, _ = AdmissionApplication.objects.update_or_create(
            application_id='CAE202500124',
            defaults={
                'student': rahul,
                'course': course_objects['BSC-CS'],
                'status': 'Rejected',
                'current_step': 5,
                'full_name': 'Rahul Sharma',
                'email': 'rahul@gmail.com',
                'phone_number': '9876543210',
                'date_of_birth': datetime.date(2005, 6, 15),
                'gender': 'Male',
                'address': '123, Green Park, New Delhi',
                'father_name': 'Amit Sharma',
                'mother_name': 'Neha Sharma',
                'guardian_contact': '9876543299',
                'previous_institution': 'Delhi Public School, R.K. Puram',
                'qualification': '12th Standard / CBSE',
                'board_university': 'CBSE',
                'passing_year': 2024,
                'percentage_cgpa': 88.50,
                'rejection_reason': 'Candidate opted to enroll in BCA program (Primary Choice). Secondary application closed.',
                'admin_remarks': 'Candidate opted for primary offer in BCA.',
                'reviewed_by': admin,
                'reviewed_at': timezone.now() - datetime.timedelta(days=1),
                'submitted_at': timezone.now() - datetime.timedelta(days=7),
            }
        )

        # 5. Documents for Rahul
        doc_sample_content = b"%PDF-1.4 sample college admission document demonstration content."
        docs_to_create = [
            ('ID_PROOF', 'Aadhaar_Card_Rahul.pdf', 'Verified'),
            ('PHOTO', 'Passport_Photo_Rahul.jpg', 'Verified'),
            ('ACADEMIC_12', '12th_CBSE_Marksheet.pdf', 'Verified'),
            ('TRANSFER_CERT', 'School_Transfer_Certificate.pdf', 'Verified'),
        ]
        for dtype, fname, dstat in docs_to_create:
            doc, _ = Document.objects.get_or_create(
                student=rahul,
                document_type=dtype,
                defaults={
                    'application': app_bca,
                    'file_name': fname,
                    'status': dstat,
                    'file_size': '450 KB',
                    'verified_by': admin if dstat == 'Verified' else None,
                    'verified_at': timezone.now() if dstat == 'Verified' else None,
                }
            )
            if not doc.file:
                doc.file.save(fname, ContentFile(doc_sample_content), save=True)

        # 6. Notifications for Rahul
        Notification.objects.get_or_create(
            recipient=rahul,
            title='Enrollment Confirmed!',
            defaults={
                'message': 'Congratulations! Your enrollment in BCA has been confirmed. Your roll number is BCA-2025-001.',
                'link': '/enrollments/confirmation/CAE202500123/',
                'notification_type': 'SUCCESS',
            }
        )
        Notification.objects.get_or_create(
            recipient=rahul,
            title='Documents Verified',
            defaults={
                'message': 'All your submitted academic and ID documents have been successfully verified.',
                'link': '/documents/',
                'notification_type': 'INFO',
            }
        )
        Notification.objects.get_or_create(
            recipient=rahul,
            title='Admission Approved for BCA',
            defaults={
                'message': 'Your admission application CAE202500123 has been approved. Please proceed to complete your enrollment.',
                'link': '/admissions/CAE202500123/',
                'notification_type': 'SUCCESS',
            }
        )

        # 7. Additional realistic Students matching Admin Dashboard image
        students_data = [
            {
                'email': 'nihal@gmail.com',
                'name': 'Nihal Ahammed',
                'course': 'BCA',
                'status': 'Pending',
                'percentage': 82.4,
                'phone': '9871122334',
                'gender': 'Male',
                'city': 'Bangalore',
            },
            {
                'email': 'fathima@gmail.com',
                'name': 'Fathima R',
                'course': 'BSC-CS',
                'status': 'Approved',
                'percentage': 91.2,
                'phone': '9872233445',
                'gender': 'Female',
                'city': 'Kochi',
            },
            {
                'email': 'arjun@gmail.com',
                'name': 'Arjun S',
                'course': 'BCOM',
                'status': 'Pending',
                'percentage': 78.5,
                'phone': '9873344556',
                'gender': 'Male',
                'city': 'Chennai',
            },
            {
                'email': 'sneha@gmail.com',
                'name': 'Sneha P',
                'course': 'BBA',
                'status': 'Approved',
                'percentage': 85.0,
                'phone': '9874455667',
                'gender': 'Female',
                'city': 'Mumbai',
            },
            {
                'email': 'vivek@gmail.com',
                'name': 'Vivek K',
                'course': 'BCA',
                'status': 'Rejected',
                'percentage': 52.0,
                'phone': '9875566778',
                'gender': 'Male',
                'city': 'Pune',
            },
            {
                'email': 'ananya@gmail.com',
                'name': 'Ananya Das',
                'course': 'BA-ENG',
                'status': 'Approved',
                'percentage': 89.4,
                'phone': '9876677889',
                'gender': 'Female',
                'city': 'Kolkata',
            },
            {
                'email': 'rohit@gmail.com',
                'name': 'Rohit Verma',
                'course': 'BSC-MATH',
                'status': 'Document Verification',
                'percentage': 86.8,
                'phone': '9877788990',
                'gender': 'Male',
                'city': 'Jaipur',
            },
            {
                'email': 'priya@gmail.com',
                'name': 'Priya Nair',
                'course': 'BSC-CS',
                'status': 'Enrolled',
                'percentage': 94.2,
                'phone': '9878899001',
                'gender': 'Female',
                'city': 'Trivandrum',
            },
        ]

        for sidx, sinfo in enumerate(students_data, start=2):
            fname, lname = sinfo['name'].split(' ', 1)
            u, _ = User.objects.get_or_create(
                email=sinfo['email'],
                defaults={
                    'username': sinfo['email'].split('@')[0],
                    'first_name': fname,
                    'last_name': lname,
                    'role': 'STUDENT',
                    'phone_number': sinfo['phone'],
                }
            )
            u.set_password('student123')
            u.save()

            StudentProfile.objects.get_or_create(
                user=u,
                defaults={
                    'student_id': f"STU2025{sidx:04d}",
                    'date_of_birth': datetime.date(2005, (sidx % 12) + 1, (sidx * 2 % 25) + 1),
                    'gender': sinfo['gender'],
                    'address': f"{sidx * 15}, Main Avenue, {sinfo['city']}",
                    'city': sinfo['city'],
                    'state': 'India',
                    'pincode': f"5600{sidx:02d}",
                    'father_name': f"Father of {fname}",
                    'mother_name': f"Mother of {fname}",
                    'guardian_contact': sinfo['phone'],
                    'previous_institution': 'National Senior Secondary School',
                    'qualification': '12th Standard',
                    'board_university': 'State Board',
                    'passing_year': 2024,
                    'percentage_cgpa': sinfo['percentage'],
                }
            )

            # Application
            target_course = course_objects[sinfo['course']]
            app_id = f"CAE202500{130 + sidx}"
            app_stat = sinfo['status']
            app, _ = AdmissionApplication.objects.update_or_create(
                application_id=app_id,
                defaults={
                    'student': u,
                    'course': target_course,
                    'status': app_stat,
                    'current_step': 5,
                    'full_name': sinfo['name'],
                    'email': sinfo['email'],
                    'phone_number': sinfo['phone'],
                    'date_of_birth': datetime.date(2005, (sidx % 12) + 1, (sidx * 2 % 25) + 1),
                    'gender': sinfo['gender'],
                    'address': f"{sidx * 15}, Main Avenue, {sinfo['city']}",
                    'father_name': f"Father of {fname}",
                    'mother_name': f"Mother of {fname}",
                    'guardian_contact': sinfo['phone'],
                    'previous_institution': 'National Senior Secondary School',
                    'qualification': '12th Standard',
                    'board_university': 'State Board',
                    'passing_year': 2024,
                    'percentage_cgpa': sinfo['percentage'],
                    'rejection_reason': 'Minimum 12th cutoff mark not met.' if app_stat == 'Rejected' else '',
                    'admin_remarks': 'Processed by admissions committee.',
                    'reviewed_by': admin if app_stat in ['Approved', 'Rejected', 'Enrolled'] else None,
                    'reviewed_at': timezone.now() - datetime.timedelta(days=sidx) if app_stat in ['Approved', 'Rejected', 'Enrolled'] else None,
                    'submitted_at': timezone.now() - datetime.timedelta(days=sidx + 2),
                }
            )

            # Timeline
            ApplicationTimeline.objects.get_or_create(
                application=app,
                status='Submitted',
                defaults={
                    'title': 'Application Submitted',
                    'description': 'Online application received.',
                    'performed_by': u
                }
            )

            # If Enrolled
            if app_stat == 'Enrolled':
                Enrollment.objects.get_or_create(
                    enrollment_id=f"ENR202500{130 + sidx}",
                    defaults={
                        'student': u,
                        'application': app,
                        'course': target_course,
                        'academic_year': '2025-2026',
                        'status': 'Confirmed',
                        'roll_number': f"{target_course.course_code}-2025-{sidx:03d}",
                        'remarks': 'Seat confirmed.'
                    }
                )

        # Admin notifications
        Notification.objects.get_or_create(
            recipient=admin,
            title='New Applications Pending Verification',
            defaults={
                'message': '5 new admission applications submitted today are awaiting document verification.',
                'link': '/admissions/admin/manage/',
                'notification_type': 'WARNING',
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo database!'))
        self.stdout.write(self.style.SUCCESS('Admin Login: admin@college.edu / admin123'))
        self.stdout.write(self.style.SUCCESS('Student Login: rahul@gmail.com / student123'))

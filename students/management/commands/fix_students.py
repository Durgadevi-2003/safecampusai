from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student

class Command(BaseCommand):
    help = "Fix Student records by linking them with matching User accounts"

    def handle(self, *args, **kwargs):
        fixed_count = 0
        for student in Student.objects.filter(user__isnull=True):
            try:
                # Match user with same username as student_id or name
                user = User.objects.filter(username=student.student_id).first()
                if not user:
                    user = User.objects.filter(username=student.name).first()

                if user:
                    student.user = user
                    student.save()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Linked Student {student.student_id} → User {user.username}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No matching user found for Student {student.student_id}"
                        )
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fixing student {student.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ Fixed {fixed_count} student records."))

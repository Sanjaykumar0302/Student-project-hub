ROLE_ADMIN = "admin"
ROLE_STUDENT = "student"

FILE_TYPE_REQUIREMENT = "requirement"
FILE_TYPE_COMPLETED = "completed"

PAYMENT_CREATED = "created"
PAYMENT_PAID = "paid"
PAYMENT_FAILED = "failed"

NEXT_STATUS = {
    "Pending": ["Accepted", "Rejected"],
    "Accepted": ["Working", "Rejected"],
    "Working": ["Completed"],
    "Completed": ["Delivered"],
    "Delivered": [],
    "Rejected": [],
}

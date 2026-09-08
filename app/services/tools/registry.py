TOOL_REGISTRY: dict[str, dict] = {
    "get_leave_balance": {
        "name": "get_leave_balance",
        "description": (
            "Retrieve the current leave balance for an employee, broken down by leave type "
            "(annual, casual, medical, etc.). Use this when the user asks about their remaining "
            "leave days, how much leave they have left, or leave entitlement for a specific type."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "endpoint": "/hr/leave/balance-summary",
        "method": "GET",
        "is_write": False,
    },
    "get_attendance_timeline": {
        "name": "get_attendance_timeline",
        "description": (
            "Get the employee's daily attendance records for the last 30 days. "
            "Each record includes the date, attendance status (Present, Absent, Late), "
            "check-in time, check-out time, total worked minutes, and whether manual "
            "attendance correction can be applied for that day. "
            "Use when the user asks about: check-in or check-out times, whether they were "
            "late or absent on a specific day, worked hours on a particular day, which days "
            "they missed or were absent, days marked as holidays in their record, or whether "
            "they can apply for manual attendance correction. "
            "Do NOT use for leave balance totals or entitlements — use get_leave_balance for that."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "endpoint": "/hr/attendance/timeline",
        "method": "GET",
        "is_write": False,
    },
    "get_employee_details": {
        "name": "get_employee_details",
        "description": (
            "Retrieve the authenticated employee's personal and office profile — "
            "includes full name, NIC, birthday, gender, blood type, marital status, "
            "mobile number, language, email, employee code, EPF/MSL numbers, join date, "
            "branch, department, designation, grade, supervisor, and TIN number. "
            "Use when the user asks about their profile, personal details, job details, "
            "who their supervisor is, or what department/designation they belong to."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "endpoint": "/hr/employee-details",
        "method": "GET",
        "is_write": False,
    },
}

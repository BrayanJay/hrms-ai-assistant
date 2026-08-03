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
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "The unique identifier of the employee whose leave balance is requested.",
                },
            },
            "required": ["employee_id"],
        },
        "endpoint": "/leave/{employee_id}",
        "method": "GET",
        "is_write": False,
    },
    "get_kpi_achievement": {
        "name": "get_kpi_achievement",
        "description": (
            "Retrieve the KPI achievement score and status for an employee for the current or a "
            "specified review period. Use this when the user asks about their KPI score, performance "
            "rating, target achievement percentage, or whether they met their goals."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "The unique identifier of the employee whose KPI data is requested.",
                },
                "period": {
                    "type": "string",
                    "description": "Review period in YYYY-Q# format (e.g. 2026-Q1). Defaults to current period if omitted.",
                },
            },
            "required": ["employee_id"],
        },
        "endpoint": "/kpi/{employee_id}",
        "method": "GET",
        "is_write": False,
    },
    "get_team_members": {
        "name": "get_team_members",
        "description": (
            "Retrieve the list of employees who report to a given manager. Use this when the user "
            "asks who is on their team, how many direct reports a manager has, or wants to see "
            "their department members."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "manager_id": {
                    "type": "string",
                    "description": "The unique identifier of the manager whose direct reports are requested.",
                },
            },
            "required": ["manager_id"],
        },
        "endpoint": "/team/{manager_id}",
        "method": "GET",
        "is_write": False,
    },
    "get_directory_details": {
        "name": "get_directory_details",
        "description": (
            "Look up employee contact and profile details from the company directory by name or job role. "
            "Use this when the user asks for a colleague's email, phone number, department, or office "
            "location, or wants to find who holds a specific role (e.g. 'who is the HR manager?')."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Full or partial name of the employee to search for.",
                },
                "role": {
                    "type": "string",
                    "description": "Job title or role to search for (e.g. 'HR Manager', 'Finance Lead').",
                },
            },
            "required": [],
        },
        "endpoint": "/directory",
        "method": "GET",
        "is_write": False,
    },
    "get_payslip_summary": {
        "name": "get_payslip_summary",
        "description": (
            "Retrieve a summary of an employee's payslip for a specific month, including gross salary, "
            "net pay, tax deductions, EPF/ETF contributions, and allowances. Use this when the user "
            "asks about their salary, pay for a specific month, deductions, or net take-home pay."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "The unique identifier of the employee whose payslip is requested.",
                },
                "month": {
                    "type": "string",
                    "description": "The payslip month in YYYY-MM format (e.g. 2026-07).",
                },
            },
            "required": ["employee_id", "month"],
        },
        "endpoint": "/payslip/{employee_id}",
        "method": "GET",
        "is_write": False,
    },
}

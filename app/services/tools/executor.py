import httpx
from app.core.config import settings
from app.services.tools.registry import TOOL_REGISTRY

HR_API_BASE_URL = settings.hr_api_base_url

class ToolCallError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)

async def execute_tool(tool_name: str,  params: dict) -> dict:
    if not HR_API_BASE_URL:
        mock_data = {
            "get_leave_balance": {
                "employee_id": params.get("employee_id"),
                "balances": {
                    "annual": 12,
                    "casual": 5,
                    "medical": 3
                }
            },
            "get_kpi_achievement": {
                "employee_id": params.get("employee_id"),
                "score": 87.5,
                "status": "On Track",
                "period": params.get("period", "2026-Q2"),
                "targets": [
                    {"name": "Sales Revenue", "target": 100, "achieved": 91.0},
                    {"name": "Customer Satisfaction", "target": 90, "achieved": 88.5},
                    {"name": "Project Delivery", "target": 95, "achieved": 100.0},
                ],
            },
            "get_team_members": {
                "manager_id": params.get("manager_id"),
                "team": [
                    {"employee_id": "EMP021", "name": "Kavindi Perera", "role": "Senior Associate", "email": "kavindi.perera@company.com"},
                    {"employee_id": "EMP034", "name": "Nuwan Silva", "role": "Associate", "email": "nuwan.silva@company.com"},
                    {"employee_id": "EMP047", "name": "Tharushi Fernando", "role": "Junior Associate", "email": "tharushi.fernando@company.com"},
                ],
                "total": 3,
            },
            "get_directory_details": {
                "results": [
                    {
                        "employee_id": "EMP009",
                        "name": params.get("name", "Amali Rodrigo"),
                        "role": params.get("role", "HR Manager"),
                        "department": "Human Resources",
                        "email": "amali.rodrigo@company.com",
                        "phone": "+94 77 123 4567",
                        "office": "Colombo HQ — Floor 3",
                    }
                ]
            },
            "get_payslip_summary": {
                "employee_id": params.get("employee_id"),
                "month": params.get("month"),
                "gross_salary": 185000.00,
                "deductions": {
                    "epf_employee": 18500.00,
                    "tax": 12400.00,
                    "other": 2500.00,
                },
                "allowances": {
                    "transport": 8000.00,
                    "meal": 5000.00,
                },
                "net_pay": 164600.00,
                "currency": "LKR",
            },
        }
        return mock_data.get(tool_name, {"message": "No mock data available"})

    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool = TOOL_REGISTRY[tool_name]
    url = HR_API_BASE_URL + tool["endpoint"].format_map(params)

    headers = {"Authorization": f"Bearer {settings.hr_api_token}"}
    async with httpx.AsyncClient() as client:
        if tool["method"] == "GET":
            response = await client.get(url, headers=headers, params=params)
        else:
            response = await client.post(url, headers=headers, json=params)

    if response.status_code >= 400:
        raise ToolCallError(response.status_code, response.text)
    return response.json()
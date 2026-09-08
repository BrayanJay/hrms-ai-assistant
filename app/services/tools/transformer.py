def _transform_attendance(raw: dict) -> dict:
    from datetime import date, timedelta

    data = raw.get("data", {})
    items = data.get("items", [])
    cutoff = date.today() - timedelta(days=30)

    def _time_only(dt_str: str | None) -> str | None:
        if not dt_str:
            return None
        parts = dt_str.replace("T", " ").split(" ")
        return parts[1][:5] if len(parts) > 1 else dt_str[:5]

    filtered = []
    for item in items:
        # skip future dates and anything older than 30 days
        if item.get("is_future"):
            continue
        if date.fromisoformat(item["timeline_date"]) < cutoff:
            continue
        filtered.append({
            "date": item["timeline_date"],
            "status": item["effective_status_name"],
            "in_time": _time_only(item.get("final_in_time")),
            "out_time": _time_only(item.get("final_out_time")),
            "worked_minutes": item.get("worked_minutes"),
            "is_working_day": item.get("is_working_day"),
            "holiday": item.get("holiday_desc") or None,
            "leave": item.get("leave_category_name"),
            "can_apply_manual": item.get("can_apply_manual_attendance", False),
        })

    return {
        "window": f"{data.get('window_start_date')} to {data.get('window_end_date')}",
        "attendance": filtered,
    }


def _transform_employee_details(raw: dict) -> dict:
    data = raw.get("data", {})
    personal = data.get("personal", {})
    office = data.get("office", {})

    return {
        "personal": {
            "nic": personal.get("staff_nicno"),
            "full_name": personal.get("staff_fullname"),
            "first_name": personal.get("staff_firstname"),
            "last_name": personal.get("staff_lastname"),
            "birthday": personal.get("staff_birthday"),
            "gender": personal.get("staff_gendername"),
            "blood_type": personal.get("staff_bloodtypename"),
            "marital_status": personal.get("staff_mariedname"),
            "mobile": personal.get("staff_mobileno_primary"),
            "language": personal.get("staff_languagename"),
            "personal_email": personal.get("staff_gmailemail"),
        },
        "office": {
            "employee_code": office.get("staff_code"),
            "epf_no": office.get("staff_epf_no"),
            "msl_no": office.get("staff_msl_no"),
            "join_date": office.get("staff_joindate", "").split(" ")[0] or None,
            "branch": office.get("staff_BranchName"),
            "department": office.get("staff_DepartmentName"),
            "designation": office.get("staff_designationname", "").strip() or None,
            "grade": office.get("staff_gradename"),
            "employment_type": office.get("staff_empcategoryname"),
            "supervisor": office.get("staff_supervisor_fullname"),
            "tin": office.get("staff_tinNumber"),
            "work_email": office.get("staff_internalemail", "").strip() or None,
        },
    }


def transform_tool_result(tool_name: str, raw: dict) -> dict:
    transformers = {
        "get_attendance_timeline": _transform_attendance,
        "get_employee_details": _transform_employee_details,
    }
    fn = transformers.get(tool_name)
    return fn(raw) if fn else raw  # unknown tools pass through unchanged

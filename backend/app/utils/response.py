def success_response(data=None, message: str = "Success", status_code: int = 200) -> dict:
    return {"status": "success", "message": message, "data": data, "code": status_code}


def error_response(message: str = "Error", status_code: int = 400, details=None) -> dict:
    return {"status": "error", "message": message, "data": details, "code": status_code}

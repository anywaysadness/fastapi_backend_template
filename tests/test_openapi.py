from fastapi import FastAPI


def test_openapi_documents_all_endpoints(app: FastAPI) -> None:
    schema = app.openapi()

    assert schema["info"]["description"]
    assert {tag["name"] for tag in schema["tags"]} == {"auth", "users"}
    assert "ErrorResponse" in schema["components"]["schemas"]
    assert schema["components"]["securitySchemes"]["AuthCookie"]["description"]

    for path, methods in schema["paths"].items():
        for operation in methods.values():
            assert operation.get("summary"), path
            assert operation.get("description"), path
            assert operation.get("responses"), path

    protected = schema["paths"]["/api/v1/auth/me"]["get"]
    login = schema["paths"]["/api/v1/auth/login"]["post"]
    assert protected["security"] == [{"AuthCookie": []}]
    assert login.get("security") is None

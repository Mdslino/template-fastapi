from pydantic import EmailStr, validate_arguments


@validate_arguments
def hide_email(email: EmailStr) -> str:
    """Hide email address."""
    parts = email.split("@")
    return (
        parts[0][0] + "*" * (len(parts[0]) - 2) + parts[0][-1] + "@" + parts[1]
    )

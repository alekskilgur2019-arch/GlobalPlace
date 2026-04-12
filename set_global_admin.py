import sys

from database import init_db
from services.global_admin_service import GlobalAdminService


def main():
    if len(sys.argv) != 3:
        print("Usage: python set_global_admin.py <username> <password>")
        raise SystemExit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    init_db()
    service = GlobalAdminService()
    result = service.ensure_global_admin(username, password)

    if not result["ok"]:
        print(result["message"])
        raise SystemExit(1)

    print(result["message"])
    print(f"Username: {result['username']}")
    print(f"Role: {result['role']}")


if __name__ == "__main__":
    main()

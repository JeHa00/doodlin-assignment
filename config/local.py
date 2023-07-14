from accounts.models import User, Employee


def make_master():
    """마스터 계정 생성"""
    email = "master@test.com"
    password = "master1234!"
    phone = "01012341234"
    name = "master"

    master_user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        phone=phone,
        name=name,
    )

    master_user.state = "AP"
    master_user.save()

    authorizations = {
        "authorization_grade": "MS",
        "signup_approval_authorization": True,
        "list_read_authorization": True,
        "update_authorization": True,
        "resign_authorization": True,
    }

    Employee.objects.create(user_id=master_user.id, **authorizations)


def make_accounts():
    """
    승인 대기 계정 생성

    기억하기 쉽게 동일한 패스워드와 패턴이 단순하게 선정

    하지만 직접 생성하여 테스트도 가능
    """

    for i in range(2, 31):
        email = f"staff{i}@test.com"
        password = "staff1234!"
        name = f"staff{i}"

        if i < 10:
            phone = f"010{'i' * 8}"
        else:
            phone = f"010{'i' * 4}" if i != 11 or 22 else f"010{i * 1000000}"

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            phone=phone,
            name=name,
        )


if __name__ == "__main__":
    make_master()
    make_accounts()

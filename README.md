# 그리팅 Backoffice Engineer 과제 전형

## 과제 안내

- 해당 포지션의 과제 전형은 주어진 요구 사항을 읽고 이를 구현하여 제출하는 과제입니다.
- [링크](https://docs.google.com/document/d/1Y77QQRgpwJtYhd9ZTWnIA3G0o_eU7NnKKg_a4BJ7Ang/edit?usp=sharing)를 참고하여 요구사항을 잘 읽고 구현해 주세요.
- 주어진 시간은 120시간(5일) 입니다.

## 과제 제출 안내

- 초대 받으신 해당 Repository 에 작성하신 코드를 push 해 주세요. 과제 마감 시 push 권한은 회수됩니다.

## 기타 문의 사항

- 과제를 진행하면서 궁금하신 내용은 <dev@doodlin.co.kr> 에 문의 해 주세요.

---

> 여기에 과제에서 요구한 README 를 작성해주세요

<br>

# 1. Local 실행 가이드

## 1.1 프로젝트 환경 설치하기

1. git clone <현재 이 repo url> 으로 가져옵니다.
2. terminal에 `pyenv virtualenv {파이썬 버전} {가상환경이름}` 을 입력합니다.
    - ex: `pyenv virtualenv 3.10.10 assignment`
    - pyenv 설치 명령어: `curl -sSL https://install.python-poetry.org | python3 -`
3. 설치된 가상환경 실행하기: `pyenv shell {가상환경 이름}`
    - ex: `pyenv shell assignment`  
4. 프로젝트 내부로 이동합니다. (git clone 하여 생긴 directory 내부로 이동)
5. `poetry init` 실행: git clone으로 가져왔다면 이미 특정 파일이 존재한다는 에러가 떴다면 성공입니다.
6. `poetry env info` 를 입력하여 **Virtualenv** 와 **System** 이 모두 pyenv를 바라보는지 확인합니다.
7. 확인하였다면 `poetry install` 로 디펜던시들을 설치합니다.
8. 다 설치가 되었다면 `python manage.py runserver` 를 하기 전에 `python manage.py migrate` 를 실행합니다.
9. `python manage.py runserver`를 통해 실행합니다.  

참조: pyenv와 poetry로 가상환경을 구성하는 게 어렵다면 [Poetry 와 Pyenv의 자주 사용하는 명령어 정리](https://jeha00.github.io/post/python/a_s_o/poetry_pyenv/#3-poetry%EC%99%80-pyenv-%EC%82%AC%EC%9A%A9-%EC%88%9C%EC%84%9C)에 정리를 해놨으니 참고하시길 바랍니다.  

<br>

## 1.2 계정 생성

마스터 계정은 admin 또는 직접 생성한 후 진행하는 걸로 생각했습니다.
superuser인 루트 계정은 별도로 생성하시고, 아래 과정을 따라서 먼저 마스터 계정을 생성하겠습니다.

- config.local은 local 실행을 위한 모의 계정들을 생성하기 위해 만든 파일입니다.  

```python
python manage.py shell

>>> from config.local import make_master
>>> make_master()

```

위 함수를 실행하면 마스터 계정이 생성되어 로그인을 하실 수 있으시고 마스터 계정이 있기 때문에 추가로 회원 가입하여 생성 후 승인을 취할 수 있습니다.

만약 여러 개의 승인 대기 계정을 생성하고 싶으시다면 아래 과정을 따라하시면 됩니다.

```python
python manage.py shell

>>> from config.local import make_accounts
>>> make_accounts()
```

<br>

---

# 2. DB Schema

## 2.1 ERD

![image](https://user-images.githubusercontent.com/78094972/253643702-613c9c1d-ca8f-414b-96a4-b0e94ff31273.png)

<br>

## 2.2 DDL

```sql
CREATE TABLE `User` (
 `id` INT NOT NULL DEFAULT ON INCREMENT,
 `email` VARCHAR(254) NOT NULL,
 `name` VARCHAR(50) NOT NULL,
 `phone` VARCHAR(11) NOT NULL,
 `state` VARCHAR(2) NOT NULL DEFAULT AW (대기)
 `rejected_at` DATETIME NULL,
 `reason_for_refusal` VARCHAR(50) NULL
);

CREATE TABLE `Employee` (
 `id` INT NOT NULL DEFAULT ON INCREMENT,
 `authorization_grade` VARCHAR(2) NULL,
 `signup_approval_authorization` BOOLEAN NOT NULL DEFAULT FALSE,
 `list_read_authorization` BOOLEAN NOT NULL DEFAULT TRUE,
 `update_authorization` BOOLEAN NOT NULL DEFAULT FALSE,
 `resign_authorization` BOOLEAN NOT NULL DEFAULT FALSE,
 `is_resigned` BOOLEAN NOT NULL DEFAULT FALSE,
 `user_id (FK)` INT NOT NULL
);

CREATE TABLE `Resignation` (
 `id` INT NOT NULL DEFAULT ON INCREMENT,
 `reason_for_resignation` VARCHAR(50) NOT NULL,
 `rejected_at` DATETIME NOT NULL,
 `resigned_user_id` INT NOT NULL
);

ALTER TABLE `User` ADD CONSTRAINT `PK_USER` PRIMARY KEY (
 `id`
);

ALTER TABLE `Employee` ADD CONSTRAINT `PK_EMPLOYEE` PRIMARY KEY (
 `id`
);

ALTER TABLE `Resignation` ADD CONSTRAINT `PK_RESIGNATION` PRIMARY KEY (
 `id`
);
```

- ERD CLOUD를 통해서 ERD를 그린 후 추출한 SQL 입니다.  

<br>

---

# 3. 프로젝트 설계 구조











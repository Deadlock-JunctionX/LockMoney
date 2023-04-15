from loguru import logger

from src.model import db, User, UserAccount, Transaction, TrustedApp
from src.passhash import hash_password


def reset_to_demo_data():
    logger.info("Clear all data")
    db.session.query(Transaction).delete()
    db.session.query(UserAccount).delete()
    db.session.query(User).delete()
    db.session.query(TrustedApp).delete()
    db.session.commit()

    logger.info("Add users")
    u1 = User(
        name="Phan Ngọc Lân",
        phone="0949791149",
        password_hash=hash_password("12345678"),
        pin_hash=hash_password("123456"),
        totp_key="XDTK6E22TYLGHN2CJLF232H2UWRWXWG7",
    )

    u2 = User(
        name="Hoàng Đức Việt",
        phone="0886272382",
        password_hash=hash_password("12345678"),
        pin_hash=hash_password("123456"),
        totp_key="F5HCEAEDW27AGCCOBX3RDHLFDTZFFNLI",
    )

    u3 = User(
        name="Bùi Mạnh Tuấn",
        phone="0389020687",
        password_hash=hash_password("12345678"),
        pin_hash=hash_password("123456"),
        totp_key="T5AII2XTVQYEV3HOKQWVRDZ37RKFZOCM",
    )
    u4 = User(
        name="Hà Hồng Sơn",
        phone="0365906800",
        password_hash=hash_password("12345678"),
        pin_hash=hash_password("123456"),
        totp_key="T5AII2XTVQYEV3HOKQWVRDZ37RKFZOCM",
    )
    users = [u1, u2, u3, u4]
    db.session.add_all(users)
    db.session.commit()
    for user in users:
        db.session.refresh(user)

    logger.info("Add user account")
    acc1_1 = UserAccount(
        user_id=u1.id,
        balance=1_000_000,
        initial_balance=1_000_000,
    )

    acc2_1 = UserAccount(
        user_id=u2.id,
        balance=200_000,
        initial_balance=100_000,
    )
    acc3_1 = UserAccount(
        user_id=u3.id,
        balance=5_000_000,
        initial_balance=5_000_000,
    )
    acc4_1 = UserAccount(
        user_id=u4.id,
        balance=100_000_000,
        initial_balance=100_000_000,
    )

    accs = [acc1_1, acc2_1, acc3_1, acc4_1]
    db.session.add_all(accs)
    db.session.commit()
    for acc in accs:
        db.session.refresh(acc)

    logger.info("Add trusted apps")
    tapp1 = TrustedApp(
        id="lockchat",
        name="Lock.Chat",
        secret_key_hash=hash_password("23oi23n9013292101n39013912339u3fnef1")
    )
    db.session.add(tapp1)
    db.session.commit()
    db.session.refresh(tapp1)

    logger.info("Add transactions")
    transactions = [
        Transaction(
            from_account_id=acc1_1.id,
            to_account_id=acc2_1.id,
            from_name="Phan Ngọc Lân",
            to_name="Hoàng Đức Việt",
            amount=100_000,
            description="Test transaction 1",
            status="success",
        ),
        Transaction(
            from_account_id=acc3_1.id,
            to_account_id=acc1_1.id,
            amount=100_000,
            to_name="Phan Ngọc Lân",
            from_name="Bùi Mạnh Tuấn",
            description="Test transaction 2",
            status="success",
            trusted_app_id=tapp1.id,
        ),
        Transaction(
            from_account_id=acc1_1.id,
            to_bank="ABC Bank",
            to_bank_account_number="204123823012",
            status="success",
            from_name="Phan Ngọc Lân",
            to_name="Hà Hồng Sơn",
            description="Test transaction 3",
            amount=520_000
        )
    ]
    db.session.add_all(transactions)
    db.session.commit()

    logger.info("All data inserted")

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
    db.session.add_all([u1, u2, u3])
    db.session.commit()
    db.session.refresh(u1)
    db.session.refresh(u2)
    db.session.refresh(u3)

    logger.info("Add user account")
    acc1_1 = UserAccount(
        user_id=u1.id,
        type="NATIVE",
        balance=1_000_000,
        initial_balance=1_000_000,
    )
    acc1_2 = UserAccount(
        user_id=u1.id,
        type="BANK_ACCOUNT",
        bank_id=1,
        bank_account_number="2019441823",
        priority=2,
        balance=500_000,
        initial_balance=500_000,
    )

    acc2_1 = UserAccount(
        user_id=u2.id,
        type="NATIVE",
        balance=200_000,
        initial_balance=100_000,
    )
    acc2_2 = UserAccount(
        user_id=u2.id,
        type="BANK_CARD",
        bank_id=2,
        bank_account_number="202392831",
        priority=2,
        balance=10_000_000,
        initial_balance=1_000_000,
    )
    acc3_1 = UserAccount(
        user_id=u3.id,
        type="BANK_ACCOUNT",
        bank_id=1,
        bank_account_number="2029213291",
        balance=5_000_000,
        initial_balance=1_000_000,
    )

    db.session.add_all([acc1_1, acc1_2, acc2_1, acc2_2, acc3_1])
    db.session.commit()
    for acc in [acc1_1, acc1_2, acc2_1, acc2_2, acc3_1]:
        db.session.refresh(acc)

    logger.info("Add trusted apps")
    tapp1 = TrustedApp(
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
            amount=100_000,
            description="Test transaction 1",
            status="success",
        ),
        Transaction(
            from_account_id=acc3_1.id,
            to_account_id=acc1_1.id,
            amount=100_000,
            description="Test transaction 2",
            status="success",
            trusted_app_id=tapp1.id,
        ),
        Transaction(
            from_account_id=acc2_2.id,
            to_account_id=acc1_2.id,
            amount=500_000,
            description="Invalid transaction",
            status="failed",
        )
    ]
    db.session.add_all(transactions)
    db.session.commit()

    logger.info("All data inserted")

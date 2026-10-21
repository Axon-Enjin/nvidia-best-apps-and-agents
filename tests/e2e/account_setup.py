"""Named test-account provisioning for browser flows; never used by runtime code."""

from sentinel.accounts import SecretBox, create_local_account

PASSWORD = "synthetic reviewer passphrase 2026"


def provision_reviewer(db, key_file, username="reviewer"):
    with db.session() as session:
        return create_local_account(session, username, PASSWORD, {"reviewer"},
                                    SecretBox.from_file(key_file, create=True))

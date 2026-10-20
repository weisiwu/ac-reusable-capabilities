"""Password verification and application supplied access policy."""

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from typing import Callable, Mapping, Protocol


class CredentialStore(Protocol):
    """Host-owned credential lookup protocol; records provide id, password_hash and optional roles; no built-in accounts.

    @ac-reusable
    @ac-capability desktop.auth.CredentialStore
    @ac-kind capability
    @ac-tags desktop, auth, CredentialStore
    @ac-contract Host-owned credential lookup protocol; records provide id, password_hash and optional roles; no built-in accounts.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def find_by_username(self, username: str) -> Mapping[str, object] | None:
        """Return credential mapping or None for the supplied username; host defines storage, lookup failures and rate limits.

        @ac-reusable
        @ac-capability desktop.auth.CredentialStore.find_by_username
        @ac-kind function
        @ac-tags desktop, auth, CredentialStore
        @ac-contract Return credential mapping or None for the supplied username; host defines storage, lookup failures and rate limits.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        ...


@dataclass(frozen=True)
class Principal:
    """Immutable subject and roles (empty frozenset by default); identity metadata only, no permission decisions.

    @ac-reusable
    @ac-capability desktop.auth.Principal
    @ac-kind capability
    @ac-tags desktop, auth, Principal
    @ac-contract Immutable subject and roles (empty frozenset by default); identity metadata only, no permission decisions.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    subject: str
    roles: frozenset[str] = field(default_factory=frozenset)


class PasswordHasher:
    """PBKDF2-SHA256 hashes with random 16-byte salts and default 310000 iterations; minimum 100000; no persistence.

    @ac-reusable
    @ac-capability desktop.auth.PasswordHasher
    @ac-kind capability
    @ac-tags desktop, auth, PasswordHasher
    @ac-contract PBKDF2-SHA256 hashes with random 16-byte salts and default 310000 iterations; minimum 100000; no persistence.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def __init__(self, iterations: int = 310_000):
        if iterations < 100_000:
            raise ValueError("iterations must be at least 100000")
        self.iterations = iterations

    def hash(self, password: str) -> str:
        """Require nonempty password; return algorithm$iterations$salt_hex$digest_hex with fresh salt; ValueError on empty input.

        @ac-reusable
        @ac-capability desktop.auth.PasswordHasher.hash
        @ac-kind function
        @ac-tags desktop, auth, PasswordHasher
        @ac-contract Require nonempty password; return algorithm$iterations$salt_hex$digest_hex with fresh salt; ValueError on empty input.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if not password:
            raise ValueError("password cannot be empty")
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, self.iterations)
        return f"pbkdf2_sha256${self.iterations}${salt.hex()}${digest.hex()}"

    def verify(self, password: str, encoded: str) -> bool:
        """Compare encoded PBKDF2 hash in constant time; false for mismatches and malformed supported text; encoded records must be trusted and size bounded.

        @ac-reusable
        @ac-capability desktop.auth.PasswordHasher.verify
        @ac-kind function
        @ac-tags desktop, auth, PasswordHasher
        @ac-contract Compare encoded PBKDF2 hash in constant time; false for mismatches and malformed supported text; encoded records must be trusted and size bounded.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        try:
            algorithm, iterations, salt, expected = encoded.split("$", 3)
            if algorithm != "pbkdf2_sha256" or int(iterations) < 100_000:
                return False
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations))
            return hmac.compare_digest(actual, bytes.fromhex(expected))
        except (ValueError, TypeError):
            return False

    def needs_rehash(self, encoded: str) -> bool:
        """True for malformed format, wrong algorithm or iterations below configured policy; never rewrites stored hashes.

        @ac-reusable
        @ac-capability desktop.auth.PasswordHasher.needs_rehash
        @ac-kind function
        @ac-tags desktop, auth, PasswordHasher
        @ac-contract True for malformed format, wrong algorithm or iterations below configured policy; never rewrites stored hashes.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        try:
            algorithm, iterations, _, _ = encoded.split("$", 3)
            return algorithm != "pbkdf2_sha256" or int(iterations) < self.iterations
        except (ValueError, TypeError):
            return True


class AuthService:
    """Inject CredentialStore and optional PasswordHasher; no account registration, sessions, throttling or credential persistence.

    @ac-reusable
    @ac-capability desktop.auth.AuthService
    @ac-kind capability
    @ac-tags desktop, auth, AuthService
    @ac-contract Inject CredentialStore and optional PasswordHasher; no account registration, sessions, throttling or credential persistence.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """
    def __init__(self, store: CredentialStore, hasher: PasswordHasher | None = None):
        self.store = store
        self.hasher = hasher or PasswordHasher()

    def authenticate(self, username: str, password: str) -> Principal | None:
        """Return Principal on valid hash or None for unknown user/wrong password; propagate host-store errors; accepts role string or iterable.

        @ac-reusable
        @ac-capability desktop.auth.AuthService.authenticate
        @ac-kind function
        @ac-tags desktop, auth, AuthService
        @ac-contract Return Principal on valid hash or None for unknown user/wrong password; propagate host-store errors; accepts role string or iterable.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        record = self.store.find_by_username(username)
        if not record or not self.hasher.verify(password, str(record.get("password_hash", ""))):
            return None
        roles = record.get("roles", ())
        if isinstance(roles, str):
            roles = (roles,)
        return Principal(subject=str(record["id"]), roles=frozenset(roles))


class AccessPolicy:
    """Require a caller-supplied allows(principal,action,resource) predicate; no default grants.

    @ac-reusable
    @ac-capability desktop.auth.AccessPolicy
    @ac-kind capability
    @ac-tags desktop, auth, AccessPolicy
    @ac-contract Require a caller-supplied allows(principal,action,resource) predicate; no default grants.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
    @ac-tests tests/test_core.py and tests/test_contracts.py
    """

    def __init__(self, allows: Callable[[Principal, str, object], bool]):
        self._allows = allows

    def require(self, principal: Principal, action: str, resource: object = None) -> None:
        """Call predicate with resource default None; return None if allowed, otherwise raise PermissionError; propagate predicate errors.

        @ac-reusable
        @ac-capability desktop.auth.AccessPolicy.require
        @ac-kind function
        @ac-tags desktop, auth, AccessPolicy
        @ac-contract Call predicate with resource default None; return None if allowed, otherwise raise PermissionError; propagate predicate errors.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py and tests/test_contracts.py
        """
        if not self._allows(principal, action, resource):
            raise PermissionError(f"action denied: {action}")

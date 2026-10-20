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
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
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
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
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
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    subject: str
    roles: frozenset[str] = field(default_factory=frozenset)


class PasswordHasher:
    """PBKDF2-SHA256 with fresh 16-byte salts, default iterations=310000 and keyword max_verify_iterations=2000000; require integer work factors within policy; no persistence.

    @ac-reusable
    @ac-capability desktop.auth.PasswordHasher
    @ac-kind capability
    @ac-tags desktop, auth, PasswordHasher
    @ac-contract PBKDF2-SHA256 with fresh 16-byte salts, default iterations=310000 and keyword max_verify_iterations=2000000; require integer work factors within policy; no persistence.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
    """
    def __init__(self, iterations: int = 310_000, *, max_verify_iterations: int = 2_000_000):
        if type(iterations) is not int or type(max_verify_iterations) is not int or not 100_000 <= iterations <= max_verify_iterations:
            raise ValueError("iterations must be integers between 100000 and max_verify_iterations")
        self.iterations = iterations
        self.max_verify_iterations = max_verify_iterations

    def _decode(self, encoded):
        if not isinstance(encoded, str) or len(encoded) > 256:
            return None
        try:
            algorithm, raw_iterations, raw_salt, raw_digest = encoded.split("$", 3)
            if algorithm != "pbkdf2_sha256" or not raw_iterations.isascii() or not raw_iterations.isdigit():
                return None
            iterations = int(raw_iterations)
            salt, digest = bytes.fromhex(raw_salt), bytes.fromhex(raw_digest)
            if not 100_000 <= iterations <= self.max_verify_iterations or len(salt) != 16 or len(digest) != 32:
                return None
            return iterations, salt, digest
        except (ValueError, TypeError):
            return None

    def hash(self, password: str) -> str:
        """Require nonempty password; return algorithm$iterations$salt_hex$digest_hex with fresh salt; ValueError on empty input.

        @ac-reusable
        @ac-capability desktop.auth.PasswordHasher.hash
        @ac-kind function
        @ac-tags desktop, auth, PasswordHasher
        @ac-contract Require nonempty password; return algorithm$iterations$salt_hex$digest_hex with fresh salt; ValueError on empty input.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if not password:
            raise ValueError("password cannot be empty")
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, self.iterations)
        return f"pbkdf2_sha256${self.iterations}${salt.hex()}${digest.hex()}"

    def verify(self, password: str, encoded: str) -> bool:
        """Return false for invalid text, malformed salt/digest or iterations outside 100000..max_verify_iterations before hashing; valid hashes compared in constant time; no storage writes.

        @ac-reusable
        @ac-capability desktop.auth.PasswordHasher.verify
        @ac-kind function
        @ac-tags desktop, auth, PasswordHasher
        @ac-contract Return false for invalid text, malformed salt/digest or iterations outside 100000..max_verify_iterations before hashing; valid hashes compared in constant time; no storage writes.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        parts = self._decode(encoded)
        if parts is None or not isinstance(password, str):
            return False
        iterations, salt, expected = parts
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
        return hmac.compare_digest(actual, expected)

    def needs_rehash(self, encoded: str) -> bool:
        """True for malformed/unsupported hashes or work below configured iterations; validate salt/digest and bounded work before deciding; never modify storage.

        @ac-reusable
        @ac-capability desktop.auth.PasswordHasher.needs_rehash
        @ac-kind function
        @ac-tags desktop, auth, PasswordHasher
        @ac-contract True for malformed/unsupported hashes or work below configured iterations; validate salt/digest and bounded work before deciding; never modify storage.
        @ac-dependencies Python >=3.11 standard library; host dependencies injected.
        @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        parts = self._decode(encoded)
        return parts is None or parts[0] < self.iterations


class AuthService:
    """Inject CredentialStore and optional PasswordHasher; no account registration, sessions, throttling or credential persistence.

    @ac-reusable
    @ac-capability desktop.auth.AuthService
    @ac-kind capability
    @ac-tags desktop, auth, AuthService
    @ac-contract Inject CredentialStore and optional PasswordHasher; no account registration, sessions, throttling or credential persistence.
    @ac-dependencies Python >=3.11 standard library; host dependencies injected.
    @ac-example See examples/desktop_demo.py and docs/contracts/auth.md.
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
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
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
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
    @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
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
        @ac-tests tests/test_core.py, tests/test_contracts.py and tests/test_review_core.py
        """
        if not self._allows(principal, action, resource):
            raise PermissionError(f"action denied: {action}")

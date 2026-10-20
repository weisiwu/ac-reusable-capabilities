---
title: "desktop.auth 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "auth"]
summary: "auth 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.auth

导入路径：`ctf_desktop.auth`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## CredentialStore

稳定标识：`desktop.auth.CredentialStore`

Host-owned credential lookup protocol; records provide id, password_hash and optional roles; no built-in accounts.

## CredentialStore.find_by_username

稳定标识：`desktop.auth.CredentialStore.find_by_username`

Return credential mapping or None for the supplied username; host defines storage, lookup failures and rate limits.

## Principal

稳定标识：`desktop.auth.Principal`

Immutable subject and roles (empty frozenset by default); identity metadata only, no permission decisions.

## PasswordHasher

稳定标识：`desktop.auth.PasswordHasher`

PBKDF2-SHA256 hashes with random 16-byte salts and default 310000 iterations; minimum 100000; no persistence.

## PasswordHasher.hash

稳定标识：`desktop.auth.PasswordHasher.hash`

Require nonempty password; return algorithm$iterations$salt_hex$digest_hex with fresh salt; ValueError on empty input.

## PasswordHasher.verify

稳定标识：`desktop.auth.PasswordHasher.verify`

Compare encoded PBKDF2 hash in constant time; false for mismatches and malformed supported text; encoded records must be trusted and size bounded.

## PasswordHasher.needs_rehash

稳定标识：`desktop.auth.PasswordHasher.needs_rehash`

True for malformed format, wrong algorithm or iterations below configured policy; never rewrites stored hashes.

## AuthService

稳定标识：`desktop.auth.AuthService`

Inject CredentialStore and optional PasswordHasher; no account registration, sessions, throttling or credential persistence.

## AuthService.authenticate

稳定标识：`desktop.auth.AuthService.authenticate`

Return Principal on valid hash or None for unknown user/wrong password; propagate host-store errors; accepts role string or iterable.

## AccessPolicy

稳定标识：`desktop.auth.AccessPolicy`

Require a caller-supplied allows(principal,action,resource) predicate; no default grants.

## AccessPolicy.require

稳定标识：`desktop.auth.AccessPolicy.require`

Call predicate with resource default None; return None if allowed, otherwise raise PermissionError; propagate predicate errors.

## 最小调用示例

```python
from ctf_desktop.auth import PasswordHasher, Principal, AccessPolicy
hasher = PasswordHasher(100_000)
assert hasher.verify("example-only", hasher.hash("example-only"))
principal = Principal("sample", frozenset({"reader"}))
AccessPolicy(lambda actor, action, resource: "reader" in actor.roles).require(principal, "read")
```

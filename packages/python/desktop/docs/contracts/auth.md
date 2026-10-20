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

导入路径：`ctf_desktop.auth`。场景接入见 [使用指南](../guides/auth.md)。

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

PBKDF2-SHA256 with fresh 16-byte salts, default iterations=310000 and keyword max_verify_iterations=2000000; require integer work factors within policy; no persistence.

## PasswordHasher.hash

稳定标识：`desktop.auth.PasswordHasher.hash`

Require nonempty password; return algorithm$iterations$salt_hex$digest_hex with fresh salt; ValueError on empty input.

## PasswordHasher.verify

稳定标识：`desktop.auth.PasswordHasher.verify`

Return false for invalid text, malformed salt/digest or iterations outside 100000..max_verify_iterations before hashing; valid hashes compared in constant time; no storage writes.

## PasswordHasher.needs_rehash

稳定标识：`desktop.auth.PasswordHasher.needs_rehash`

True for malformed/unsupported hashes or work below configured iterations; validate salt/digest and bounded work before deciding; never modify storage.

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

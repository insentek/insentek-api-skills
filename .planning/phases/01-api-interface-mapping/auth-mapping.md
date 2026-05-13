# Auth API Mapping — /v3/token

> Source: `ref/api-document-latest.pdf` §0x03, `ref/api-repo/src/main/java/com/insentek/openapi/model/EcoApiAuth.java`
> Locked Decisions: D-10, D-11, D-12

---

## 1. Endpoint Overview

| Item | Value |
|------|-------|
| Endpoint | `GET /v3/token` |
| Base URL | `http://openapi.ecois.info` (HTTPS recommended for production) |
| Content-Type | `application/json` |
| Auth Method | Query parameter (appid + secret) |

This is the entry-point for all API access. Every other endpoint requires the `token` returned by this call to be passed in the `Authorization` header.

---

## 2. Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `appid` | String | Yes | 在 E 生态创建的应用 ID |
| `secret` | String | Yes | 在 E 生态创建的应用密钥 |

**Example Request:**
```
GET http://openapi.ecois.info/v3/token?appid=test&secret=test
```

---

## 3. Response Format

### Success Response (200 OK)

```json
{
  "message": "ok",
  "token": "wj3eZGGKofgv7GyzuCmuoLukVUvUsuDq",
  "expires": 7200
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | String | Always `"ok"` on success |
| `token` | String | Access token for Authorization header |
| `expires` | Integer | Token validity period in seconds (default: 7200 = 2 hours) |

### Error Responses

| HTTP Status | Scenario | Skill-Level Handling |
|-------------|----------|---------------------|
| 400 | Invalid request format | Prompt user to check appid/secret format |
| 401 | Invalid appid or secret | **"认证失败，请检查 appid 和 secret 是否正确"** — prompt user to verify credentials |
| 403 | Token expired (on subsequent calls) | Auto-refresh: re-call /v3/token with cached appid/secret |
| 500 | Server error | Retry with exponential backoff (max 3 retries), then fail with clear message |

**HTTP Status Code Reference (from PDF §0x02):**

| Status | Meaning | Applies To |
|--------|---------|------------|
| 200 OK | Success | GET |
| 201 CREATED | Created | POST / PUT / PATCH |
| 202 Accepted | Accepted | — |
| 204 NO CONTENT | No content | DELETE |
| 400 INVALID REQUEST | Bad request | POST / PUT / PATCH |
| 401 Unauthorized | Authentication failed | — |
| 403 Forbidden | Forbidden | — |
| 404 NOT FOUND | Resource not found | — |
| 406 Not Acceptable | Not acceptable | GET |
| 410 Gone | Resource gone | GET |
| 422 Unprocesable entity | Validation error | POST / PUT / PATCH |
| 500 INTERNAL SERVER ERROR | Server error | — |

---

## 4. Token Lifecycle

### 4.1 Acquisition
```
User provides appid + secret
    → Skill calls GET /v3/token?appid={appid}&secret={secret}
    → Store: token + expires_timestamp (current_time + expires)
```

### 4.2 Reuse (Conversation-Level Cache)
- Store `token` and `expires_at` in conversation context
- All subsequent API calls include header: `Authorization: {token}`
- **Do not re-request token for every API call** (per D-12)

### 4.3 Refresh Triggers
- **Proactive**: When `expires_at - current_time < 300` (5 min buffer)
- **Reactive**: When API call returns 401 or 403
- **Action**: Re-call `/v3/token` with cached appid/secret, update stored token

### 4.4 Header Format
```bash
curl -H 'Content-Type: application/json' \
     -H 'Authorization: wj3eZGGKofgv7GyzuCmuoLukVUvUsuDq' \
     'http://openapi.ecois.info/v3/devices?page=1&limit=100'
```

---

## 5. Source Code Insights

### EcoApiAuth Model (DB Schema)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | String | Auth record name |
| `token` | String | Cached token (server-side) |
| `uid` | Integer | User ID |
| `ipAllow` | String | Allowed IP whitelist |
| `debug` | Boolean | Debug mode flag |
| `createTime` | DateTime | Record creation time |
| `updateTime` | DateTime | Record update time |
| `appid` | String | Application ID |
| `appsecret` | String | Application secret |
| `notify_url` | String | Webhook notification URL |
| `lastModifyTime` | DateTime | Last modification time |

### Service Layer
- `EcoApiAuthService.getAuthByAppId(appid, secret)` — validates credentials, returns auth record
- `EcoApiAuthService.getAuthByToken(token)` — validates existing token
- `EcoApiAuthService.getAuthByUid(uid)` — lookup by user id

---

## 6. Skill Mapping

### Skill Tool: `authenticate`

| Aspect | Specification |
|--------|---------------|
| **Purpose** | Obtain and manage API access token |
| **Mapped Endpoint** | `GET /v3/token` |
| **Parameters** | `appid` (String, required), `secret` (String, required) |
| **Returns** | `token` (String), `expires` (Integer, seconds) |
| **Behavior** | Call /v3/token → cache token + expires → reuse for all subsequent calls |
| **Auto-Refresh** | On 401/403 or expiry approaching (within 5 min) |
| **Error Handling** | 401 → prompt user to check credentials; 500 → retry 3x then fail |

### Prompt Instruction for skill.md

```markdown
## Authentication

Before making any API calls, the skill must authenticate using the user's appid and secret:

1. Call `GET /v3/token?appid={appid}&secret={secret}`
2. Cache the returned `token` and calculate `expires_at = now + expires_seconds`
3. Include `Authorization: {token}` header in all subsequent requests
4. When a call returns 401/403, or when token expires within 5 minutes,
   automatically re-authenticate to refresh the token

**Security Note**: Never log or display appid/secret in conversation output.
```

---

*Referenced Decisions: D-10 (authenticate tool), D-11 (token expiry + auto-refresh), D-12 (conversation-level token reuse)*
*Requirements: AUTH-01 (API 认证引导), AUTH-02 (认证错误处理)*

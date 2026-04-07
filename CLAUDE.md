# Lost & Found Platform — Backend

## Product Overview

A web application that helps people report and recover lost personal belongings. Supports two workflows:

- **Finders** report items they discovered in public places
- **Owners** report items they lost, and the system proactively matches them against found-item posts

The platform uses category, location, date range, and keyword similarity to automatically detect potential matches and notify both parties. Claims go through a verification process using hidden item details to prevent fraud.

## Core Domain Concepts

### Users & Roles
- **Finder** — reports found items, reviews claims, approves contact with verified claimants
- **Owner** — reports lost items, browses found items, submits claim requests
- **Admin/Moderator** — oversees platform activity, resolves disputes

### Item Reports
Every report (lost or found) has two layers of information:

- **Public info** (visible to all): category, title/description, approximate location, date, optional image
- **Private verification info** (hidden): brand, specific color, unique markings, contents/accessories, exact location

Private information is never publicly displayed. It is used solely for claim verification.

### Report Types
- **Found-item post** — created by a finder; includes where/when the item was discovered
- **Lost-item report** — created by an owner; includes where/when the item was lost (supports date ranges)

### Report Lifecycle Statuses
- **Active** — open and visible in search/matching
- **Claimed** — a verified claim has been accepted; item return in progress
- **Resolved** — item successfully returned to owner
- **Expired** — configurable time limit passed without resolution
- **Closed** — manually closed by user (e.g., item found elsewhere)

When a lost report and found post are linked through a successful claim, both should update status.

## Feature Areas

### 1. User Account Management
- Registration, login/logout
- Forgot password (logged out), change password (logged in)
- User profile

### 2. Found-Item Posts
- Finder creates post with public + private fields
- Post appears in listings and becomes eligible for matching

### 3. Lost-Item Reports
- Owner creates report with public + private fields
- Report appears in listings and becomes eligible for matching
- Private info on lost reports must also be hidden — prevents finders from using those details to fabricate matching found posts

### 4. Browse & Search
- Search across both found-item posts and lost-item reports
- Filter by: category, location, keywords, date, report type (lost/found)
- Results show only public information
- Finders can browse lost reports; owners can browse found posts

### 5. Automatic Matching
Matching parameters:
- **Category** — must match
- **Location proximity** — within reasonable geographic range
- **Date range** — found date should be on or after lost date (configurable window)
- **Keywords/description** — overlap in title or description terms

Behavior:
- Triggered when a new report (lost or found) is created
- Checks against existing reports of the opposite type
- Suggestions shown to both parties via in-app notification
- Match is a suggestion only — does not auto-initiate a claim

Match statuses:
- **Pending** — suggested, no action taken
- **Claim Submitted** — owner submitted a claim based on this match
- **Dismissed** — one or both parties dismissed the suggestion

### 6. Secure Claim Request
- Owner answers verification questions based on the found item's hidden details
- Questions cover: brand, color, distinguishing marks, exact location, etc.

### 7. Claim Verification & Fraud Prevention
- Limited claim attempts per item per user
- Cooldown periods after failed attempts
- Rate limiting against automated guessing
- Generic error responses (don't reveal which answers were wrong)
- Successful matches forwarded to finder for review

### 8. Claim Review & Contact
- Finder reviews verified claims
- Platform provides controlled contact method between finder and claimant

## User Flows

### Finder Flow
1. Register/login
2. Create found-item post (public + private info)
3. Post visible in listings; system checks for matching lost reports
4. Notified if potential match found
5. Optionally browse lost-item reports
6. Review and approve verified claims

### Owner Flow
1. Register/login
2. Create lost-item report (public + private info)
3. System checks for matching found posts; notified of matches
4. Browse/search found-item listings
5. Submit claim request, answer verification questions
6. If verified, finder reviews and approves contact

### Matching Flow
1. New report created (lost or found)
2. System compares against opposite-type reports (category, location, date, keywords)
3. Both parties notified of potential matches
4. Owner decides whether to submit a claim
5. Finder can dismiss irrelevant suggestions
6. Claims follow standard verification process

## Tech Stack & Architecture

- **Framework:** FastAPI with async/await
- **Database:** PostgreSQL via SQLAlchemy async + asyncpg
- **Migrations:** Alembic (async-compatible)
- **Auth:** JWT (python-jose) + bcrypt (passlib, pinned `bcrypt<4.0.0` for compatibility)
- **Validation:** Pydantic v2 + pydantic-settings
- **Server:** Uvicorn
- **Tests:** pytest + pytest-asyncio + httpx

### Project Structure
Domain-driven modules under `src/app/`:
- `auth/` — registration, login, JWT, token refresh, password management
- `items/` — CRUD for lost and found items (single table, type discriminator)
- `search/` — browse & filter with pagination
- `matching/` — automatic matching engine, match suggestions
- `claims/` — claim submission, verification, fraud prevention
- `notifications/` — in-app notifications
- `utils/` — shared utility functions (e.g. `validators.py` for password strength)
- `middleware/` — CORS (`cors.py`), IP-based rate limiting (`rate_limit.py`)

Each domain follows: `router.py` → `service.py` → `repository.py` + `models.py` + `schemas.py`

### Auth Endpoints
| Method | Path | Auth | Rate Limited |
|--------|------|------|--------------|
| POST | `/api/v1/auth/register` | No | Yes (5/min) |
| POST | `/api/v1/auth/login` | No | Yes (5/min) |
| POST | `/api/v1/auth/refresh` | No (token is credential) | No |
| GET | `/api/v1/auth/me` | Yes | No |
| PUT | `/api/v1/auth/change-password` | Yes | No |

**Token strategy:** Access token (30 min, `type: "access"`) + Refresh token (7 days, `type: "refresh"`), both HS256 JWTs. Refresh rotates both tokens on each call.

**Password rules:** Minimum 8 characters, at least 1 uppercase letter, at least 1 digit. Enforced via `validate_password_strength()` in `utils/validators.py`. Rules are constants in `constants.py`.

### Key Commands
```bash
# Dev server
uvicorn app.main:app --reload --app-dir src

# Migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Tests
pytest

# Docker
docker-compose up
```

### API Prefix
All domain routes are under `/api/v1/`. Health check is at `/health`.

## Out of Scope (MVP)
- Mobile applications
- Map-based item location visualization
- Real-time chat
- Automated image recognition
- Payment/reward systems
- Advanced reputation systems
- AI-based or semantic matching (simple parameter comparison only)

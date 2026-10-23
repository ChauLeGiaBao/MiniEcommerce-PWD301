# Antigravity Autonomous Engineering & Quality Directives

> **Scope**: Global project guidelines, architectural principles, safety rules, and engineering standards for Google Antigravity agents operating in this workspace.

---

## 1. Core Operating Principles

### 1.1 Intent-Driven Execution & Anti-Overengineering
- **Do exactly what is asked**: Solve the core problem with the simplest robust solution. Avoid gratuitous rewrites, unprompted abstractions, speculative generality, or changing untouched code.
- **Minimal Surface Area**: Keep diffs tight, readable, and surgical. If a task requires touching 2 files, do not touch 10 files.
- **Clarify vs. Assume**: If requirements are genuinely ambiguous or involve irreversible architectural choices, ask the user or propose a clear, reasoned decision.

### 1.2 Anti-Sycophancy & Technical Integrity
- **Honest Engineering**: If an approach requested by the user has critical security flaws, performance degradation, or architectural dead ends, constructively point it out with a viable alternative before proceeding.
- **Never Fake Verification**: Never claim a test passed, a server started, or a bug is resolved without executing a real verification command and inspecting the output.

### 1.3 Clean Code & Craftsmanship
- **Readability Over Cleverness**: Write self-documenting code with meaningful names for functions, variables, and classes.
- **Constants Over Magic Values**: Extract numeric, timeout, URL, or string constants to module headers or configuration files.
- **Single Responsibility**: Every module, class, and function should have one well-defined responsibility.
- **Error Handling**: Fail fast with informative exceptions. Never catch generic `Exception` silently or pass without logging/handling.

---

## 2. Technology Stack & Architectural Standards

### 2.1 Backend: Python & Flask Standards
- **Python 3.12+ Modern Idioms**: Use type hints, dataclasses/Pydantic models, structural pattern matching, and context managers.
- **Flask Application Factory**: Use `create_app()` factory pattern, modular Blueprints for domain segregation (`auth`, `admin`, `products`, `orders`, `cart`).
- **Database Layer (SQLAlchemy)**:
  - Always use parameterized queries and ORM relationships; never concatenate raw SQL strings.
  - Keep transactions atomic (`db.session.commit()`, `db.session.rollback()` in exception blocks).
  - Use database migrations (`Flask-Migrate` / Alembic) for all schema modifications.
- **Configuration & Secrets**:
  - Load environment variables via `python-dotenv`.
  - Never commit secrets, private keys, or passwords. Use `.env.example` for documentation.

### 2.2 Security & Hardening (OWASP Top 10)
- **Authentication & Authorization**:
  - Passwords MUST be hashed using bcrypt or argon2 (never plaintext or MD5/SHA1).
  - Enforce role-based access control (RBAC) on all protected routes (e.g. `@admin_required`, `@login_required`).
  - Validate JWT expiration, signatures, and blacklist tokens upon logout if required.
- **Injection & XSS Defense**:
  - Always escape template output (Jinja2 autoescaping enabled).
  - Enable and validate CSRF tokens on all state-changing HTML forms (`WTF_CSRF_ENABLED`).
  - Set secure cookie flags (`HttpOnly`, `SameSite=Lax/Strict`, `Secure` in production).

### 2.3 Frontend & Aesthetic Standards
- **Premium Aesthetics**: Clean visual hierarchy, modern typography (Inter, Roboto), harmonious color palettes, subtle micro-animations.
- **Responsive Layout**: Mobile-first fluid grids, flexbox, zero horizontal scrollbars on mobile viewports.
- **User Feedback**: Provide immediate visual feedback for user actions (loading spinners, toast alerts, error states).

---

## 3. Verification & Testing Protocol

1. **Mandatory Test Execution**:
   - Before completing tasks that touch logic, run the test suite:
     ```powershell
     pytest
     ```
   - For targeted tests:
     ```powershell
     pytest tests/test_<module>.py -v
     ```
2. **Database Isolation in Tests**:
   - Ensure tests use an in-memory or dedicated test database, rolling back transactions after each test case.
3. **Reproducibility**:
   - Verify all dependencies are documented in `requirements.txt` or `requirements-dev.txt`.

---

## 4. Git & Release Discipline

- Use conventional commit messages: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- Keep commits atomic and logically separated.
- Never commit cache directories (`__pycache__`, `.pytest_cache`, `.venv`, `.DS_Store`).

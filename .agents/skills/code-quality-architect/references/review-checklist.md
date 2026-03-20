# Review Checklist

Use this checklist to systematically review generated code before finalization.

## 1. Correctness & Logic
- [ ] Does the code fulfill all functional requirements?
- [ ] Are there any obvious logic flaws or off-by-one errors?
- [ ] is edge case handling present (empty inputs, null values, errors)?

## 2. Security
- [ ] Are there any hardcoded secrets or credentials?
- [ ] Is input validation performed where necessary?
- [ ] Are common vulnerabilities addressed (SQL injection, XSS, insecure defaults)?

## 3. Readability & Maintainability
- [ ] Are variable and function names descriptive and idiomatic?
- [ ] Is the code properly modularized (no "God functions")?
- [ ] Are comments meaningful (explaining *why*, not *what*)?
- [ ] is the DRY (Don't Repeat Yourself) principle followed?

## 4. Performance & Efficiency
- [ ] Are there any unnecessary loops or heavy operations?
- [ ] Is memory usage considered for large data structures?
- [ ] Are efficient built-in functions/libraries used?

## 5. Standards & Style
- [ ] Does the code follow language-specific standards (PEP 8 for Python, etc.)?
- [ ] are types/interfaces defined where appropriate (TypeScript, Python type hints)?
- [ ] Is the formatting consistent?

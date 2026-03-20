---
name: code-quality-architect
description: Generates high-quality code and performs automated self-reviews. Use when creating new features, refactoring logic, or implementing complex algorithms to ensure adherence to best practices, security, and performance standards.
---

# Code Quality Architect

## Overview
This skill implements a rigorous "Plan → Build → Review → Refine" workflow. It ensures that every piece of code generated is not only functional but also secure, idiomatic, and maintainable.

## Core Workflow

### 1. Requirements Gathering
- Understand the user's request and clarify any ambiguities.
- Identify the target language, framework, and any specific constraints.

### 2. Implementation (Plan & Build)
- Reference [best-practices.md](references/best-practices.md) for language-specific standards.
- Generate the code, prioritizing readability and correctness.
- Ensure proper type safety and documentation are included from the start.

### 3. Automated Self-Review
- IMMEDIATELY after generating the code, load and execute the [review-checklist.md](references/review-checklist.md).
- Critically evaluate the code against each category: Logic, Security, Readability, Performance, and Style.
- Identify at least 2-3 potential improvements or points of verification.

### 4. Refinement
- Apply the fixes or optimizations identified in the review.
- If the changes are significant, explain the rationale behind the refinements.

### 5. Final Presentation
- Present the final, polished code.
- Provide a brief "Review Summary" highlighting the improvements made during the refinement phase.

## Guidelines for Review
- **Be your own harshest critic**: Don't settle for the first working solution.
- **Look for edge cases**: What happens if input is empty? What if the network fails?
- **Enforce consistency**: Ensure naming and structure match the existing codebase if applicable.
- **Security first**: Never ignore hardcoded paths or lack of validation.

## Example Triggers
- "Create a Python script to process these logs..."
- "Refactor this TypeScript function to be more efficient..."
- "Write a new API endpoint for handling user uploads..."
- "Implement a sorting algorithm for this specific data structure..."

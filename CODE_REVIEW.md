# Code Review Summary

## Critical Issues

### 1. Missing Context Initialization
**File:** `django_mongodb_cli/utils.py`
**Issue:** `self.ctx` is accessed without initialization in `ensure_repo()` and other methods.
**Fix:** Initialize `self.ctx = None` in `__init__` and add guards before accessing.

### 2. Incorrect Path Handling
**File:** `django_mongodb_cli/project.py:434`
**Issue:** `directory = Path(name)` overwrites the function parameter.
**Fix:** Use the `directory` parameter that was passed in.

## High Priority

### 3. Duplicate Import Statements
**File:** `django_mongodb_cli/utils.py`
**Issue:** `re` is imported at module level (line 2) but also inside methods (lines 809, 836).
**Fix:** Remove redundant imports inside methods.

### 4. Inconsistent Executable Reference
**Files:** `django_mongodb_cli/utils.py:859`, `django_mongodb_cli/__init__.py:15`
**Issue:** Uses `os.sys.executable` instead of standard `sys.executable`.
**Fix:** Use `sys.executable` consistently.

### 5. Missing Error Handling
**File:** `django_mongodb_cli/project.py:342`
**Issue:** `subprocess.run()` result not checked for frontend install.
**Fix:** Check return code and handle failures.

## Medium Priority

### 6. Missing Return Type Annotations
**Issue:** Many functions lack return type hints.
**Fix:** Add return type annotations for better type safety.

### 7. Duplicate MONGODB_URI Logic
**Files:** `django_mongodb_cli/repo.py`, `django_mongodb_cli/project.py`
**Issue:** MONGODB_URI handling duplicated in multiple places.
**Fix:** Centralize in a utility function.

## Low Priority / Nice to Have

### 8. Code Organization
- Consider extracting constants to a separate file
- Some methods in `Repo` class are quite long (e.g., `install_package`)

### 9. Documentation
- Add docstrings to some helper functions
- Consider adding type hints to all public methods

### 10. Testing
- No visible test files for the CLI itself
- Consider adding unit tests for utility functions

## Positive Aspects

✅ Good use of Typer for CLI structure
✅ Helpful user feedback with emojis and colors
✅ Pre-commit hooks configured
✅ No linting errors
✅ Good separation of concerns
✅ Safe command parsing with `shlex.split`
✅ Comprehensive error messages

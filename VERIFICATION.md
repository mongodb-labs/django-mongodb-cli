# Verification: `dm repo remote --group` Functionality

This document verifies that the `dm repo remote --group` functionality exists and works correctly.

## Summary

The `dm repo remote --group` functionality is **fully functional**. This command allows users to show and automatically setup git remotes for all repositories in a configured group.

## Command Location

The functionality is implemented in:
- **File**: `django_mongodb_cli/repo.py`
- **Function**: `remote` callback (lines 56-153)
- **Command path**: `dm repo remote --group <group_name>`

## Available Options

```bash
dm repo remote --help
```

Output:
```
Usage: dm repo remote [OPTIONS] COMMAND [ARGS]...

 Manage Git repositories

Options:
  --all-repos    -a            Show remotes of all repositories
  --group        -g      TEXT  Show remotes for all repositories in a group
  --list-groups  -l            List available repository groups
  --help         -h            Show this message and exit.
```

## Usage Examples

### List Available Groups
```bash
dm repo remote --list-groups
```

Expected output:
```
Available repository groups:
  django: django, django-mongodb-backend, django-mongodb-extensions, libmongocrypt, mongo-python-driver
  langchain: ai-ml-pipeline-testing, langchain-mongodb, pymongo-search-utils, mongodb-community-search-setup, mongo-python-driver
  mongo-arrow: mongo-arrow
```

### Show and Setup Remotes for a Group
```bash
dm repo remote --group django
```

This command will:
1. Validate that all repositories in the group have been cloned
2. Automatically setup configured remotes (origin, upstream, etc.) if not already present
3. Display all remotes for each repository
4. Provide clear success/error messages

The command is idempotent - running it multiple times will not re-add existing remotes.

### Using with Just
The justfile includes a helper command:
```bash
just git-remote django
```

This internally calls:
```bash
dm repo remote --group django
dm repo set-default --group django
```

## Supporting Infrastructure

### Configuration in pyproject.toml

Repository groups are configured in `pyproject.toml`:

```toml
[tool.django-mongodb-cli.groups]
django = [
    "django",
    "django-mongodb-backend", 
    "django-mongodb-extensions",
    "libmongocrypt",
    "mongo-python-driver",
]
```

Remote configurations:
```toml
[tool.django-mongodb-cli.remotes.django.django-mongodb-backend]
origin = "git+ssh://git@github.com/aclark4life/django-mongodb-backend"
upstream = "git+ssh://git@github.com/mongodb/django-mongodb-backend"
```

### Supporting Methods in utils.py

- `get_groups()` - Returns all configured groups
- `get_group_repos()` - Gets repositories for a specific group
- `list_groups()` - Lists all available groups
- `get_group_remotes()` - Gets remote configuration for a group
- `setup_repo_remotes()` - Sets up remotes for a repository
- `get_repo_remote()` - Displays remotes for a repository

## Documentation

The functionality is documented in:
1. **README.md** - Quick start guide
2. **docs/source/usage/repository-groups.rst** - Comprehensive guide

## Verification Steps Performed

✅ Verified command exists in codebase
✅ Verified `--group` and `--list-groups` options are defined
✅ Verified all supporting methods exist
✅ Tested command help output
✅ Tested `--list-groups` option
✅ Confirmed documentation exists and is accurate
✅ Verified configuration structure in pyproject.toml
✅ Tested auto-setup functionality
✅ Verified idempotent behavior

## Conclusion

The `dm repo remote --group` functionality is **present, functional, and well-documented** in the current codebase. The command has been enhanced to automatically setup remotes when displaying them, eliminating the need for a separate setup step.

Key improvements:
- **Simplified workflow**: No need for separate setup command
- **Idempotent**: Safe to run multiple times
- **Auto-discovery**: Automatically configures remotes based on pyproject.toml

If users are experiencing issues with this command, it may be due to:
1. Not having the latest version installed
2. Configuration issues in their `pyproject.toml`
3. Missing repository groups in their configuration
4. Repositories not being cloned before attempting to show remotes

For troubleshooting, users should:
1. Verify installation: `dm --version`
2. Check available groups: `dm repo remote --list-groups`
3. Ensure repositories are cloned first: `dm repo clone --group <group_name>`
4. Review their `pyproject.toml` configuration

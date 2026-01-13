# Fix for "dm repo test langchain-mongodb -k langgraph" Import Error

## Quick Fix Instructions

If you're getting this error when running `dm repo test langchain-mongodb -k langgraph`:
```
ImportError: cannot import name 'content' from 'langchain_core.messages'
```

Apply the fix patch:

```bash
cd src/langchain-mongodb
git apply ../../langchain-mongodb-import-fix.patch
cd ../..
dm repo test langchain-mongodb -k langgraph
```

## What this fixes

The patch makes langchain_ollama imports optional in test files so that:
- Test collection doesn't fail when langchain_ollama is incompatible with langchain_core
- Tests that don't use langchain_ollama (like langgraph tests) can run successfully
- The fix is backward compatible with environments where langchain_ollama works

## More details

See LANGCHAIN_MONGODB_FIX.md for detailed documentation and manual fix instructions.

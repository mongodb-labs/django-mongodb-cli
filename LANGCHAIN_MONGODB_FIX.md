# Fix for langchain-mongodb Test Import Error

## Problem
When running `dm repo test langchain-mongodb -k langgraph`, pytest fails during test collection with:
```
ImportError: cannot import name 'content' from 'langchain_core.messages'
```

This error originates from `langchain_ollama` being incompatible with the installed version of `langchain_core`.

## Root Cause
The `dm repo test langchain-mongodb -k langgraph` command collects tests from both:
- `src/langchain-mongodb/libs/langchain-mongodb/tests` 
- `src/langchain-mongodb/libs/langgraph-store-mongodb/tests`

During collection, pytest imports test utility files which have hard imports of `langchain_ollama`, even though the `-k langgraph` filter means those tests won't actually run.

## Solution
Make the `langchain_ollama` imports optional so test collection doesn't fail when the package is not installed or incompatible.

## Changes Required

### File 1: `src/langchain-mongodb/libs/langchain-mongodb/tests/utils.py`

Replace:
```python
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI, ChatOpenAI
```

With:
```python
from langchain_core.outputs import ChatGeneration, ChatResult

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None  # type: ignore

from langchain_openai import AzureChatOpenAI, ChatOpenAI
```

And replace the `create_llm()` function:
```python
def create_llm() -> BaseChatModel:
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return AzureChatOpenAI(model="o4-mini", timeout=60, cache=False, seed=12345)
    if os.environ.get("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", timeout=60, cache=False, seed=12345)
    return ChatOllama(model="llama3:8b", cache=False, seed=12345)
```

With:
```python
def create_llm() -> BaseChatModel:
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return AzureChatOpenAI(model="o4-mini", timeout=60, cache=False, seed=12345)
    if os.environ.get("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", timeout=60, cache=False, seed=12345)
    if ChatOllama is not None:
        return ChatOllama(model="llama3:8b", cache=False, seed=12345)
    raise ImportError(
        "No chat model available. Please set AZURE_OPENAI_ENDPOINT or OPENAI_API_KEY, "
        "or install langchain-ollama."
    )
```

### File 2: `src/langchain-mongodb/libs/langchain-mongodb/tests/integration_tests/conftest.py`

Replace:
```python
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
```

With:
```python
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

try:
    from langchain_ollama.embeddings import OllamaEmbeddings
except ImportError:
    OllamaEmbeddings = None  # type: ignore

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
```

And replace the `embedding()` fixture:
```python
@pytest.fixture(scope="session")
def embedding() -> Embeddings:
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAIEmbeddings(
            openai_api_key=os.environ["OPENAI_API_KEY"],  # type: ignore # noqa
            model="text-embedding-3-small",
        )
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return AzureOpenAIEmbeddings(model="text-embedding-3-small")

    return OllamaEmbeddings(model="all-minilm:l6-v2")
```

With:
```python
@pytest.fixture(scope="session")
def embedding() -> Embeddings:
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAIEmbeddings(
            openai_api_key=os.environ["OPENAI_API_KEY"],  # type: ignore # noqa
            model="text-embedding-3-small",
        )
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return AzureOpenAIEmbeddings(model="text-embedding-3-small")

    if OllamaEmbeddings is not None:
        return OllamaEmbeddings(model="all-minilm:l6-v2")
    
    raise ImportError(
        "No embedding model available. Please set OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT, "
        "or install langchain-ollama."
    )
```

## Applying the Fix

### Option 1: Apply as a patch
Save the git diff output to a file and apply it:
```bash
cd src/langchain-mongodb
# Apply the changes manually or use git apply with a patch file
```

### Option 2: Manual edit
Edit the two files listed above directly in your `src/langchain-mongodb` clone.

## Verification

After applying the fix, test collection should work:
```bash
dm repo test langchain-mongodb -k langgraph
```

The command should now complete test collection without the `langchain_ollama` import error.

## Notes
- This fix makes `langchain_ollama` optional during import
- Tests that actually need `langchain_ollama` will fail at runtime with a clear error message
- Tests that don't need it (like the langgraph tests) will work fine
- The fix is backward compatible - when `langchain_ollama` is properly installed, everything works as before

# `.evergreen` Shell Script Dependency Map (mongo-python-driver, drivers-evergreen-tools)

This document describes how the `.sh` scripts under `src/mongo-python-driver/.evergreen` and `src/drivers-evergreen-tools/.evergreen`
depend on and call each other (and key external scripts).

Arrows mean “calls or sources”.

---

## 0. Evergreen generated configs

The `.evergreen/generated_configs/*.yml` files that reference these shell scripts are **generated**, not hand-written:

- Entry config: [`.evergreen/config.yml`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/config.yml) includes:
  - [`.evergreen/generated_configs/functions.yml`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/generated_configs/functions.yml)
  - [`.evergreen/generated_configs/tasks.yml`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/generated_configs/tasks.yml)
  - [`.evergreen/generated_configs/variants.yml`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/generated_configs/variants.yml)
- Generator:
  - Shell entrypoint: [`.evergreen/scripts/generate-config.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/generate-config.sh)
  - Python generator: [`.evergreen/scripts/generate_config.py`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/generate_config.py)
- To regenerate configs after changing the generator:

  ```bash
  bash .evergreen/scripts/generate-config.sh
  ```

  This re-writes the three `generated_configs` files based on the logic in `generate_config.py` / `generate_config_utils.py`.

---

## 1. High-level overview

Key top-level scripts (GitHub):
- [`.evergreen/combine-coverage.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/combine-coverage.sh)
- [`.evergreen/just.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/just.sh)
- [`.evergreen/remove-unimplemented-tests.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/remove-unimplemented-tests.sh)
- [`.evergreen/resync-specs.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/resync-specs.sh)
- [`.evergreen/run-mongodb-aws-ecs-test.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/run-mongodb-aws-ecs-test.sh) — indirectly uses **drivers-evergreen-tools** via `setup_tests.py` / `run_tests.py`
- [`.evergreen/run-mongodb-oidc-test.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/run-mongodb-oidc-test.sh) — indirectly uses **drivers-evergreen-tools** via `setup_tests.py` / `run_tests.py`
- [`.evergreen/run-tests.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/run-tests.sh) — indirectly uses **drivers-evergreen-tools** via `run_tests.py`
- [`.evergreen/setup-spawn-host.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/setup-spawn-host.sh) — indirectly uses **drivers-evergreen-tools** via remote `setup-system.sh`
- [`.evergreen/sync-spawn-host.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/sync-spawn-host.sh)

Key helper scripts under `.evergreen/scripts/` (GitHub):
- [`.evergreen/scripts/check-import-time.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/check-import-time.sh)
- [`.evergreen/scripts/cleanup.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/cleanup.sh) — cleans up **drivers-evergreen-tools** checkout (`$DRIVERS_TOOLS`)
- [`.evergreen/scripts/configure-env.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/configure-env.sh) — clones and configures **drivers-evergreen-tools** into `$DRIVERS_TOOLS`
- [`.evergreen/scripts/create-spec-pr.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/create-spec-pr.sh) — uses **drivers-evergreen-tools** GitHub app under `../drivers-tools/.evergreen/github_app`
- [`.evergreen/scripts/download-and-merge-coverage.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/download-and-merge-coverage.sh)
- [`.evergreen/scripts/generate-config.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/generate-config.sh)
- [`.evergreen/scripts/install-dependencies.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/install-dependencies.sh)
- [`.evergreen/scripts/perf-submission-setup.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/perf-submission-setup.sh)
- [`.evergreen/scripts/perf-submission.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/perf-submission.sh)
- [`.evergreen/scripts/resync-all-specs.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/resync-all-specs.sh)
- [`.evergreen/scripts/run-getdata.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/run-getdata.sh) — sources `${DRIVERS_TOOLS}/.evergreen/get-distro.sh` from **drivers-evergreen-tools**
- [`.evergreen/scripts/run-server.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/run-server.sh)
- [`.evergreen/scripts/setup-dev-env.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-dev-env.sh)
- [`.evergreen/scripts/setup-system.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-system.sh) — calls `$DRIVERS_TOOLS/.evergreen/setup.sh` in **drivers-evergreen-tools**
- [`.evergreen/scripts/setup-tests.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-tests.sh)
- [`.evergreen/scripts/setup-uv-python.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-uv-python.sh)
- [`.evergreen/scripts/stop-server.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/stop-server.sh) — calls `${DRIVERS_TOOLS}/.evergreen/stop-orchestration.sh` in **drivers-evergreen-tools**
- [`.evergreen/scripts/teardown-tests.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/teardown-tests.sh)
- [`.evergreen/scripts/upload-coverage-report.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/upload-coverage-report.sh)

```text
Top-level entry scripts (Evergreen / humans)
────────────────────────────────────────────
combine-coverage.sh
just.sh
remove-unimplemented-tests.sh
resync-specs.sh
run-mongodb-aws-ecs-test.sh
run-mongodb-oidc-test.sh
run-tests.sh
setup-spawn-host.sh
sync-spawn-host.sh

Core helper scripts under .evergreen/scripts
─────────────────────────────────────────────
- env/test env handling:
    env.sh            (generated by configure-env.sh)
    test-env.sh       (generated by setup_tests.py)
    setup-system.sh
    configure-env.sh
    setup-dev-env.sh
    setup-uv-python.sh
    install-dependencies.sh
    cleanup.sh

- test lifecycle:
    setup-tests.sh
    run-tests.sh      (top-level)
    teardown-tests.sh

- specs:
    resync-specs.sh   (top-level)
    scripts/resync-all-specs.sh
    scripts/create-spec-pr.sh

- coverage:
    combine-coverage.sh    (top-level)
    scripts/download-and-merge-coverage.sh
    scripts/upload-coverage-report.sh

- misc:
    scripts/check-import-time.sh
    scripts/run-server.sh
    scripts/run-getdata.sh
    scripts/perf-submission-setup.sh
    scripts/perf-submission.sh
    scripts/generate-config.sh
    scripts/stop-server.sh
    setup-spawn-host.sh
    sync-spawn-host.sh
```

---

## 2. Main flows / chains

### 2.1 Dev/test environment flow

Key scripts:
- [`.evergreen/combine-coverage.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/combine-coverage.sh)
- [`.evergreen/just.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/just.sh)
- [`.evergreen/scripts/check-import-time.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/check-import-time.sh)
- [`.evergreen/scripts/setup-dev-env.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-dev-env.sh)
- [`.evergreen/scripts/install-dependencies.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/install-dependencies.sh)
- [`.evergreen/scripts/setup-uv-python.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-uv-python.sh)

```text
combine-coverage.sh
  -> .evergreen/scripts/setup-dev-env.sh
       -> env.sh         (if present, sourced)
       -> test-env.sh    (if present, sourced)
       -> install-dependencies.sh
       -> setup-uv-python.sh
```

```text
just.sh
  -> .evergreen/scripts/setup-dev-env.sh
       -> env.sh
       -> test-env.sh
       -> install-dependencies.sh
       -> setup-uv-python.sh
```

```text
scripts/check-import-time.sh
  -> scripts/env.sh
  -> scripts/setup-dev-env.sh
       -> env.sh
       -> test-env.sh
       -> install-dependencies.sh
       -> setup-uv-python.sh
```

**Example tests using these scripts**

- Any Evergreen task that uses the `run tests` function in `.evergreen/generated_configs/functions.yml` goes through `.evergreen/just.sh setup-tests` → `scripts/setup-dev-env.sh` → `scripts/setup-tests.sh` and finally `run-tests.sh`.
- Examples:
  - `test-no-toolchain-sync-noauth-nossl-standalone` → `TEST_NAME=default_sync` (sync CRUD-style tests against a standalone server).
  - `test-no-toolchain-async-noauth-ssl-replica-set` → `TEST_NAME=default_async` (async tests against a replica set, SSL on).
  - `test-aws-lambda-deployed` → `TEST_NAME=aws_lambda` (Lambda packaging/perf tests, still driven by `setup-tests` + `run-tests`).
  - `test-min-deps-python3.10-sync-noauth-nossl-standalone` → `TEST_MIN_DEPS=1` and minimal dependency resolution, but still via the same `setup-dev-env.sh` + `setup-tests.sh` + `run-tests.sh` chain.

### 2.2 System + spawn-host setup

Key scripts:
- [`.evergreen/scripts/setup-system.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-system.sh)
- [`.evergreen/scripts/configure-env.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/configure-env.sh)
- [`.evergreen/scripts/setup-dev-env.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-dev-env.sh)
- [`.evergreen/setup-spawn-host.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/setup-spawn-host.sh)
- [`.evergreen/sync-spawn-host.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/sync-spawn-host.sh)

```text
scripts/setup-system.sh
  -> scripts/configure-env.sh
       -> (writes) scripts/env.sh
       -> (clones) drivers-evergreen-tools into $DRIVERS_TOOLS
       -> (writes) $DRIVERS_TOOLS/.env
  -> scripts/env.sh
  -> $DRIVERS_TOOLS/.evergreen/setup.sh      (external, from drivers-evergreen-tools)
  -> scripts/setup-dev-env.sh (if not CI)
       -> install-dependencies.sh
       -> setup-uv-python.sh
       -> env.sh / test-env.sh (if present)
```

```text
setup-spawn-host.sh
  -> (rsync project to remote)
  -> ssh $target "$remote_dir/.evergreen/scripts/setup-system.sh"
```

```text
sync-spawn-host.sh
  -> (rsync + fswatch loop; no extra .sh deps)
```

**Example usages / test flows**

- Evergreen tasks that use the `setup system` function in `.evergreen/generated_configs/functions.yml` invoke `scripts/setup-system.sh` before running their actual tests.
- Typical pattern on a spawn host:
  - Locally: `./.evergreen/setup-spawn-host.sh user@host` to rsync the repo and run `setup-system.sh` remotely.
  - On the host: run `just setup-tests <TEST_NAME> <SUB_TEST_NAME>` followed by `just run-tests` (for example, `just setup-tests default_sync standalone` + `just run-tests`).
- This means **any** test suite (sync/async, auth_aws, kms, ocsp, perf, etc.) can be run on a spawn host once `setup-system.sh` has prepared MongoDB + drivers-tools.

### 2.3 Test lifecycle (setup / run / teardown)

Key scripts:
- [`.evergreen/scripts/setup-tests.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup-tests.sh)
- [`.evergreen/run-tests.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/run-tests.sh)
- [`.evergreen/scripts/teardown-tests.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/teardown-tests.sh)
- [`.evergreen/scripts/setup_tests.py`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/setup_tests.py)
- [`.evergreen/scripts/run_tests.py`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/run_tests.py)
- [`.evergreen/scripts/teardown_tests.py`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/teardown_tests.py)

```text
scripts/setup-tests.sh
  -> scripts/env.sh       (if present)
  -> (python) scripts/setup_tests.py
       -> generates scripts/test-env.sh
```

```text
run-tests.sh
  -> scripts/env.sh       (if present)
  -> scripts/test-env.sh  (required; generated)
  -> (python) scripts/run_tests.py
```

```text
scripts/teardown-tests.sh
  -> scripts/env.sh       (if present)
  -> scripts/test-env.sh  (if present)
  -> (python) scripts/teardown_tests.py
```

**Example Evergreen tasks hitting this lifecycle**

All tasks that call the `run tests` function in `.evergreen/generated_configs/functions.yml` eventually invoke:

```text
.evergreen/just.sh setup-tests ${TEST_NAME} ${SUB_TEST_NAME}
.evergreen/just.sh run-tests
```

which maps to `scripts/setup-tests.sh` and `run-tests.sh`.

Sample tasks and the tests they run:

- **Core sync/async suites**
  - `test-no-toolchain-sync-noauth-nossl-standalone` → `TEST_NAME=default_sync` → sync tests against standalone, no auth, no SSL.
  - `test-no-toolchain-async-noauth-ssl-replica-set` → `TEST_NAME=default_async` → async tests against a replica set with SSL.
- **AWS lambda / performance**
  - `test-aws-lambda-deployed` → `TEST_NAME=aws_lambda` → builds a Lambda-compatible wheel and runs `test/lambda` perf/functional tests.
- **KMS / FLE**
  - `test-gcpkms` → `TEST_NAME=kms`, `SUB_TEST_NAME=gcp` → KMS tests that ultimately drive remote or local KMS helpers via `kms_tester`.
  - `test-gcpkms-fail` / `test-azurekms-fail` → same `TEST_NAME=kms` with failure scenarios and orchestration.
- **OCSP**
  - Any `test-ocsp-*` task (e.g. `test-ocsp-ecdsa-valid-cert-server-does-not-staple-v4.4-python3.10`) → `TEST_NAME=ocsp`, various `ORCHESTRATION_FILE`/`OCSP_SERVER_TYPE` combinations.
- **mod_wsgi**
  - `mod-wsgi-replica-set-python3.10` → `TEST_NAME=mod_wsgi`, `SUB_TEST_NAME=standalone` → WSGI integration tests.
- **Perf harness**
  - Tasks with `TEST_PERF` set (not shown here) use the same `run-tests.sh` entrypoint, but `run_tests.py` writes `results.json` / `report.json` via `handle_perf`.

### 2.4 AWS / OIDC auth test flows

Key scripts:
- [`.evergreen/run-mongodb-aws-ecs-test.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/run-mongodb-aws-ecs-test.sh)
- [`.evergreen/run-mongodb-oidc-test.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/run-mongodb-oidc-test.sh)
- [`.evergreen/just.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/just.sh)

```text
run-mongodb-aws-ecs-test.sh
  -> .evergreen/just.sh setup-tests auth_aws ecs-remote
       -> scripts/setup-dev-env.sh
       -> scripts/setup-tests.sh        (via just recipe)
  -> .evergreen/just.sh run-tests
       -> scripts/setup-dev-env.sh
       -> run-tests.sh
            -> scripts/env.sh
            -> scripts/test-env.sh
            -> scripts/run_tests.py
```

```text
run-mongodb-oidc-test.sh
  -> .evergreen/just.sh setup-tests auth_oidc $SUB_TEST_NAME
       -> scripts/setup-dev-env.sh
       -> scripts/setup-tests.sh
  -> .evergreen/just.sh run-tests
       -> scripts/setup-dev-env.sh
       -> run-tests.sh
            -> scripts/env.sh
            -> scripts/test-env.sh
            -> scripts/run_tests.py
```

**Example AWS / OIDC tasks**

- **AWS auth (Evergreen)** — from `.evergreen/generated_configs/tasks.yml`:
  - `test-auth-aws-4.4-regular-python3.10` → `TEST_NAME=auth_aws`, `SUB_TEST_NAME=regular`.
  - `test-auth-aws-6.0-ec2-python3.12` → `TEST_NAME=auth_aws`, `SUB_TEST_NAME=ec2`.
  - `test-auth-aws-latest-ecs-python3.10` → `TEST_NAME=auth_aws`, `SUB_TEST_NAME=ecs`.
  - All of these flow through the generic `run tests` function (`just setup-tests` + `just run-tests`) and therefore use `setup-tests.sh` / `run-tests.sh` on the Evergreen host.
- **AWS ECS remote**
  - For the **remote ECS host** itself, `.evergreen/run-mongodb-aws-ecs-test.sh` is the entrypoint; it consumes a `MONGODB_URI`, then invokes `just setup-tests auth_aws ecs-remote` and `just run-tests` inside the repo, reusing the same test harness.
- **OIDC auth**
  - OIDC Evergreen tasks use `TEST_NAME=auth_oidc` and various `SUB_TEST_NAME` values (e.g. `azure-remote`, `okta-remote`, `k8s-remote`).
  - On the remote OIDC host, `.evergreen/run-mongodb-oidc-test.sh` uses `$OIDC_ENV` / `$K8S_VARIANT` to construct `SUB_TEST_NAME=${OIDC_ENV}-remote` and then runs `just setup-tests auth_oidc <sub>` + `just run-tests`.

### 2.5 Specs resync + PR creation

Key scripts:
- [`.evergreen/scripts/resync-all-specs.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/resync-all-specs.sh)
- [`.evergreen/resync-specs.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/resync-specs.sh)
- [`.evergreen/scripts/create-spec-pr.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/create-spec-pr.sh)

```text
scripts/resync-all-specs.sh
  -> ../resync-specs.sh           (top-level .evergreen/resync-specs.sh)
  -> scripts/create-spec-pr.sh    (only under CI / when changes exist)
       -> ../drivers-tools/.evergreen/github_app/utils.sh
       -> ../drivers-tools/.evergreen/github_app/get-access-token.sh
```

```text
resync-specs.sh (top-level)
  -> (no further .sh deps; does all work inline)
```

**Examples of spec suites affected**

- Running `.evergreen/resync-specs.sh crud` will:
  - Replace JSON spec files under `test/crud/` with those from the `specifications` repo.
  - Affect CRUD-related unified tests (e.g. `test_crud_unified_*` pytest cases) that load those JSONs.
- Running `.evergreen/resync-specs.sh unified` will:
  - Update `test/unified-test-format/` from `unified-test-format/tests/` in the `specifications` repo.
  - Affect unified test runners that execute JSON test definitions across many areas (transactions, retryable reads/writes, SDAM, etc.).
- The CI entrypoint `.evergreen/scripts/resync-all-specs.sh`:
  - Clones `github.com/mongodb/specifications` if needed.
  - Runs a Python helper to choose which specs to sync.
  - If changes are detected, calls `scripts/create-spec-pr.sh` to open a `[Spec Resync]` pull request containing only spec-test updates.

### 2.6 Coverage download / upload

Key scripts:
- [`.evergreen/scripts/download-and-merge-coverage.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/download-and-merge-coverage.sh)
- [`.evergreen/combine-coverage.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/combine-coverage.sh)
- [`.evergreen/scripts/upload-coverage-report.sh`](https://github.com/mongodb/mongo-python-driver/blob/master/.evergreen/scripts/upload-coverage-report.sh)

```text
scripts/download-and-merge-coverage.sh
  -> (no .sh deps; uses aws cli)

combine-coverage.sh
  -> scripts/setup-dev-env.sh
  -> (coverage combine / coverage html)

scripts/upload-coverage-report.sh
  -> (no .sh deps; uses aws cli)
```

**Example coverage-related tasks**

- Evergreen function `download and merge coverage` in `.evergreen/generated_configs/functions.yml`:
  - Downloads raw `.coverage` files from S3 using `scripts/download-and-merge-coverage.sh`.
  - Runs `.evergreen/combine-coverage.sh` to `coverage combine` all task coverage into a single DB and generate `htmlcov/`.
  - Uploads the HTML report via `scripts/upload-coverage-report.sh`.
- The `coverage-report` task in `.evergreen/generated_configs/tasks.yml`:
  - Depends on all test tasks tagged with `coverage` and then runs the `download and merge coverage` function.
  - Produces a combined report that includes coverage from suites such as `default_sync`, `default_async`, `auth_aws`, `kms`, `ocsp`, etc., i.e., anything that ran with `COVERAGE` enabled and uploaded a per-task `.coverage` file.

---

## 3. Adjacency list (per script)

### 3.1 Top-level `.evergreen/*.sh`

```text
combine-coverage.sh
  -> scripts/setup-dev-env.sh

just.sh
  -> scripts/setup-dev-env.sh

remove-unimplemented-tests.sh
  -> (no .sh dependencies)

resync-specs.sh
  -> (no .sh dependencies)

run-mongodb-aws-ecs-test.sh
  -> .evergreen/just.sh

run-mongodb-oidc-test.sh
  -> .evergreen/just.sh

run-tests.sh
  -> scripts/env.sh        (if exists)
  -> scripts/test-env.sh   (if exists)
  -> (python) scripts/run_tests.py

setup-spawn-host.sh
  -> remote .evergreen/scripts/setup-system.sh (over ssh)

sync-spawn-host.sh
  -> (no extra .sh dependencies; rsync + fswatch)
```

### 3.2 `.evergreen/scripts/*.sh`

```text
scripts/check-import-time.sh
  -> scripts/env.sh
  -> scripts/setup-dev-env.sh

scripts/cleanup.sh
  -> scripts/env.sh        (if exists)

scripts/configure-env.sh
  -> scripts/env.sh        (if env.sh already exists, it is sourced)
  -> (writes) scripts/env.sh
  -> (clones) drivers-evergreen-tools into $DRIVERS_TOOLS
  -> (writes) $DRIVERS_TOOLS/.env

scripts/create-spec-pr.sh
  -> ../drivers-tools/.evergreen/github_app/utils.sh
  -> ../drivers-tools/.evergreen/github_app/get-access-token.sh

scripts/download-and-merge-coverage.sh
  -> (no .sh deps)

scripts/generate-config.sh
  -> (no .sh deps; runs generate_config.py)

scripts/install-dependencies.sh
  -> scripts/env.sh        (if exists)

scripts/perf-submission-setup.sh
  -> (no .sh deps)

scripts/perf-submission.sh
  -> (no .sh deps)

scripts/resync-all-specs.sh
  -> ../resync-specs.sh
  -> scripts/create-spec-pr.sh

scripts/run-getdata.sh
  -> ${DRIVERS_TOOLS}/.evergreen/get-distro.sh

scripts/run-server.sh
  -> scripts/env.sh

scripts/setup-dev-env.sh
  -> scripts/env.sh        (if exists)
  -> scripts/test-env.sh   (if exists)
  -> scripts/install-dependencies.sh
  -> scripts/setup-uv-python.sh

scripts/setup-system.sh
  -> scripts/configure-env.sh
  -> scripts/env.sh
  -> $DRIVERS_TOOLS/.evergreen/setup.sh
  -> scripts/setup-dev-env.sh   (if not CI)

scripts/setup-tests.sh
  -> scripts/env.sh        (if exists)
  -> (python) scripts/setup_tests.py

scripts/setup-uv-python.sh
  -> scripts/env.sh        (if exists)
  -> scripts/test-env.sh   (if exists)

scripts/stop-server.sh
  -> scripts/env.sh        (if exists)
  -> ${DRIVERS_TOOLS}/.evergreen/stop-orchestration.sh

scripts/teardown-tests.sh
  -> scripts/env.sh        (if exists)
  -> scripts/test-env.sh   (if exists)
  -> (python) scripts/teardown_tests.py

scripts/upload-coverage-report.sh
  -> (no .sh deps)
```

---

## 4. drivers-evergreen-tools `.evergreen` dependency map

This section summarizes the main shell scripts under `src/drivers-evergreen-tools/.evergreen` that are used by `mongo-python-driver`, and how they depend on each other. Links point to the upstream
`mongodb-labs/drivers-evergreen-tools` repository.

### 4.1 Orchestration core

Key scripts:
- [`.evergreen/run-orchestration.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/run-orchestration.sh)
- [`.evergreen/start-orchestration.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/start-orchestration.sh)
- [`.evergreen/stop-orchestration.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/stop-orchestration.sh)
- [`.evergreen/orchestration/setup.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/orchestration/setup.sh)
- [`.evergreen/orchestration/drivers-orchestration`](https://github.com/mongodb-labs/drivers-evergreen-tools/tree/master/.evergreen/orchestration)
- [`.evergreen/handle-paths.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/handle-paths.sh)

```text
run-orchestration.sh
  -> handle-paths.sh
  -> orchestration/setup.sh
  -> orchestration/drivers-orchestration run

start-orchestration.sh
  -> handle-paths.sh
  -> orchestration/setup.sh
  -> orchestration/drivers-orchestration start

stop-orchestration.sh
  -> handle-paths.sh
  -> orchestration/setup.sh
  -> orchestration/drivers-orchestration stop
```

These are the entrypoints pymongo uses (indirectly) to start/stop MongoDB topologies via drivers-evergreen-tools.

### 4.2 drivers-evergreen-tools setup / teardown

Key scripts:
- [`.evergreen/setup.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/setup.sh)
- [`.evergreen/teardown.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/teardown.sh)
- [`.evergreen/orchestration/setup.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/orchestration/setup.sh)
- [`.evergreen/docker/teardown.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/docker/teardown.sh)
- [`.evergreen/run-load-balancer.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/run-load-balancer.sh)
- [`.evergreen/get-distro.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/get-distro.sh)
- [`.evergreen/find-python3.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/find-python3.sh)

```text
setup.sh (drivers-tools)
  -> handle-paths.sh
  -> find-python3.sh
  -> orchestration/setup.sh

teardown.sh (drivers-tools)
  -> handle-paths.sh
  -> stop-orchestration.sh
  -> docker/teardown.sh
  -> run-load-balancer.sh stop

run-load-balancer.sh
  -> handle-paths.sh
  -> (haproxy binary, no further .sh deps)

get-distro.sh
  -> (no .sh deps; prints DISTRO string)
```

`mongo-python-driver` calls these via its `.evergreen/scripts/setup-system.sh` and `.evergreen/scripts/stop-server.sh` wrappers.

### 4.3 Secrets and CSFLE helpers

Key scripts:
- [`.evergreen/secrets_handling/setup-secrets.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/secrets_handling/setup-secrets.sh)
- [`.evergreen/csfle/setup-secrets.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/csfle/setup-secrets.sh)
- [`.evergreen/csfle/start-servers.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/csfle/start-servers.sh)
- [`.evergreen/csfle/stop-servers.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/csfle/stop-servers.sh)
- [`.evergreen/csfle/await-servers.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/csfle/await-servers.sh)
- [`.evergreen/process-utils.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/process-utils.sh)

```text
secrets_handling/setup-secrets.sh
  -> ../handle-paths.sh
  -> ../auth_aws/activate-authawsvenv.sh
  -> (python) setup_secrets.py

csfle/setup-secrets.sh
  -> ../handle-paths.sh
  -> ../secrets_handling/setup-secrets.sh
  -> ./activate-kmstlsvenv.sh
  -> (python) setup_secrets.py

csfle/start-servers.sh
  -> ../handle-paths.sh
  -> ./stop-servers.sh
  -> ../process-utils.sh (killport helper)
  -> ./activate-kmstlsvenv.sh
  -> (python) kms_*_server.py, bottle.py fake_azure:imds
  -> ./await-servers.sh
```

These scripts provide the FLE/KMS test infrastructure that pymongo consumes via `TEST_NAME=encryption` / `kms`.

### 4.4 OCSP helpers

Key scripts:
- [`.evergreen/ocsp/setup.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/ocsp/setup.sh)
- [`.evergreen/ocsp/teardown.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/ocsp/teardown.sh)
- [`.evergreen/ocsp/activate-ocspvenv.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/ocsp/activate-ocspvenv.sh)

```text
ocsp/setup.sh
  -> ../handle-paths.sh
  -> teardown.sh
  -> ./activate-ocspvenv.sh
  -> (python) ocsp_mock.py

ocsp/teardown.sh
  -> ../handle-paths.sh
  -> (kills ocsp_mock.py via pid file)
```

`mongo-python-driver` calls this via `setup_tests.py` when `TEST_NAME=ocsp`, passing `OCSP_ALGORITHM` and `SERVER_TYPE`.

### 4.5 AWS auth and Atlas helpers

Key scripts:
- [`.evergreen/auth_aws/aws_setup.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/auth_aws/aws_setup.sh)
- [`.evergreen/auth_aws/activate-authawsvenv.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/auth_aws/activate-authawsvenv.sh)
- [`.evergreen/auth_aws/setup-secrets.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/auth_aws/setup-secrets.sh)
- [`.evergreen/atlas/setup-atlas-cluster.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/atlas/setup-atlas-cluster.sh)
- [`.evergreen/atlas/setup-secrets.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/atlas/setup-secrets.sh)
- [`.evergreen/atlas/atlas-utils.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/atlas/atlas-utils.sh)
- [`.evergreen/atlas/setup-variables.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/atlas/setup-variables.sh)
- [`.evergreen/aws_lambda/run-deployed-lambda-aws-tests.sh`](https://github.com/mongodb-labs/drivers-evergreen-tools/blob/master/.evergreen/aws_lambda/run-deployed-lambda-aws-tests.sh)

```text
auth_aws/aws_setup.sh
  -> ../handle-paths.sh
  -> ./activate-authawsvenv.sh
  -> (optionally) ./setup-secrets.sh
  -> (python) aws_tester.py
  -> source ./test-env.sh

atlas/setup-atlas-cluster.sh
  -> ../handle-paths.sh
  -> ./secrets-export.sh (if present)
  -> (optionally) ./setup-secrets.sh
  -> ./setup-variables.sh
  -> ./atlas-utils.sh
  -> (curl via atlas-utils.sh to create/check Atlas deployment)

aws_lambda/run-deployed-lambda-aws-tests.sh
  -> ../handle-paths.sh
  -> ../atlas/secrets-export.sh (if present)
  -> (AWS CLI + `sam` CLI to build/deploy/invoke Lambda)
```

Pymongo uses these indirectly when `TEST_NAME` is `auth_aws`, `aws_lambda`, or when `TEST_NAME=search_index` (which also relies on Atlas helpers).

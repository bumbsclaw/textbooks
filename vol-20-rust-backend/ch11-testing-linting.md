# Chapter 11 — Testing, Linting, and Tooling: clippy, rustfmt, cargo-audit, criterion, cargo-nextest, and Miri

*What this chapter covers:* the operational tooling layer that turns a Rust backend codebase from "it compiles" into "it is safe to ship at 200 deploys per day." Rust's compiler catches memory and type errors, but the remaining failure modes — logic bugs, performance regressions, style drift, supply-chain compromise, and undefined behavior through `unsafe` — require an explicit harness. This chapter builds that harness end-to-end: the test execution model (`cargo test` versus `cargo nextest`), fixture and property-testing patterns that survive in a microservices monorepo, the `clippy` and `rustfmt` gates that keep 50 engineers from diverging, the `cargo-audit`/`cargo-deny` supply-chain guardrails that connect to Chapter 1's registry threat model, the `criterion`/`iai-callgrind` benchmarking stack that prevents p99 latency regressions, and the heavyweight correctness tools `Miri`, `loom`, and `shuttle` that deterministically hunt concurrency and UB bugs the type system cannot see. Every tool is presented with its architecture, its config, its CI wiring, and its failure mode when you get it wrong.

**Learning goals:**

- Explain the `cargo test` execution model (one process per test binary, one thread pool per binary) and why it breaks under parallelism, isolation, and flaky-test pressure — and how `cargo nextest` replaces it with process-per-test isolation, test partitioning, and JUnit-aware retries.
- Configure `cargo-nextest` for a workspace (`nextest.toml`), shard tests across CI runners with `--partition`, and interpret JUnit and `libtest` output in CI dashboards.
- Write effective fixtures (`rstest`, `once_cell`/`OnceLock`, `testcontainers`) and property-based tests (`proptest`, `quickcheck`) and know when snapshot testing, fuzz testing, and property testing are substitutes versus complements.
- Classify `clippy` lint groups (correctness, suspicious, complexity, perf, style, pedantic, nursery, restriction, cargo) by signal-to-noise and configure them via `[lints.clippy]` / `[lints.rust]` in `Cargo.toml` and `clippy.toml` for a production gate.
- Distinguish pedantic/nursery/restriction from the default set, enable and suppress lints at the right granularity, and extend clippy with custom lints via `dylint` or `marker`.
- Enforce `rustfmt` deterministically via `rustfmt.toml` and a `--check` gate, handle `rustfmt` version pinning, and prevent merge-conflict churn in a high-frequency monorepo.
- Operate `cargo-audit` (RustSec advisory DB) and `cargo-deny` (advisories, bans, licenses, sources, yanked) as supply-chain controls, interpret `RUSTSEC-YYYY-NNNN` findings, and wire them into a CI gate that fails the build.
- Benchmark with `criterion` (statistical measurement, HTML report), complement with instruction-count benchmarking via `iai-callgrind`, evaluate `divan` as a lighter alternative, and gate performance regressions in CI without noise.
- Run `Miri` to detect UB (use-after-free, data races on `UnsafeCell`, out-of-bounds, invalid `transmute`), understand its interpreter model and constraints (FFI, inline assembly, unsupported syscalls), and contrast it with `loom` and `shuttle` for deterministic concurrency exploration.
- Compose a cached, partitioned CI pipeline using `Swatinem/rust-cache` (or `sccache`), correctly invalidate caches on `rustc` version and `Cargo.lock` changes, and express the full lint → format → audit → test → bench → Miri pipeline in GitHub Actions.

---

## 1. The Backend Tooling Problem: Why `cargo test` Alone Does Not Scale

A single-service Rust project of 5 kLOC can survive on `cargo test && cargo clippy && cargo fmt --check`. A backend organization running 40 services, 200 crates, and 15,000 tests across a Cargo workspace cannot. Three pressures force a richer harness:

1. **Isolation failures.** `cargo test`'s shared-process model means a test that leaks global state (a Tokio global runtime, an env-var mutation, a temp-file collision) silently corrupts its neighbors. At 15,000 tests the flake rate from this alone can exceed 2%.
2. **Feedback latency.** Sequential test-binary execution and naive recompilation waste minutes per PR. At 200 PRs/day, every wasted minute is a developer-hour burned.
3. **Supply-chain and correctness drift.** Without automated `clippy`, `rustfmt`, `cargo-deny`, and `Miri` gates, code style diverges, `unsafe` UB ships, and a yanked or GPL-licensed transitive dependency lands in production.

The mature Rust backend standardizes on a gate pipeline that typically runs in this order inside CI — fastest and cheapest first — and fails the PR on any red signal:

```
rustfmt --check  →  clippy --workspace -- -D warnings  →  cargo deny check  →  cargo nextest run  →  criterion (nightly or on main)  →  miri (nightly, allowlist)
```

Each tool in this chapter is one stage of that pipeline. Understanding what it does *underneath* — not just which flags to pass — is what lets you tune it for 10x scale.

### 1.1 Distributed-Systems Lens

In a distributed backend you do not have one test suite — you have a *fleet* of suites that share dependencies but diverge in topology, feature flags, and data fixtures. A change to `crates/protocol` can break `crates/api-server` and `crates/storage-engine` transitively. The tooling must therefore operate at **workspace scope** (`--workspace`), produce machine-readable outputs (JUnit XML, SARIF, `clippy --message-format=json`), and shard cleanly across runners. Tools that only emit human-readable terminal output are not CI tools.

---

## 2. Testing at Scale: `cargo test` vs `cargo nextest`, Fixtures, and Property Testing

### 2.1 How `cargo test` Actually Executes

`cargo test` is a thin orchestrator around the `libtest` harness compiled into every `#[test]` binary.

```mermaid
flowchart TB
    subgraph CargoTest["cargo test — one process per binary"]
        A["cargo test --workspace"] --> B["cargo build --tests"]
        B --> C["Binary: my_crate-abc123<br/>(all #[test] fns)"]
        B --> D["Binary: integration_tests-ghi789"]
        C --> E["Process C: libtest thread pool<br/>all tests share address space"]
        D --> F["Process D: libtest thread pool"]
        E --> G["Shared global state<br/>env vars, statics, temp dirs<br/>one panic poisons neighbors"]
    end
    subgraph NextestFlow["cargo nextest — process per test"]
        H["cargo nextest run --workspace"] --> I["cargo build --tests<br/>(same artifacts)"]
        I --> J["Scheduler: N processes<br/>each test = fresh process"]
        J --> K["Test aaa — process 1"]
        J --> L["Test bbb — process 2"]
        J --> M["Test ccc — process 3"]
        K --> N["JUnit XML — per-test status + duration"]
        L --> N
        M --> N
        N --> O["CI: partition hash:4/m + retries"]
    end
    CargoTest -.->|"same build, different runner"| NextestFlow
    style CargoTest fill:#fff3bf,stroke:#333
    style NextestFlow fill:#d3f9d8,stroke:#333
```

Mechanism:

- `cargo test` builds one test binary per crate (plus one per `[[test]]` integration file and one for doctests). Each binary embeds every `#[test]` function discovered by macro expansion.
- At runtime, `libtest` enumerates the tests, optionally filters by name (`cargo test substring`), and runs them on an internal thread pool (default `std::thread::available_parallelism()` threads). Tests in *different* binaries run sequentially by default (Cargo serializes binary invocations unless `--no-fail-fast` with concurrent binary scheduling on newer Cargo).
- All tests within a binary share the same process: the same `std::env`, the same `OnceLock` singletons, the same filesystem view. A test that calls `std::env::set_var` or leaks a Tokio runtime handle contaminates every other test in the binary.
- `libtest` output is unstructured by default; `cargo test -- --format=json` exists but is unstable, and `cargo test -- --report-time` is coarse.

Consequences for backends:

| Property | `cargo test` | Pain at scale |
|---|---|---|
| Isolation | Threads in one process | Global-state flakes; `unsafe` UB in one test corrupts others |
| Scheduling | Thread pool per binary; binaries sequential | Under-utilized CI cores; slow feedback on many small crates |
| Timeout/cancel | No per-test timeout; Ctrl-C kills entire binary | One hanging test blocks the whole binary; no granular cancel |
| Retry | None; rerun the whole binary | Flaky tests force full reruns; no `flake: 2/10` signal |
| Structured output | Text + unstable JSON | CI cannot render per-test history or JUnit without brittle parsers |

`cargo test` is correct for local development on a single crate. It is not a CI test runner.

### 2.2 `cargo nextest`: Process-per-Test, Partitioning, and JUnit

`cargo nextest` (from Embark Studios, now community-maintained) replaces `libtest` scheduling entirely while reusing Cargo's build; the combined diagram above shows the contrast.

Key architectural differences:

- **Process-per-test.** Each `#[test]` runs in its own process. Leaked state, env-var mutation, and even `SIGSEGV` in one test cannot affect another. The cost is process spawn overhead (~2–5 ms on Linux), amortized by parallelism.
- **Pre-enumeration.** Nextest first runs `cargo test --no-run --message-format=json` to discover all test binaries and then lists tests inside each without executing them. This lets it build a full inventory for partitioning and counting before any test runs.
- **Work-stealing scheduler.** Tests are dispatched to a fixed-size worker pool (default: `num_cpus`). Finished workers steal from the queue. Slow tests do not head-of-line block fast ones because each test is an independent unit, unlike `cargo test` where one slow test occupies a thread inside a shared binary.
- **Per-test timeout, retries, and slow-test detection.** Configured in `nextest.toml`; nextest can automatically rerun flaky tests and distinguish "always fails" from "fails 1 in 5."
- **Partitioning for sharded CI.** `cargo nextest run --partition count:2/3` deterministically assigns tests to shards by hash, so N CI runners each run 1/N of the suite with zero coordination.

#### Installing and Running

```bash
# Install (pinned version in CI — do not use `cargo install --latest` unpinned)
cargo install cargo-nextest --locked --version 0.9.72

# Equivalent of `cargo test --workspace`
cargo nextest run --workspace

# Profile-aware: nextest respects Cargo profiles
cargo nextest run --workspace --profile ci   # if you define [profile.ci] in Cargo.toml

# JUnit output for CI dashboards (GitHub Actions test reporter, Datadog, etc.)
cargo nextest run --workspace --message-format libtest-json

# Partition for sharded CI (2 runners)
# Runner 1:
cargo nextest run --workspace --partition count:2/1 --message-format junit --output-file junit1.xml
# Runner 2:
cargo nextest run --workspace --partition count:2/2 --message-format junit --output-file junit2.xml
```

Example output (trimmed):

```
$ cargo nextest run -p api-server
    Starting 3 tests across 2 binaries (8 tests in total)
        PASS [   0.032s] api-server::handlers::test_health_ok
        PASS [   0.041s] api-server::handlers::test_auth_rejects_expired
        FAIL [   0.089s] api-server::handlers::test_rate_limit_burst
            --- STDOUT:              api-server::handlers::test_rate_limit_burst ---

            assertion failed: `(left == right)`
              left: `429`,
             right: `200`

        PASS [   0.015s] api-server::middleware::test_request_id_propagation
    Summary [   0.120s] 3 passed, 1 failed, 0 skipped
    JUnit report written to target/nextest/junit.xml
```

#### `nextest.toml` — The Config That Matters

Place `.config/nextest.toml` (or `nextest.toml` at workspace root) to control retries, timeouts, and overrides per test. This is the file you will tune more than any other testing config.

```toml
# .config/nextest.toml
[profile.default]
# Fail the run quickly on first failure — invert for flake hunting
fail-fast = false
# Per-test timeout: kill tests that hang (deadlocked Tokio runtime, leaked connection)
slow-timeout = { period = "30s", terminate-after = 5 }
# JUnit output for CI
junit.store-success-output = true
junit.store-failure-output = true

# Retries: rerun failures up to 2 times, only if the test passed before (flake detection)
[profile.default.retries]
backoff = "exponential"
count = 2
delay = "1s"
# Only retry if the test is known-flaky or failed intermittently
# Use `cargo nextest run --retries 2` to force retry regardless

# Override for known-slow integration tests (testcontainers, real Postgres)
[[profile.default.overrides]]
filter = "test(integration_postgres_*)"
slow-timeout = { period = "120s", terminate-after = 2 }
retries = 3

# Override for doctests (inherently single-threaded in some setups)
[[profile.default.overrides]]
filter = "test(doctest)"
threads-required = 1

# Partition-aware profile for CI
[profile.ci]
# Inherit default but add junit path
junit.path = "junit.xml"
retries = 2

# Example: mark a known flaky test as expected-flaky (does not fail the run if it flakes)
# [[profile.default.overrides]]
# filter = "test(test_eventual_consistency_replica_lag)"
# retries = 5
# flaky = true  # hypothetical — nextest uses `status = { flaky = 5 }` patterns via junit
```

```toml
# Cargo.toml — optional [profile.ci] for faster test builds in CI
[profile.ci]
inherits = "dev"
# Disable debug symbols in CI test builds for speed (tune per your needs)
debug = 0
incremental = false
```

And the corresponding CI invocation:

```bash
# CI runner: use the `ci` nextest profile
cargo nextest run --workspace --profile ci --partition hash:4/1
cargo nextest run --workspace --profile ci --partition hash:4/2
cargo nextest run --workspace --profile ci --partition hash:4/3
cargo nextest run --workspace --profile ci --partition hash:4/4
```

> **Why `hash` vs `count` partitioning:** `count` assigns tests round-robin by enumeration order (fast but sensitive to test insertion order). `hash` assigns by hash of `binary_id + test_name` — stable across runs even as tests are added, so shard timing remains balanced without re-tuning.

### 2.3 Fixtures: Shared Setup Without Shared Mutable State

Backend tests need databases, message brokers, and config. The challenge is doing this without reintroducing the global-state sharing that nextest just isolated away.

**Pattern 1 — `rstest` for parameterized fixtures.** Replaces manual `#[test]` duplication with declarative cases.

```rust
use rstest::rstest;

#[derive(Debug, Clone)]
struct RateLimitConfig { burst: u32, refill_per_sec: u32 }

// rstest generates one #[test] per case — each runs in its own nextest process
#[rstest]
#[case(RateLimitConfig { burst: 10, refill_per_sec: 1 }, 10, true)]
#[case(RateLimitConfig { burst: 10, refill_per_sec: 1 }, 11, false)]
#[case(RateLimitConfig { burst: 100, refill_per_sec: 50 }, 100, true)]
fn test_rate_limit_cases(
    #[case] cfg: RateLimitConfig,
    #[case] requests: u32,
    #[case] should_allow: bool,
) {
    let limiter = RateLimiter::new(cfg);
    let allowed = (0..requests).filter(|_| limiter.try_acquire()).count() as u32;
    assert_eq!(allowed == requests, should_allow);
}

// Fixture composition — `#[fixture]` functions are injected by name
#[rstest::fixture]
fn base_config() -> RateLimitConfig {
    RateLimitConfig { burst: 50, refill_per_sec: 10 }
}

#[rstest]
fn test_with_injected_fixture(base_config: RateLimitConfig) {
    assert!(base_config.burst > 0);
}
```

**Pattern 2 — `OnceLock` for expensive shared setup within one binary.** When multiple tests need the same compiled regex or schema, `OnceLock` is the correct primitive (not `lazy_static` which predates `std::sync::OnceLock`).

```rust
use std::sync::OnceLock;

static COMPILED_SCHEMA: OnceLock<JsonSchema> = OnceLock::new();

fn test_schema() -> &'static JsonSchema {
    COMPILED_SCHEMA.get_or_init(|| {
        let raw = std::fs::read_to_string("tests/fixtures/schema.json").unwrap();
        JsonSchema::compile(&raw).unwrap()
    })
}

#[test]
fn test_schema_validates_ok() {
    assert!(test_schema().validate(r#"{"id": 1}"#).is_ok());
}
```

> With nextest's process-per-test, `OnceLock` reinitializes once *per process* — cost is one init per test, not per binary. For truly expensive setup (spawning Postgres), use `testcontainers` inside each test process rather than trying to share a singleton across processes.

**Pattern 3 — `testcontainers` for real dependencies.** Each test process starts its own container; no cross-test port collision if you let the crate assign random ports.

```rust
use testcontainers::{clients::Cli, images::postgres::Postgres, Container};
use sqlx::PgPool;

#[tokio::test]
async fn test_user_insert_roundtrip() {
    let docker = Cli::default();
    let pg: Container<Postgres> = docker.run(Postgres::default());
    let port = pg.get_host_port_ipv4(5432);
    let url = format!("postgres://postgres:postgres@127.0.0.1:{port}/postgres");

    // Run migrations against the ephemeral instance
    let pool = PgPool::connect(&url).await.unwrap();
    sqlx::migrate!("./migrations").run(&pool).await.unwrap();

    let repo = UserRepo::new(pool);
    let id = repo.insert("alice@example.com").await.unwrap();
    let user = repo.get(id).await.unwrap();
    assert_eq!(user.email, "alice@example.com");
    // Container drops here — no cleanup needed, no shared state leaked
}
```

**Pattern 4 — Snapshot testing with `insta`.** For API response shapes, error messages, and serialized configs that you want to diff-review in PRs.

```rust
#[test]
fn test_error_response_snapshot() {
    let err = ApiError::RateLimited { retry_after_secs: 60 };
    // First run: `cargo insta review` accepts the snapshot
    // Subsequent runs: insta diff on mismatch — visible in PR
    insta::assert_json_snapshot!(err.to_response_body(), @r###"
    {
      "error": "rate_limited",
      "retry_after": 60
    }
    "###);
}
```

### 2.4 Property-Based Testing: `proptest` and `quickcheck`

Unit tests assert `f(2) == 4`. Property tests assert `∀ x: f(x) ≥ 0` over hundreds of randomly generated inputs. For backend invariants — serialization roundtrips, idempotency, ordering — this is dramatically more powerful than hand-picked examples.

```rust
use proptest::prelude::*;

// Invariant: encode → decode roundtrip is identity for all valid messages
proptest! {
    #[test]
    fn test_codec_roundtrip(payload in prop::collection::vec(any::<u8>(), 0..4096)) {
        let msg = Message { id: 42, payload: payload.clone() };
        let encoded = msg.encode();
        let decoded = Message::decode(&encoded).unwrap();
        prop_assert_eq!(decoded.payload, payload);
    }

    #[test]
    fn test_idempotent_retry_dedup(
        keys in prop::collection::vec(any::<String>(), 1..20),
        // Strategy: generate distinct keys, then duplicate some
    ) {
        let deduped = deduplicate(keys.clone());
        // Property: dedup is stable, order-preserving, and never grows
        prop_assert!(deduped.len() <= keys.len());
        // Property: dedup applied twice is same as once (idempotent)
        prop_assert_eq!(deduped.clone(), deduplicate(deduped.clone()));
    }
}

// Custom strategy: generate valid request objects, not just raw bytes
fn arb_valid_request() -> impl Strategy<Value = ApiRequest> {
    (1..10000u64, "[a-z]{3,20}", 0..1000u32)
        .prop_map(|(id, name, ttl_secs)| ApiRequest { id, name, ttl_secs })
}
```

`quickcheck` is a lighter alternative with automatic `Arbitrary` derivation:

```rust
use quickcheck::quickcheck;

quickcheck! {
    fn prop_reverse_twice_is_identity(xs: Vec<u8>) -> bool {
        let mut ys = xs.clone();
        ys.reverse(); ys.reverse();
        ys == xs
    }
}
```

| Tool | Generation | Shrinking | `proptest` vs `quickcheck` |
|---|---|---|---|
| `proptest` | Strategy combinators (`prop::collection::vec`, `prop_oneof!`) | Integrated, finds minimal failing input, persists regressions in `proptest-regressions/` | Explicit strategies, better shrinking, heavier API |
| `quickcheck` | `Arbitrary` trait derivation | Minimal shrinking | Derive `Arbitrary` on your types, less control |
| `cargo fuzz` (libFuzzer) | Coverage-guided mutation | No shrinking, but finds deeper paths via coverage feedback | Complementary — property tests for invariants, fuzz for parser/codec crash hunting |

Best practice for backends: use `proptest` for serialization, state-machine, and business-logic invariants (run in `nextest` as normal `#[test]`); use `cargo fuzz` as a nightly job for wire-format parsers and `unsafe` boundaries.

> **Distributed-systems tip:** Property tests are how you encode distributed invariants. "For any partition of requests across N shards, the union of deduped results equals the deduped union" is a property test. Run it with `proptest`'s default 256 cases locally and 5,000 cases in CI nightly — the extra cases catch ordering-dependent bugs that unit tests miss.

---

## 3. Clippy: The Lint Harness That Prevents Production Bugs

Clippy is not a style checker — it is a suite of ~700 lints that run as a `rustc` driver plugin, analyzing HIR (high-level IR) and MIR after type checking. It catches logic errors, performance pitfalls, and API misuse that `rustc` warnings do not cover.

### 3.1 Architecture: How Clippy Sees Your Code

`rustc` proceeds: source → macro expansion → HIR → type check → MIR → LLVM IR. Clippy interposes after HIR/MIR construction: Cargo invokes `cargo clippy`, which calls `clippy-driver` (a `rustc` wrapper) instead of `rustc`. The driver loads clippy's lint passes as callbacks — each pass visits HIR nodes (expressions, items, patterns) and emits diagnostics. Because it runs as a compiler plugin, clippy has full type information — it can tell `Vec<u8>` from `Bytes` and flag `clone()` calls that are actually expensive.

### 3.2 Lint Levels and the Pyramid

```mermaid
flowchart TB
    subgraph Pyramid["Clippy lint pyramid — signal vs noise"]
        L0["allow — lint exists but never fires"]
        L1["warn — show diagnostic, build succeeds"]
        L2["deny — diagnostic + fail build"]
        L3["forbid — deny that cannot be overridden<br/>by inner #[allow(...)]"]
        L0 --> L1 --> L2 --> L3
    end
    subgraph Groups["Clippy lint groups — by intent"]
        G0["cargo<br/>manifest lints"]
        G1["correctness<br/>almost always a bug — deny"]
        G2["suspicious<br/>likely a bug — deny"]
        G3["complexity<br/>cognitive load — warn"]
        G4["perf<br/>unnecessary clone, needless collect — warn/deny"]
        G5["style<br/>naming, redundant code — warn"]
        G6["pedantic<br/>opinionated, high false-positive — opt-in"]
        G7["nursery<br/>experimental, unstable — opt-in + expect churn"]
        G8["restriction<br/>paranoid, bans patterns entirely — case-by-case"]
        G0 --- G1 --- G2 --- G3 --- G4 --- G5 --- G6 --- G7 --- G8
        style G1 fill:#ffc9c9,stroke:#333
        style G2 fill:#ffd8a8,stroke:#333
        style G6 fill:#d0ebff,stroke:#333
        style G7 fill:#e7f5ff,stroke:#333
        style G8 fill:#f3f0ff,stroke:#333
    end
```

The default `cargo clippy` enables: `correctness`, `suspicious`, `complexity`, `perf`, `style`, and `cargo`. It does **not** enable `pedantic`, `nursery`, or `restriction`. This is intentional — pedantic alone adds ~180 lints, many with high false-positive rates on backend idioms (e.g., `module_name_repetitions`, `missing_errors_doc`).

Recommended production posture for a backend workspace:

| Group | CI level | Rationale |
|---|---|---|
| `correctness`, `suspicious` | `deny` | Almost always real bugs (e.g., `clippy::nonminimal_bool`, `clippy::await_holding_lock`) |
| `complexity`, `perf` | `deny` | Real performance bugs (`clippy::needless_collect`, `clippy::large_enum_variant`, `clippy::uninlined_format_args`) |
| `style` | `warn` (or `deny` if team agrees) | Low-risk; noise if denied too aggressively |
| `pedantic` | `allow` globally, `warn` selectively per lint | Enable only high-value pedantic lints like `clippy::pedantic::borrow_as_ptr` or `clippy::pedantic::nursery` subset |
| `nursery` | `allow` | Unstable; only preview locally |
| `restriction` | Never globally — `warn` per lint if policy requires | Bans patterns like `unwrap` entirely — useful as team policy, not as default |

#### Canonical `cargo clippy` Invocations

```bash
# Local: workspace clippy, pedantic subset, fail on warnings
cargo clippy --workspace --all-targets --all-features -- -D warnings

# CI: same, but with explicit cache key and JSON for SARIF upload
cargo clippy --workspace --all-targets --all-features --message-format=json -- -D warnings 2> clippy.json

# Diagnose a single lint
cargo clippy -- -W clippy::pedantic -W clippy::nursery --explain clippy::cognitive_complexity

# Run clippy on nightly for latest lints without pinning nightly as default toolchain
cargo +nightly clippy --workspace -- -D warnings
```

### 3.3 Configuring Clippy: `Cargo.toml` `[lints]` and `clippy.toml`

Since Rust 1.74, the idiomatic place for lint levels is `Cargo.toml` `[lints]` with `workspace.lints` inheritance — not ad-hoc `RUSTFLAGS` or `.clippy.toml` flags. This gives per-crate inheritance, `cargo clippy` auto-discovery, and `cargo fix` support.

```toml
# Cargo.toml  — workspace root
[workspace.lints.rust]
# Rustc lints you almost always want as deny in backends
unsafe_op_in_unsafe_fn = "warn"
missing_docs = "allow"
unreachable_pub = "allow"

[workspace.lints.clippy]
# --- High-signal: deny ---
correctness = { level = "deny", priority = -1 }
suspicious  = { level = "deny", priority = -1 }
complexity  = { level = "warn", priority = -1 }
perf        = { level = "deny", priority = -1 }

# --- Style: warn, not deny, to avoid PR churn on bike-shedding ---
style = { level = "warn", priority = -1 }

# --- Pedantic: cherry-pick, do not blanket-enable ---
pedantic = "allow"
# Re-enable the few pedantic lints with high value for backends
# (list from: cargo clippy -- -W clippy::pedantic --explain)
# Each is `warn` individually:
cognitive_complexity = "warn"    # caps function complexity — real review signal
missing_errors_doc   = "allow"   # too noisy for internal crates
module_name_repetitions = "allow"
return_self_not_must_use = "allow"
# Perf-adjacent pedantic lints worth denying:
inline_always = "warn"
needless_pass_by_value = "warn"

# --- Restriction: only if you have a policy ---
# Example: ban `unwrap`/`expect` in library crates (enforce via `expect` with context)
# unwrap_used = "deny"
# expect_used = "deny"

[workspace.lints.rustdoc]
broken_intra_doc_links = "warn"

# Per-crate opt-in — crates inherit workspace lints
[lints]
workspace = true

# Override for a specific crate that legitimately needs unwrap in tests
# crates/tooling/Cargo.toml:
# [lints.clippy]
# workspace = true
# unwrap_used = "allow"
```

```toml
# clippy.toml — fine-grained clippy options (not lint levels; those are in Cargo.toml)
# https://doc.rust-lang.org/clippy/configuration.html

# Cognitive complexity threshold — functions above this trigger the lint
cognitive-complexity-threshold = 30

# Too many arguments — backend handlers often need many params
too-many-arguments-threshold = 8

# Doc link resolution
doc-valid-idents = ["...", "Axum", "Tokio", "gRPC"]

# Disallowed methods — enforce team policy (example: ban `std::env::var` in favor of config crate)
# disallowed-methods = [
#     { path = "std::env::var", reason = "use `config::env_var` for typed, validated env access" },
# ]

# Maximum trait bounds — keeps generic APIs reviewable
max-trait-bounds = 3
```

#### Suppressing Lints at the Right Granularity

```rust
// Crate-level: allow a lint for the whole crate (rare — prefer Cargo.toml)
#![allow(clippy::module_name_repetitions)]

// Function-level: the common case — one function legitimately violates a lint
#[allow(clippy::too_many_arguments)]
pub fn handle_request(
    req: Request, pool: &PgPool, cache: &Cache, metrics: &Metrics,
    limiter: &RateLimiter, config: &Config, span: Span,
) -> Response {
    // ...
}

// Expression-level: narrowest scope
#[allow(clippy::unwrap_used)]
let port: u16 = std::env::var("PORT").unwrap().parse().unwrap();

// Expect with reason — clippy's `expect_used` lint accepts this but `unwrap_used` does not
let port: u16 = std::env::var("PORT")
    .expect("PORT env var must be set in production");

// For `restriction` lints you intentionally violate: document why
#[allow(clippy::disallowed_methods)] // test helper — env mutation is the point under test
fn set_test_env() { std::env::set_var("TEST_MODE", "1"); }
```

### 3.4 Custom Lints: `dylint` and `marker`

When team conventions outgrow clippy's built-in lints ("every handler must return `Result<Response, ApiError>`" or "never call `tokio::time::sleep` in production code"), write custom lints.

- **`dylint`** — dynamically loaded clippy lints as shared libraries. Each lint is a crate with `dylint_lint` in `Cargo.toml`; `cargo dylint` loads them via `LD_LIBRARY_PATH` interposition over `clippy-driver`. No fork of clippy required.
- **`marker`** — a newer API for custom lints with a stable HIR-visitor interface and `cargo marker` runner. Preferred for new custom lints; supports `marker_lints` registry.

```toml
# Cargo.toml for a dylint crate
[package]
name = "backend_lints"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
clippy_utils = { version = "0.1", default-features = false }
dylint_linting = "3.0"

[lints.rust]
unexpected_cfgs = { level = "warn", check-cfg = ["cfg(dylint_lib)"] }
```

Custom lints are how large organizations turn tribal knowledge ("always use `config::env_var`") into compiler errors. Treat them as part of the build — versioned, tested, and cached like any other tool.

### 3.5 Distributed-Systems Lens

In a 50-engineer organization, clippy is not a suggestion — it is a coordination mechanism. Without a shared `[workspace.lints]` and `clippy.toml`, each team evolves its own lint suppressions, PR review devolves into style arguments, and "fix clippy" commits create merge conflicts at 200 PRs/day. Pin the clippy version via `rust-toolchain.toml` (`components = ["clippy"]`), deny `correctness`/`suspicious`/`perf` globally, and require `#[allow(...)]` on any suppression with a comment — then clippy becomes a reviewer that never sleeps.

---

## 4. rustfmt: Deterministic Formatting as a Coordination Primitive

`rustfmt` is the official Rust formatter. It parses source into an AST, applies a deterministic set of formatting rules controlled by `rustfmt.toml`, and rewrites the file. Its critical property is **idempotence**: `rustfmt(rustfmt(x)) == rustfmt(x)`. Running it twice produces the same output, so CI can gate on `rustfmt --check` without flakiness.

### 4.1 `rustfmt.toml` — The Few Options That Matter

Most teams should start from defaults and only tune the options that affect diff size and merge-conflict rate.

```toml
# rustfmt.toml — workspace root (or .rustfmt.toml for backwards compat)

# --- Edition and style edition ---
# edition is inferred from Cargo.toml; only set here if you have standalone .rs files
# style_edition = "2024"  # opts into newer formatting (e.g., 2024 match-arm style)

# --- Line width and import layout ---
max_width = 100              # default 100; 80 is too narrow for backend generics
hard_tabs = false
tab_spaces = 4
newline_style = "Unix"       # enforce LF — never "Auto" in a cross-platform team
use_small_heuristics = "Default"

# --- Imports ---
imports_granularity = "Crate"  # group imports by crate — reduces diff churn vs "Module"
group_imports = "StdExternalCrate"  # std → external → crate
reorder_imports = true
reorder_modules = true

# --- Trailing commas and lists ---
trailing_comma = "Vertical"
trailing_semicolon = true

# --- Edition 2024 options (enable when style_edition = "2024") ---
# match_block_trailing_comma = true
# overflow_delimited_expr = true

# --- Stability: pin what you can ---
# These are the defaults; explicitly listing them prevents surprise on rustfmt upgrades
wrap_comments = false
comment_width = 100
normalize_comments = false
normalize_doc_attributes = false
format_strings = false        # do not reformat string literals
```

> **What not to tune:** `rustfmt` intentionally exposes fewer options than `clang-format` or `prettier`. This is a feature — fewer options mean fewer team debates. Resist the urge to micro-tune `chain_width` or `single_line_if_else_max_width`; the defaults are chosen to minimize churn.

### 4.2 The CI Gate and Local Workflow

```bash
# Local: format the workspace
cargo fmt --all

# CI: check without modifying (fails with diff on mismatch)
cargo fmt --all -- --check

# Alternative: direct rustfmt invocation for finer control
rustfmt --edition 2021 --config-path rustfmt.toml --check src/main.rs

# Git hook — format on commit (install via `cargo install rustfmt` is already present)
# .git/hooks/pre-commit:
#!/bin/sh
cargo fmt --all -- --check || {
  echo "Run 'cargo fmt --all' and re-commit."
  exit 1
}
```

#### Version Pinning

`rustfmt` output can change between Rust releases, even within the same `rustfmt.toml`. Pin the toolchain to avoid "format churn" commits:

```toml
# rust-toolchain.toml — pins rustfmt (and clippy, miri) to a known version
[toolchain]
channel = "1.82.0"
components = ["rustfmt", "clippy", "rust-src"]
# Optional: nightly for miri
# targets = ["x86_64-unknown-linux-gnu"]
```

Without pinning, upgrading the CI runner's Rust version can produce a flood of "run `cargo fmt`" failures unrelated to any code change.

### 4.3 Distributed-Systems Lens

Formatting is a social problem, not a technical one. In a high-throughput monorepo, inconsistent formatting causes three concrete costs: (1) PRs with unrelated whitespace diffs that obscure the real change during incident review, (2) merge conflicts on every concurrent edit to the same file, and (3) blame pollution that destroys `git blame` as an incident-investigation tool. A deterministic `cargo fmt --check` gate that runs as the *first* CI step (cheapest, fastest feedback) eliminates all three. Treat `rustfmt.toml` as a team contract — change it via RFC, not drive-by PR.

---

## 5. Supply-Chain Auditing: `cargo-audit`, `cargo-deny`, and `cargo-vet`

Chapter 1 established that `crates.io` is an uncurated registry: anyone can publish, typosquatting exists, and transitive dependencies can introduce vulnerable or copyleft-licensed code. This section makes that threat model operational.

### 5.1 `cargo audit` — RustSec Advisory Scanning

`cargo audit` queries the [RustSec Advisory Database](https://github.com/RustSec/advisory-db) — a curated, OSV-compatible database of `RUSTSEC-YYYY-NNNN` advisories — and cross-references it against your `Cargo.lock`.

```bash
# Install
cargo install cargo-audit --locked

# Scan the workspace (reads Cargo.lock)
cargo audit

# Example output — a vulnerable transitive dependency:
# Crate:     time 0.3.22
# Title:     Potential segfault in `time` when using `format_description` macro
# Date:      2023-03-19
# ID:        RUSTSEC-2023-0040
# URL:       https://rustsec.org/advisories/RUSTSEC-2023-0040.html
# Solution: Upgrade to >=0.3.26
# Dependency tree:
# time 0.3.22
# └── my-service 0.1.0

# Audit a specific Cargo.lock without building
cargo audit --file /path/to/Cargo.lock

# JSON for CI integration
cargo audit --json --deny warnings
```

`cargo audit` also detects:

- **Yanked crates** — versions removed from crates.io (often due to a security issue or broken release) that are still pinned in your `Cargo.lock`.
- **Unsound feature combinations** — advisories that only apply when specific features are enabled.

Fix is `cargo update -p time --precise 0.3.26` or bumping the direct dependency that pulls `time`.

### 5.2 `cargo deny` — Policy Engine for Bans, Licenses, Sources, and Advisories

`cargo audit` answers "is anything known-vulnerable?" `cargo deny` answers that plus "is anything banned, copyleft, yanked, or from an untrusted source?" It is a policy engine driven by `deny.toml`.

`cargo deny` checks four policy axes against `Cargo.lock` + `Cargo.toml` + `deny.toml`: **advisories** (RustSec DB), **bans** (deny/allow/skip crates), **licenses** (allow/deny per SPDX), and **sources** (allow only crates.io + private registry). All four converge on `cargo deny check` (exit 0 or 1), which fails the PR on any violation.

#### `deny.toml` — Reference Config for a Backend Workspace

```toml
# deny.toml — workspace root

[graph]
# Exclude dev-dependencies from checks (test-only crates don't ship)
exclude-dev = true
targets = [
    { triple = "x86_64-unknown-linux-gnu" },
    { triple = "aarch64-unknown-linux-gnu" },
]

[advisories]
version = 2
# Where to find advisories — RustSec is the default; add private advisory DB if you have one
db-path = "~/.cargo/advisory-db"
db-urls = ["https://github.com/rustsec/advisory-db"]
# Yanked crates: warn in dev, deny in CI (override via --severity)
yanked = "warn"
unmaintained = "warn"
unsound = "warn"
ignore = [
    # Example: ignore a specific advisory that was triaged as non-exploitable
    # Each entry must have a reason — deny enforces this
    # { id = "RUSTSEC-2023-0040", reason = "affected code path not used; time::format_description not called" },
]

[bans]
# Deny specific crates entirely (known-malicious, deprecated, or replaced)
# allow = []  — allowlist mode: only listed crates may be used
multiple-versions = "warn"   # warn when two versions of the same crate are resolved
wildcards = "allow"          # deny `*` version requirements
highlight = "all"
# Example: ban a crate that bundles OpenSSL unsafely
# deny = [
#     { name = "openssl-sys", reason = "use rustls/ring — see ADR-014" },
# ]
# Example: skip a crate that is yanked but still needed transiently (with reason)
# skip = [
#     { name = "old-crate", version = "0.1.0", reason = "waiting on upstream fix #123" },
# ]
# Skip tree for large workspaces — exclude dev tooling from duplicate checks
# skip-tree = [
#     { name = "cargo-nextest", reason = "dev tooling" },
# ]

[licenses]
version = 2
# SPDX license allowlist — backend services typically allow permissive + MPL, deny AGPL/GPL
allow = [
    "MIT",
    "Apache-2.0",
    "Apache-2.0 WITH LLVM-exception",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-DFS-2016",
    "MPL-2.0",
    "CDLA-Permissive-2.0",
]
# Copyleft that is never allowed in proprietary backend services
deny = [
    "GPL-2.0",
    "GPL-3.0",
    "AGPL-3.0",
]
# Require license files to be present for crates that claim allowlisted licenses
confidence-threshold = 0.8
exceptions = [
    # Example: ring is ISC but deny.toml cannot infer it — explicitly allow
    # { name = "ring", allow = ["ISC"], reason = "ring LICENSE is ISC" },
]

[sources]
unknown-registry = "deny"
unknown-git = "deny"
# Only allow crates.io and your private registry
allow-registry = [
    "https://github.com/rust-lang/crates.io-index",
    # "https://my-registry.internal/index"  # private registry
]
# Allow specific git dependencies if you have patched forks (with reason)
# allow-git = [
#     "https://github.com/myorg/tokio",
# ]
```

#### CI Snippet — `cargo audit` + `cargo deny` Together

```yaml
# .github/workflows/supply-chain.yml
name: supply-chain

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    # Nightly audit — catches new advisories on unchanged Cargo.lock
    - cron: "0 03 * * *"

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@master
        with:
          toolchain: stable

      - name: Cache Rust (Swatinem)
        uses: Swatinem/rust-cache@v2

      - name: Install cargo-audit and cargo-deny
        run: cargo install cargo-audit cargo-deny --locked

      - name: cargo audit — RustSec advisories + yanked
        run: cargo audit --deny warnings

      - name: cargo deny — bans, licenses, sources, advisories
        run: cargo deny check advisories bans licenses sources

      # Optional: SARIF upload for GitHub code scanning
      - name: cargo audit SARIF (optional)
        if: always()
        run: cargo audit --json | cargo audit sarif > audit.sarif
      # - uses: github/codeql-action/upload-sarif@v3
      #   with: { sarif_file: audit.sarif }
```

> **When to use which:** `cargo audit` is the minimal viable supply-chain gate (advisories + yanked). `cargo deny` subsumes it and adds license/source/ban policy — prefer `cargo deny check advisories` over `cargo audit` if you already run `cargo deny`. Some teams run both for defense-in-depth and because `cargo audit --json` output is easier to pipe to dashboards.

### 5.3 `cargo vet` — Supply-Chain Vetting Beyond Advisories

For teams that want stronger guarantees than "no known CVE," [`cargo vet`](https://mozilla.github.io/cargo-vet/) (from Mozilla) adds **publisher vetting**: each crate version must be audited by a trusted publisher (you, Mozilla, or a delegated auditor) before it is allowed. `cargo vet` stores audits in `supply-chain/audits.toml` and can import audits from Mozilla and Google's registries. It complements `cargo deny`'s license/ban checks with a human-review signal.

### 5.4 Distributed-Systems Lens

Supply-chain policy cannot be per-service. If `service-a` allows `GPL-3.0` and `service-b` denies it, the organization has no policy — it has a lottery. Centralize `deny.toml` and `audits.toml` in a shared repository or Cargo workspace template, distribute it via a `cargo deny --workspace` that runs on the entire dependency closure, and make the nightly scheduled audit (not just PR-triggered) mandatory — a new `RUSTSEC` can land on a `Cargo.lock` that has not changed in weeks, and without the cron you will ship it.

---

## 6. Benchmarking: `criterion`, `iai-callgrind`, and `divan`

Backend Rust is often chosen for performance. Without continuous benchmarking, performance is a rumor. This section builds a benchmarking harness that produces stable, statistically sound measurements and gates regressions in CI.

### 6.1 `criterion` — Statistical Benchmarking with HTML Reports

`criterion` (the successor to `bencher`) is the standard Rust benchmarking crate. Unlike `cargo bench`'s built-in `#[bench]` harness (nightly-only, no statistics), `criterion` runs each benchmark many times, applies warmup, measures with statistical analysis (mean, median, standard deviation, outlier detection), and produces an HTML report with violin plots and regression detection against a saved baseline.

```mermaid
flowchart TB
    subgraph CriterionFlow["criterion bench lifecycle"]
        A["benches/my_bench.rs<br/>Criterion::default().bench_function"] --> B["Warmup phase<br/>3s default — stabilize caches"]
        B --> C["Measurement phase<br/>N samples, ~5s — time each iter"]
        C --> D["Statistics<br/>mean, median, stddev<br/>outlier classification"]
        D --> E["Comparison vs baseline<br/>saved in target/criterion/<bench>/base"]
        E --> F["HTML report<br/>target/criterion/report/index.html<br/>violin + regression plot"]
        E --> G["CI gate<br/>cargo bench -- --save-baseline main<br/>criterion-compare"]
    end
    style B fill:#e7f5ff,stroke:#333
    style D fill:#fff3bf,stroke:#333
    style F fill:#d3f9d8,stroke:#333
```

#### Setting Up `criterion`

```toml
# Cargo.toml
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "codec_bench"
harness = false   # disable built-in cargo bench harness — use criterion's
```

```rust
// benches/codec_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion, Throughput, BenchmarkId};
use my_service::codec::{Message, encode, decode};

fn bench_codec(c: &mut Criterion) {
    let mut group = c.benchmark_group("codec");

    // Throughput annotation — criterion reports bytes/sec and ns/byte
    for size in [64usize, 512, 4096, 65536] {
        let payload = vec![0xAB_u8; size];
        let msg = Message { id: 1, payload };

        group.throughput(Throughput::Bytes(size as u64));

        group.bench_with_input(
            BenchmarkId::new("encode", size),
            &msg,
            |b, m| b.iter(|| encode(black_box(m))),
        );

        let encoded = encode(&msg);
        group.bench_with_input(
            BenchmarkId::new("decode", size),
            &encoded,
            |b, buf| b.iter(|| decode(black_box(buf))),
        );

        // Combined roundtrip — the metric that matters for RPC path
        group.bench_with_input(
            BenchmarkId::new("roundtrip", size),
            &msg,
            |b, m| b.iter(|| {
                let enc = encode(black_box(m));
                decode(black_box(&enc)).unwrap()
            }),
        );
    }
    group.finish();
}

fn bench_handler(c: &mut Criterion) {
    // Async benchmarks — use `to_async` with a runtime
    let rt = tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .unwrap();

    c.bench_function("handler_1k_rps", |b| {
        b.to_async(&rt).iter(|| async {
            // black_box prevents the compiler from optimizing away the call
            let req = black_box(fake_request());
            handle(black_box(req)).await
        })
    });
}

criterion_group!(benches, bench_codec, bench_handler);
criterion_main!(benches);
```

Running:

```bash
# Run benchmarks, save baseline, open report
cargo bench --bench codec_bench
# HTML report at target/criterion/report/index.html

# Save a named baseline for regression comparison (e.g., on main)
cargo bench --bench codec_bench -- --save-baseline main

# Compare current branch against main baseline
cargo bench --bench codec_bench -- --baseline main
# Output:
# codec/encode/4096     time:   [1.234 µs 1.245 µs 1.258 µs]
#                       change: [+2.34% +3.10% +3.88%] (p=0.00 < 0.05)
#                       Performance has regressed.

# CI: bench on PR and compare to main — fail if regression exceeds threshold
cargo bench --bench codec_bench -- --baseline main 2>&1 | tee bench.log
# Use `cargo bench -- --output-format bencher` for machine-readable if needed
```

Example `criterion` report structure (what the HTML shows): a summary table (mean, median, stddev, change vs baseline) plus a violin plot of sample distribution, a regression line of time versus input size, and outlier classification. The violin PDF reveals bimodality when it exists.

> **Why `black_box`:** Without `black_box`, LLVM can prove a benchmark's result is unused and eliminate the entire computation. `criterion::black_box` is an opaque identity function that defeats dead-code elimination and constant folding. Always wrap inputs and outputs.

#### Tuning `criterion` for Backend Workloads

```rust
use criterion::{Criterion, SamplingMode};

let mut c = Criterion::default()
    // Longer warmup for benchmarks that touch the allocator or page cache
    .warm_up_time(std::time::Duration::from_secs(5))
    // More samples for noisy benchmarks (network, disk)
    .sample_size(200)
    // Flat sampling for benchmarks with stable timing; linear for scaling studies
    .sampling_mode(SamplingMode::Flat)
    // Significance level for regression detection
    .significance_level(0.05)
    .measurement_time(std::time::Duration::from_secs(10));
```

### 6.2 `iai-callgrind` — Instruction-Count Benchmarking

`criterion` measures wall-clock time — sensitive to CPU frequency scaling, thermal throttling, and noisy neighbors in CI. `iai-callgrind` measures **instruction and cache events** via Valgrind's Callgrind, producing deterministic, noise-free counts that are ideal for CI regression gates.

```toml
# Cargo.toml
[dev-dependencies]
iai-callgrind = "0.12"

[[bench]]
name = "codec_instr"
harness = false
```

```rust
// benches/codec_instr.rs
use iai_callgrind::{library_benchmark, library_benchmark_group, main};
use my_service::codec::{Message, encode};

#[library_benchmark]
fn bench_encode_4k() -> Vec<u8> {
    let msg = Message { id: 1, payload: vec![0xAB; 4096] };
    encode(&msg)
}

library_benchmark_group!(name = codec; benchmarks = bench_encode_4k);
main!(library_benchmark_groups = codec);
```

```bash
cargo bench --bench codec_instr -- --callgrind
# Output (deterministic — same on every run on same binary):
# codec::bench_encode_4k:
#   Instructions:               4821
#   L1 Hits:                    5134
#   L2 Hits:                       2
#   RAM Hits:                      1
#   Total read (RW):            5210
#   Estimated Cycles:           5288
```

`iai-callgrind` is complementary to `criterion`: use `criterion` for latency distributions (p50/p99) and `iai-callgrind` for deterministic CI gates ("this PR adds 400 instructions to the encode path").

### 6.3 `divan` — A Lighter Alternative

[`divan`](https://github.com/nvzqz/divan) is a newer benchmarking crate that aims for `criterion`'s ergonomics with simpler setup and faster iteration. It supports `#[divan::bench]` attributes and groups, uses less statistical machinery, and integrates with `cargo bench` without `harness = false`. Evaluate it for new projects; stick with `criterion` if you need its HTML reports and baseline comparison.

| Crate | Metric | Determinism | Report | Best for |
|---|---|---|---|---|
| `criterion` | Wall time (ns) with statistics | Noisy — needs multiple samples | HTML violin + regression | Latency, throughput, p99 analysis |
| `iai-callgrind` | Instructions, cache, cycles | Deterministic | Text + callgrind flame | CI regression gate, instruction-level diff |
| `divan` | Wall time, lightweight stats | Noisy but fast | Text | Quick local iteration, simple benchmarks |

### 6.4 Distributed-Systems Lens

Benchmark the path that matters under load, not the microbenchmark that looks good in a README. For a gateway, that is `request → routing → handler → encode → write` end-to-end, not `encode` alone. Gate on **throughput regression** (requests/sec) and **instruction-count delta**, not just wall time — wall time in shared CI is noisy, instruction counts are not. Store `criterion` baselines as artifacts (not in git) and compare PR baselines against `main` baselines fetched from the default branch's last successful run. A 5% wall-time regression that is actually a noisy neighbor is not a regression; a 5% instruction-count regression always is.

---

## 7. Correctness Beyond the Type System: `Miri`, `loom`, and `shuttle`

Rust's borrow checker eliminates data races in safe code and the compiler rejects use-after-free — but `unsafe` blocks, `UnsafeCell`, raw pointers, and concurrent `Atomics` escape those guarantees. Three tools close the gap.

### 7.1 `Miri` — An Interpreter That Catches Undefined Behavior

```mermaid
flowchart TB
    subgraph MiriArch["Miri — MIR interpreter with UB checks"]
        A["Your crate<br/>lib.rs + tests"] --> B["rustc --emit=mir<br/>MIR for every function"]
        B --> C["Miri interpreter<br/>executes MIR, not machine code"]
        C --> D["Memory model<br/>allocation tracking<br/>borrow stack / Tree Borrows"]
        C --> E["UB detectors<br/>use-after-free<br/>out-of-bounds<br/>invalid transmute<br/>data race on UnsafeCell<br/>uninitialized read"]
        D --> E
        E --> F["Miri error<br/>stack trace + allocation history<br/>or PASS"]
        C --> G["Shims<br/>syscalls emulated<br/>FFI / inline asm = unsupported"]
        style C fill:#d0ebff,stroke:#333
        style E fill:#ffc9c9,stroke:#333
    end
```

Miri is a MIR interpreter inside `rustc` that executes your code abstractly, tracking every allocation, borrow, and pointer provenance. When your code does anything that is UB per the Rust Abstract Machine — even if it "works" on x86 — Miri reports it with a precise trace.

**What Miri catches:**

- Use-after-free and double-free (including via `Box::from_raw` misuse)
- Out-of-bounds access through raw pointers
- Data races on `UnsafeCell` / `Cell` / `RefCell` when accessed concurrently without synchronization
- Invalid `transmute`, uninitialized memory reads, misaligned pointer dereference
- Violations of Stacked Borrows / Tree Borrows aliasing rules (the `unsafe` borrow discipline)
- Leaked allocations (with `-Zmiri-leak-check`)

**What Miri cannot do:**

- Run FFI, inline assembly, or syscalls that Miri has no shim for (network I/O, file I/O beyond `std::fs` shims, `io_uring`). Tests that hit these boundaries will error with "unsupported operation" — isolate UB-sensitive code into pure-Rust modules that Miri can exercise.
- Detect UB that requires code generation to manifest (e.g., LLVM miscompilation of UB — Miri catches the UB at the MIR level before that).
- Run at production speed: Miri is 10–100x slower than native execution. Run it on a focused subset in CI, not the entire test suite.

#### Running Miri

```bash
# Install (requires nightly — Miri is tightly coupled to rustc internals)
rustup +nightly component add miri

# Run the test suite under Miri (all tests)
cargo +nightly miri test

# Run only a specific module's tests under Miri (faster, recommended for CI)
cargo +nightly miri test -p my-service --lib unsafe_helpers

# Test a single file with Miri
cargo +nightly miri test --test my_integration

# With flags — e.g., enable Tree Borrows (new aliasing model, default since 1.78) and leak check
MIRIFLAGS="-Zmiri-tree-borrows -Zmiri-leak-check" cargo +nightly miri test

# Example failure — use-after-free reported by Miri:
# error: Undefined Behavior: pointer to alloc123 was dereferenced after this allocation got freed
#   --> src/pool.rs:42:13
#    |
# 42 |             *ptr = 0;
#    |             ^^^^^^^ dereferencing after free
#    |
#    = note: inside `pool::recycle` at src/pool.rs:42:13
#    = note: inside `pool::tests::test_recycle` at src/pool.rs:89:9
```

Example UB that passes `cargo test` but fails under Miri:

```rust
// src/pool.rs — a hand-rolled buffer pool with unsafe reuse
use std::alloc::{alloc, dealloc, Layout};

pub struct RawPool {
    ptr: *mut u8,
    layout: Layout,
}

impl RawPool {
    pub fn new(size: usize) -> Self {
        let layout = Layout::array::<u8>(size).unwrap();
        let ptr = unsafe { alloc(layout) };
        assert!(!ptr.is_null());
        Self { ptr, layout }
    }

    // BUG: caller can call `recycle` twice, double-freeing
    pub unsafe fn recycle(&mut self) {
        unsafe { dealloc(self.ptr, self.layout) };
        // Missing: self.ptr = std::ptr::null_mut();
    }
}

#[test]
fn test_pool_smoke() {
    let mut p = RawPool::new(64);
    unsafe { p.recycle(); }
    // cargo test: passes (memory not reused yet, no visible corruption)
    // cargo miri test: error — second drop double-frees
}

#[test]
fn test_double_recycle_is_ub() {
    let mut p = RawPool::new(64);
    unsafe { p.recycle(); }
    unsafe { p.recycle(); } // Miri: error — dereferencing after free
}
```

### 7.2 `loom` and `shuttle` — Deterministic Concurrency Testing

`Miri` catches UB in single-threaded execution plus some data races. `loom` and `shuttle` explore **all possible thread interleavings** of concurrent code, deterministically.

```mermaid
flowchart TB
    subgraph Loom["loom — model checker for Send/Sync types"]
        A["Your concurrent code<br/>using loom::sync::Arc<br/>loom::sync::Mutex<br/>loom::sync::atomic::AtomicUsize"] --> B["loom::model(|| { ... })<br/>replaces std sync with model"]
        B --> C["Permutation engine<br/>exhaustively interleaves<br/>every atomic / lock / thread op"]
        C --> D["Exploration<br/>N threads x M ops<br/>exponential — bounded"]
        D --> E["Violation?<br/>data race, deadlock,<br/>assertion failure"]
        E -->|yes| F["Minimal trace<br/>interleaving that triggers bug"]
        E -->|no| G["PASS — all interleavings safe<br/>up to exploration bound"]
    end
    subgraph Shuttle["shuttle — runtime for Tokio / async"]
        H["Your async code<br/>tokio::sync, shuttle::future"] --> I["shuttle::check_random(|| { ... }, 1000)"]
        I --> J["Randomized scheduler<br/>controls task poll order<br/>+ chaos on channels/timers"]
        J --> K["Property violation?<br/>panic, deadlock, invariant"]
    end
    style C fill:#fff3bf,stroke:#333
    style J fill:#d3f9d8,stroke:#333
```

**`loom`** — for `std` synchronization primitives. You rewrite your concurrent data structure to use `loom::sync::*` types behind a `cfg(loom)` gate, then `loom::model` exhaustively explores interleavings.

```rust
// Cargo.toml
// [target.'cfg(loom)'.dependencies]
// loom = "0.7"

#[cfg(loom)]
use loom::sync::{Arc, Mutex};
#[cfg(not(loom))]
use std::sync::{Arc, Mutex};

use loom::thread;

// A lock-free-adjacent counter with a subtle race — correct only with loom's checker
fn concurrent_increment(counter: Arc<Mutex<u64>>, n: usize) {
    let mut handles = Vec::new();
    for _ in 0..n {
        let c = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            let mut g = c.lock().unwrap();
            *g += 1;
        }));
    }
    for h in handles { h.join().unwrap(); }
}

#[cfg(loom)]
#[test]
fn test_concurrent_increment_loom() {
    loom::model(|| {
        let counter = Arc::new(Mutex::new(0u64));
        concurrent_increment(Arc::clone(&counter), 2);
        // Loom explores both orderings of the two increments
        assert_eq!(*counter.lock().unwrap(), 2);
    });
}

// For a buggy structure, loom finds the interleaving that breaks it.
// Example: a double-checked locking init without proper fences —
// loom reports "caused data race" with the exact permutation.
```

Loom is exhaustive but exponential — it is practical for 2–3 threads and a handful of operations. Beyond that, it times out. Use it for `Mutex`/`RwLock` wrappers, lock-free queues, and `Atomic*` state machines with small state spaces.

**`shuttle`** — for `tokio` and `async` code. Shuttle replaces Tokio's scheduler with a controlled, randomized scheduler that explores poll orderings, channel rendezvous orderings, and timer interleavings. It does not require `cfg` gating on your sync types — it interposes at the runtime level.

```rust
// Cargo.toml
// [dev-dependencies]
// shuttle = { version = "0.7", features = ["tokio"] }

use shuttle::{check_random, thread};

#[test]
fn test_channel_ordering_deterministic() {
    // shuttle explores many schedules (here, 500 random interleavings)
    check_random(
        || {
            let (tx, rx) = shuttle::sync::mpsc::channel(1);
            thread::spawn(move || tx.send(42).unwrap());
            let val = rx.recv().unwrap();
            assert_eq!(val, 42);
        },
        500,
    );
}

// For async channels and JoinSet, use shuttle's tokio integration:
#[test]
fn test_join_set_no_deadlock() {
    shuttle::check_random(
        || {
            shuttle::future::block_on(async {
                let (tx, mut rx) = shuttle::sync::mpsc::channel(2);
                let jh = shuttle::future::spawn(async move {
                    tx.send(1).await.unwrap();
                });
                let _ = rx.recv().await;
                jh.await.unwrap();
            });
        },
        200,
    );
}
```

| Tool | Model | Scope | Determinism | Runtime | When to use |
|---|---|---|---|---|---|
| `Miri` | MIR interpreter | Single-threaded + `UnsafeCell` races | Deterministic | Native + interpreter | Any `unsafe` code, UB, aliasing |
| `loom` | Exhaustive permutation | `std::sync` / atomics, 2–3 threads | Exhaustive (limited bound) | Model checker | Lock-free structures, `Mutex` wrappers, atomic state machines |
| `shuttle` | Randomized scheduling | `tokio` / `async` / channels | Randomized (configurable iters) | Controlled Tokio | Async task interleavings, `JoinSet`, `select!` races |

#### Concurrency Test Matrix — Choosing the Right Tool

```mermaid
flowchart TB
    A["Is the code unsafe / raw-pointer?"] -->|yes| B["Miri<br/>cargo +nightly miri test"]
    A -->|no| C["Is the bug a thread interleaving?"]
    C -->|std sync / atomics<br/>small state space| D["loom<br/>exhaustive model"]
    C -->|tokio / async / channels| E["shuttle<br/>randomized scheduler"]
    C -->|both| F["loom for sync primitives<br/>shuttle for async orchestration<br/>+ miri for unsafe inside either"]
    B --> G["Add proptest for state-machine<br/>invariants across interleavings"]
    D --> G
    E --> G
    style B fill:#ffc9c9,stroke:#333
    style D fill:#ffd8a8,stroke:#333
    style E fill:#d3f9d8,stroke:#333
```

> **Rule:** If your concurrent code contains `unsafe`, run *both* `Miri` (for UB) and `loom`/`shuttle` (for interleaving). Miri does not explore interleavings; loom/shuttle do not detect aliasing UB. They are complementary.

---

## 8. CI Pipeline: Caching, Partitioning, and Gate Composition

All of the above is worthless if CI takes 25 minutes and developers bypass it. This section composes the full pipeline with correct caching and partitioning.

### 8.1 Caching — `Swatinem/rust-cache` and `sccache`

Compiling a Rust workspace is dominated by `rustc` invocations — each crate compiles to an `rlib`/`rmeta` in `target/`. Caching `target/` naively causes stale or poisoned builds; the correct cache keys on `rustc` version, `Cargo.lock`, and `rust-toolchain.toml`.

`Swatinem/rust-cache` (the community standard, used by the Rust project itself) handles this correctly out of the box:

```mermaid
flowchart LR
    subgraph CacheFlow["CI cache lifecycle — Swatinem/rust-cache"]
        A["Checkout"] --> B["restore cache<br/>key: rustc --version<br/>+ Cargo.lock hash<br/>+ runner OS"]
        B --> C["cargo build / clippy / nextest<br/>incremental: reuses target/"]
        C --> D["save cache<br/>on success — prunes stale artifacts"]
        D --> E["Next run: hit → 70-90% faster<br/>miss → full rebuild"]
        F["rust-toolchain.toml<br/>channel + components"] -.-> B
        G["Cargo.lock"] -.-> B
        H["deny.toml / clippy.toml"] -.-> C
    end
    subgraph Sccache["sccache — compiler wrapper cache"]
        I["RUSTC_WRAPPER=sccache"] --> J["sccache caches rustc<br/>object files by input hash<br/>shared across branches"]
        J --> K["S3 / GHA cache backend"]
    end
    style B fill:#d0ebff,stroke:#333
    style D fill:#d3f9d8,stroke:#333
    style I fill:#fff3bf,stroke:#333
```

Correct configuration:

```yaml
# .github/workflows/ci.yml — the complete gate
name: ci

on:
  pull_request:
  push:
    branches: [main]

env:
  CARGO_TERM_COLOR: always
  RUSTFLAGS: "-D warnings"   # deny warnings globally — clippy inherits this

jobs:
  # ── Fast gates first: format + clippy + audit (no build needed for fmt) ──
  fmt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@master
        with:
          toolchain: stable
          components: rustfmt
      - run: cargo fmt --all -- --check

  clippy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@master
        with:
          toolchain: stable
          components: clippy
      - uses: Swatinem/rust-cache@v2
        with:
          # Shared cache key across jobs — Swatinem handles prefixing internally
          shared-key: "ci"
          save-if: ${{ github.ref == 'refs/heads/main' }}
      - run: cargo clippy --workspace --all-targets --all-features -- -D warnings

  deny:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@master
        with: { toolchain: stable }
      - uses: Swatinem/rust-cache@v2
      - run: cargo install cargo-deny --locked
      - run: cargo deny check advisories bans licenses sources

  # ── Test gate: nextest with partitioning ──
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        partition: ["hash:4/1", "hash:4/2", "hash:4/3", "hash:4/4"]
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@master
        with: { toolchain: stable }
      - uses: Swatinem/rust-cache@v2
        with: { shared-key: "ci" }
      - name: Install nextest
        uses: taiki-e/install-action@v2
        with: { tool: cargo-nextest }
      - name: Run tests (partition ${{ matrix.partition }})
        run: cargo nextest run --workspace --profile ci --partition ${{ matrix.partition }} --message-format junit --output-file junit-${{ strategy.job-index }}.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: junit-${{ strategy.job-index }}
          path: junit-*.xml

  # ── Nightly-only gates: miri + loom (allow failure on PR, deny on main) ──
  miri:
    runs-on: ubuntu-latest
    # Only run on main + nightly schedule to avoid slowing every PR
    if: github.ref == 'refs/heads/main' || github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@master
        with:
          toolchain: nightly
          components: miri
      - uses: Swatinem/rust-cache@v2
      - run: cargo +nightly miri test -p my-service --lib -- --test-threads=1

  # ── Benchmark gate: criterion comparison (main vs PR) ──
  bench:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: dtolnay/rust-toolchain@master
        with: { toolchain: stable }
      - uses: Swatinem/rust-cache@v2
      # Restore main baseline from cache / artifact
      - run: cargo bench --bench codec_bench -- --save-baseline main || true
      - run: git checkout ${{ github.event.pull_request.head.sha }}
      - run: cargo bench --bench codec_bench -- --baseline main
```

#### Cache Invalidation Done Right

`Swatinem/rust-cache` automatically keys on:

- `rustc --version --verbose` hash (so toolchain bumps invalidate)
- `Cargo.lock` hash (so dependency changes invalidate selectively via prefix matching)
- Runner OS (`ubuntu-latest` vs `macos-latest` have separate caches)

Add these to avoid silent staleness:

```yaml
- uses: Swatinem/rust-cache@v2
  with:
    # Include rustfmt.toml / clippy.toml / deny.toml in the cache context
    # so a lint-config change does not serve a stale clippy result
    workspaces: ". -> target"
    cache-provider: buildjet  # or default GHA cache
    # Do not cache on PRs that only touch docs — opt-in via path filter
```

For **self-hosted runners** or **cross-branch sharing**, add `sccache` as a second layer:

```bash
# Install sccache and wrap rustc
cargo install sccache --locked
export RUSTC_WRAPPER=sccache
export SCCACHE_GHA_ENABLED=true   # uses GHA cache as backend
# sccache caches at the rustc-invocation level, so even a new branch
# hits the cache for unchanged crates — complementary to Swatinem's target/ cache
```

### 8.2 Putting It All Together — Pipeline Ordering

The gate order matters for cost and latency:

```mermaid
flowchart LR
    A["PR opened"] --> B["fmt --check<br/>~5s"]
    B -->|pass| C["clippy --workspace<br/>~60s"]
    C -->|pass| D["cargo deny check<br/>~10s"]
    D -->|pass| E["cargo nextest run<br/>4 shards × ~90s<br/>parallel shards"]
    E -->|pass| F["bench compare<br/>~120s"]
    F -->|pass| G["✅ mergeable"]
    B -->|fail| X["❌ fail fast<br/>no further jobs"]
    C -->|fail| X
    D -->|fail| X
    E -->|fail| X
    H["Nightly cron<br/>on main"] --> I["miri test<br/>~600s"]
    H --> J["loom/shuttle<br/>~300s"]
    H --> K["cargo audit<br/>scheduled"]
    style B fill:#e7f5ff,stroke:#333
    style E fill:#d3f9d8,stroke:#333
    style I fill:#ffc9c9,stroke:#333
    style X fill:#ffc9c9,stroke:#333
```

- **PR pipeline:** `fmt` → `clippy` → `deny` → `nextest` (sharded) → `bench` comparison. Fastest, cheapest first; `miri`/`loom` excluded from PR to keep latency under 5 minutes.
- **Main + nightly pipeline:** all of the above plus `miri`, `loom`/`shuttle`, `cargo audit` (scheduled, because new advisories appear without code changes), and full `criterion` baselines saved as artifacts.
- **Required status checks in GitHub:** `fmt`, `clippy`, `deny`, and all `test` partitions must be required; `miri` and `bench` can be non-required on PRs but required on `main` branch protection.

### 8.3 Distributed-Systems Lens

CI is a distributed system. Your test suite is sharded across runners that share a cache — a cache with consistency and invalidation semantics you must understand. A poisoned or stale `target/` cache produces "works in CI, fails locally" and vice versa — the distributed analogue of a stale read. Use `Swatinem/rust-cache`'s content-addressed keys, never hand-roll `actions/cache` with `hashFiles('**/Cargo.lock')` as the sole key (it ignores `rustc` version), and make the cache `save-if: main` so PRs read from `main`'s cache but do not pollute it. Partition tests by `hash`, not by crate — crate-based sharding creates stragglers when one crate has 80% of the tests. And treat `miri`/`loom` like chaos engineering: run them on `main` nightly, not on every PR — their value is high but their cost (10–100x slowdown) is incompatible with PR latency SLOs.

---

## Key Takeaways

- `cargo test`'s thread-per-test, process-per-binary model leaks global state and serializes binaries. `cargo nextest`'s process-per-test model isolates each test, enables per-test timeouts/retries, and supports `hash`-stable partitioning across CI runners. Adopt `nextest.toml` with `slow-timeout`, `retries`, and per-suite overrides as the workspace standard.
- Fixtures must respect process-per-test isolation: use `rstest` for parameterization, `testcontainers` for real dependencies (one container per process, random ports), and `OnceLock` only for cheap in-process singletons. Snapshot tests (`insta`) make response-shape regressions reviewable.
- Property tests (`proptest`/`quickcheck`) encode invariants, not examples. State roundtrips, idempotency, and shard-union properties are their highest-value targets in backends. Complement with coverage-guided fuzzing (`cargo fuzz`) for parsers and `unsafe` boundaries.
- Clippy is a compiler plugin with ~700 lints organized into `correctness`, `suspicious`, `complexity`, `perf`, `style`, `cargo`, `pedantic`, `nursery`, and `restriction`. Deny `correctness`/`suspicious`/`perf`, warn on `complexity`/`style`, cherry-pick `pedantic`, and never blanket-enable `nursery` or `restriction`. Configure via `[workspace.lints.clippy]` in `Cargo.toml` and fine-tune via `clippy.toml`; suppress at the narrowest scope with `#[allow]` and a comment.
- `rustfmt` is idempotent and deterministic — gate CI with `cargo fmt --all -- --check`, pin the toolchain in `rust-toolchain.toml`, and keep `rustfmt.toml` minimal. Formatting is a coordination primitive: the earlier it fails in CI, the cheaper.
- `cargo audit` (RustSec advisories + yanked) and `cargo deny` (advisories, bans, licenses, sources) are the supply-chain gates. Centralize `deny.toml` across the workspace, run both on every PR and on a nightly cron (new advisories land without code changes), and complement with `cargo vet` for publisher vetting when human review is required.
- `criterion` measures latency distributions with statistical rigor and HTML reports; `iai-callgrind` measures deterministic instruction/cache counts for CI gates; `divan` trades statistical depth for ergonomic speed. Gate throughput and instruction-count deltas, not just wall time — wall time in shared CI is noisy, instruction counts are not.
- `Miri` interprets MIR to catch UB (use-after-free, data races, invalid transmute) that native execution hides. `loom` exhaustively explores `std::sync` interleavings for small state spaces; `shuttle` randomized-tests `tokio`/`async` interleavings. Run `Miri` + `loom`/`shuttle` on `unsafe` and concurrent code — they are complementary, not substitutes.
- Compose CI as `fmt → clippy → deny → nextest (sharded) → bench` on PRs and add `miri`/`loom`/`audit` on `main` nightly. Cache with `Swatinem/rust-cache` (keys on `rustc` version + `Cargo.lock` + OS), optionally layer `sccache` for cross-branch object caching, and partition tests by `hash` for stable shard balance. Make fast gates required, nightly gates informational on PRs and required on `main`.

---

## Further Reading

- **Rust Toolchain & Testing**
  - `cargo nextest` book — https://nexte.st/book/ — partitioning, profiles, JUnit, retries, and `nextest.toml` reference.
  - `cargo test` and `libtest` — https://doc.rust-lang.org/cargo/commands/cargo-test.html and https://doc.rust-lang.org/rustc/tests/index.html
  - `rstest` — https://github.com/la10736/rstest
  - `testcontainers-rs` — https://docs.rs/testcontainers
  - `insta` snapshot testing — https://insta.rs/docs/

- **Property Testing & Fuzzing**
  - `proptest` book — https://proptest-rs.github.io/proptest/
  - `quickcheck` — https://github.com/BurntSushi/quickcheck
  - `cargo fuzz` (libFuzzer) — https://rust-fuzz.github.io/book/cargo-fuzz.html
  - *Finding property tests via state-machine modeling* — https://proptest-rs.github.io/proptest/proptest/tutorial.html#stateful-testing

- **Clippy & Formatting**
  - Clippy lint list and configuration — https://rust-lang.github.io/rust-clippy/master/index.html and https://doc.rust-lang.org/clippy/configuration.html
  - `dylint` — https://github.com/trailofbits/dylint
  - `marker` — https://github.com/rust-marker/marker
  - `rustfmt` configuration — https://rust-lang.github.io/rustfmt/ and https://github.com/rust-lang/rustfmt/blob/master/Configurations.md

- **Supply-Chain Auditing**
  - RustSec Advisory Database — https://rustsec.org/ and https://github.com/RustSec/advisory-db
  - `cargo audit` — https://github.com/RustSec/rustsec/tree/main/cargo-audit
  - `cargo deny` — https://embarkstudios.github.io/cargo-deny/
  - `cargo vet` — https://mozilla.github.io/cargo-vet/
  - `cargo-supply-chain` — https://github.com/rust-secure-code/cargo-supply-chain

- **Benchmarking**
  - `criterion.rs` book — https://bheisler.github.io/criterion.rs/book/
  - `iai-callgrind` — https://github.com/iai-callgrind/iai-callgrind
  - `divan` — https://github.com/nvzqz/divan

- **Miri, Loom, Shuttle**
  - Miri — https://github.com/rust-lang/miri and https://doc.rust-lang.org/nightly/nightly-rustc/miri.html
  - Tree Borrows (Miri aliasing model) — https://perso.crans.org/vanitori/treeborrows/
  - `loom` — https://github.com/tokio-rs/loom
  - `shuttle` — https://github.com/awslabs/shuttle (now https://github.com/shuttle-hq/shuttle is a different project — the model checker is `awslabs/shuttle`)
  - *Testing concurrent Rust with loom and shuttle* — https://docs.rs/loom and https://docs.rs/shuttle

- **CI & Caching**
  - `Swatinem/rust-cache` — https://github.com/Swatinem/rust-cache
  - `sccache` — https://github.com/mozilla/sccache
  - `cargo bench` and `cargo test` profiles — https://doc.rust-lang.org/cargo/reference/profiles.html


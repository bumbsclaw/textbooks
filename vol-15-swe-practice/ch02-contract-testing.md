# Chapter 2 — Contract Testing, Test Doubles, and Testability

**What this chapter covers.** A backend service never runs alone — it calls databases, queues, peer services, and third-party APIs, and every one of those boundaries is a seam where assumptions diverge and bugs hide. This chapter is about testing those seams without coupling your suite to someone else's deployment schedule. You will learn the full taxonomy of test doubles and when each earns its keep, how consumer-driven contract testing with Pact (and schema-based alternatives) catches drift that integration tests miss, and how to design services for testability in the first place — so that seams are explicit, deterministic, and cheap to exercise. Every technique is grounded in runnable Pact, WireMock, and fake-based examples.

Learning goals — after this chapter you should be able to:

- Distinguish dummies, stubs, spies, mocks, and fakes, and choose the right double for a given dependency and test goal.
- Explain mockist vs. classical testing styles, their trade-offs, and why fakes are usually preferable to mocks for domain-critical collaborators.
- Write and verify consumer-driven contracts with Pact (consumer and provider sides), operate a Pact Broker, and integrate contract verification into CI with `can-i-deploy`.
- Apply schema-based contract testing (OpenAPI, JSON Schema, protobuf breaking-change detection) where Pact is not the right fit.
- Design for testability via ports and adapters, dependency injection, clock/random boundaries, and seams — and recognise testability anti-patterns (statics, hidden I/O, time coupling).
- Decide when to use a real dependency (Testcontainers), a fake, a stub, or a contract test — and compose them into a coherent portfolio with Chapter 1's strategy.

---

## The seam is the risk

### Why boundaries deserve their own testing discipline

Inside a single service, the compiler and the type system catch a large class of mistakes — a renamed field fails to compile, a wrong arity fails to type-check. Across a network boundary, none of that holds. Two services can agree on a field name on Monday, diverge on Tuesday, and discover the mismatch only when a deserialisation exception pages someone at 03:00. The same is true for subtler contracts: pagination semantics, error-code vocabularies, idempotency guarantees, retry expectations, and nullability assumptions that are never written down but are load-bearing all the same.

Three facts make boundary testing distinct from in-process testing:

1. **Independent deployability.** The consumer and provider evolve on different cadences, owned by different teams, with different release trains. A test that requires both to be deployed together is not a unit of independent progress.
2. **Asymmetric knowledge.** The consumer knows how it *uses* the provider; the provider knows what it *guarantens*. Neither view is complete, and the gap between them is where drift lives.
3. **Shared-nothing verification.** Ideally each side can verify its obligations without running the other side — otherwise every change requires a full integration environment, which is precisely the bottleneck contract testing is designed to remove.

Test doubles isolate one side of a seam; contract tests verify that the two sides' assumptions about the seam are compatible. Testability is the design discipline that makes both possible without contortion.

---

## Test doubles: a precise taxonomy

The term "mock" is used colloquially to mean any test double. Gerard Meszaros's taxonomy (*xUnit Test Patterns*, 2007) — refined by Martin Fowler — distinguishes five kinds. The distinction is not pedantry; each double has different coupling, fidelity, and maintenance characteristics.

```mermaid
flowchart TB
    SUT["System Under Test"]

    SUT --> Dummy["Dummy<br/>passed but never used<br/>fills a required param"]
    SUT --> Stub["Stub<br/>canned answers<br/>to calls made during test"]
    SUT --> Spy["Spy<br/>records calls<br/>for later assertion"]
    SUT --> Mock["Mock<br/>pre-programmed<br/>expectations verified<br/>automatically"]
    SUT --> Fake["Fake<br/>working implementation<br/>with simplified internals<br/>e.g. in-memory DB"]

    style Fake fill:#e8f5e9
    style Mock fill:#fff3e0
    style Stub fill:#e3f2fd
```

*Figure 2-1: The five test doubles. Dummies, stubs, spies, and mocks are all hollow — they have no real behaviour. Fakes are the exception: they have real (but simplified) behaviour.*

| Double | Answers calls? | Records calls? | Has real logic? | Verifies expectations? | Typical use |
|--------|---------------|----------------|-----------------|------------------------|-------------|
| **Dummy** | No (or throws) | No | No | No | Satisfy a required parameter that the SUT does not touch in this test. |
| **Stub** | Yes — canned | No | No | No | Control indirect inputs: "when the clock is 2026-08-20, the discount is expired." |
| **Spy** | Optionally | Yes | No | Manually (assert after) | Observe indirect outputs: "was `sendEmail` called once with this payload?" |
| **Mock** | Yes — programmed | Yes | No | Automatically (fails if expectations unmet) | Specify interaction protocol: "must call `charge` exactly once before `confirm`." |
| **Fake** | Yes — real logic | Optionally | **Yes** (simplified) | Optionally | Replace a volatile dependency with a fast, deterministic, in-memory realisation. |

### The decision rule

```
Is the collaborator volatile (network, clock, FS, randomness, slow)?
├── No  → Use the real thing (value object, pure function, in-memory mapper).
└── Yes → Can you write a small, faithful, in-memory implementation?
         ├── Yes → Prefer a Fake (highest fidelity among doubles).
         └── No  → Is the test about the interaction protocol itself?
                  ├── Yes → Mock (or Spy + assert).
                  └── No  → Stub (canned answer) or Spy (observe outcome).
```

**Fakes dominate for domain-critical collaborators** because they preserve behaviour rather than specifying interactions. An in-memory `OrderRepository` that actually enforces uniqueness and supports `findById` exercises the SUT's logic against realistic semantics; a mock of the same repository exercises the SUT's logic against the test author's *assumptions* about what the repository does — which is precisely what you are trying to verify.

### Mocks, stubs, and fakes in code

**Go — interfaces, fakes, and `mockgen`/`testify/mock`:**

```go
// internal/ports/ports.go
package ports

import "context"

type PaymentGateway interface {
    Charge(ctx context.Context, req ChargeRequest) (ChargeResult, error)
}
type ChargeRequest struct {
    AmountCents int64
    Token       string
    IdempotencyKey string
}
type ChargeResult struct {
    ChargeID string
    Status   string // "succeeded" | "failed"
}

// internal/payments/service.go
package payments

import "context"

type Service struct {
    gateway ports.PaymentGateway
    repo    OrderRepository // interface — can be faked in tests
}

func NewService(gw ports.PaymentGateway, repo OrderRepository) *Service {
    return &Service{gateway: gw, repo: repo}
}

func (s *Service) Checkout(ctx context.Context, orderID, token, idemKey string) error {
    order, err := s.repo.Find(ctx, orderID)
    if err != nil {
        return err
    }
    res, err := s.gateway.Charge(ctx, ports.ChargeRequest{
        AmountCents: order.TotalCents,
        Token: token,
        IdempotencyKey: idemKey,
    })
    if err != nil {
        return err
    }
    if res.Status != "succeeded" {
        return ErrChargeFailed
    }
    return s.repo.MarkPaid(ctx, orderID, res.ChargeID)
}
```

```go
// internal/payments/fake_gateway_test.go — a Fake
package payments

type FakeGateway struct {
    Charges []ports.ChargeRequest
    // Control behaviour per test without re-programming expectations
    NextResult ports.ChargeResult
    NextErr    error
}

func (f *FakeGateway) Charge(_ context.Context, req ports.ChargeRequest) (ports.ChargeResult, error) {
    f.Charges = append(f.Charges, req)
    if f.NextErr != nil {
        return ports.ChargeResult{}, f.NextErr
    }
    return f.NextResult, nil
}

// In-memory fake repo — real map, real concurrency guard, real semantics
type FakeOrderRepo struct {
    mu     sync.Mutex
    orders map[string]Order
}

func (r *FakeOrderRepo) Find(_ context.Context, id string) (Order, error) {
    r.mu.Lock()
    defer r.mu.Unlock()
    o, ok := r.orders[id]
    if !ok {
        return Order{}, ErrNotFound
    }
    return o, nil
}
func (r *FakeOrderRepo) MarkPaid(_ context.Context, id, chargeID string) error {
    r.mu.Lock()
    defer r.mu.Unlock()
    o := r.orders[id]
    o.ChargeID = chargeID
    o.Status = "paid"
    r.orders[id] = o
    return nil
}
```

```go
// internal/payments/service_test.go — using the fakes
func TestCheckout_Succeeds(t *testing.T) {
    gw := &FakeGateway{NextResult: ports.ChargeResult{ChargeID: "ch-1", Status: "succeeded"}}
    repo := &FakeOrderRepo{orders: map[string]Order{
        "ord-1": {ID: "ord-1", TotalCents: 9900},
    }}
    svc := NewService(gw, repo)

    err := svc.Checkout(context.Background(), "ord-1", "tok_visa", "idem-1")
    require.NoError(t, err)
    require.Len(t, gw.Charges, 1)
    assert.Equal(t, int64(9900), gw.Charges[0].AmountCents)
    assert.Equal(t, "idem-1", gw.Charges[0].IdempotencyKey)

    got, _ := repo.Find(context.Background(), "ord-1")
    assert.Equal(t, "paid", got.Status)
}

func TestCheckout_IdempotencyKeyPropagated(t *testing.T) {
    gw := &FakeGateway{NextResult: ports.ChargeResult{ChargeID: "ch-1", Status: "succeeded"}}
    repo := &FakeOrderRepo{orders: map[string]Order{"ord-1": {ID: "ord-1", TotalCents: 500}}}
    svc := NewService(gw, repo)

    // The service must propagate the idempotency key — a contract property
    // that a mock-based test would assert via expectation, and a fake-based
    // test asserts via recorded state. Both work; the fake also proves the
    // charge would be deduplicated if the gateway were real.
    _ = svc.Checkout(context.Background(), "ord-1", "tok_visa", "idem-abc")
    _ = svc.Checkout(context.Background(), "ord-1", "tok_visa", "idem-abc")
    // Two calls recorded — deduplication is the gateway's job; the service's
    // job is to send the same key. A contract test (below) verifies the gateway honours it.
    assert.Equal(t, "idem-abc", gw.Charges[0].IdempotencyKey)
    assert.Equal(t, "idem-abc", gw.Charges[1].IdempotencyKey)
}
```

For cases where a fake is genuinely infeasible (a third-party SDK with no interface, a complex protocol), use a generated mock — but keep it narrow:

```go
//go:generate mockgen -source=../ports/ports.go -destination=mocks/gateway_mock.go -package=mocks
// In test:
ctrl := gomock.NewController(t)
mgw := mocks.NewMockPaymentGateway(ctrl)
mgw.EXPECT().Charge(gomock.Any(), gomock.Any()).Return(
    ports.ChargeResult{ChargeID: "ch-1", Status: "succeeded"}, nil,
).Times(1)
```

**Python — `unittest.mock` vs. `pytest-mock` vs. hand-rolled fake:**

```python
# tests/test_payments.py
from unittest.mock import MagicMock, call
import pytest
from app.payments import CheckoutService

# --- Stub: canned clock ---
class FixedClock:
    def now(self): return datetime(2026, 8, 20, tzinfo=timezone.utc)

# --- Fake: in-memory gateway with real idempotency semantics ---
class FakeGateway:
    def __init__(self):
        self.charges: list[dict] = []
        self._by_key: dict[str, dict] = {}

    def charge(self, *, amount_cents, token, idempotency_key):
        if idempotency_key in self._by_key:
            return self._by_key[idempotency_key]  # deduplicate
        result = {"charge_id": f"ch-{len(self.charges)+1}", "status": "succeeded"}
        self.charges.append({"amount_cents": amount_cents, "token": token,
                              "idempotency_key": idempotency_key})
        self._by_key[idempotency_key] = result
        return result

def test_checkout_deduplicates_via_fake():
    gw = FakeGateway()
    svc = CheckoutService(gateway=gw)
    svc.checkout(order_id="o1", token="tok", idempotency_key="k1")
    svc.checkout(order_id="o1", token="tok", idempotency_key="k1")
    assert len(gw.charges) == 1  # fake enforces real semantics

# --- Mock: when the interaction protocol IS the requirement ---
def test_checkout_calls_charge_once(mocker):
    gw = mocker.Mock()
    gw.charge.return_value = {"charge_id": "ch-1", "status": "succeeded"}
    svc = CheckoutService(gateway=gw)
    svc.checkout(order_id="o1", token="tok", idempotency_key="k1")
    gw.charge.assert_called_once_with(amount_cents=9900, token="tok", idempotency_key="k1")

# Prefer the fake version above unless you specifically need to verify
# the interaction shape. Mocks couple to call structure; fakes couple to behaviour.
```

### The mockist trap

Mock-heavy suites exhibit a characteristic pathology: they are **highly coupled to implementation, lowly coupled to behaviour**. Renaming an internal helper, inlining a private method, or reordering two independent calls breaks dozens of tests even though observable behaviour is unchanged. Symptoms:

- Tests that assert `mock.Verify(x => x.Foo(It.IsAny<string>()), Times.Once)` for every collaborator call — the test knows *how* the SUT works, not *what* it does.
- Mocks returning mocks (a mock's return value is itself a mock) — a sign the abstraction is not a seam but a leaky decomposition.
- Tests that pass when the mock is lenient and fail when strict, with no change in production code — the suite is testing its own setup.

The remedy is not to ban mocks but to **default to fakes and real collaborators**, reaching for mocks only when the interaction protocol is the contract under test (e.g., "must not call `charge` twice with different idempotency keys").

---

## Contract testing

Integration tests verify collaboration by running both sides together. Contract tests verify it by **capturing each side's assumptions as a shareable, versioned artefact** and checking that the two sets of assumptions are compatible — without requiring both sides to be deployed at the same time.

### Two flavours

| Flavour | Who defines the contract? | What is verified? | Best for |
|---------|--------------------------|-------------------|----------|
| **Consumer-driven (Pact)** | Consumer records its expectations; provider verifies it can satisfy them. | Consumer's actual usage — only the fields and behaviours the consumer depends on. | Internal service-to-service APIs where consumers and providers are separate teams. |
| **Provider-driven / schema-based** | Provider publishes its schema; consumers verify they conform. | Provider's declared surface — the full API as specified. | Public APIs, OpenAPI-governed surfaces, protobuf/gRPC with breaking-change detection, third-party providers. |

In practice most organisations use both: Pact for the service graph they control, schema testing for the boundaries they publish or consume from outside.

### Consumer-driven contracts with Pact

Pact formalises the consumer's expectations as a **pact file** (JSON) that records every interaction the consumer depends on: request shape, response shape, headers, status codes, and matching rules. The consumer test generates the pact; the provider test replays it against the real provider. A **Pact Broker** mediates — storing pacts, triggering provider verification, and gating deployments with `can-i-deploy`.

```mermaid
sequenceDiagram
    participant Consumer as Consumer<br/>(Order Service)
    participant Pact as Pact file<br/>(JSON)
    participant Broker as Pact Broker
    participant Provider as Provider<br/>(Payment Service)
    participant CI as CI / CD

    Consumer->>Pact: consumer test generates pact<br/>"given order ord-1 exists,<br/>when POST /charges,<br/>then 201 with charge_id"
    Pact->>Broker: publish pact<br/>(consumer version, branch, tags)
    Broker->>Provider: webhook — pact changed
    Provider->>Broker: fetch pacts for verification
    Provider->>Provider: replay interactions<br/>against real provider
    Provider->>Broker: publish verification result
    CI->>Broker: can-i-deploy?<br/>(consumer + provider versions)
    Broker->>CI: yes / no — all pacts verified?
    CI->>CI: gate deployment
```

*Figure 2-2: The Pact lifecycle. Consumer and provider never need to be deployed together — the pact file and the broker decouple their verification. The `can-i-deploy` check is the deployment gate.*

#### Consumer test (TypeScript — `@pact-foundation/pact`)

```typescript
// consumer/pact/payment.pact.test.ts
import { PactV4, MatchersV3 } from '@pact-foundation/pact';
import { PaymentClient } from '../src/payment-client';

const { like, uuid, iso8601DateTimeWithMillis } = MatchersV3;

const provider = new PactV4({
  consumer: 'order-service',
  provider: 'payment-service',
});

describe('PaymentClient — consumer contract', () => {
  it('creates a charge for a valid order', async () => {
    await provider
      .addInteraction()
      .given('order ord-1 exists with total 9900')
      .uponReceiving('a request to create a charge')
      .withRequest({
        method: 'POST',
        path: '/v1/charges',
        headers: { 'Content-Type': 'application/json', 'Idempotency-Key': like('idem-abc-123') },
        body: { order_id: 'ord-1', amount_cents: 9900, token: 'tok_visa' },
      })
      .willRespondWith({
        status: 201,
        headers: { 'Content-Type': 'application/json' },
        body: {
          charge_id: uuid('ch-550e8400-e29b-41d4-a716-446655440000'),
          status: like('succeeded'),
          created_at: iso8601DateTimeWithMillis('2026-08-20T12:00:00.000Z'),
        },
      })
      .executeTest(async (mockServer) => {
        const client = new PaymentClient(mockServer.url);
        const result = await client.createCharge({
          orderId: 'ord-1',
          amountCents: 9900,
          token: 'tok_visa',
          idempotencyKey: 'idem-abc-123',
        });
        expect(result.charge_id).toBeDefined();
        expect(result.status).toBe('succeeded');
      });
  });

  it('returns 422 for an unknown order', async () => {
    await provider
      .addInteraction()
      .given('order ord-unknown does not exist')
      .uponReceiving('a charge for an unknown order')
      .withRequest({
        method: 'POST',
        path: '/v1/charges',
        body: { order_id: 'ord-unknown', amount_cents: 100, token: 'tok_visa' },
      })
      .willRespondWith({
        status: 422,
        headers: { 'Content-Type': 'application/json' },
        body: { error: like('order not found'), code: like('ORDER_NOT_FOUND') },
      })
      .executeTest(async (mockServer) => {
        const client = new PaymentClient(mockServer.url);
        await expect(
          client.createCharge({ orderId: 'ord-unknown', amountCents: 100, token: 'tok_visa', idempotencyKey: 'k2' }),
        ).rejects.toMatchObject({ status: 422 });
      });
  });
});
```

Running this test starts a local mock provider, replays the interactions, and writes `pacts/order-service-payment-service.json`. Matching rules (`like`, `uuid`, `iso8601DateTimeWithMillis`) distinguish **structure** (must be a UUID) from **example values** (this particular UUID), so the provider can return any valid UUID and still satisfy the contract.

**Publishing to the broker (CI):**

```bash
# consumer CI — after pact tests pass
pact-broker publish ./pacts \
  --consumer-app-version "$GIT_SHA" \
  --branch "$GIT_BRANCH" \
  --broker-base-url "$PACT_BROKER_BASE_URL" \
  --broker-token "$PACT_BROKER_TOKEN"

# Or via the Pact CLI Docker image / npm script:
# npx pact-broker publish ...
```

#### Provider verification (Go — `pact-go` v2)

```go
// provider/pact/verify_test.go
package pact_test

import (
    "fmt"
    "net"
    "net/http"
    "os"
    "testing"

    "github.com/pact-foundation/pact-go/v2/models"
    "github.com/pact-foundation/pact-go/v2/provider"

    "example.com/payment-service/internal/app"
    "example.com/payment-service/internal/store"
)

func TestPactProvider(t *testing.T) {
    // Bring up the real provider with a test double for its own downstream
    // (or a Testcontainers DB — provider verification should be as real as possible)
    db := newTestDB(t) // Testcontainers Postgres, migrated
    srv := app.NewServer(db)
    ln, err := net.Listen("tcp", "127.0.0.1:0")
    if err != nil {
        t.Fatal(err)
    }
    go func() { _ = http.Serve(ln, srv.Handler()) }()
    t.Cleanup(func() { _ = ln.Close() })
    baseURL := fmt.Sprintf("http://%s", ln.Addr().String())

    verifier := provider.NewVerifier()

    // State handlers — set up the provider state named in .given()
    stateHandlers := models.StateHandlers{
        "order ord-1 exists with total 9900": func(setup bool, s models.ProviderState) error {
            if setup {
                return store.SeedOrder(db, s.Params, map[string]any{
                    "id": "ord-1", "total_cents": 9900,
                })
            }
            return store.CleanOrder(db, "ord-1")
        },
        "order ord-unknown does not exist": func(setup bool, s models.ProviderState) error {
            if setup {
                return store.DeleteOrder(db, "ord-unknown")
            }
            return nil
        },
    }

    err = verifier.VerifyProvider(t, provider.VerifyRequest{
        Provider:              "payment-service",
        ProviderBaseURL:       baseURL,
        BrokerURL:             os.Getenv("PACT_BROKER_BASE_URL"),
        BrokerToken:           os.Getenv("PACT_BROKER_TOKEN"),
        ConsumerVersionSelectors: []models.Selector{
            // Verify the pacts for the main branch + any deployed consumer versions
            {Branch: "main", Latest: true},
            {DeployedOrReleased: true},
        },
        StateHandlers:         stateHandlers,
        PublishVerificationResults: true,
        ProviderVersion:       os.Getenv("GIT_SHA"),
        ProviderBranch:        os.Getenv("GIT_BRANCH"),
        // Fail the test if the provider is missing a handler for a given state
        BeforeEach: func() error { return nil },
    })
    if err != nil {
        t.Error(err)
    }
}
```

**Provider verification with `pact-stub-service` for local development:**

```bash
# Run the provider's pact stub locally so consumers can develop without the real provider
docker run --rm -p 8080:8080 \
  -v $(pwd)/pacts:/pacts \
  pactfoundation/pact-stub-server -p 8080 -d /pacts
```

#### Pact Broker and `can-i-deploy`

The broker is the source of truth for "which consumer versions are compatible with which provider versions." The deployment gate is a single command:

```bash
# In each service's CD pipeline — before deploying to any environment
pact-broker can-i-deploy \
  --pacticipant order-service --version "$GIT_SHA" \
  --pacticipant payment-service --version "$PROVIDER_SHA" \
  --broker-base-url "$PACT_BROKER_BASE_URL" \
  --broker-token "$PACT_BROKER_TOKEN" \
  --to-environment production

# Exit code 0 → safe to deploy; non-zero → a pact is unverified, block deploy
# Wire as a required check in GitHub/GitLab branch protection
```

**Broker deployment (self-hosted):**

```yaml
# docker-compose.pact-broker.yaml
services:
  postgres:
    image: postgres:16-alpine
    environment: { POSTGRES_DB: pact_broker, POSTGRES_USER: pact_broker, POSTGRES_PASSWORD: pact }
  broker:
    image: pactfoundation/pact-broker:latest
    ports: ["9292:9292"]
    environment:
      PACT_BROKER_DATABASE_URL: postgres://pact_broker:pact@postgres/pact_broker
      PACT_BROKER_DATABASE_ADAPTER: postgres
      PACT_BROKER_BASIC_AUTH_USERNAME: broker
      PACT_BROKER_BASIC_AUTH_PASSWORD: "${BROKER_PASSWORD}"
    depends_on: [postgres]
```

For teams that prefer managed, PactFlow (https://pactflow.io) provides the same broker with additional features (webhooks, secret scanning, analytics). The wire protocol is identical.

#### Pact for message queues (async contracts)

Pact also supports async messages (Kafka, SQS, RabbitMQ). The consumer defines the expected message shape; the provider verifies it can produce it:

```typescript
// consumer/pact/order-events.pact.test.ts
import { MessageConsumerPact, MatchersV3 } from '@pact-foundation/pact';

const messagePact = new MessageConsumerPact({
  consumer: 'order-service',
  provider: 'payment-service',
  dir: './pacts',
});

describe('OrderCreated event', () => {
  it('produces a valid OrderCreated message', async () => {
    await messagePact
      .given('an order is placed')
      .expectsToReceive('an OrderCreated event')
      .withContent({
        event_type: 'OrderCreated',
        order_id: MatchersV3.uuid(),
        total_cents: MatchersV3.integer(9900),
        created_at: MatchersV3.iso8601DateTimeWithMillis(),
      })
      .withMetadata({ 'contentType': 'application/json', 'kafka_topic': 'orders' })
      .verify(async (message) => {
        // handler under test — must be able to parse this message
        await handleOrderCreated(JSON.parse(message.contentsAsString()));
        expect(handleOrderCreated).toHaveSucceeded();
      });
  });
});
```

### Schema-based contracts (when Pact is not the answer)

Pact excels when the consumer's usage is a *subset* of the provider's surface and you want to verify only that subset. For other boundaries, schema-based approaches are more economical:

| Scenario | Tool | What it catches |
|----------|------|-----------------|
| REST/HTTP with OpenAPI | `schemathesis`, `openapi-diff`, `optic` | Breaking changes (removed fields, narrowed types, new required params), response conformance. |
| gRPC / protobuf | `buf breaking`, `protodiff` | Field number reuse, type changes, package renames. Gated in CI. |
| JSON Schema / AsyncAPI | `ajv` + snapshot, `asyncapi diff` | Event payload drift between producers and consumers. |
| GraphQL | `graphql-inspector diff` | Removed fields, changed nullability, new required args. |

**OpenAPI response conformance in tests (Python — `schemathesis` + `openapi-core`):**

```python
# tests/test_openapi_conformance.py
import schemathesis
from hypothesis import settings

schema = schemathesis.from_path("openapi.yaml")

@schema.parametrize()
@settings(max_examples=200)
def test_api_conforms_to_openapi(case):
    # Schemathesis generates requests from the OpenAPI spec and checks
    # that responses conform to the declared schemas — a property-based
    # contract test for free.
    response = case.call()
    case.validate_response(response)
```

**Protobuf breaking-change gate (CI):**

```bash
# .github/workflows/proto.yaml
- uses: bufbuild/buf-breaking-action@v1
  with:
    input: proto
    against: 'https://github.com/org/repo.git#branch=main,subdir=proto'
    # Fails if a breaking change is detected (field removal, type change, etc.)
```

**WireMock / Mountebank for provider-driven stubs:**

When the provider is outside your control (third-party API), record its behaviour once and replay it as a stub. WireMock is the standard for HTTP:

```json
// wiremock/mappings/payment-stub.json
{
  "request":  { "method": "POST", "url": "/v1/charges" },
  "response": {
    "status": 201,
    "headers": { "Content-Type": "application/json" },
    "jsonBody": { "charge_id": "ch-test-123", "status": "succeeded" }
  }
}
```

```yaml
# docker-compose.wiremock.yaml
services:
  wiremock:
    image: wiremock/wiremock:3
    ports: ["8080:8080"]
    volumes: ["./wiremock:/home/wiremock"]
    command: ["--global-response-templating", "--enable-stub-cors"]
```

Prefer contract-verified stubs (Pact or OpenAPI-validated) over hand-written ones — a hand-written stub encodes the author's *belief* about the provider, not the provider's *actual* behaviour, and the two diverge silently.

---

## Designing for testability

The cheapest way to test a seam is to make the seam explicit in the design. Testability is not a testing concern — it is an architectural concern. Code that is hard to test is usually hard to reason about, hard to change, and hard to operate.

### Ports and adapters (hexagonal architecture)

The core idea: the domain depends on **ports** (interfaces it owns), and infrastructure implements **adapters** that satisfy those ports. The domain never imports `net/http`, `sql.DB`, or `kafka.Producer` directly — it imports its own interfaces, which are trivial to fake in tests.

```mermaid
flowchart TB
    subgraph Domain["Domain — pure, no I/O imports"]
        Svc["CheckoutService<br/>business rules"]
        PortGW["PaymentGateway<br/>port (interface)"]
        PortRepo["OrderRepository<br/>port (interface)"]
        Svc --> PortGW
        Svc --> PortRepo
    end
    subgraph Adapters["Adapters — I/O, outside the domain"]
        Stripe["StripeGateway<br/>implements PaymentGateway"]
        Postgres["PostgresOrderRepo<br/>implements OrderRepository"]
        FakeGW["FakeGateway<br/>test double"]
        FakeRepo["FakeOrderRepo<br/>test double"]
    end
    Stripe -. implements .-> PortGW
    Postgres -. implements .-> PortRepo
    FakeGW -. implements .-> PortGW
    FakeRepo -. implements .-> PortRepo

    style Domain fill:#e8f5e9
    style Adapters fill:#e3f2fd
```

*Figure 2-3: Ports and adapters. The domain owns the interfaces; adapters (including test doubles) plug into them. Swapping a real adapter for a fake requires no change to the domain.*

**Dependency injection — constructor injection over service locators:**

```go
// main.go — composition root (the only place that knows about concrete adapters)
func main() {
    db := mustConnectPostgres(os.Getenv("DATABASE_URL"))
    gw := stripe.NewGateway(os.Getenv("STRIPE_KEY"))
    repo := postgres.NewOrderRepo(db)
    svc := payments.NewService(gw, repo) // domain wired with real adapters
    http.ListenAndServe(":8080", app.NewHandler(svc))
}

// payments/service_test.go — same domain, fake adapters, no other change
func TestCheckout(t *testing.T) {
    gw := &FakeGateway{}
    repo := &FakeOrderRepo{}
    svc := payments.NewService(gw, repo) // same constructor, different adapters
    // ...
}
```

In Go, `wire` or `fx` can manage larger graphs; in Python, plain constructors or `dependency-injector`; in JVM, Dagger/Spring. The mechanism matters less than the principle: **no global singletons, no hidden constructors, no package-level `init` that dials a database.**

### The four seams that must be explicit

| Seam | Anti-pattern | Testable alternative |
|------|-------------|---------------------|
| **Time** | `time.Now()` scattered through domain logic | Inject a `Clock` interface; production uses `SystemClock`, tests use `FixedClock` or ` advancing Clock`. Enables deterministic expiry, scheduling, and window tests. |
| **Randomness / IDs** | `uuid.New()` / `rand.Intn` inline | Inject an `IDGenerator` / `RNG` interface. Tests use a seeded or sequential generator and assert on known IDs. |
| **I/O (network, FS, DB)** | Direct `http.Get`, `os.ReadFile`, `sql.Query` in domain | Behind a port interface. The domain never sees raw I/O — only typed methods on ports it owns. |
| **Configuration** | `os.Getenv` read at arbitrary call sites | Read once at startup into a typed `Config` struct; pass the struct (or the fields) to constructors. Tests construct `Config` literals. |

```go
// ports/clock.go — the Clock seam
type Clock interface {
    Now() time.Time
}
type SystemClock struct{}
func (SystemClock) Now() time.Time { return time.Now() }

type FixedClock struct{ T time.Time }
func (c FixedClock) Now() time.Time { return c.T }

// Domain uses the seam — not time.Now()
func (s *Service) IsExpired(ctx context.Context, orderID string) (bool, error) {
    o, err := s.repo.Find(ctx, orderID)
    if err != nil {
        return false, err
    }
    return s.clock.Now().After(o.ExpiresAt), nil
}

// Test is deterministic — no sleep, no flake
func TestIsExpired(t *testing.T) {
    clk := FixedClock{T: time.Date(2026, 8, 20, 12, 0, 0, 0, time.UTC)}
    svc := NewServiceWithClock(&FakeOrderRepo{...}, clk)
    expired, _ := svc.IsExpired(context.Background(), "ord-1")
    assert.True(t, expired)
}
```

### Testability checklist for backend services

- [ ] **Constructors take interfaces, not concretes** — and the interfaces are owned by the consumer (domain), not the infrastructure package.
- [ ] **No package-level mutable state** — no global DB handle, no `var defaultClient = http.DefaultClient` mutated at init.
- [ ] **Time, randomness, and IDs are injected** — or at minimum wrapped in an interface that tests can replace without build tags or monkey-patching.
- [ ] **Side effects are observable** — a method that sends an email returns an error or emits an event that tests can assert on; it does not fire-and-forget into a global queue.
- [ ] **Adapters are thin** — mapping and I/O only, no business logic. If an adapter contains an `if`, that `if` probably belongs in the domain where it can be unit-tested.
- [ ] **Seams are narrow** — a port with 2–4 methods is easy to fake; a port with 20 methods is a leaky abstraction that will be mocked badly. Split broad ports.
- [ ] **Errors are typed** — `ErrNotFound`, `ErrConflict`, `ErrUpstreamTimeout` as sentinel or structured errors, not stringly-typed messages that tests must substring-match.

---

## Composing the portfolio

Chapter 1 gave you the pyramid; this chapter gives you the rules for filling it at the seams:

```mermaid
flowchart LR
    Q1{"Do you control<br/>both sides?"}
    Q1 -->|Yes| Q2{"Can you run<br/>the dependency<br/>as a container?"}
    Q1 -->|No| Q3{"Is the provider<br/>contract formal<br/>(OpenAPI/proto)?"}
    Q2 -->|Yes| Real["Real integration test<br/>Testcontainers<br/>highest fidelity"]
    Q2 -->|No| Fake["Fake<br/>in-memory impl<br/>domain-owned port"]
    Q3 -->|Yes| Schema["Schema contract test<br/>openapi-diff / buf breaking<br/>+ response conformance"]
    Q3 -->|No| Pact["Consumer-driven Pact<br/>consumer + provider<br/>+ Broker gate"]
    Real --> Gate["CI: can-i-deploy / breaking-change gate"]
    Fake --> Gate
    Schema --> Gate
    Pact --> Gate

    style Real fill:#e8f5e9
    style Fake fill:#e3f2fd
    style Pact fill:#f3e5f5
    style Schema fill:#fff3e0
```

*Figure 2-4: Choosing the right seam test. When you control both sides and can run the dependency, a real integration test is the strongest signal. Otherwise, the choice between Pact and schema testing follows who owns the contract.*

A mature suite uses all four, each where it is strongest:

- **Real integration tests** for your own data stores and queues (where Testcontainers gives you the actual engine).
- **Fakes** for domain-owned collaborators that need to be fast and deterministic (repositories, gateways behind ports).
- **Pact** for service-to-service HTTP and message contracts where consumer usage is a subset of provider surface.
- **Schema tests** for published APIs, protobuf surfaces, and third-party boundaries where the schema is the contract.

None of these replaces E2E — E2E still owns the question "does the assembled, configured, deployed system do what the user asked?" But with seams tested at the right layer, E2E can stay small, focused, and fast.

---

## Key takeaways

- There are five test doubles — dummy, stub, spy, mock, fake — and they are not interchangeable. Prefer real collaborators where possible, fakes where the dependency is volatile but fakeable, and mocks only when the interaction protocol itself is the requirement.
- Mock-heavy suites couple to implementation and hide behaviour. Default to fakes and classical assertions on observable outcomes; reach for mocks narrowly and deliberately.
- Consumer-driven contract testing with Pact decouples consumer and provider verification via a shared pact file and a broker. The `can-i-deploy` gate is the deployment-time enforcement that makes the whole system trustworthy.
- Async (message) contracts need the same discipline as HTTP contracts — use Pact's message support or schema-based validation for event payloads.
- Where Pact is not the right fit (public APIs, protobuf surfaces, third-party providers), schema-based testing — OpenAPI diff + response conformance, `buf breaking`, `graphql-inspector` — provides a lighter-weight contract check.
- Testability is architecture: ports and adapters, constructor injection, and explicit seams for time, randomness, I/O, and configuration. Code that is hard to test is usually hard to change — fix the design, not the test.
- Compose seam tests by ownership and feasibility: real integration where you can run the dependency, fakes where you own the port, Pact where consumer usage drives the contract, schema tests where the spec is the contract.

## Further reading

- Gerard Meszaros — *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007) — the definitive taxonomy of test doubles, fixtures, and patterns.
- Martin Fowler — "Mocks Aren't Stubs" (2007) — https://martinfowler.com/articles/mocksArentStubs.html — mockist vs. classical styles.
- Martin Fowler — "Test Double" (2018) — https://martinfowler.com/bliki/TestDouble.html
- Pact documentation — https://docs.pact.io/ — consumer/provider guides, matching rules, broker operation, and `can-i-deploy`.
- PactFlow — https://pactflow.io/ — managed broker and additional contract-testing workflow.
- *Ports and Adapters* (Alistair Cockburn, 2005) — https://alistair.cockburn.us/hexagonal-architecture/ — the original hexagonal architecture paper.
- Vladimir Khorikov — *Unit Testing: Principles, Practices, and Patterns* (Manning, 2020) — when to mock, when to fake, and how to avoid test-induced damage.
- Schemathesis — https://schemathesis.readthedocs.io/ — property-based OpenAPI testing.
- Buf — https://buf.build/docs/breaking/overview/ — protobuf breaking-change detection.
- WireMock — https://wiremock.org/docs/ — HTTP stubbing and response templating.

---

*Next: Chapter 3 — Load, Performance, and Chaos Testing — where the focus shifts from correctness to behaviour under pressure: how the system performs when traffic is heavy, resources are constrained, and failures are injected deliberately.*

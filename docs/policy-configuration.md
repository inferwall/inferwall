# Policy Configuration

## Policy Profiles

Policy profiles control which signatures are active, how they score, and what actions to take.

### Default Policy (`default.yaml`)

```yaml
name: default
version: "2.0.0"
mode: enforce
thresholds:
  inbound_flag: 4.0
  inbound_block: 10.0
  outbound_flag: 3.0
  outbound_block: 7.0
  early_exit: 13.0
signatures: {}
```

> **Scoring v2**: Each match score = `confidence (0.0-1.0) x severity (1-15)`. The effective
> score uses max-primary + diminishing corroboration, not simple summation. See QUICKSTART.md
> for the full scoring flow.

### Enforcement Modes

| Mode | Behavior |
|------|----------|
| `monitor` | All signatures run and log matches, but no blocking |
| `enforce` | Signatures contribute to scoring and threshold actions |

### Per-Signature Overrides

Override individual signatures within a policy:

```yaml
signatures:
  INJ-D-001:
    action: monitor        # Override to monitor even in enforce mode
    anomaly_points: 3      # Override scoring points
  INJ-D-008:
    action: enforce        # Force enforce even in monitor mode
```

### Override Precedence

1. Per-signature override (highest priority)
2. Global policy mode
3. Signature default action (lowest priority)

## Thresholds

| Threshold | Description | Default | Strict |
|-----------|-------------|---------|--------|
| `inbound_flag` | Score to flag incoming requests | 4.0 | 2.5 |
| `inbound_block` | Score to block incoming requests | 10.0 | 7.0 |
| `outbound_flag` | Score to flag outgoing responses | 3.0 | 2.0 |
| `outbound_block` | Score to block outgoing responses | 7.0 | 5.0 |
| `early_exit` | Score to skip downstream engines | 13.0 | 10.0 |

## Deployment Workflow

1. Deploy with `mode: monitor`
2. Observe logged matches for 1-2 weeks
3. Configure allowlists for false positives
4. Flip high-confidence signatures to enforce individually
5. Switch global mode to enforce

## Custom Policies

The pipeline auto-discovers policy files from `~/.inferwall/policies/`. To create a custom policy:

### 1. Copy the default policy

```bash
mkdir -p ~/.inferwall/policies
cp $(python -c "import inferwall; print(inferwall.__path__[0])")/policies/default.yaml \
   ~/.inferwall/policies/my-policy.yaml
```

### 2. Modify thresholds, overrides, or mode

Edit `~/.inferwall/policies/my-policy.yaml`:

```yaml
name: my-policy
version: "1.0.0"
mode: monitor                   # Start in monitor mode

thresholds:
  inbound_flag: 6.0             # Raise flag threshold to reduce noise
  inbound_block: 12.0           # Raise block threshold
  outbound_flag: 4.0
  outbound_block: 8.0
  early_exit: 15.0

signatures:
  INJ-D-001:
    action: enforce             # Force-enforce this signature even in monitor mode
    anomaly_points: 12          # Increase weight
  CS-T-003:
    action: monitor             # Demote to monitor-only
```

### 3. Use IW_POLICY_PATH

To explicitly select a policy file (instead of relying on auto-discovery), set the `IW_POLICY_PATH` environment variable:

```bash
export IW_POLICY_PATH=~/.inferwall/policies/my-policy.yaml
```

This is useful in CI/CD pipelines or container deployments where you want deterministic policy selection.

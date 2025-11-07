# Test Scripts

This directory contains scripts to test Semgrep with different rule configurations.

## Available Scripts

### 1. `test-local-scan-custom.sh` 
**Tests CUSTOM RULES ONLY**

```bash
bash scripts/test-local-scan-custom.sh
```

- Uses rules from `custom-rules/` directory
- Tests your team-specific security and code quality rules
- Results: `tests/results-custom-*.json`

**Use when:** You want to validate your custom rules are working correctly.

---

### 2. `test-local-scan-native.sh`
**Tests NATIVE SEMGREP RULES ONLY**

```bash
bash scripts/test-local-scan-native.sh
```

- Uses Semgrep's `p/security-audit` ruleset
- Includes 1000+ built-in security rules from Semgrep registry
- Results: `tests/results-native-*.json`

**Use when:** You want to see what Semgrep's default rules catch.

---

### 3. `test-local-scan-all.sh`
**Tests BOTH CUSTOM + NATIVE RULES**

```bash
bash scripts/test-local-scan-all.sh
```

- Combines your custom rules with Semgrep's security-audit ruleset
- Maximum coverage - catches everything
- Results: `tests/results-all-*.json`

**Use when:** You want comprehensive scanning with all available rules.

---

### 4. `test-local-scan.sh` (Original)
**Legacy script - being phased out**

The original test script. Recommend using one of the specific scripts above instead.

---

## Quick Comparison

| Script | Custom Rules | Native Rules | Use Case |
|--------|-------------|--------------|----------|
| `test-local-scan-custom.sh` | ✅ | ❌ | Validate custom rules |
| `test-local-scan-native.sh` | ❌ | ✅ | See Semgrep defaults |
| `test-local-scan-all.sh` | ✅ | ✅ | Maximum coverage |

---

## Making Scripts Executable

If you get permission errors, run:

```bash
chmod +x scripts/test-local-scan-custom.sh
chmod +x scripts/test-local-scan-native.sh
chmod +x scripts/test-local-scan-all.sh
```

---

## Expected Results

### Custom Rules (~17 findings)
- Your custom security rules (eval, hardcoded secrets, XSS, etc.)
- Your code quality rules (console.log, TODOs, magic numbers, etc.)

### Native Rules (~20-50 findings)
- Semgrep's built-in security rules
- More comprehensive coverage
- May include some overlaps with custom rules

### All Rules (~30-60 findings)
- Combined coverage from both sets
- Some rules may trigger on the same issues (duplicates)
- Most comprehensive testing

---

## Test Files

Scripts scan these sample files:
- `tests/sample-code/vulnerable.js` - Intentionally vulnerable JavaScript
- `tests/sample-code/vulnerable.py` - Intentionally vulnerable Python

---

## Output Files

Results are saved in JSON format:
- `tests/results-custom-*.json` - Custom rule results
- `tests/results-native-*.json` - Native rule results  
- `tests/results-all-*.json` - Combined results

**Note:** These files are gitignored and not committed to the repository.


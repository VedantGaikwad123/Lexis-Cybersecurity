/**
 * Secret Pattern Test Suite
 * Verifies that the security secret scanner correctly flags synthetic test secrets
 * and ignores non-secret strings.
 */

const SECRET_PATTERNS = [
  { name: 'OpenAI API Key', pattern: /sk-[a-zA-Z0-9]{20,}/ },
  { name: 'AWS Access Key ID', pattern: /AKIA[0-9A-Z]{16}/ },
  { name: 'GitHub Access Token', pattern: /(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{60,})/ },
  { name: 'Google API Key', pattern: /AIzaSy[a-zA-Z0-9_-]{33}/ },
  { name: 'Private Key Header', pattern: /-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----/ }
];

const TEST_CASES = [
  { input: 'const key = "sk-1234567890abcdefghijklmnopqrstuvwxyz";', expectedMatch: 'OpenAI API Key' },
  { input: 'const awsKey = "AKIAIOSFODNN7EXAMPLE";', expectedMatch: 'AWS Access Key ID' },
  { input: 'const ghToken = "ghp_1234567890abcdefghijklmnopqrstuvwxyz12";', expectedMatch: 'GitHub Access Token' },
  { input: 'const gKey = "AIzaSyA1234567890abcdefghijklmnopqrstuv";', expectedMatch: 'Google API Key' },
  { input: '-----BEGIN RSA PRIVATE KEY-----', expectedMatch: 'Private Key Header' },
  { input: 'const title = "LEXIS Platform Security Blueprint";', expectedMatch: null }
];

function runTests() {
  console.log('=====================================================');
  echo = console.log;
  echo('[LEXIS Security] Running Secret Scanner Verification Tests...');
  console.log('=====================================================');

  let passed = 0;
  let failed = 0;

  TEST_CASES.forEach((test, idx) => {
    let matchedPatternName = null;

    for (const p of SECRET_PATTERNS) {
      if (p.pattern.test(test.input)) {
        matchedPatternName = p.name;
        break;
      }
    }

    if (matchedPatternName === test.expectedMatch) {
      console.log(`[PASS] Test #${idx + 1}: ${test.expectedMatch ? `Correctly detected ${matchedPatternName}` : 'Clean content passed'}`);
      passed++;
    } else {
      console.error(`[FAIL] Test #${idx + 1}: Expected '${test.expectedMatch}' but got '${matchedPatternName}' for input: "${test.input}"`);
      failed++;
    }
  });

  console.log('-----------------------------------------------------');
  console.log(`[SUMMARY] Total: ${TEST_CASES.length} | Passed: ${passed} | Failed: ${failed}`);

  if (failed > 0) {
    process.exit(1);
  } else {
    console.log('[SECURITY VERIFIED] All secret scanner patterns are operating as expected.');
  }
}

runTests();

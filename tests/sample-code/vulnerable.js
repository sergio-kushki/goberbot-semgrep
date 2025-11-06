// Sample vulnerable code for testing Semgrep rules

// SHOULD TRIGGER: dangerous-eval-usage
function unsafeEval(userInput) {
  const result = eval(userInput);
  return result;
}

// SHOULD TRIGGER: hardcoded-password
const config = {
  username: "admin",
  password: "SuperSecret123!",
  apiKey: "sk_test_FakeKey1234567890abcdefghijklmnopqrstuvwxyz" // Fake test key for demonstration
};

// SHOULD TRIGGER: unsafe-innerhtml
function updateContent(userContent) {
  document.getElementById('content').innerHTML = userContent;
}

// SHOULD TRIGGER: insecure-random
function generateToken() {
  return Math.random().toString(36).substring(7);
}

// SHOULD TRIGGER: no-console-log
function debugUser(user) {
  console.log("User data:", user);
  console.debug("Debug info:", user.id);
  return user;
}

// SHOULD TRIGGER: empty-catch-block
async function fetchData() {
  try {
    const response = await fetch('/api/data');
    return await response.json();
  } catch (error) {
    // Empty catch - should be flagged
  }
}

// SHOULD TRIGGER: todo-comment
function calculateTotal(items) {
  // TODO: Add tax calculation
  // FIXME: This doesn't handle discounts properly
  return items.reduce((sum, item) => sum + item.price, 0);
}

// SHOULD TRIGGER: weak-crypto-md5
const crypto = require('crypto');
function hashPassword(password) {
  return crypto.createHash('md5').update(password).digest('hex');
}

// SHOULD TRIGGER: magic-numbers
function processPayment(amount) {
  if (amount > 10000) {
    throw new Error('Amount too large');
  }
  return amount * 1.0825; // Tax rate hardcoded
}

module.exports = {
  unsafeEval,
  config,
  updateContent,
  generateToken,
  debugUser,
  fetchData,
  calculateTotal,
  hashPassword,
  processPayment
};


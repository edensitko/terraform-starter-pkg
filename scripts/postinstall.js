#!/usr/bin/env node

/**
 * postinstall — creates a Python venv and installs tf-starter dependencies.
 *
 * Runs automatically after `npm install`.
 * Can also be triggered manually: `node scripts/postinstall.js`
 */

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const PKG_ROOT = path.resolve(__dirname, "..");
const VENV_DIR = path.join(PKG_ROOT, ".venv");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function findPython() {
  const candidates = process.platform === "win32"
    ? ["python", "python3"]
    : ["python3", "python"];

  for (const cmd of candidates) {
    try {
      const version = execSync(`${cmd} --version`, { encoding: "utf-8" }).trim();
      // Ensure it's Python 3.9+
      const match = version.match(/Python (\d+)\.(\d+)/);
      if (match) {
        const major = parseInt(match[1], 10);
        const minor = parseInt(match[2], 10);
        if (major >= 3 && minor >= 9) {
          return cmd;
        }
      }
    } catch {
      // not found
    }
  }
  return null;
}

function run(cmd, opts = {}) {
  console.log(`  $ ${cmd}`);
  execSync(cmd, { stdio: "inherit", cwd: PKG_ROOT, ...opts });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  console.log("\n  tf-starter postinstall — setting up Python environment\n");

  // 1. Find Python
  const python = findPython();
  if (!python) {
    console.warn(
      "  ⚠  Python 3.9+ not found. tf-starter requires Python.\n" +
      "     Install Python from https://www.python.org/downloads/\n" +
      "     Then run: npm run postinstall\n"
    );
    // Don't fail the npm install — user may install Python later
    return;
  }

  const version = execSync(`${python} --version`, { encoding: "utf-8" }).trim();
  console.log(`  ✔  Found ${version}\n`);

  // 2. Create venv if it doesn't exist
  if (!fs.existsSync(VENV_DIR)) {
    console.log("  Creating Python virtual environment...");
    run(`${python} -m venv "${VENV_DIR}"`);
    console.log("  ✔  Virtual environment created\n");
  } else {
    console.log("  ✔  Virtual environment already exists\n");
  }

  // 3. Determine pip path
  const isWin = process.platform === "win32";
  const pip = isWin
    ? path.join(VENV_DIR, "Scripts", "pip.exe")
    : path.join(VENV_DIR, "bin", "pip3");

  // 4. Upgrade pip
  console.log("  Upgrading pip...");
  run(`"${pip}" install --upgrade pip --quiet`);

  // 5. Install the package in editable mode
  console.log("\n  Installing tf-starter and dependencies...");
  run(`"${pip}" install -e "${PKG_ROOT}" --quiet`);

  console.log("\n  ✔  tf-starter installed successfully!");
  console.log("  Usage: tf-starter --provider aws --project-name myapp\n");
}

try {
  main();
} catch (err) {
  console.error(`\n  ⚠  postinstall failed: ${err.message}`);
  console.error("     You can retry with: npm run postinstall\n");
  // Don't fail npm install
}

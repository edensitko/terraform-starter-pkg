#!/usr/bin/env node

/**
 * tf-starter — Enterprise Terraform IaC Project Generator
 *
 * Thin Node.js wrapper that delegates to the Python CLI.
 * The Python venv is created automatically during `npm install` (postinstall).
 */

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const PKG_ROOT = path.resolve(__dirname, "..");
const VENV_DIR = path.join(PKG_ROOT, ".venv");

// Resolve the Python binary inside the managed venv
function getVenvPython() {
  const isWin = process.platform === "win32";
  const bin = isWin
    ? path.join(VENV_DIR, "Scripts", "python.exe")
    : path.join(VENV_DIR, "bin", "python3");
  return fs.existsSync(bin) ? bin : null;
}

// Fallback: try system python
function getSystemPython() {
  const candidates = process.platform === "win32"
    ? ["python", "python3"]
    : ["python3", "python"];

  for (const cmd of candidates) {
    try {
      require("child_process").execSync(`${cmd} --version`, { stdio: "ignore" });
      return cmd;
    } catch {
      // not found, try next
    }
  }
  return null;
}

function main() {
  let pythonBin = getVenvPython();

  if (!pythonBin) {
    // Venv not set up — try system python with the module directly
    pythonBin = getSystemPython();
    if (!pythonBin) {
      console.error(
        "Error: Python 3.9+ is required but was not found.\n" +
        "Install Python from https://www.python.org/downloads/ and try again.\n" +
        "Or run: npm run postinstall"
      );
      process.exit(1);
    }

    console.error(
      "Warning: tf-starter venv not found. Run `npm run postinstall` to set it up.\n" +
      `Falling back to system Python: ${pythonBin}\n`
    );
  }

  // Forward all CLI arguments to the Python entry point
  const args = ["-m", "tf_starter.cli", ...process.argv.slice(2)];

  const child = spawn(pythonBin, args, {
    cwd: PKG_ROOT,
    stdio: "inherit",
    env: {
      ...process.env,
      PYTHONPATH: PKG_ROOT,
      // Ensure the venv's site-packages are on the path
      VIRTUAL_ENV: VENV_DIR,
    },
  });

  child.on("error", (err) => {
    console.error(`Failed to start Python process: ${err.message}`);
    process.exit(1);
  });

  child.on("close", (code) => {
    process.exit(code ?? 0);
  });
}

main();

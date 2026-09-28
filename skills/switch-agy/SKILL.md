---
name: switch-agy
description: >-
  Interactive profile & account switcher for Google Antigravity (AGY) CLI.
  Use when the user types /switch-agy, asks to switch Google accounts, change agy profile,
  swap active account between Profil 1 and Profil 2, or check which account is currently active.
  Presents an interactive modal/choice to pick an account and switches Windows Credential Manager seamlessly.
---

# Switch AGY Account & Profile Manager

This skill allows seamless, instant switching between multiple Google accounts in Antigravity CLI without requiring manual re-authentication every time. It coordinates Windows Credential Manager (`gemini:antigravity`) with Antigravity profile directories.

## How to Handle `/switch-agy` or Account Switch Requests:

When the user triggers `/switch-agy` or asks to switch/change accounts:

1. **Check Current Status**:
   Execute the status command to inspect active account and saved profiles:
   ```powershell
   python "$env:LOCALAPPDATA\agy\bin\switch-agy-core.py" status
   ```

2. **Present Interactive Choice (via `ask_question`)**:
   Just like the `/model` selector in the AGY terminal, present the user with an interactive choice:
   - Identify which account is currently active.
   - If Account 1 is active, list Account 2 as `(Recommended)`.
   - If Account 2 is active, list Account 1 as `(Recommended)`.
   - Example options:
     - `(Recommended) Beralih ke Akun 1 (pyxvin124@gmail.com)`
     - `Beralih ke Akun 2 (py.purnomoygt@gmail.com)`
     - `Cek Status Akun Aktif`
     - `Setup Akun Baru`

3. **Execute Switch Based on User Selection**:
   - If user chooses Akun 1:
     ```powershell
     python "$env:LOCALAPPDATA\agy\bin\switch-agy-core.py" 1
     ```
   - If user chooses Akun 2:
     ```powershell
     python "$env:LOCALAPPDATA\agy\bin\switch-agy-core.py" 2
     ```
   - If user chooses Setup:
     ```powershell
     python "$env:LOCALAPPDATA\agy\bin\switch-agy-core.py" setup 2
     ```

4. **Verify & Confirm**:
   Output the result showing the newly active account and prompt them to continue with `agy -c`.

## CLI Usage (Outside Chat):
- `switch-agy` : Auto-toggle between Account 1 & Account 2
- `switch-agy 1` : Switch directly to Account 1
- `switch-agy 2` : Switch directly to Account 2
- `switch-agy status` : Check active account and profile status
- `switch-agy save <1|2>` : Save current active account to slot 1 or 2
- `switch-agy setup <1|2>` : Prepare environment for logging in a new account

# 🎨 Visual Studio Code Setup Guide

Complete guide for developing the Bingo Bot in Visual Studio Code with optimal configuration.

## Table of Contents
- [Quick Start](#quick-start)
- [What's Included](#whats-included)
- [Opening the Project](#opening-the-project)
- [Recommended Extensions](#recommended-extensions)
- [Debugging](#debugging)
- [Running Tasks](#running-tasks)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Tips and Tricks](#tips-and-tricks)

---

## Quick Start

### 1. Open Project in VS Code

```bash
code /path/to/bingo-bot-free
```

Or: **File → Open Folder** → Select `bingo-bot-free` directory

### 2. Install Recommended Extensions

VS Code will prompt you to install recommended extensions. Click **"Install All"**.

Or manually: Press `Ctrl+Shift+X` (Cmd+Shift+X on Mac) and search for:
- Python
- Pylance
- GitLens

### 3. Set Up Environment

Press `Ctrl+Shift+P` (Cmd+Shift+P on Mac) and run:
```
Tasks: Run Task → Full Setup (First Time)
```

This will:
- Create virtual environment
- Install dependencies
- Copy .env.example to .env

### 4. Configure Environment Variables

Edit `.env` file with your credentials:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
```

### 5. Start Debugging

Press `F5` or go to **Run and Debug** (Ctrl+Shift+D) and click **"Start Debugging"**

---

## What's Included

### Configuration Files

All configuration is stored in the `.vscode/` directory:

```
.vscode/
├── settings.json      # Editor and Python settings
├── launch.json        # Debug configurations
├── tasks.json         # Automated tasks
└── extensions.json    # Recommended extensions
```

### Features Configured

✅ **Python Development**
- Virtual environment detection
- Auto-imports
- IntelliSense with Pylance
- Type checking

✅ **Code Quality**
- Flake8 linting (on save)
- Autopep8 formatting
- Line length at 80/120 characters

✅ **Testing**
- Test discovery
- Run tests in UI
- Debug individual tests

✅ **Debugging**
- Breakpoints
- Variable inspection
- Step through code
- Multiple debug configs

✅ **Tasks**
- One-click bot start
- Run all tests
- Install dependencies
- Clear database

---

## Opening the Project

### Method 1: Command Line
```bash
cd bingo-bot-free
code .
```

### Method 2: VS Code UI
1. Open VS Code
2. **File → Open Folder**
3. Select `bingo-bot-free` directory
4. Click **"Select Folder"**

### Method 3: Recent Projects
1. Open VS Code
2. **File → Open Recent**
3. Select `bingo-bot-free`

---

## Recommended Extensions

When you open the project, VS Code will suggest installing these extensions:

### Essential (Auto-suggested)

**Python Development:**
- **Python** (ms-python.python) - Core Python support
- **Pylance** (ms-python.vscode-pylance) - Fast IntelliSense

**Code Quality:**
- **Flake8** (ms-python.flake8) - Python linter
- **autopep8** (ms-python.autopep8) - Code formatter

**Git:**
- **GitLens** (eamodio.gitlens) - Enhanced Git integration
- **Git Graph** (mhutchie.git-graph) - Visualize git history

**Documentation:**
- **Markdown All in One** (yzhang.markdown-all-in-one)
- **markdownlint** (DavidAnson.vscode-markdownlint)

**Utilities:**
- **DotENV** (mikestead.dotenv) - .env file syntax
- **SQLite** (alexcvzz.vscode-sqlite) - View game.db
- **Error Lens** (usernamehw.errorlens) - Inline errors
- **Code Spell Checker** (streetsidesoftware.code-spell-checker)

### Installing Extensions

**Automatic:**
1. VS Code will show a popup: "This workspace has extension recommendations"
2. Click **"Install All"**

**Manual:**
1. Press `Ctrl+Shift+X` (Cmd+Shift+X on Mac)
2. Search for extension name
3. Click **"Install"**

---

## Debugging

### Debug Configurations

Press `F5` or click **Run and Debug** icon. Available configurations:

#### 1. Python: Bot (Current File)
**Default configuration** - Uses environment variables from your system or .env file

**Usage:**
1. Press `F5`
2. Bot starts with debugger attached
3. Set breakpoints by clicking left of line numbers

#### 2. Python: Bot with .env
Explicitly loads `.env` file for credentials

**Usage:**
1. Create/edit `.env` file
2. Select this configuration in debug dropdown
3. Press `F5`

#### 3. Python: Current Test File
Debug the currently open test file

**Usage:**
1. Open `test_bingo.py` (or any test file)
2. Select this configuration
3. Press `F5`

#### 4. Python: All Tests
Run all tests with debugger

#### 5. Python: Bot (Manual Env)
Hardcode credentials in launch.json (for quick testing)

### Setting Breakpoints

1. Click in the left margin (gutter) next to line number
2. Red dot appears = breakpoint set
3. Run debugger (F5)
4. Code pauses at breakpoint

### Debug Actions

When paused at breakpoint:

- **Continue** (F5) - Resume execution
- **Step Over** (F10) - Execute current line
- **Step Into** (F11) - Enter function
- **Step Out** (Shift+F11) - Exit function
- **Restart** (Ctrl+Shift+F5) - Restart debugging
- **Stop** (Shift+F5) - Stop debugging

### Inspect Variables

When debugging:
- **Variables panel** - View all variables in scope
- **Watch panel** - Monitor specific expressions
- **Call Stack** - See execution path
- **Debug Console** - Execute Python expressions

---

## Running Tasks

Tasks automate common operations. Access via:
- `Ctrl+Shift+P` → "Tasks: Run Task"
- **Terminal → Run Task**

### Available Tasks

#### Start Bot
Run the bot in terminal (default build task)
- Shortcut: `Ctrl+Shift+B`

#### Run All Tests
Execute all test files with verbose output
- Shortcut: `Ctrl+Shift+T` (if configured)

#### Run Individual Tests
- Run Test: Bingo
- Run Test: Inline Menu
- Run Test: Player Data

#### Install Dependencies
Runs `pip install -r requirements.txt`

#### Create Virtual Environment
Creates `venv` folder with virtual environment

#### Setup Environment
Copies `.env.example` to `.env`

#### Clear Database
Deletes `game.db` file

#### Check Python Syntax
Validates bot.py syntax

#### Full Setup (First Time)
Runs in sequence:
1. Create virtual environment
2. Install dependencies
3. Setup environment

**Perfect for first-time setup!**

### Running Tasks

**Method 1: Command Palette**
1. `Ctrl+Shift+P`
2. Type "run task"
3. Select "Tasks: Run Task"
4. Choose task from list

**Method 2: Terminal Menu**
1. **Terminal** → **Run Task**
2. Select task

**Method 3: Keyboard Shortcut**
- `Ctrl+Shift+B` - Run default build task (Start Bot)

---

## Testing

### Test Discovery

VS Code automatically discovers tests matching `test*.py` pattern.

**View Tests:**
1. Click **Testing** icon in sidebar (beaker icon)
2. See all discovered tests
3. Click to run individual tests

### Running Tests

**All Tests:**
- Click **Run All Tests** in Testing sidebar
- Or: `Ctrl+Shift+P` → "Test: Run All Tests"
- Or: Use "Run All Tests" task

**Individual Test:**
- Click play button next to test in Testing sidebar
- Or: Open test file and click "Run Test" above function

**Test File:**
- Open test file
- Click "Run Tests" at top of file
- Or: Right-click file in Explorer → "Run Tests"

### Debug Tests

1. Set breakpoint in test code
2. Right-click test in Testing sidebar
3. Select **"Debug Test"**
4. Debugger starts and pauses at breakpoint

---

## Code Quality

### Linting (Flake8)

**Automatic linting** on file save (configured in settings.json)

**View Problems:**
- **Problems panel** (Ctrl+Shift+M)
- Red squiggles in editor
- Error Lens extension shows inline

**Settings:**
- Max line length: 120
- Ignores: E501, W503, E203

**Manual check:**
```bash
flake8 bot.py --max-line-length=120
```

### Formatting (autopep8)

**Not automatic** by default (formatOnSave: false)

**Format document:**
- Right-click in editor → **"Format Document"**
- Or: `Shift+Alt+F`

**Format selection:**
- Select code
- Right-click → **"Format Selection"**

**Auto-format on save:**
Edit `.vscode/settings.json`:
```json
"editor.formatOnSave": true
```

---

## Tips and Tricks

### Keyboard Shortcuts

**Essential:**
- `F5` - Start debugging
- `Ctrl+Shift+B` - Run default task (Start Bot)
- `Ctrl+Shift+P` - Command palette
- `Ctrl+Shift+X` - Extensions
- `Ctrl+Shift+E` - Explorer
- `Ctrl+Shift+D` - Run and Debug
- `Ctrl+Shift+M` - Problems panel
- `Ctrl+`` - Toggle terminal

**Code Navigation:**
- `Ctrl+P` - Quick open file
- `Ctrl+Shift+F` - Search in files
- `F12` - Go to definition
- `Alt+F12` - Peek definition
- `Shift+F12` - Find all references

**Editing:**
- `Ctrl+D` - Select next occurrence
- `Ctrl+Shift+L` - Select all occurrences
- `Alt+Up/Down` - Move line up/down
- `Shift+Alt+Up/Down` - Copy line up/down
- `Ctrl+/` - Toggle comment

### Multi-cursor Editing

- `Alt+Click` - Add cursor
- `Ctrl+Alt+Up/Down` - Add cursor above/below
- `Ctrl+D` - Select next occurrence (adds cursor)

### Integrated Terminal

**Open:**
- `` Ctrl+` `` - Toggle terminal
- `Ctrl+Shift+`` - New terminal

**Multiple terminals:**
- Click `+` to create new
- Dropdown to switch between

**Split terminal:**
- Click split icon in terminal toolbar

### Python Interactive Window

Run Python code interactively:
1. Select code
2. Right-click → **"Run Selection/Line in Python Interactive Window"**
3. Or: `Shift+Enter`

### Workspace Settings

Settings in `.vscode/settings.json` only apply to this project.

**User settings** (global) are separate.

### File Watching

VS Code watches for file changes automatically.

**If issues:**
- `Ctrl+Shift+P` → "Developer: Reload Window"

---

## Troubleshooting

### Python Interpreter Not Found

**Problem:** VS Code can't find Python

**Solution:**
1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choose:
   - `./venv/bin/python` (if venv exists)
   - System Python (e.g., `/usr/bin/python3`)
3. Or install Python from python.org

### Virtual Environment Not Activating

**Problem:** Terminal doesn't activate venv

**Solution:**
1. Close all terminals
2. `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose `./venv/bin/python`
4. Open new terminal (`` Ctrl+` ``)
5. Should see `(venv)` in prompt

### Linting Not Working

**Problem:** No lint errors shown

**Solution:**
1. Install flake8: `pip install flake8`
2. `Ctrl+Shift+P` → "Python: Select Linter"
3. Choose "flake8"
4. Check settings.json: `"python.linting.flake8Enabled": true`

### Tests Not Discovered

**Problem:** Tests don't appear in Testing sidebar

**Solution:**
1. Check test files match `test*.py` pattern
2. `Ctrl+Shift+P` → "Test: Refresh Tests"
3. Check settings.json testing configuration
4. Ensure tests are valid Python

### Debug Configuration Not Working

**Problem:** Can't start debugging

**Solution:**
1. Check `.env` file exists with credentials
2. Verify `BOT_TOKEN` and `ADMIN_ID` are set
3. Try "Python: Bot (Manual Env)" configuration
4. Check launch.json for syntax errors

### Extensions Not Installing

**Problem:** Extension installation fails

**Solution:**
1. Check internet connection
2. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
3. Try manual install: Extensions sidebar → Search → Install
4. Check VS Code is up to date

---

## Advanced Configuration

### Custom Settings

Edit `.vscode/settings.json` to customize:

**Enable format on save:**
```json
"editor.formatOnSave": true
```

**Change linter:**
```json
"python.linting.pylintEnabled": true,
"python.linting.flake8Enabled": false
```

**Type checking:**
```json
"python.analysis.typeCheckingMode": "strict"
```

### Custom Tasks

Add to `.vscode/tasks.json`:

```json
{
    "label": "Your Task Name",
    "type": "shell",
    "command": "your-command",
    "args": ["arg1", "arg2"],
    "problemMatcher": []
}
```

### Custom Debug Configuration

Add to `.vscode/launch.json`:

```json
{
    "name": "Your Config Name",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/your_script.py",
    "console": "integratedTerminal"
}
```

---

## Integration with Git

### Source Control View

**Access:** `Ctrl+Shift+G`

**Features:**
- View changes
- Stage/unstage files
- Commit with message
- Push/pull
- View history (with GitLens)

### Git Graph

With Git Graph extension:
1. Click "Git Graph" in status bar
2. Or: `Ctrl+Shift+P` → "Git Graph: View Git Graph"
3. Visual branch history

### GitLens Features

- Inline blame annotations
- File history
- Compare with previous
- Line history

---

## Resources

**Official Documentation:**
- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [Debugging in VS Code](https://code.visualstudio.com/docs/editor/debugging)
- [Tasks in VS Code](https://code.visualstudio.com/docs/editor/tasks)

**Project Documentation:**
- [README.md](README.md) - Project overview
- [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) - General launch instructions
- [PLAYER_DATA_LOGGING.md](PLAYER_DATA_LOGGING.md) - Data logging features
- [INLINE_MENU_FLOW.md](INLINE_MENU_FLOW.md) - Menu system

**Extensions:**
- [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)

---

## Quick Reference Card

### Must-Know Shortcuts

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Command Palette | Ctrl+Shift+P | Cmd+Shift+P |
| Quick Open | Ctrl+P | Cmd+P |
| Start Debug | F5 | F5 |
| Run Task | Ctrl+Shift+B | Cmd+Shift+B |
| Toggle Terminal | Ctrl+` | Cmd+` |
| Toggle Sidebar | Ctrl+B | Cmd+B |
| Search Files | Ctrl+Shift+F | Cmd+Shift+F |
| Go to Definition | F12 | F12 |
| Format Document | Shift+Alt+F | Shift+Option+F |

### Common Commands

```bash
# Tasks
Ctrl+Shift+P → Tasks: Run Task → [task name]

# Python
Ctrl+Shift+P → Python: Select Interpreter
Ctrl+Shift+P → Python: Run Python File in Terminal

# Testing
Ctrl+Shift+P → Test: Run All Tests
Ctrl+Shift+P → Test: Debug Test

# Git
Ctrl+Shift+P → Git: Commit
Ctrl+Shift+P → Git: Push
```

---

## Success! 🎉

You're now set up for optimal Python development in VS Code!

**Next Steps:**
1. Press `F5` to start debugging the bot
2. Explore the Testing sidebar
3. Try running tasks with `Ctrl+Shift+B`
4. Install recommended extensions
5. Check out GitLens features

**Happy Coding!** 🚀

# 🎨 Visual Studio Code Quick Reference

Visual guide for using VS Code with the Bingo Bot project.

## Opening the Project

### Method 1: From Terminal
```bash
cd /path/to/bingo-bot-free
code .
```

### Method 2: From VS Code
```
File → Open Folder → Select bingo-bot-free
```

---

## First Time Setup (One-Time)

### Step 1: Install Recommended Extensions

When you open the project, VS Code will show a popup:

```
┌────────────────────────────────────────────────────────┐
│ This workspace has extension recommendations           │
│                                                        │
│ [Show Recommendations] [Install All] [Ignore]        │
└────────────────────────────────────────────────────────┘
```

**Click "Install All"** to install all 15 recommended extensions.

### Step 2: Run Full Setup Task

Press `Ctrl+Shift+P` and type:
```
Tasks: Run Task
```

Select: **"Full Setup (First Time)"**

This will:
1. Create virtual environment
2. Install dependencies
3. Create .env file

### Step 3: Configure Environment

Edit `.env` file:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
```

### Step 4: Select Python Interpreter

Press `Ctrl+Shift+P` and type:
```
Python: Select Interpreter
```

Choose: **`./venv/bin/python`**

---

## Daily Workflow

### Starting the Bot

**Method 1: Debug Mode (Recommended)**
```
Press F5
```

**Method 2: Run Without Debugging**
```
Press Ctrl+F5
```

**Method 3: Using Task**
```
Press Ctrl+Shift+B
```

### Setting Breakpoints

```
1. Open bot.py
2. Click in the left margin (gutter) next to line number
3. Red dot appears = breakpoint set
4. Press F5 to start debugging
5. Code pauses at breakpoint
```

### Debugging Controls

When paused at breakpoint:

```
F5          - Continue
F10         - Step Over (next line)
F11         - Step Into (enter function)
Shift+F11   - Step Out (exit function)
Shift+F5    - Stop Debugging
Ctrl+Shift+F5 - Restart Debugging
```

---

## Running Tests

### View All Tests

```
1. Click Testing icon in sidebar (beaker 🧪)
2. See all discovered tests
3. Click refresh button if needed
```

### Run All Tests

**Method 1: Testing Sidebar**
```
Click "Run All Tests" button in Testing sidebar
```

**Method 2: Task**
```
Ctrl+Shift+P → Tasks: Run Task → Run All Tests
```

**Method 3: Command**
```
Ctrl+Shift+P → Test: Run All Tests
```

### Run Individual Test

```
1. Open Testing sidebar
2. Hover over test name
3. Click play button (▶)
```

### Debug a Test

```
1. Open Testing sidebar
2. Right-click test name
3. Select "Debug Test"
4. Set breakpoints in test code
```

---

## Code Quality

### Linting

Automatic linting on save (Flake8 configured).

**View Problems:**
```
Press Ctrl+Shift+M
or
View → Problems
```

**Problems show:**
- ❌ Errors (red)
- ⚠️ Warnings (yellow)
- ℹ️ Info (blue)

### Formatting

**Format Entire File:**
```
Right-click in editor → Format Document
or
Press Shift+Alt+F (Windows/Linux)
Press Shift+Option+F (Mac)
```

**Format Selection:**
```
1. Select code
2. Right-click → Format Selection
```

**Auto-format on Save:**
```
Edit .vscode/settings.json:
"editor.formatOnSave": true
```

---

## File Navigation

### Quick Open File

```
Press Ctrl+P
Type filename
Press Enter
```

Examples:
```
Ctrl+P → bot
Ctrl+P → test_bingo
Ctrl+P → .env
```

### Go to Definition

```
1. Right-click on function/variable
2. Select "Go to Definition"
or
Press F12
```

### Peek Definition

```
1. Right-click on function/variable
2. Select "Peek Definition"
or
Press Alt+F12
```

### Find All References

```
1. Right-click on function/variable
2. Select "Find All References"
or
Press Shift+F12
```

### Search in Files

```
Press Ctrl+Shift+F
Type search term
See results across all files
```

---

## Terminal Usage

### Open Terminal

```
Press Ctrl+` (backtick)
or
View → Terminal
```

### Multiple Terminals

```
1. Click + icon in terminal panel
2. Dropdown to switch between terminals
```

### Split Terminal

```
Click split icon in terminal toolbar
```

### Terminal Shortcuts

```
Ctrl+`          - Toggle terminal
Ctrl+Shift+`    - New terminal
Ctrl+C          - Stop running process
Clear           - Clear terminal
```

---

## Git Integration

### View Changes

```
Press Ctrl+Shift+G
or
Click Source Control icon (branch icon)
```

### Stage Changes

```
1. Open Source Control view (Ctrl+Shift+G)
2. Hover over file
3. Click + icon to stage
```

### Commit

```
1. Stage files
2. Type commit message in text box
3. Press Ctrl+Enter
or
Click ✓ Commit button
```

### Push/Pull

```
Click ... (More Actions) in Source Control view
Select Push or Pull
```

### View Git Graph (with GitLens)

```
Click "Git Graph" in status bar
or
Ctrl+Shift+P → Git Graph: View Git Graph
```

---

## Sidebar Views

### Explorer (Files)
```
Press Ctrl+Shift+E
or
Click top icon in sidebar
```

### Search
```
Press Ctrl+Shift+F
or
Click magnifying glass icon
```

### Source Control (Git)
```
Press Ctrl+Shift+G
or
Click branch icon
```

### Run and Debug
```
Press Ctrl+Shift+D
or
Click play icon with bug
```

### Extensions
```
Press Ctrl+Shift+X
or
Click blocks icon
```

### Testing
```
Click beaker icon (🧪)
```

---

## Useful Commands (Command Palette)

Press `Ctrl+Shift+P` and type:

### Python Commands
```
Python: Select Interpreter
Python: Run Python File in Terminal
Python: Create Terminal
```

### Testing Commands
```
Test: Run All Tests
Test: Debug Test
Test: Refresh Tests
```

### Git Commands
```
Git: Commit
Git: Push
Git: Pull
Git: Sync
Git: View History
```

### Task Commands
```
Tasks: Run Task
Tasks: Run Build Task (Ctrl+Shift+B)
Tasks: Show Running Tasks
Tasks: Terminate Task
```

### View Commands
```
View: Toggle Sidebar Visibility
View: Toggle Panel
View: Toggle Terminal
View: Split Editor
```

---

## Keyboard Shortcuts Cheat Sheet

### Essential
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Command Palette | Ctrl+Shift+P | Cmd+Shift+P |
| Quick Open | Ctrl+P | Cmd+P |
| Toggle Sidebar | Ctrl+B | Cmd+B |
| Toggle Terminal | Ctrl+` | Cmd+` |
| Save | Ctrl+S | Cmd+S |
| Save All | Ctrl+K S | Cmd+K S |

### Debugging
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Start/Continue | F5 | F5 |
| Stop | Shift+F5 | Shift+F5 |
| Restart | Ctrl+Shift+F5 | Cmd+Shift+F5 |
| Step Over | F10 | F10 |
| Step Into | F11 | F11 |
| Step Out | Shift+F11 | Shift+F11 |
| Toggle Breakpoint | F9 | F9 |

### Editing
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Format Document | Shift+Alt+F | Shift+Option+F |
| Go to Definition | F12 | F12 |
| Peek Definition | Alt+F12 | Option+F12 |
| Find References | Shift+F12 | Shift+F12 |
| Rename Symbol | F2 | F2 |
| Toggle Comment | Ctrl+/ | Cmd+/ |
| Duplicate Line | Shift+Alt+Down | Shift+Option+Down |
| Move Line | Alt+Up/Down | Option+Up/Down |
| Delete Line | Ctrl+Shift+K | Cmd+Shift+K |

### Search
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Find | Ctrl+F | Cmd+F |
| Replace | Ctrl+H | Cmd+H |
| Find in Files | Ctrl+Shift+F | Cmd+Shift+F |
| Replace in Files | Ctrl+Shift+H | Cmd+Shift+H |

### Navigation
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Go to Line | Ctrl+G | Cmd+G |
| Go to File | Ctrl+P | Cmd+P |
| Go to Symbol | Ctrl+Shift+O | Cmd+Shift+O |
| Navigate Back | Alt+Left | Ctrl+- |
| Navigate Forward | Alt+Right | Ctrl+Shift+- |

### Terminal
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Toggle Terminal | Ctrl+` | Cmd+` |
| New Terminal | Ctrl+Shift+` | Cmd+Shift+` |
| Kill Terminal | Ctrl+K | Cmd+K |

### Multi-cursor
| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Add Cursor | Alt+Click | Option+Click |
| Add Cursor Above | Ctrl+Alt+Up | Cmd+Option+Up |
| Add Cursor Below | Ctrl+Alt+Down | Cmd+Option+Down |
| Select Next | Ctrl+D | Cmd+D |
| Select All | Ctrl+Shift+L | Cmd+Shift+L |

---

## Pro Tips

### 1. Split Editor

```
Ctrl+\ - Split editor
Ctrl+1/2/3 - Focus editor group
```

Work on bot.py and test file side-by-side!

### 2. Zen Mode

```
Ctrl+K Z - Enter Zen Mode (distraction-free)
Esc Esc - Exit Zen Mode
```

### 3. Minimap

Shows small overview of file on right side.

**Toggle:**
```
View → Show Minimap
```

### 4. Breadcrumbs

Shows file path and symbol at top.

**Toggle:**
```
View → Show Breadcrumbs
```

### 5. Timeline

View file history (Git commits affecting file).

**Access:**
```
Explorer sidebar → Timeline at bottom
```

### 6. Problems Filter

```
Click filter icon in Problems panel
Filter by severity, text, folder
```

### 7. IntelliSense Trigger

```
Press Ctrl+Space
Force IntelliSense suggestions
```

### 8. Parameter Hints

```
Press Ctrl+Shift+Space
Show function parameter hints
```

### 9. Quick Fix

```
Click lightbulb icon
or
Press Ctrl+.
Apply quick fixes
```

### 10. Code Snippets

Start typing and press Tab:
```
def → def function():
class → class ClassName:
if → if condition:
for → for item in items:
```

---

## Common Tasks Quick Reference

### Start Bot
```
F5 or Ctrl+Shift+B
```

### Run Tests
```
Ctrl+Shift+P → Test: Run All Tests
```

### View Problems
```
Ctrl+Shift+M
```

### Format Code
```
Shift+Alt+F
```

### Open Terminal
```
Ctrl+`
```

### Search Files
```
Ctrl+Shift+F
```

### Git View
```
Ctrl+Shift+G
```

### Install Extension
```
Ctrl+Shift+X → Search → Install
```

---

## Troubleshooting Quick Fixes

### Extension Not Working
```
Ctrl+Shift+P → Developer: Reload Window
```

### Python Not Found
```
Ctrl+Shift+P → Python: Select Interpreter
Choose ./venv/bin/python
```

### Tests Not Showing
```
Ctrl+Shift+P → Test: Refresh Tests
```

### Terminal Not Activating venv
```
Close all terminals
Open new terminal (Ctrl+`)
```

### Linting Not Working
```
Install flake8:
Terminal → pip install flake8
Reload window
```

---

## Resources

**Official:**
- [VS Code Docs](https://code.visualstudio.com/docs)
- [Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)
- [Debugging Guide](https://code.visualstudio.com/docs/editor/debugging)

**Project:**
- [VS_CODE_SETUP.md](VS_CODE_SETUP.md) - Detailed guide
- [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md) - Launch instructions
- [README.md](README.md) - Project overview

**Help:**
- Press F1 in VS Code for help
- Hover over settings for descriptions
- Check extension documentation

---

## Success Indicators ✅

You're set up correctly when:

- ✅ Python interpreter shows `./venv/bin/python` in status bar
- ✅ Tests appear in Testing sidebar
- ✅ Linting works (see problems on save)
- ✅ IntelliSense suggests completions
- ✅ F5 starts bot with debugger
- ✅ Breakpoints pause execution
- ✅ Terminal activates venv automatically

**Enjoy coding!** 🚀

# Graphviz Setup Guide

## For Visual Mindmaps

To display interactive visual mindmaps, you need to install the Graphviz software on your system.

### Windows Installation

1. **Download Graphviz:**

   - Go to: https://graphviz.org/download/
   - Download the Windows installer (e.g., `graphviz-2.50.0-win32.exe`)

2. **Install Graphviz:**

   - Run the installer
   - Make sure to check "Add Graphviz to PATH" during installation
   - Or manually add `C:\Program Files\Graphviz\bin` to your system PATH

3. **Verify Installation:**
   ```bash
   dot -V
   ```
   Should show the Graphviz version.

### Alternative: Use Text-based Mindmaps

If you can't install Graphviz, the app will automatically fall back to text-based mindmaps that are still very useful for understanding document structure.

### Troubleshooting

- **"dot not found" error**: Graphviz is not in your PATH
- **Permission errors**: Run as administrator during installation
- **Still not working**: Restart your terminal/IDE after installation

## Current Status

✅ **Python graphviz package**: Installed  
❌ **Graphviz software**: Needs to be installed for visual mindmaps  
✅ **Text fallback**: Available and working

The mindmap feature works with both visual and text-based displays!

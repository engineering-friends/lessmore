# About 

Combine multiple formats into one callable. 

Created to use a single external tool for formatting in IntelliJ IDEA.

# How to use 

Create `config.yaml` and include formatters for different file extensions. 

Run ```python <path_to_combo_formatter_directory> <path1> <path2> ... <pathn>``` to format the file or all files in the directory.

# How to configure external tool in IntelliJ IDEA

## Create an external tool 

Go to: `File` -> `Settings` -> `Tools` -> `External Tools` -> `+`

Name: combo_formatter
Description: combo_formatter
Group: External Tools

### Tool Settings:

Program: poetry
Arguments: run python <path_to_combo_formatter_directory> $FilePath$
Working directory: <path_to_lessmore_utils>

### Advanced Options:
Synchronize files after execution: Checked
Open console for tool output: Unchecked (check it when you want to debug the formatter)
Make console active on message in stdout: Checked
Make console active on message in stderr: Checked
Output filters: Each line is a regex, available macros: $FILE_PATH$, $LINES$, and $COLUMNS$

## Set a shortcut

Go to: `File` -> `Settings` -> `Keymap` -> `External Tools` -> `combo_formatter` -> `Add Keyboard Shortcut`

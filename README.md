# 🐘 PHP Learning Lab: Environment Setup & Basics

A hands-on experiment to master PHP fundamentals, from environment configuration to working with variables, data types, and system information.

## 📋 Overview

This experiment consists of four progressive exercises that will take you from complete beginner to confidently writing PHP scripts. You'll learn how to set up development environments, understand PHP's output mechanisms, work with variables and data types, and even build a professional system information dashboard.

## 🎯 Learning Objectives

By completing these exercises, you'll be able to:
- Set up and verify a PHP development environment (XAMPP)
- Use PHP's built-in development server
- Write PHP scripts using different output methods (`echo`, `var_dump`, `print_r`)
- Work with variables, constants, and all PHP data types
- Access server information using PHP superglobals
- Format dates and times in PHP
- Implement basic loops and arrays

## 📁 Project Structure

```text
Exp_8/
├── Exercise 1/
│   ├── info.php              # (temporary - delete after use!)
│   └── Screenshots...
├── Exercise 2/
│   ├── about.php
│   ├── index.php
│   └── Screenshots...
├── Exercise 3/
│   ├── constants.php         
│   ├── data_types.php        
│   ├── profile.php           
│   └── Screenshots...
└── Exercise 4/
    ├── sysinfo.php           
    └── Screenshots...
```

## 🚀 Exercises

### Exercise 1: Install & Verify Your Environment

Set up a proper PHP development environment using XAMPP.

**Steps:**
1. Download XAMPP from [apachefriends.org](https://www.apachefriends.org/)
2. Install with default settings
3. Start Apache from the XAMPP Control Panel
4. Create an `info.php` file under your project directory with `<?php phpinfo(); ?>`
5. Visit the associated local URL based on your configuration.
6. **Important:** Delete `info.php` immediately after checking!

**Screenshots:**
![XAMPP Setup 1](Exercise%201/Screenshot%202026-04-06%20104702.png)
![XAMPP Setup 2](Exercise%201/Screenshot%202026-04-06%20104906.png)
![PHP Info](Exercise%201/Screenshot%202026-04-06%20105914.png)

> **💡 Troubleshooting:** If Apache won't start on port 80, change to port 8080 in `httpd.conf` and use `http://localhost:8080/`

### Exercise 2: The Built-in PHP Server

Learn to run PHP without Apache using the lightweight built-in server.

**Steps:**
1. Verify PHP is available: `php --version`
2. Open terminal in the development folder.
3. Run the built-in server: `php -S localhost:8000`
4. Test PHP files via `localhost:8000`.
5. Watch terminal logs for request status codes.
6. Stop server with `Ctrl+C`.

**Screenshots:**
![Built-in Server 1](Exercise%202/Screenshot%202026-04-06%20110142.png)
![Built-in Server 2](Exercise%202/Screenshot%202026-04-06%20111338.png)
![Terminal Log](Exercise%202/Screenshot%202026-04-06%20111904.png)

> **💡 Windows PATH Note:** If `php` isn't recognized, add `C:\xampp\php` to your system PATH via Environment Variables.

### Exercise 3: PHP Basics — Output and Variables

Create three scripts demonstrating PHP's output methods and variable handling.

**Files Created:**
- **`profile.php`**: Personal information page
- **`constants.php`**: Constants demonstration
- **`data_types.php`**: Type exploration

**Screenshots:**
![Profile Output](Exercise%203/Screenshot%202026-04-06%20112426.png)
![Constants Output](Exercise%203/Screenshot%202026-04-06%20112638.png)
![Data Types Output](Exercise%203/Screenshot%202026-04-06%20112803.png)

> **💡 Pro Tip:** Always wrap debugging output: `echo '<pre>'; var_dump($var); echo '</pre>';`

### Exercise 4: Challenge — Build a PHP System Info Page

Create a professional-looking system information dashboard that showcases real PHP functionality.

**`sysinfo.php` features:**
- Display: PHP version, OS, max integer, EOL type
- Show today's date and a live clock
- Server info: `$_SERVER['DOCUMENT_ROOT']` and `$_SERVER['SCRIPT_FILENAME']`
- Array of favorite technologies displayed with `foreach` loop

**Screenshot:**
![System Info Dashboard](Exercise%204/Screenshot%202026-04-06%20113122.png)

## 💡 Key PHP Concepts Covered

| Concept | Exercise | Key Functions/Features |
|---------|----------|------------------------|
| Environment setup | 1, 2 | XAMPP, built-in server |
| Output methods | 3 | `echo`, `var_dump`, `print_r` |
| Variables | 3 | `$variable`, type checking |
| Constants | 3 | `define()`, magic constants |
| Data types | 3 | scalar, compound, special types |
| Superglobals | 4 | `$_SERVER` |
| Date/Time | 4 | `date()` function |
| Arrays & loops | 4 | indexed arrays, `foreach` |
| String handling | 3 | quotes, concatenation |

## 📚 What You'll Learn Beyond Code

- **Security habits:** Never leave `phpinfo()` on a production server
- **Debugging techniques:** Using `var_dump()` and `print_r()` effectively
- **Server awareness:** Understanding document roots, script paths, and request lifecycle
- **Environment differences:** XAMPP vs built-in server use cases

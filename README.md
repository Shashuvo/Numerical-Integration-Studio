# 📐 Numerical Integration Studio

**Numerical Integration with Visualization, Analysis & Reporting**

Numerical Integration Studio is a desktop application for approximating definite integrals using multiple numerical integration methods. Built as a **university project** with **AI-assisted development**, the application provides numerical results, function visualization, error analysis, convergence analysis, algorithm comparison, calculation history, and PDF/CSV report generation.

---

## 📖 Overview

Numerical Integration Studio provides an interactive environment for studying and comparing numerical integration techniques.

Users can:

* Enter mathematical functions and integration limits
* Select one or multiple numerical integration methods
* Calculate approximate definite integrals
* Visualize the original function and numerical approximation
* Compare the accuracy and execution time of different methods
* Analyze convergence as the number of intervals increases
* Review previous calculations through calculation history
* Export calculation results as PDF or CSV reports

The project was developed as a **university Numerical Methods project** with the assistance of **AI tools during development**.

---

## ✨ Features

### Numerical Integration

* **Trapezoidal Rule**
* **Simpson's 1/3 Rule**

  * Automatically adjusts the number of intervals to the nearest even value
* **Simpson's 3/8 Rule**

  * Automatically adjusts the number of intervals to the nearest multiple of 3
* **Taylor's Method**

  * Uses a 4th-order Taylor series step method

### 📊 Visualization

* Plot the input mathematical function
* Visualize numerical integration approximations
* Compare numerical results graphically
* Matplotlib-powered plotting

### 📈 Analysis

* Absolute and relative error analysis
* Execution time comparison
* Convergence analysis
* Error vs. number of intervals
* Execution time vs. number of intervals
* Side-by-side algorithm comparison
* Most accurate method highlighting

### 🗂️ Calculation History

* Automatically stores previous calculations
* Browse historical calculations
* Reopen previous calculations
* Delete calculation history

### 📄 Reports

* Export calculation results as **PDF**
* Export results as **CSV**
* Generate reports containing numerical results and analysis

### 🖥️ Desktop Interface

* Built with **PySide6**
* Tab-based result, plot, and comparison views
* Interactive calculation workflow
* User-friendly desktop interface

---

## 🛠️ Tech Stack

| Layer                | Technology   |
| -------------------- | ------------ |
| Language             | Python 3.12+ |
| GUI Framework        | PySide6      |
| Numerical Computing  | NumPy, SciPy |
| Symbolic Mathematics | SymPy        |
| Visualization        | Matplotlib   |
| PDF Reports          | ReportLab    |
| Configuration        | PyYAML       |
| Database             | SQLite       |
| Testing              | pytest       |
| Architecture         | MVC          |

---

## 📁 Project Structure

```text
Numerical-Integration-Studio/
├── algorithms/
│   ├── trapezoidal.py
│   ├── simpson_one_third.py
│   ├── simpson_three_eighth.py
│   └── taylor_method.py
│
├── controllers/          # Application controllers
├── models/               # Application data models
├── views/                # PySide6 UI components
├── services/             # Application/business services
├── database/             # SQLite database and history management
├── plots/                # Function and numerical approximation plots
├── reports/              # PDF and CSV report generation
├── utils/                # Shared utility functions
│
├── data/
│   └── history.db        # Calculation history
│
├── config.yaml            # Application configuration
├── main.py                # Application entry point
├── requirements.txt
├── tests/                 # Automated tests
└── docs/
    └── architecture.md   # Architecture documentation
```

---

## 🚀 Getting Started

### Prerequisites

* Python **3.12+**
* pip
* Windows, macOS, or Linux

### Installation

Clone the repository:

```bash
git clone https://github.com/Shashuvo/Numerical-Integration-Studio.git
cd Numerical-Integration-Studio
```

Create a virtual environment:

```bash
python -m venv venv
```

### Activate the Virtual Environment

**Windows PowerShell:**

```powershell
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the application with:

```bash
python main.py
```

On the first run, the application automatically creates:

```text
config.yaml
data/history.db
```

These files contain application settings and calculation history.

---

## 🧪 Running Tests

Run the complete test suite:

```bash
pytest tests/
```

For a coverage report:

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

---

## 🧮 Supported Methods

### 1. Trapezoidal Rule

Approximates the area under a curve by dividing the interval into smaller trapezoids.

```text
             f(x)
              │
          ────●
         /    │\
        /     │ \
       ●──────┴──●
```

The composite trapezoidal rule is implemented for numerical approximation over the selected interval.

### 2. Simpson's 1/3 Rule

Uses quadratic interpolation to approximate the function over pairs of subintervals.

The application automatically adjusts `n` to an **even number** when required.

### 3. Simpson's 3/8 Rule

Uses cubic interpolation over groups of three subintervals.

The application automatically adjusts `n` to the **nearest valid multiple of 3** when required.

### 4. Taylor's Method

The application implements a **4th-order Taylor series step method** for numerical approximation.

> **Note:** Taylor's Method is not a single universally standardized numerical integration rule like the Trapezoidal or Simpson rules. This implementation follows a 4th-order Taylor series step formulation. The exact formulation can be found in `algorithms/taylor_method.py`.

---

## 📊 Application Workflow

```text
Enter Function
      │
      ▼
Set Integration Limits
      │
      ▼
Set Number of Intervals
      │
      ▼
Select Integration Methods
      │
      ▼
    Compute
      │
      ├───────────────┐
      ▼               ▼
   Results           Plot
      │
      ▼
 Comparison
      │
      ▼
Error & Convergence Analysis
      │
      ▼
 PDF / CSV Export
```

---

## 📈 Convergence Analysis

The **Convergence Analysis** feature allows users to evaluate how numerical methods behave as the number of intervals increases.

The analysis includes:

* Approximation error
* Absolute error
* Execution time
* Number of intervals
* Method-to-method comparison

This makes it possible to observe the convergence behavior and computational performance of each integration method.

---

## 🗃️ Calculation History

Every calculation can be stored locally in an SQLite database.

Users can:

* View previous calculations
* Inspect stored results
* Reopen calculations
* Delete historical records

The database is automatically initialized when the application is first launched.

---

## 📄 Export Reports

Numerical results can be exported using:

### PDF

Generates a formatted report containing calculation details, numerical results, and analysis.

### CSV

Exports numerical results in a spreadsheet-compatible CSV format for further processing.

Reports can be generated from:

```text
File → Export PDF
File → Export CSV
```

---

## 🖥️ Application Usage

1. Enter a mathematical function of `x`.

   Examples:

   ```text
   sin(x)
   x^2
   sqrt(x)
   exp(-x)
   ```

2. Enter the lower integration limit.

3. Enter the upper integration limit.

4. Enter the number of intervals.

5. Select one or more numerical integration methods.

6. Click **Compute**.

7. Review the results in the **Results** tab.

8. View the function and approximation in the **Plot** tab.

9. Compare methods in the **Comparison** tab.

10. Use **Analysis → Convergence Analysis** for convergence and performance analysis.

11. Export results using **File → Export PDF** or **File → Export CSV**.

12. Use **File → Open History** to manage previous calculations.

---

## 🏗️ Architecture

The application follows an **MVC-inspired layered architecture** to separate the user interface, application logic, numerical algorithms, data management, visualization, and reporting.

```text
┌──────────────────────────────┐
│            Views             │
│         PySide6 GUI          │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│         Controllers          │
│      Application Logic       │
└──────────────┬───────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Algorithms  │   │  Services   │
│ Numerical   │   │ Application │
│ Methods     │   │ Services    │
└─────────────┘   └──────┬──────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Database     Plots      Reports
           SQLite    Matplotlib   PDF/CSV
```

For a detailed architecture breakdown, see:

```text
docs/architecture.md
```

---

## 🤖 AI-Assisted Development

This project was developed as a **university project with AI-assisted development**.

AI tools were used during development for areas such as:

* Code assistance and implementation
* Debugging
* Architecture discussions
* Documentation
* Test development
* UI and usability improvements

The numerical methods, project requirements, and final implementation were reviewed and integrated as part of the project development process.

---

## 🎓 University Project

**Numerical Integration Studio** was developed as part of a university course/project focused on **Numerical Methods**.

The project demonstrates practical implementation of numerical integration techniques together with software engineering concepts such as:

* Object-oriented programming
* MVC architecture
* Modular design
* Automated testing
* Data persistence
* Visualization
* Error analysis
* Performance analysis
* Report generation

---

## 👤 Author

**MD. Shahariat Hossen**

GitHub: [@Shashuvo](https://github.com/Shashuvo)

---

## 📄 License

This project is licensed under the **ISC License**.

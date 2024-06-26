# SQL Converter: MS SQL Server to Snowflake

A web application for converting MS SQL Server syntax to Snowflake SQL, powered by Python and Flask.

## Overview

This project provides a user-friendly interface for SQL developers to convert their MS SQL Server scripts to Snowflake-compatible SQL. The application uses regular expressions and custom logic to handle various SQL constructs and functions, ensuring a smooth transition between the two platforms.

[Live Demo](https://sqlconverter.pythonanywhere.com/)

## Features

- Drag-and-drop interface for file uploads
- Real-time conversion of SQL syntax
- Downloadable converted SQL files
- Handling of complex SQL constructs and functions
- Responsive web design

## Technology Stack

- Backend: Python, Flask
- Frontend: HTML5, CSS3, JavaScript
- SQL Parsing: Custom regex-based parser
- Hosting: PythonAnywhere

## Project Structure

```
sql_converter/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── templates/
│   └── index.html
│
├── app.py
└── sql_converter.py
```

## Usage

1. Navigate to [https://sqlconverter.pythonanywhere.com/](https://sqlconverter.pythonanywhere.com/)
2. Upload an MS SQL Server .sql file or drag and drop it into the designated area
3. Click "Convert" to process the SQL
4. Download the converted Snowflake-compatible SQL file

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install flask`
3. Run the application: `python app.py`
4. Access the application at `http://localhost:5000`

## Contributing

Contributions are welcome. Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgements

- Flask: Web framework
- Regular Expressions: SQL parsing logic
- PythonAnywhere: Application hosting

For more information or to report issues, please visit our [GitHub repository](https://github.com/Sehajbirsingh/sql_converter).

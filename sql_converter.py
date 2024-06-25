import re
from datetime import datetime


def convert_sql_to_snowflake(input_sql):
    def complex_replace(match, pattern, replacement):
        return re.sub(pattern, replacement, match.group(0), flags=re.IGNORECASE)

    # List of conversion patterns
    conversions = [
        # Data Types
        (r'\bNVARCHAR\(MAX\)', 'VARCHAR'),
        (r'\bNVARCHAR\b', 'VARCHAR'),
        (r'\bVARCHAR\(MAX\)', 'VARCHAR'),
        (r'\bDATETIME\b', 'TIMESTAMP_NTZ'),
        (r'\bDATETIME2\b', 'TIMESTAMP_NTZ'),
        (r'\bDATE\b', 'DATE'),
        (r'\bTINYINT\b', 'SMALLINT'),
        (r'\bSMALLDATETIME\b', 'TIMESTAMP_NTZ'),
        (r'\bMONEY\b', 'NUMBER(19,4)'),
        (r'\bSMALLMONEY\b', 'NUMBER(10,4)'),
        (r'\bUNIQUEIDENTIFIER\b', 'VARCHAR'),
        (r'\bBIT\b', 'BOOLEAN'),
        (r'\bDECIMAL\b', 'NUMBER'),
        (r'\bNUMERIC\b', 'NUMBER'),
        (r'\bFLOAT\b', 'FLOAT'),
        (r'\bREAL\b', 'FLOAT'),
        (r'\bCHAR\b', 'CHAR'),
        (r'\bNTEXT\b', 'VARCHAR'),
        (r'\bTEXT\b', 'VARCHAR'),
        (r'\bIMAGE\b', 'BINARY'),
        (r'\bVARBINARY\(MAX\)', 'BINARY'),

        # Funs
        (r'\bISNULL\(', 'COALESCE('),
        (r'\bCOALESCE\(', 'COALESCE('),
        (r'\bIIF\(', 'IFF('),
        (r'\bSYSDATE\b', 'CURRENT_TIMESTAMP()'),
        (r'\bGETDATE\(\)', 'CURRENT_TIMESTAMP()'),
        (r'\bGETUTCDATE\(\)', 'CURRENT_TIMESTAMP()'),
        (r'\bCURRENT_TIMESTAMP\b', 'CURRENT_TIMESTAMP'),
        (r'\bNEWID\(\)', 'UUID_STRING()'),
        (r'\bISDATE\((.*?)\)', r'TRY_TO_DATE(\1) IS NOT NULL'),
        (r'\bLEN\(', 'LENGTH('),

        # Syntax
        (r'\bWITH\s*\(\s*NOLOCK\s*\)', ''),
        (r'\[', ''),
        (r'\]', ''),
        (r'\bGO\b', ''),
        (r'CREATE\s+PROCEDURE', 'CREATE OR REPLACE PROCEDURE'),
        (r'CREATE\s+FUNCTION', 'CREATE OR REPLACE FUNCTION'),
        (r'CREATE\s+VIEW', 'CREATE OR REPLACE VIEW'),
        (r'ALTER\s+PROCEDURE', 'CREATE OR REPLACE PROCEDURE'),
        (r'ALTER\s+FUNCTION', 'CREATE OR REPLACE FUNCTION'),
        (r'ALTER\s+VIEW', 'CREATE OR REPLACE VIEW'),
        (r'USE\s+(\w+)', 'USE DATABASE \\1'),
        (r'BEGIN\s+TRAN(?:SACTION)?', 'BEGIN TRANSACTION'),
        (r'EXEC\s+', 'CALL '),

        # Window Functions (these are similar, but included for completeness)
        (r'ROW_NUMBER\(\)\s+OVER\s*\(ORDER BY (.*?)\)', 'ROW_NUMBER() OVER (ORDER BY \\1)'),
        (r'RANK\(\)\s+OVER\s*\(ORDER BY (.*?)\)', 'RANK() OVER (ORDER BY \\1)'),
        (r'DENSE_RANK\(\)\s+OVER\s*\(ORDER BY (.*?)\)', 'DENSE_RANK() OVER (ORDER BY \\1)'),

        # Others
        (r'\bNOT\s+FOR\s+REPLICATION\b', ''),
        (r'\bCLUSTERED\b', ''),
        (r'\bNONCLUSTERED\b', ''),
        (r'WITH\s*\(PAD_INDEX\s*=\s*OFF,\s*STATISTICS_NORECOMPUTE\s*=\s*OFF,.*?\)', ''),
    ]

    conversions.extend([
        (r"'(\d{2})-([A-Z]{3})-(\d{4})'",
         lambda m: f"'{m.group(3)}-{datetime.strptime(m.group(2), '%b').month:02d}-{m.group(1)}'"),  # Date format
        #(r'@prompt\((.*?)\)', r':\1'),  # @prompt to bind variables
        (r'WITH\s*\(\s*NOLOCK\s*\)', ''),  # Remove NOLOCK hints
        #(r'TOP\s+(\d+)', r'LIMIT \1'),  # TOP to LIMIT
        (r'\bDATEADD\((.*?),(.*?),(.*?)\)', r'DATEADD(\1, \2, \3)'),
        (r'\bDATEDIFF\((.*?),(.*?),(.*?)\)', r'DATEDIFF(\1, \2, \3)'),
        (r'\bDATEPART\((.*?),(.*?)\)', r'DATE_PART(\1, \2)'),
        #few more  left out cases, probably test individual each:-
        # System functions
        (r'\bSYSTEM_USER\b', 'CURRENT_USER()'),
        (r'\bdb_name\(\)', 'CURRENT_DATABASE()'),
        (r'\bSUSER_NAME\(\)', 'CURRENT_USER()'),

        # STUFF function
        (r'\bSTUFF\((.*?),(.*?),(.*?),(.*?)\)',
         r'CONCAT(SUBSTRING(\1, 1, \2 - 1), \4, SUBSTRING(\1, \2 + \3)) /* Verify this STUFF conversion */'),

        # datetimeoffset
        (r'\bdatetimeoffset\b', 'TIMESTAMP_TZ'),

        # Temp tables
        (r'#(\w+)', r'TEMPORARY TABLE \1 /* Verify temp table usage */'),

        # PIVOT and UNPIVOT
        (r'\bPIVOT\b', '/* PIVOT - Manual conversion required */'),
        (r'\bUNPIVOT\b', '/* UNPIVOT - Manual conversion required */'),

        # CROSS APPLY and OUTER APPLY
        (r'\bCROSS APPLY\b', '/* CROSS APPLY - Manual conversion required */'),
        (r'\bOUTER APPLY\b', '/* OUTER APPLY - Manual conversion required */'),

        # XML functions
        (r'\bFOR XML\b', '/* FOR XML - Manual conversion required, Snowflake has different XML handling */'),

        # SOUNDEX and DIFFERENCE
        (r'\bSOUNDEX\((.*?)\)', r'/* SOUNDEX(\1) - No direct equivalent in Snowflake */'),
        (r'\bDIFFERENCE\((.*?)\)', r'/* DIFFERENCE(\1) - No direct equivalent in Snowflake */'),

        # hierarchyid
        (r'\bhierarchyid\b', '/* hierarchyid - Manual conversion required, no direct equivalent in Snowflake */'),

        # FILESTREAM
        (r'\bFILESTREAM\b', '/* FILESTREAM - Manual conversion required, use Snowflake stage objects */'),

        #few more leftover 24-06
        (r'DECLARE\s+@(\w+)\s+(\w+)\s*=\s*(.+?);',
         lambda m: f"SET {m.group(1)} = {m.group(3)}::{m.group(2)};"),

        # Temporary tables
        (r'CREATE\s+TABLE\s+#(\w+)',
         r'CREATE OR REPLACE TEMPORARY TABLE \1'),

        # String concatenation
        (r'\s*\+\s*', ' || '),

        # DATEADD and DATEDIFF
        (r'DATEADD\((\w+),\s*([^,]+),\s*([^)]+)\)',
         r'DATEADD(\1, \2, \3)'),
        (r'DATEDIFF\((\w+),\s*([^,]+),\s*([^)]+)\)',
         r'DATEDIFF(\1, \2, \3)'),


    ])

    def convert_prompt_lines_to_snowflake(sql):
        # Define the pattern to match @prompt(...) occurrences
        pattern = r"@prompt\('(.*?)'\s*,\s*'.*?'\s*,\s*.*?\)"

        # Use re.sub with a lambda function to replace matched prompts
        return re.sub(pattern, "'your_value'", sql)

    def remove_schema_names(sql):
        return re.sub(r'(\w+)\.(\w+)\.(\w+)', r'\3', sql)


    def convert_window_functions(sql):
        return re.sub(r'(MAX|MIN|SUM|AVG|COUNT)\((.*?)\)\s+OVER\s*\((.*?)\)',
                      r'\1(\2) OVER (\3)',
                      sql, flags=re.IGNORECASE)

    def convert_isnull_to_coalesce(sql):
        return re.sub(r'ISNULL\((.*?),\s*(.*?)\)',
                      lambda m: f"COALESCE({m.group(1)}, {m.group(2)})",
                      sql, flags=re.IGNORECASE)

    def convert_substring(sql):
        return re.sub(r'SUBSTRING\((.*?),\s*(\d+),\s*(\d+)\)',
                      r'SUBSTRING(\1, \2, \3)',
                      sql, flags=re.IGNORECASE)

    def convert_create_alter_statements(sql):
        return re.sub(r'(CREATE|ALTER)\s+(PROCEDURE|FUNCTION|VIEW)',
                      r'CREATE OR REPLACE \2',
                      sql, flags=re.IGNORECASE)

    def remove_go_statements(sql):
        return re.sub(r'\bGO\b', '', sql, flags=re.IGNORECASE)

    def convert_use_database(sql):
        return re.sub(r'USE\s+(\w+)', r'USE DATABASE \1', sql, flags=re.IGNORECASE)

    def replace_at_with_dollar(sql):
        pattern = r'@'
        replacement = '$'
        output_string = re.sub(pattern, replacement, sql)
        return output_string

    # Apply simple conversions
    for pattern, replacement in conversions:
        input_sql = re.sub(pattern, replacement, input_sql, flags=re.IGNORECASE)

    ##code added after left out testing on 23-06-24,23:00

    # Function to handle MERGE statement conversion
    def convert_merge(match):
        merge_sql = match.group(0)
        # comment for manual verification
        merge_sql = "/* MERGE statement - Verify and adjust the following conversion */\n" + merge_sql
        # This is a simplified conversion and will need manual verification
        merge_sql = re.sub(r'WHEN NOT MATCHED BY SOURCE', 'WHEN NOT MATCHED BY SOURCE AND <condition>', merge_sql)
        return merge_sql

    # Apply MERGE conversion
    input_sql = re.sub(r'MERGE.*?;', convert_merge, input_sql, flags=re.DOTALL | re.IGNORECASE)

    # Function to handle dynamic SQL
    def convert_dynamic_sql(match):
        dynamic_sql = match.group(1)
        return f"EXECUTE IMMEDIATE '{dynamic_sql}' /* Verify dynamic SQL conversion */"

    # Apply dynamic SQL conversion
    input_sql = re.sub(r'EXEC\s*\(\s*@(.*?)\s*\)', convert_dynamic_sql, input_sql, flags=re.IGNORECASE)

    # Function to handle TRY...CATCH
    def convert_try_catch(match):
        try_block = match.group(1)
        catch_block = match.group(2)
        return f"""
        /* TRY...CATCH conversion - Verify the following */
        BEGIN
            {try_block}
        EXCEPTION
            WHEN OTHER THEN
                {catch_block}
        END;
        """

    # Apply TRY...CATCH conversion
    input_sql = re.sub(r'BEGIN TRY(.*?)END TRY\s*BEGIN CATCH(.*?)END CATCH', convert_try_catch, input_sql,
                       flags=re.DOTALL | re.IGNORECASE)

    # Function to handle complex OVER clauses
    def convert_over_clause(match):
        full_clause = match.group(0)
        return f"{full_clause} /* Verify OVER clause conversion */"

    # Apply complex OVER clause conversion
    input_sql = re.sub(r'OVER\s*\(.*?\)', convert_over_clause, input_sql, flags=re.IGNORECASE)


    # Handle TOP clause
    top_match = re.search(r'\bTOP\s+(\d+)\b', input_sql, re.IGNORECASE)
    if top_match:
        limit = top_match.group(1)
        input_sql = re.sub(r'\bTOP\s+\d+\b', '', input_sql, flags=re.IGNORECASE)  # Remove the TOP clause
        input_sql = re.sub(r'\s*;\s*$', f' LIMIT {limit}', input_sql)  # Add the LIMIT clause before the semicolon

    ###Convert CONVERT function
    input_sql = re.sub(r'CONVERT\s*\(\s*(\w+)\s*,\s*([^,\)]+)(?:\s*,\s*(\d+))?\s*\)',
                       lambda m: f"CAST({m.group(2)} AS {m.group(1)})" if m.group(1).upper() != 'DATETIME'
                       else f"CAST({m.group(2)} AS TIMESTAMP_NTZ)",
                       input_sql, flags=re.IGNORECASE)

    # Convert CAST function for DATETIME
    input_sql = re.sub(r'CAST\s*\(\s*([^,]+?)\s+AS\s+DATETIME\s*\)',
                       r'CAST(\1 AS TIMESTAMP_NTZ)',
                       input_sql, flags=re.IGNORECASE)

    # Convert DATEADD function
    input_sql = re.sub(r'DATEADD\s*\(\s*(\w+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)',
                       r'DATEADD(\1, \2, \3)',
                       input_sql, flags=re.IGNORECASE)

    # Convert DATEDIFF function
    input_sql = re.sub(r'DATEDIFF\s*\(\s*(\w+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)',
                       r'DATEDIFF(\1, \2, \3)',
                       input_sql, flags=re.IGNORECASE)

    # Convert DATEPART function
    input_sql = re.sub(r'DATEPART\s*\(\s*(\w+)\s*,\s*([^)]+)\s*\)',
                       r'DATE_PART(\1, \2)',
                       input_sql, flags=re.IGNORECASE)

    # Handle identity columns
    input_sql = re.sub(r'IDENTITY\((\d+),\s*(\d+)\)',
                       lambda m: f'IDENTITY({m.group(1)}, {m.group(2)})',
                       input_sql, flags=re.IGNORECASE)

    # Convert SELECT INTO to CREATE TABLE AS
    input_sql = re.sub(r'SELECT\s+(.*?)\s+INTO\s+(\w+)\s+FROM',
                       r'CREATE OR REPLACE TABLE \2 AS SELECT \1 FROM',
                       input_sql, flags=re.IGNORECASE | re.DOTALL)

    # Convert string concatenation
    input_sql = re.sub(r'(\w+|\))\s*\+\s*', r'\1 || ', input_sql)

    # Handle @@ROWCOUNT
    input_sql = input_sql.replace('@@ROWCOUNT', 'SQLROWCOUNT')

    # Ensure there's only one semicolon at the end
    input_sql = re.sub(r';*\s*$', ';', input_sql)

    input_sql = remove_schema_names(input_sql)
    input_sql = convert_window_functions(input_sql)
    input_sql = convert_isnull_to_coalesce(input_sql)
    input_sql = convert_substring(input_sql)
    input_sql = convert_create_alter_statements(input_sql)
    input_sql = remove_go_statements(input_sql)
    input_sql = convert_use_database(input_sql)
    input_sql = convert_prompt_lines_to_snowflake(input_sql)
    input_sql = replace_at_with_dollar(input_sql)

     # Add a general warning at the end of the converted SQL
    input_sql += "\n\n/* IMPORTANT: This is an automated conversion. Please review all changes and comments carefully. Some features may require manual adjustment or redesign for Snowflake compatibility. */"


    return input_sql
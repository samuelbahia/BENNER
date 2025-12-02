"""
SQL Builder Agent
A smart agent to build SQL queries with table and column selectors and join support.
"""

import json
import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class JoinType(Enum):
    """Supported join types"""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"


@dataclass
class Column:
    """Represents a database column"""
    name: str
    table: str
    data_type: str
    nullable: bool
    description: str = ""
    
    @property
    def qualified_name(self) -> str:
        """Returns fully qualified column name"""
        return f"{self.table}.{self.name}"


@dataclass
class Table:
    """Represents a database table"""
    name: str
    columns: List[Column] = field(default_factory=list)
    description: str = ""
    
    def get_column(self, column_name: str) -> Optional[Column]:
        """Get a column by name"""
        for col in self.columns:
            if col.name.upper() == column_name.upper():
                return col
        return None


@dataclass
class Join:
    """Represents a join between tables"""
    join_type: JoinType
    table: str
    on_condition: str
    
    def to_sql(self) -> str:
        """Generate SQL for this join"""
        return f"{self.join_type.value} {self.table} ON {self.on_condition}"


class SQLBuilderAgent:
    """
    Intelligent SQL Builder Agent
    Constructs SQL queries based on table and column selections with joins
    """
    
    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self.selected_columns: List[Column] = []
        self.joins: List[Join] = []
        self.where_conditions: List[str] = []
        self.order_by: List[str] = []
        self.group_by: List[str] = []
        self.limit: Optional[int] = None
        
    def load_schema_from_dict(self, schema_text: str):
        """
        Parse the schema from the data dictionary text file
        """
        current_table = None
        lines = schema_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect table name (pattern: "NUMBER. TABLE_NAME:")
            table_match = re.match(r'^\d+\.\s+([A-Z_]+):\s*$', line)
            if table_match:
                table_name = table_match.group(1)
                current_table = Table(name=table_name)
                self.tables[table_name] = current_table
                continue
            
            # Parse column definitions
            if current_table and '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    col_name = parts[0].strip()
                    col_type = parts[1].strip()
                    nullable = parts[2].strip() == 'S'
                    description = parts[3].strip() if len(parts) > 3 else ""
                    
                    if col_name and col_type:
                        column = Column(
                            name=col_name,
                            table=current_table.name,
                            data_type=col_type,
                            nullable=nullable,
                            description=description
                        )
                        current_table.columns.append(column)
    
    def add_table(self, table: Table):
        """Add a table to the schema"""
        self.tables[table.name] = table
    
    def select_column(self, table_name: str, column_name: str, alias: Optional[str] = None):
        """Select a column for the query"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found in schema")
        
        table = self.tables[table_name]
        column = table.get_column(column_name)
        
        if not column:
            raise ValueError(f"Column '{column_name}' not found in table '{table_name}'")
        
        self.selected_columns.append(column)
    
    def add_join(self, join_type: JoinType, table_name: str, 
                 left_table: str, left_column: str,
                 right_table: str, right_column: str):
        """
        Add a join condition
        
        Args:
            join_type: Type of join (INNER, LEFT, etc.)
            table_name: Name of the table to join
            left_table: Left side table
            left_column: Left side column
            right_table: Right side table
            right_column: Right side column
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found in schema")
        
        on_condition = f"{left_table}.{left_column} = {right_table}.{right_column}"
        join = Join(join_type=join_type, table=table_name, on_condition=on_condition)
        self.joins.append(join)
    
    def add_where(self, condition: str):
        """Add a WHERE condition"""
        self.where_conditions.append(condition)
    
    def add_order_by(self, column: str, ascending: bool = True):
        """Add an ORDER BY clause"""
        direction = "ASC" if ascending else "DESC"
        self.order_by.append(f"{column} {direction}")
    
    def add_group_by(self, column: str):
        """Add a GROUP BY clause"""
        self.group_by.append(column)
    
    def set_limit(self, limit: int):
        """Set the LIMIT clause"""
        self.limit = limit
    
    def get_involved_tables(self) -> Set[str]:
        """Get all tables involved in the query"""
        tables = set()
        
        for column in self.selected_columns:
            tables.add(column.table)
        
        for join in self.joins:
            tables.add(join.table)
        
        return tables
    
    def infer_joins(self, tables: List[str]) -> List[Join]:
        """
        Intelligently infer join conditions based on common patterns
        This is a simplified version - can be enhanced with foreign key metadata
        """
        inferred_joins = []
        
        # Common join patterns based on naming conventions
        for i, table1 in enumerate(tables[:-1]):
            for table2 in tables[i+1:]:
                # Check for common ID columns
                if table1 in self.tables and table2 in self.tables:
                    t1 = self.tables[table1]
                    t2 = self.tables[table2]
                    
                    # Look for HANDLE columns (primary keys)
                    for col1 in t1.columns:
                        for col2 in t2.columns:
                            # Match on HANDLE or foreign key patterns
                            if (col1.name == "HANDLE" and col2.name.upper() == table1.upper()) or \
                               (col2.name == "HANDLE" and col1.name.upper() == table2.upper()):
                                on_condition = f"{table1}.{col1.name} = {table2}.{col2.name}"
                                join = Join(
                                    join_type=JoinType.INNER,
                                    table=table2,
                                    on_condition=on_condition
                                )
                                inferred_joins.append(join)
                                break
        
        return inferred_joins
    
    def build_query(self, auto_infer_joins: bool = False) -> str:
        """
        Build the final SQL query
        
        Args:
            auto_infer_joins: If True, automatically infer joins between tables
            
        Returns:
            Complete SQL query string
        """
        if not self.selected_columns:
            raise ValueError("No columns selected for the query")
        
        # Build SELECT clause
        select_parts = []
        for col in self.selected_columns:
            select_parts.append(col.qualified_name)
        
        select_clause = "SELECT " + ", ".join(select_parts)
        
        # Build FROM clause
        involved_tables = self.get_involved_tables()
        if not involved_tables:
            raise ValueError("No tables involved in the query")
        
        # Start with the first table
        from_table = list(involved_tables)[0]
        from_clause = f"FROM {from_table}"
        
        # Build JOIN clauses
        join_clauses = []
        
        if auto_infer_joins and not self.joins:
            # Automatically infer joins
            inferred_joins = self.infer_joins(list(involved_tables))
            join_clauses = [join.to_sql() for join in inferred_joins]
        else:
            # Use manually specified joins
            join_clauses = [join.to_sql() for join in self.joins]
        
        # Build WHERE clause
        where_clause = ""
        if self.where_conditions:
            where_clause = "WHERE " + " AND ".join(self.where_conditions)
        
        # Build GROUP BY clause
        group_by_clause = ""
        if self.group_by:
            group_by_clause = "GROUP BY " + ", ".join(self.group_by)
        
        # Build ORDER BY clause
        order_by_clause = ""
        if self.order_by:
            order_by_clause = "ORDER BY " + ", ".join(self.order_by)
        
        # Build LIMIT clause
        limit_clause = ""
        if self.limit:
            limit_clause = f"LIMIT {self.limit}"
        
        # Combine all parts
        query_parts = [select_clause, from_clause]
        
        if join_clauses:
            query_parts.extend(join_clauses)
        
        if where_clause:
            query_parts.append(where_clause)
        
        if group_by_clause:
            query_parts.append(group_by_clause)
        
        if order_by_clause:
            query_parts.append(order_by_clause)
        
        if limit_clause:
            query_parts.append(limit_clause)
        
        return "\n".join(query_parts) + ";"
    
    def reset(self):
        """Reset the query builder"""
        self.selected_columns.clear()
        self.joins.clear()
        self.where_conditions.clear()
        self.order_by.clear()
        self.group_by.clear()
        self.limit = None
    
    def get_table_list(self) -> List[str]:
        """Get list of all available tables"""
        return sorted(self.tables.keys())
    
    def get_columns_for_table(self, table_name: str) -> List[Dict[str, str]]:
        """Get columns for a specific table"""
        if table_name not in self.tables:
            return []
        
        table = self.tables[table_name]
        return [
            {
                "name": col.name,
                "type": col.data_type,
                "nullable": "Yes" if col.nullable else "No",
                "description": col.description
            }
            for col in table.columns
        ]
    
    def export_schema_json(self) -> str:
        """Export the schema as JSON"""
        schema = {}
        for table_name, table in self.tables.items():
            schema[table_name] = {
                "description": table.description,
                "columns": [
                    {
                        "name": col.name,
                        "type": col.data_type,
                        "nullable": col.nullable,
                        "description": col.description
                    }
                    for col in table.columns
                ]
            }
        return json.dumps(schema, indent=2)


def main():
    """Example usage of the SQL Builder Agent"""
    agent = SQLBuilderAgent()
    
    # Example: Create sample tables
    users_table = Table(name="USERS")
    users_table.columns = [
        Column(name="HANDLE", table="USERS", data_type="Integer", nullable=False, description="User ID"),
        Column(name="NAME", table="USERS", data_type="Varchar(80)", nullable=False, description="User name"),
        Column(name="EMAIL", table="USERS", data_type="Varchar(100)", nullable=True, description="Email address"),
    ]
    
    orders_table = Table(name="ORDERS")
    orders_table.columns = [
        Column(name="HANDLE", table="ORDERS", data_type="Integer", nullable=False, description="Order ID"),
        Column(name="USER_ID", table="ORDERS", data_type="Integer", nullable=False, description="User ID"),
        Column(name="TOTAL", table="ORDERS", data_type="Number", nullable=False, description="Total amount"),
    ]
    
    agent.add_table(users_table)
    agent.add_table(orders_table)
    
    # Build a query
    agent.select_column("USERS", "HANDLE")
    agent.select_column("USERS", "NAME")
    agent.select_column("ORDERS", "TOTAL")
    
    # Add a join
    agent.add_join(
        JoinType.INNER,
        "ORDERS",
        "USERS", "HANDLE",
        "ORDERS", "USER_ID"
    )
    
    # Add conditions
    agent.add_where("ORDERS.TOTAL > 100")
    agent.add_order_by("USERS.NAME", ascending=True)
    
    # Generate SQL
    sql = agent.build_query()
    print("Generated SQL:")
    print(sql)


if __name__ == "__main__":
    main()

"""
Tests for SQL Builder Agent
"""

import unittest
from sql_builder_agent import SQLBuilderAgent, JoinType, Table, Column


class TestSQLBuilderAgent(unittest.TestCase):
    """Test cases for the SQL Builder Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = SQLBuilderAgent()
        
        # Create test tables
        self.users_table = Table(name="USERS")
        self.users_table.columns = [
            Column(name="HANDLE", table="USERS", data_type="Integer", nullable=False, description="User ID"),
            Column(name="NAME", table="USERS", data_type="Varchar(80)", nullable=False, description="User name"),
            Column(name="EMAIL", table="USERS", data_type="Varchar(100)", nullable=True, description="Email address"),
        ]
        
        self.orders_table = Table(name="ORDERS")
        self.orders_table.columns = [
            Column(name="HANDLE", table="ORDERS", data_type="Integer", nullable=False, description="Order ID"),
            Column(name="USER_ID", table="ORDERS", data_type="Integer", nullable=False, description="User ID"),
            Column(name="TOTAL", table="ORDERS", data_type="Number", nullable=False, description="Total amount"),
            Column(name="STATUS", table="ORDERS", data_type="Varchar(20)", nullable=False, description="Order status"),
        ]
        
        self.agent.add_table(self.users_table)
        self.agent.add_table(self.orders_table)
    
    def test_add_table(self):
        """Test adding a table to the agent"""
        self.assertIn("USERS", self.agent.tables)
        self.assertIn("ORDERS", self.agent.tables)
        self.assertEqual(len(self.agent.tables), 2)
    
    def test_select_column(self):
        """Test selecting columns"""
        self.agent.select_column("USERS", "NAME")
        self.agent.select_column("USERS", "EMAIL")
        
        self.assertEqual(len(self.agent.selected_columns), 2)
        self.assertEqual(self.agent.selected_columns[0].name, "NAME")
        self.assertEqual(self.agent.selected_columns[1].name, "EMAIL")
    
    def test_select_invalid_table(self):
        """Test selecting from non-existent table"""
        with self.assertRaises(ValueError):
            self.agent.select_column("INVALID_TABLE", "COLUMN")
    
    def test_select_invalid_column(self):
        """Test selecting non-existent column"""
        with self.assertRaises(ValueError):
            self.agent.select_column("USERS", "INVALID_COLUMN")
    
    def test_add_join(self):
        """Test adding a join"""
        self.agent.add_join(
            JoinType.INNER,
            "ORDERS",
            "USERS", "HANDLE",
            "ORDERS", "USER_ID"
        )
        
        self.assertEqual(len(self.agent.joins), 1)
        self.assertEqual(self.agent.joins[0].join_type, JoinType.INNER)
        self.assertEqual(self.agent.joins[0].table, "ORDERS")
    
    def test_add_where_condition(self):
        """Test adding WHERE conditions"""
        self.agent.add_where("ORDERS.TOTAL > 100")
        self.agent.add_where("ORDERS.STATUS = 'COMPLETED'")
        
        self.assertEqual(len(self.agent.where_conditions), 2)
    
    def test_add_order_by(self):
        """Test adding ORDER BY"""
        self.agent.add_order_by("USERS.NAME", ascending=True)
        self.agent.add_order_by("ORDERS.TOTAL", ascending=False)
        
        self.assertEqual(len(self.agent.order_by), 2)
        self.assertIn("ASC", self.agent.order_by[0])
        self.assertIn("DESC", self.agent.order_by[1])
    
    def test_add_group_by(self):
        """Test adding GROUP BY"""
        self.agent.add_group_by("USERS.NAME")
        
        self.assertEqual(len(self.agent.group_by), 1)
        self.assertEqual(self.agent.group_by[0], "USERS.NAME")
    
    def test_set_limit(self):
        """Test setting LIMIT"""
        self.agent.set_limit(100)
        
        self.assertEqual(self.agent.limit, 100)
    
    def test_simple_query(self):
        """Test building a simple query"""
        self.agent.select_column("USERS", "NAME")
        self.agent.select_column("USERS", "EMAIL")
        
        sql = self.agent.build_query()
        
        self.assertIn("SELECT", sql)
        self.assertIn("USERS.NAME", sql)
        self.assertIn("USERS.EMAIL", sql)
        self.assertIn("FROM USERS", sql)
        self.assertTrue(sql.endswith(";"))
    
    def test_query_with_join(self):
        """Test building a query with JOIN"""
        self.agent.select_column("USERS", "NAME")
        self.agent.select_column("ORDERS", "TOTAL")
        
        self.agent.add_join(
            JoinType.INNER,
            "ORDERS",
            "USERS", "HANDLE",
            "ORDERS", "USER_ID"
        )
        
        sql = self.agent.build_query()
        
        self.assertIn("SELECT", sql)
        self.assertIn("INNER JOIN", sql)
        self.assertIn("USERS.HANDLE = ORDERS.USER_ID", sql)
    
    def test_query_with_left_join(self):
        """Test building a query with LEFT JOIN"""
        self.agent.select_column("USERS", "NAME")
        self.agent.select_column("ORDERS", "TOTAL")
        
        self.agent.add_join(
            JoinType.LEFT,
            "ORDERS",
            "USERS", "HANDLE",
            "ORDERS", "USER_ID"
        )
        
        sql = self.agent.build_query()
        
        self.assertIn("LEFT JOIN", sql)
    
    def test_query_with_where(self):
        """Test building a query with WHERE"""
        self.agent.select_column("USERS", "NAME")
        self.agent.add_where("USERS.NAME LIKE '%John%'")
        
        sql = self.agent.build_query()
        
        self.assertIn("WHERE", sql)
        self.assertIn("USERS.NAME LIKE '%John%'", sql)
    
    def test_query_with_multiple_where(self):
        """Test building a query with multiple WHERE conditions"""
        self.agent.select_column("ORDERS", "TOTAL")
        self.agent.add_where("ORDERS.TOTAL > 100")
        self.agent.add_where("ORDERS.STATUS = 'COMPLETED'")
        
        sql = self.agent.build_query()
        
        self.assertIn("WHERE", sql)
        self.assertIn("AND", sql)
    
    def test_query_with_order_by(self):
        """Test building a query with ORDER BY"""
        self.agent.select_column("USERS", "NAME")
        self.agent.add_order_by("USERS.NAME", ascending=True)
        
        sql = self.agent.build_query()
        
        self.assertIn("ORDER BY", sql)
        self.assertIn("ASC", sql)
    
    def test_query_with_group_by(self):
        """Test building a query with GROUP BY"""
        self.agent.select_column("USERS", "NAME")
        self.agent.add_group_by("USERS.NAME")
        
        sql = self.agent.build_query()
        
        self.assertIn("GROUP BY", sql)
    
    def test_query_with_limit(self):
        """Test building a query with LIMIT"""
        self.agent.select_column("USERS", "NAME")
        self.agent.set_limit(10)
        
        sql = self.agent.build_query()
        
        self.assertIn("LIMIT 10", sql)
    
    def test_complex_query(self):
        """Test building a complex query with all features"""
        self.agent.select_column("USERS", "NAME")
        self.agent.select_column("ORDERS", "TOTAL")
        self.agent.select_column("ORDERS", "STATUS")
        
        self.agent.add_join(
            JoinType.LEFT,
            "ORDERS",
            "USERS", "HANDLE",
            "ORDERS", "USER_ID"
        )
        
        self.agent.add_where("ORDERS.TOTAL > 50")
        self.agent.add_where("ORDERS.STATUS = 'ACTIVE'")
        self.agent.add_order_by("ORDERS.TOTAL", ascending=False)
        self.agent.set_limit(100)
        
        sql = self.agent.build_query()
        
        # Verify all parts are present
        self.assertIn("SELECT", sql)
        self.assertIn("USERS.NAME", sql)
        self.assertIn("ORDERS.TOTAL", sql)
        self.assertIn("LEFT JOIN", sql)
        self.assertIn("WHERE", sql)
        self.assertIn("ORDER BY", sql)
        self.assertIn("LIMIT", sql)
    
    def test_reset(self):
        """Test resetting the agent"""
        self.agent.select_column("USERS", "NAME")
        self.agent.add_where("USERS.NAME = 'Test'")
        self.agent.add_order_by("USERS.NAME")
        
        self.agent.reset()
        
        self.assertEqual(len(self.agent.selected_columns), 0)
        self.assertEqual(len(self.agent.where_conditions), 0)
        self.assertEqual(len(self.agent.order_by), 0)
        self.assertIsNone(self.agent.limit)
    
    def test_get_table_list(self):
        """Test getting table list"""
        tables = self.agent.get_table_list()
        
        self.assertIn("USERS", tables)
        self.assertIn("ORDERS", tables)
        self.assertEqual(len(tables), 2)
    
    def test_get_columns_for_table(self):
        """Test getting columns for a table"""
        columns = self.agent.get_columns_for_table("USERS")
        
        self.assertEqual(len(columns), 3)
        self.assertEqual(columns[0]['name'], "HANDLE")
        self.assertEqual(columns[1]['name'], "NAME")
        self.assertEqual(columns[2]['name'], "EMAIL")
    
    def test_qualified_column_name(self):
        """Test qualified column name"""
        column = Column(name="NAME", table="USERS", data_type="Varchar(80)", nullable=False)
        
        self.assertEqual(column.qualified_name, "USERS.NAME")
    
    def test_no_columns_error(self):
        """Test building query without columns"""
        with self.assertRaises(ValueError):
            self.agent.build_query()
    
    def test_join_to_sql(self):
        """Test join SQL generation"""
        from sql_builder_agent import Join
        
        join = Join(
            join_type=JoinType.INNER,
            table="ORDERS",
            on_condition="USERS.HANDLE = ORDERS.USER_ID"
        )
        
        sql = join.to_sql()
        
        self.assertEqual(sql, "INNER JOIN ORDERS ON USERS.HANDLE = ORDERS.USER_ID")


class TestSchemaLoading(unittest.TestCase):
    """Test schema loading from data dictionary"""
    
    def test_load_schema_from_dict(self):
        """Test loading schema from text"""
        agent = SQLBuilderAgent()
        
        schema_text = """
1. Z_GRUPOUSUARIOS:  
NOMETIPONULLDESCRIÇÃOTABELA
HANDLE	Integer	NCódigo
Z_GRUPO	Integer	NGrupo
NOME	Varchar (80)	NNome

2. PR_PROCESSOS:  
NOME	TIPONULLDESCRIÇÃOTABELA
HANDLE	Integer	NCódigo
NUMERO	Varchar (40)	NNúmero
USUARIO	Integer	SUsuárioZ_GRUPOUSUARIOS
"""
        
        agent.load_schema_from_dict(schema_text)
        
        # Verify tables were loaded
        self.assertIn("Z_GRUPOUSUARIOS", agent.tables)
        self.assertIn("PR_PROCESSOS", agent.tables)
        
        # Verify columns were loaded
        users_cols = agent.get_columns_for_table("Z_GRUPOUSUARIOS")
        self.assertTrue(len(users_cols) > 0)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()

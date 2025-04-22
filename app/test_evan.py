import pytest
from app import create_app, mysql 
from flask import current_app

@pytest.fixture
def client():
    app = create_app(testing=True)

    with app.app_context():
        cur = mysql.connection.cursor()
        # Clear or reset test tables if needed
        cur.execute("DELETE FROM income")
        cur.execute("DELETE FROM expenses")
        cur.execute("DELETE FROM budgets")
        cur.close()
        mysql.connection.commit()

    with app.test_client() as client:
        yield client


class TestBudget:

    def test_create_budget(self, client):
        response = client.post('/createBudget/', json={
            'username': 'ana',
            'monthly_limit': 2000.00
        })
        assert response.status_code == 201
        assert response.json['message'] == 'Budget created successfully'

    def test_prevent_duplicate_budget(self, client):
        client.post('/createBudget/', json={'username': 'ana', 'monthly_limit': 2000.00})
        response = client.post('/budgets', json={'username': 'ana', 'monthly_limit': 2500.00})
        assert response.status_code == 400
        assert 'error' in response.json


class TestIncome:

    def test_add_income(self, client):
        response = client.post('/addIncome', json={
            'username': 'ana',
            'income_source': 'Freelancing',
            'income_amount': 1200.00
        })
        assert response.status_code == 201
        assert response.json['message'] == 'Income added successfully'


class TestExpense:

    def test_add_expense(self, client):
        response = client.post('/addExpenses', json={
            'username': 'ana',
            'expense_source': 'Groceries',
            'expense_amount': 150.00
        })
        assert response.status_code == 201
        assert response.json['message'] == 'Expense added successfully'


class TestTotals:

    def test_total_calculation(self, client):
        response = client.get('/view_budget/ana')
        assert response.status_code == 200
        assert 'total_income' in response.json
        assert 'total_expense' in response.json


class TestPrediction:

    def test_chatgpt_prediction(self, client, mocker):
        mock_response = {
            'can_afford': True,
            'reason': 'You have enough income to cover this expense.'
        }
        mocker.patch('app.routes.chat_evan_response', return_value=mock_response)

        response = client.post('/report', json={
            'username': 'ana',
            'new_expense': 100.00
        })

        assert response.status_code == 200
        assert response.json['can_afford'] is True
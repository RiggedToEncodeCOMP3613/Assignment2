import pytest, unittest, json
from App.main import create_app
from App.database import db, create_db
from App.models import User, Driver, Drive, Resident, StopRequest

class AdminAPITests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        create_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Helper method to create test data
    def create_test_data(self):
        """Create a set of test data in the database"""
        # Create user
        user = User(username="testuser", password="pass")
        db.session.add(user)
        
        # Create driver and drive
        driver = Driver(username="driver_api", password="pass", status="active")
        db.session.add(driver)
        db.session.commit()
        drive = driver.add_drive(current_location="Test Route")
        
        # Create resident
        resident = Resident(username="resident_api", password="pass", name="TestResident", street="Test St")
        db.session.add(resident)
        db.session.commit()
        
        # Create stop request
        stop_request = resident.create_stop_request(drive)
        
        return {
            'user': user,
            'driver': driver,
            'drive': drive,
            'resident': resident,
            'stop_request': stop_request
        }

    def test_get_all_data(self):
        """Test GET /api/admin/data endpoint"""
        test_data = self.create_test_data()
        response = self.client.get('/api/admin/data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['users']), 1)
        self.assertEqual(len(data['drivers']), 1)
        self.assertEqual(len(data['drives']), 1)
        self.assertEqual(len(data['residents']), 1)
        self.assertEqual(len(data['stop_requests']), 1)

    def test_get_users(self):
        """Test GET /api/admin/users endpoint"""
        test_data = self.create_test_data()
        response = self.client.get('/api/admin/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'testuser')

    def test_create_user(self):
        """Test POST /api/admin/users endpoint"""
        response = self.client.post('/api/admin/users',
            json={'username': 'newuser', 'password': 'newpass'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'newuser')

    def test_get_drivers(self):
        """Test GET /api/admin/drivers endpoint"""
        test_data = self.create_test_data()
        response = self.client.get('/api/admin/drivers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], 'active')

    def test_create_driver(self):
        """Test POST /api/admin/drivers endpoint"""
        response = self.client.post('/api/admin/drivers',
            json={'username': 'driver_api2', 'password': 'pass', 'status': 'active'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'active')

    def test_get_driver_schedule(self):
        """Test GET /api/admin/drivers/<id>/schedule endpoint"""
        test_data = self.create_test_data()
        response = self.client.get(f'/api/admin/drivers/{test_data["driver"].id}/schedule')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)

    def test_get_drives(self):
        """Test GET /api/admin/drives endpoint"""
        test_data = self.create_test_data()
        response = self.client.get('/api/admin/drives')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['driver_id'], test_data['driver'].id)

    def test_create_drive(self):
        """Test POST /api/admin/drives endpoint"""
        driver = Driver(username="driver_api3", password="pass", status="active")
        db.session.add(driver)
        db.session.commit()

        response = self.client.post('/api/admin/drives',
            json={'driver_id': driver.id, 'current_location': 'Test Route'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_get_residents(self):
        """Test GET /api/admin/residents endpoint"""
        test_data = self.create_test_data()
        response = self.client.get('/api/admin/residents')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'TestResident')
        self.assertEqual(data[0]['street'], 'Test St')

    def test_create_resident(self):
        """Test POST /api/admin/residents endpoint"""
        response = self.client.post('/api/admin/residents',
            json={'username': 'resident_api2', 'password': 'pass', 'name': 'NewResident', 'street': 'New St'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'NewResident')
        self.assertEqual(data['street'], 'New St')

    def test_get_resident_inbox(self):
        """Test GET /api/admin/residents/<id>/inbox endpoint"""
        test_data = self.create_test_data()
        response = self.client.get(f'/api/admin/residents/{test_data["resident"].id}/inbox')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)

    def test_get_stop_requests(self):
        """Test GET /api/admin/stop-requests endpoint"""
        test_data = self.create_test_data()
        response = self.client.get('/api/admin/stop-requests')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['requestee_id'], test_data['resident'].id)
        self.assertEqual(data[0]['drive_id'], test_data['drive'].id)

    def test_create_stop_request(self):
        """Test POST /api/admin/stop-requests endpoint"""
        # Create required related objects first
        driver = Driver(username="driver_api4", password="pass", status="active")
        db.session.add(driver)
        db.session.commit()
        drive = driver.add_drive(current_location="Test Route")
        
        resident = Resident(username="resident_api3", password="pass", name="TestResident", street="Test St")
        db.session.add(resident)
        db.session.commit()

        response = self.client.post('/api/admin/stop-requests',
            json={
                'resident_id': resident.id,
                'drive_id': drive.id,
                'street': 'Test St'
            })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_error_cases(self):
        """Test various error cases for API endpoints"""
        # Test creating user without required fields
        response = self.client.post('/api/admin/users', json={})
        self.assertEqual(response.status_code, 400)

        # Test creating drive with non-existent driver
        response = self.client.post('/api/admin/drives',
            json={'driver_id': 999, 'current_location': 'Test'})
        self.assertEqual(response.status_code, 404)

        # Test getting schedule for non-existent driver
        response = self.client.get('/api/admin/drivers/999/schedule')
        self.assertEqual(response.status_code, 200)  # Returns empty list
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

        # Test creating stop request with invalid IDs
        response = self.client.post('/api/admin/stop-requests',
            json={'resident_id': 999, 'drive_id': 999})
        self.assertEqual(response.status_code, 404)
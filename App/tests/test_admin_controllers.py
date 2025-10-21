import unittest
from App.controllers import (
    list_all_data,
    print_users, print_drivers, print_drives,
    print_residents, print_stop_requests
)
from App.models import User, Driver, Drive, Resident, StopRequest
from App.database import db, create_db
from App.main import create_app

class AdminControllersUnitTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        self.app_context = self.app.app_context()
        self.app_context.push()
        create_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_list_all_data_empty(self):
        """Test list_all_data returns correct structure with empty database"""
        data = list_all_data()
        self.assertIsInstance(data, dict)
        self.assertIn('users', data)
        self.assertIn('drivers', data)
        self.assertIn('drives', data)
        self.assertIn('residents', data)
        self.assertIn('stop_requests', data)
        self.assertEqual(len(data['users']), 0)
        self.assertEqual(len(data['drivers']), 0)
        self.assertEqual(len(data['drives']), 0)
        self.assertEqual(len(data['residents']), 0)
        self.assertEqual(len(data['stop_requests']), 0)

    def test_list_all_data_with_data(self):
        """Test list_all_data returns correct data with populated database"""
        # Create test data
        user = User(username="testuser", password="pass")
        db.session.add(user)
        
        driver = Driver(status="active")
        db.session.add(driver)
        
        resident = Resident(name="Alice", street="Main St")
        db.session.add(resident)
        db.session.commit()

        # Get data
        data = list_all_data()
        
        # Check users
        self.assertEqual(len(data['users']), 1)
        self.assertEqual(data['users'][0]['username'], "testuser")
        
        # Check drivers
        self.assertEqual(len(data['drivers']), 1)
        self.assertEqual(data['drivers'][0]['status'], "active")
        
        # Check residents
        self.assertEqual(len(data['residents']), 1)
        self.assertEqual(data['residents'][0]['name'], "Alice")
        self.assertEqual(data['residents'][0]['street'], "Main St")

    def test_print_users(self):
        """Test print_users returns correct data"""
        user = User(username="testuser", password="pass")
        db.session.add(user)
        db.session.commit()

        users = print_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], "testuser")

    def test_print_drivers(self):
        """Test print_drivers returns correct data"""
        driver = Driver(status="active")
        db.session.add(driver)
        db.session.commit()

        drivers = print_drivers()
        self.assertEqual(len(drivers), 1)
        self.assertEqual(drivers[0]['status'], "active")

    def test_print_drives(self):
        """Test print_drives returns correct data"""
        driver = Driver(status="active")
        db.session.add(driver)
        db.session.commit()
        
        drive = driver.add_drive(current_location="North Route")

        drives = print_drives()
        self.assertEqual(len(drives), 1)
        self.assertEqual(drives[0]['driver_id'], driver.id)

    def test_print_residents(self):
        """Test print_residents returns correct data"""
        resident = Resident(name="Bob", street="Oak Ave")
        db.session.add(resident)
        db.session.commit()

        residents = print_residents()
        self.assertEqual(len(residents), 1)
        self.assertEqual(residents[0]['name'], "Bob")
        self.assertEqual(residents[0]['street'], "Oak Ave")

    def test_print_stop_requests(self):
        """Test print_stop_requests returns correct data"""
        driver = Driver(status="active")
        db.session.add(driver)
        drive = driver.add_drive(current_location="North Route")
        
        resident = Resident(name="Charlie", street="Pine St")
        db.session.add(resident)
        db.session.commit()
        
        stop_request = resident.create_stop_request(drive)

        requests = print_stop_requests()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['requestee_id'], resident.id)
        self.assertEqual(requests[0]['drive_id'], drive.id)
        self.assertEqual(requests[0]['street_name'], "Pine St")
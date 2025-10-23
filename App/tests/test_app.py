import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime, timezone

from App.main import create_app
from App.database import db, create_db
from App.models import User, Driver, Drive, Resident, StopRequest
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user,
    create_driver,
    get_driver,
    create_drive,
    get_driver_schedule,
    create_resident,
    get_resident,
    create_stop_request,
    get_resident_inbox
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_create_user(self):
        user = User("john_doe", "password123") # mock data for unit test
        self.assertIsNone(user.id)
        self.assertEqual(user.username, "john_doe") 
    
    def test_create_driver(self):
        driver = Driver(username="driver1", password="pass", status="Available") # mock data for unit test
        self.assertIsNone(driver.id)
        self.assertEqual(driver.username, "driver1")
        self.assertEqual(driver.status, "Available")
    
    def test_create_drive(self):
        drive = Drive(datetime="2026-01-10 18:00", current_location="Main St", driver=None) # mock data for unit test
        self.assertIsNone(drive.id)
        self.assertIsNone(drive.driver)
        self.assertEqual(drive.datetime, "2026-01-10 18:00")
        self.assertEqual(drive.current_location, "Main St")
        
    def test_create_resident(self):
        resident = Resident(username="alice", password="pass", name="Alice", street="Main St") # mock data for unit test
        self.assertIsNone(resident.id)
        self.assertEqual(resident.username, "alice")
        self.assertEqual(resident.name, "Alice")
        self.assertEqual(resident.street, "Main St")
    
    def test_create_stop_request(self):
        stop_request = StopRequest(drive=None, street_name="Main St", requestee=None) # mock data for unit test
        self.assertIsNone(stop_request.id)
        self.assertIsNone(stop_request.drive_id)
        self.assertIsNone(stop_request.drive)
        self.assertIsNone(stop_request.requestee_id)
        self.assertIsNone(stop_request.requestee)
        self.assertEqual(stop_request.street_name, "Main St")
    
    def test_hashed_password(self):
        user = User("john_doe", "mypass") # mock data for unit test
        user.set_password("mypass")
        self.assertNotEqual(user.password, "mypass")

    def test_check_password(self):
        user = User("john_doe", "mypass") # mock data for unit test
        user.set_password("mypass")
        check = user.check_password("mypass")
        self.assertTrue(check)
        
    
    #############################################################
    '''
    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob", "bobpass")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob"})
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)
    '''
    

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


def test_authenticate():
    user = create_user("bob", "bobpass")
    assert login("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "bobpass")
        assert user.username == "rick"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

    # Tests data changes in the database
    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"

    ###################################################################   
    def test_create_user(self):
        john = create_user("john_doe", "password123")
        self.assertIsNotNone(john)
        assert login("john_doe", "password123") != None
        
        user = get_user_by_username(john.username)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, john.username)

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertIsNotNone(users_json)

        usernames = [user["username"] for user in users_json]
        self.assertIsNotNone(usernames)

    def test_create_driver_with_schedule(self):
        driver = Driver(username="driver2", password="pass", status="Available")
        db.session.add(driver)
        db.session.commit()
        self.assertIsNotNone(driver.id)
        self.assertEqual(driver.username, "driver2")
        self.assertEqual(driver.status, "Available")

        drive1 = create_drive(driver.id, when="2026-01-10 18:00", current_location="Main St")
        self.assertIsNotNone(drive1.id)
        self.assertEqual(drive1.current_location, "Main St")
        expected_dt = datetime.strptime("2026-01-10 18:00", "%Y-%m-%d %H:%M")
        self.assertEqual(drive1.datetime, expected_dt)
        
        drive2 = create_drive(driver.id, when="2026-02-11 18:00", current_location="Side St")
        self.assertIsNotNone(drive2.id)
        self.assertEqual(drive2.current_location, "Side St")
        expected_dt = datetime.strptime("2026-02-11 18:00", "%Y-%m-%d %H:%M")
        self.assertEqual(drive2.datetime, expected_dt)

        schedule = get_driver_schedule(driver.id)
        self.assertIsNotNone(schedule)
        self.assertGreater(len(schedule), 1)
        
    def test_create_resident_with_street(self):
        alice = Resident(username="alice2", password="pass", name="Alice", street="Main St")
        db.session.add(alice)
        db.session.commit()
        self.assertIsNotNone(alice.id)
        self.assertEqual(alice.username, "alice2")
        self.assertEqual(alice.name, "Alice")
        self.assertEqual(alice.street, "Main St")
        
        resident = get_resident(alice.id)
        self.assertIsNotNone(resident.id)
        self.assertEqual(resident.id, alice.id)
    
    #Resident views scheduled drive and creates stop request. Verify stop request is linked to correct drive and resident
    def test_stop_request_workflow(self):
        # Setup driver and resident
        driver = Driver(username="driver3", password="pass", status="Available")
        db.session.add(driver)
        db.session.commit()
        self.assertIsNotNone(driver.id)

        drive = create_drive(driver.id, when="2026-01-10 18:00", current_location="Main St")
        self.assertIsNotNone(drive.id)

        resident = Resident(username="resident3", password="pass", name="Alice", street="Main St")
        db.session.add(resident)
        db.session.commit()
        self.assertIsNotNone(resident.id)

        schedules = get_driver_schedule(driver.id)
        self.assertIsNotNone(schedules)
        for schedule in schedules:
            if resident.street == schedule.current_location:
                drive = schedule
        stop_request = resident.create_stop_request(drive, resident.street)
        self.assertIsNotNone(stop_request.id)
        self.assertEqual(stop_request.drive_id, drive.id)
        self.assertEqual(stop_request.requestee_id, resident.id)
    
    # When driver schedules a drive to a street, verify resident on that street sees drive in inbox 
    def test_resident_inbox_notification(self):
        resident = Resident(username="resident4", password="pass", name="Bob", street="Main St")
        db.session.add(resident)
        db.session.commit()

        driver = Driver(username="driver4", password="pass", status="Available")
        db.session.add(driver)
        db.session.commit()

        drive = create_drive(driver.id, when="2026-01-10 18:00", current_location="Main St")
        stop_request = resident.create_stop_request(drive, resident.street)
        inbox = get_resident_inbox(resident.id, resident.street)

        flag = False
        for s in inbox: #inbox contains a list of stop requests
            if s == stop_request: #check to see if the stop_request just made is in the inbox
                flag = True
        self.assertIsNotNone(inbox)
        self.assertGreater(len(inbox), 0)
        self.assertTrue(flag)


    # Driver updates status during active drive. Verify status change persists and is visible to residents viewing the drive
    def test_driver_status_update_visibility(self):
        resident = Resident(username="resident5", password="pass", name="Eve", street="Main St")
        db.session.add(resident)
        db.session.commit()

        driver = Driver(username="driver5", password="pass", status="Available")
        db.session.add(driver)
        db.session.commit()

        drive = create_drive(driver.id, when="2026-01-10 18:00", current_location="Main St")
        stop_request = resident.create_stop_request(drive, resident.street)
        driver.status = "On the way"
        db.session.commit()

        inbox = get_resident_inbox(resident.id, resident.street)
        self.assertIsNotNone(inbox)
        for request in inbox:
            if request.drive.driver_id == driver.id:
                status = resident.view_driver_status(driver)
                self.assertIsNotNone(status)
                self.assertEqual(status, "On the way")
     

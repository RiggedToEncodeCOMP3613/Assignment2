import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Driver, Drive, Resident
from App.controllers import (
    create_user,
    get_all_users_json,
    get_all_users,
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
    get_resident_inbox, 
    view_driver_status
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_create_user(self):
        user = User("john_doe", "password123") # mock data for unit test
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "john_doe") 
    
    # Calls the database 
    def test_get_user_by_username(self): 
        user = User("john_doe", "password123")
        user = get_user_by_username("john_doe")
        self.assertEqual(user.username, "john_doe")

    # Calls the database 
    def test_get_user_by_id(self):
        user = User("john_doe", "password123")
        user = get_user(1)
        self.assertEqual(user.id, 1)
        self.assertIsNotNone(user.username)
    
    # Calls the database 
    def test_get_all_users(self):
        user = User("john_doe", "password123")
        users = get_all_users()
        self.assertGreater(len(users), 0)
    
    def test_create_driver(self):
        driver = Driver(status="Available") # mock data for unit test
        self.assertIsNotNone(driver.id)
        self.assertEqual(driver.status, "Available")

    # Calls the database 
    def test_get_driver(self):
        driver = Driver(status="Available")
        driver = get_driver(1)
        self.assertEqual(driver.id, 1)
    
    def test_create_drive(self):
        drive = Drive(1, when="2026-01-10 18:00", current_location="Main St") # mock data for unit test
        self.assertIsNotNone(drive)
        self.assertEqual(drive.current_location, "Main St")
        
    # Calls the database    
    def test_get_driver_schedule(self):
        schedule = get_driver_schedule(1)
        self.assertIsNotNone(schedule)
    
    def test_create_resident(self):
        resident = Resident(name="Alice", street="Main St") # mock data for unit test
        self.assertEqual(resident.name, "Alice")
        self.assertEqual(resident.street, "Main St")
    
    # Calls the database 
    def test_get_resident(self):
        resident = get_resident(1)
        self.assertEqual(resident.id, 1)

    
    def test_create_stop_request(self):
        resident = Resident(name="Alice", street="Main St") # mock data for unit test
        drive = Drive(1, when="2026-01-10 18:00", current_location="Main St") # mock data for unit test
        stop_request = create_stop_request(resident.id, drive.id, "Main St") # mock data for unit test
        self.assertIsNotNone(stop_request)
        self.assertEqual(stop_request.street, "Main St")
    
    # Calls the database
    def test_get_resident_inbox(self):
        inbox = get_resident_inbox(1, street="Main St")
        self.assertIsNotNone(inbox)
    
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
        
        user = get_user_by_username(john.username)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, john.username)

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        self.assertIsNotNone(users_json)

        usernames = [user["username"] for user in users_json]
        self.assertIsNotNone(usernames)
        self.assertIn("bob", usernames)
        self.assertIn("john_doe", usernames)

    def test_create_driver_with_schedule(self):
        driver = create_driver(status="Available")
        self.assertIsNotNone(driver)
        self.assertEqual(driver.status, "Available")

        drive1 = create_drive(driver.id, when="2026-01-10 18:00", current_location="Main St")
        self.assertIsNotNone(drive1)
        self.assertEqual(drive1.current_location, "Main St")
        
        drive2 = create_drive(driver.id, when="2026-02-11 18:00", current_location="Side St")
        self.assertIsNotNone(drive2)
        self.assertEqual(drive2.current_location, "Side St")

        schedule = get_driver_schedule(driver.id)
        self.assertIsNotNone(schedule)
        self.assertGreater(len(schedule), 1)
        
    def test_create_resident_with_street(self):
        alice = create_resident(name="Alice", street="Main St")
        self.assertIsNotNone(alice)
        self.assertEqual(alice.name, "Alice")
        self.assertEqual(alice.street, "Main St")
        
        resident = get_resident(alice.id)
        self.assertIsNotNone(resident)
        self.assertEqual(resident.id, alice.id)
    
    #Resident views scheduled drive and creates stop request. Verify stop request is linked to correct drive and resident
    def test_stop_request_workflow(self):
        schedules = get_driver_schedule(1) # get the schedule of driver (list of existing Drives)
        self.assertIsNotNone(schedules)
        
        resident = get_resident(1) # get resident
        self.assertIsNotNone(resident)
        
        for schedule in schedules: # resident can see the streets and chooses the drive with their street to make a stop request
            if resident.street == schedule.current_location:
                drive = schedule
        
        stop_request = resident.create_stop_request(resident.id, drive.id, resident.street) #resident creates stop_request with their street
        self.assertIsNotNone(stop_request)
        self.assertEqual(stop_request.drive_id, drive.id)
        self.assertEqual(stop_request.requestee_id, resident.id)
    
    # When driver schedules a drive to a street, verify resident on that street sees drive in inbox (???)
    def test_resident_inbox_notification(self):
        resident = get_resident(1)
        self.assertIsNotNone(resident)
        inbox = get_resident_inbox(resident.id, resident.street) # check if inbox populated witt the stop_request resident created
        
        self.assertIsNotNone(inbox) # ensure inbox is not empty
        self.assertGreater(len(inbox), 0) # check if inbox has at least 1 stop_request

    # Driver updates status during active drive. Verify status change persists and is visible to residents viewing the drive
    def test_driver_status_update_visibility(self):
        resident = get_resident(1)
        self.assertIsNotNone(resident)

        driver = get_driver(1)
        self.assertIsNotNone(driver)
        driver.update_driver_status(status="On the way")
        # where is update_driver_status()

        inbox = get_resident_inbox(resident.id, resident.street)
        self.assertIsNotNone(inbox)

        d = inbox[0] # get a drive from the inbox

        for request in inbox: # get a drive from the inbox
            if request.drive.driver_id == driver.id: # if driver accepted request
                status = view_driver_status(driver) # check the driver's status
                self.assertIsNotNone(status)
                self.assertEqual(status, "On the way") # check if resident can see if the status updated

    # Driver updates location multiple times during drive. Verify all location updates persist with timestamps
    # create_driver(), create_drive(), update_current_location(), get_driver()
    #def test_driver_location_tracking(self):
        # update_current_location(): where is method
        	
    # Test full drive lifecycle: schedule, residents view, stop requests created, driver updates status, drive completed. Verify data correct at each stage
    # create_driver(), create_drive(), create_resident(), create_stop_request(), update_driver_status(), complete_drive()
    #def test_complete_drive_lifecycle(self):
        # update_driver_status(), complete_drive(): where are these methods

    # Only authenticated drivers can create and manage drives. Verify unauthorized attempts are rejected
    # authenticate(), create_driver(), create_drive()
    def test_authentication_driver_authorization(self):
        user = create_user("guy", "guypass")
        assert login("guy", "guynotpass") == None
        #is the method authenticate() or login()?

        drive = user.create_drive(user.id, when="2026-01-10 18:00", current_location="Main St") 
        self.assertIsNone(drive) # user cannot create_drive because not logged in
    
    # Only authenticated residents can create stop requests. Verify unauthorized attempts are rejected
    # authenticate(), create_resident(), create_stop_request()
    def test_authentication_resident_authorization(self):
        user = create_user("brock", "brockpass")
        assert login("brock", "brocknotpass") == None
        #is the method authenticate() or login()?

        stop_request = user.create_stop_request(user.id, 1, "Yellow St") 
        self.assertIsNone(stop_request) # user cannot create_stop_reuest because not logged in

    # User account is associated with driver profile. Verify driver actions traced back to user account
    # create_user(), create_driver(), link_user_driver()
    # def test_user_driver_association(self):
        # where is link method

    # User account is associated with resident profile. Verify resident actions traced back to user account
    # create_user(), create_resident(), link_user_resident()
    # def test_user_resident_association(self):
        # where is link method



'''
1. Resident want bread, he make a stop request.
2. A driver sees the stop request, and creates modifies his drive to fulfill said stop request
3. Resident should see in their inbox it is satisfy
'''        

import os
import re
from enum import Enum

import bs4
from requests import Session
from requests_toolbelt import MultipartEncoder


class PersonalDetails(Enum):
    EMP_NUMBER = 'txtEmpID'
    FIRST_NAME = 'txtEmpFirstName'
    MIDDLE_NAME = 'txtEmpMiddleName'
    LAST_NAME = 'txtEmpLastName'
    EMP_ID = 'txtEmployeeId'
    OTHER_ID = 'txtOtherID'
    LICENCE_NUMBER = 'txtLicenNo'
    LICENCE_DATE = 'txtLicExpDate'
    NIC_NUMBER = 'txtNICNo'
    SSN = 'txtSINNo'
    MARITAL_STATUS = 'cmbMarital'
    NATIONALITY = 'cmbNation'
    DOB = 'DOB'
    NICK_NAME = 'txtEmpNickName'
    MILITARY = 'txtMilitarySer'


class HRM():
    def __init__(self):
        self.url = "http://hrm-online.portnov.com/symfony/web/index.php"
        self.sess = Session()
        self.sess.headers.update({
                                     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'})

    def login(self, username='admin', password='password'):
        # Step 1: get the landing page - contains login form
        login_uri = '/auth/login'
        resp = self.sess.get(self.url + login_uri)

        # Step 2 : extract CSRF token
        soup = bs4.BeautifulSoup(resp.content, 'html5lib')
        result = soup.find('input', attrs={'name': '_csrf_token'})
        token = result['value']

        authenticate_uri = '/auth/validateCredentials'

        # Step 3: login by posting credentials + CSRF token
        login_data = {
            '_csrf_token': token,
            'txtUsername': username,
            'txtPassword': password
        }

        return self.sess.post(self.url + authenticate_uri, data=login_data)

    def add_employee(self, emp_id, first_name, last_name, img_file=None):
        # Step 1: get the add employee page - contains the form to add employee
        add_employee_uri = '/pim/addEmployee'
        resp1 = self.sess.get(self.url + add_employee_uri)

        # Step 2: extract CSRF token from add Employee
        # install html5lib package
        soup = bs4.BeautifulSoup(resp1.content, 'html5lib')
        token = soup.find('input', attrs={'name': '_csrf_token'})['value']

        file_name = os.path.basename(img_file)

        emp_data = {
            'firstName': first_name,
            'lastName': last_name,
            '_csrf_token': token,
            'employeeId': emp_id,  # has to be unique each time
            'empNumber': emp_id,
            'photofile': (file_name, open(img_file, 'rb'), 'image/jpeg')
            # rb means read as binary, text/plain for text file, its a tuple.
        }

        multipart_data = MultipartEncoder(fields=emp_data)

        # Step 3: add employee - posting new employee data + CSRF token
        self.sess.headers.update({'Content-Type': multipart_data.content_type})
        return self.sess.post(self.url + add_employee_uri, data=multipart_data)

    def get_employee_details(self, emp_id):
        """ Takes emp_id as a number, string or as full/partial url """
        num_id = str(emp_id) if str(emp_id).isdigit() else None
        if not num_id:
            match = re.match(r'.*/(\d+)', emp_id)
            num_id = match.group(1) if match else None
        return self.sess.get(self.url + '/pim/viewPersonalDetails/empNumber/' + num_id)

    def close(self):
        self.sess.close()

    def add_candidate(self, first_name, last_name, email, resume):
        # Step 1: get the add employee page - contains the form to add employee
        add_candidate_uri = '/recruitment/addCandidate/id/'
        resp = self.sess.get(self.url + add_candidate_uri)

        # Step 2: Extract CSRF token
        soup = bs4.BeautifulSoup(resp.content, 'html5lib')
        token = soup.find('input', attrs={'id': 'addCandidate__csrf_token'})['value']

        file_name = os.path.basename(resume)

        multipart_data = MultipartEncoder(
            fields={
                'addCandidate[_csrf_token]': token,
                'addCandidate[firstName]': first_name,
                'addCandidate[lastName]': last_name,
                'addCandidate[resume]': (file_name, open(resume, 'rb'), 'text/plain'),
                'addCandidate[appliedDate]': '05-27-2020',
                'addCandidate[email]': email
            }
        )

        self.sess.headers.update({'Content-Type': multipart_data.content_type})

        # Step 3: add the candidate  - posting the candidate data  + CSRF token
        return self.sess.post(self.url + add_candidate_uri, data=multipart_data)

    def update_employee_personal_details(self, emp_number, *args):
        prefix = 'personal[{0}]'

        resp = self.get_employee_details(emp_number)

        soup = bs4.BeautifulSoup(resp.content, 'html5lib')
        _csrf_token = soup.find(attrs={'name': 'personal[_csrf_token]'})['value']

        personal_details_data = {'personal[_csrf_token]': _csrf_token}
        for member in PersonalDetails:
            field_name = prefix.format(member.value)
            found = soup.find(attrs={'name': field_name})
            info = found.get('value', None)
            personal_details_data.update({field_name: info})

        for (member, value) in args:
            if member in PersonalDetails:
                personal_details_data.update({prefix.format(member.value): value})

        return self.sess.post(self.url + '/pim/viewEmployee/empNumber/' + str(emp_number), data=personal_details_data)

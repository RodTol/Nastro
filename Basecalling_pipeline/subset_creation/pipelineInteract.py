#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import requests
from requests.auth import HTTPBasicAuth

class Jenkins_trigger:

    def __init__(self): 
        #TODO mask the credentials
        self.jenkins_url='http://jenkins-sandbox.rd.areasciencepark.it:8080'
        self.username ="tolloi"
        self.password = "Alfredo95"
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

        #Get the Jenkins server info
        self._get_jenkins_info

    def _get_jenkins_info(self):
        # Create a session to persist the authentication cookies
        api_url = f"{self.jenkins_url}/me/api/json"

        try:
            # Fetch user information
            response = self.session.get(api_url)
            response.raise_for_status() 
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Jenkins: {e}")

        # Parse response JSON
        user_info = response.json()
        user_name = user_info.get('fullName', 'Unknown')
            
        try:
            # Fetch Jenkins version
            request = requests.Request('GET', self.jenkins_url)
            request.headers['X-Jenkins'] = '0.0'
            response = self.session.send(self.session.prepare_request(request))
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
            raise Exception("Error communicating with server[%s]" % self.url)

        # Parse response JSON
        jenkins_version = response.headers.get('X-Jenkins')
        print('Hello %s from Jenkins %s' % (user_name, jenkins_version))

    def _get_jenkins_crumb(self):
        crumb_url = f"{self.jenkins_url}/crumbIssuer/api/json"

        try:
            response = self.session.get(crumb_url)
            response.raise_for_status()
            crumb_data = response.json()
            return {crumb_data['crumbRequestField']: crumb_data['crumb']}
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get Jenkins crumb: {e}")   

    def stop_job(self, job_name, build_number):
        # Construct the URL to stop the build
        crumb_header = self._get_jenkins_crumb()
        # Note that job name must be correct (example: "Nastro/job/basecalling_pipeline/")
        stop_url = f'{self.jenkins_url}/job/{self.username}/job/{job_name}/{build_number}/stop'  
        print('Stop url:  ', stop_url)
        try:
        # Send the stop request
            response = self.session.post(stop_url, headers=crumb_header)
        
        # Check if the request was successful
            if response.status_code == 200:
                print('Build stopped successfully')
            else:
                print(f'Failed to stop the build. Status code: {response.status_code}')
                print('Response:', response.text)
        except requests.RequestException as e:
            print(f'An error occurred: {e}')

    def _get_job_folder(self, name):
        '''Return the name and folder (see cloudbees plugin)
        :param name: Job name, ``str``
        :returns: Tuple [ 'folder path for Request', 'Name of job without folder path' ]
        '''
        a_path = name.split('/')
        short_name = a_path[-1]
        folder_url = (('job/' + '/job/'.join(a_path[:-1]) + '/')
                      if len(a_path) > 1 else '')

        return folder_url, short_name


    def _build_job_url_for_start(self, job_name, token, parameters):
        folder_url, short_name = self._get_job_folder(job_name)
        base_url = self.jenkins_url + f'/{folder_url}job/{short_name}' + "/buildWithParameters"
        params_string = '&'.join([f"{key}={value}" for key, value in parameters.items()])

        url = f"{base_url}?{params_string}&token={token}"

        return url

    def start_job(self, job_name, token, parameters):
        
        #Trigger the build on jenkins
        build_url = self._build_job_url_for_start(job_name, token, parameters)
        print('Start url:  ', build_url)
        #print(build_url)
        crumb_header = self._get_jenkins_crumb()

        try:
            response = self.session.post(build_url, headers=crumb_header)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.RequestException as e:
            print(f"Error triggering build: {e}")
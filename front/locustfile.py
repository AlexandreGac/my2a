from locust import HttpUser, task, between

"""
Test the simultanate connexion of hundred of users with locust.
To launch the test enter >>locust in a terminal at the path my2a/front then go to http://localhost:8089 

Tried to test the generation of the PDF, but failed due to token problems.
"""


class My2AUser(HttpUser):
    host = "https://my2a.enpc.org/"
    wait_time = between(1, 3)  # 1 to 3 seconds

    @task
    def visit_homepage(self):
        # Visit the homepage
        response_homepage = self.client.get("https://my2a.enpc.org")
        if response_homepage.status_code == 200:
            print("Homepage loaded successfully")
        else:
            print(f"Failed to load homepage: {response_homepage.status_code}")

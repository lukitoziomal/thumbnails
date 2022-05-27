# Simple API view that allows user to upload images, create resized thumbnails and generate temporary links.

## Quickstart
Create a virtual environment to store your projects dependencies separately.

` pip install virtualenv `

` virtualenv venv `

This will create a new directory called ` venv `.

Clone or download this repository.

` git clone https://github.com/lukitoziomal/thumbnails.git `

Activate your virtual environment.

` path-to-venv\venv\Scripts\activate `

Install project dependencies.

` cd thumbnails `

` pip install -r requirements.txt `

Setup the database.

` py manage.py makemigrations `

` py manage.py migrate `

Setup initial plans. IMPORTANT: do it before creating superuser.

` py manage.py runscript setup_plans `

Now create superuser.

` py manage.py createsuperuser `

Run server.

` py manage.py runserver `


Admin can access ` all-images ` to see all user uploaded files and generate links. Normal user can only access ` user-images ` to view his images and do actions based on account plan.

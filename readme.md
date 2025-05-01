# Django Todos Application

## Requirements :

- Python (must be avalaible on your command line machine)

- Django version compatible with your python version

- Google Account

- PostgreSQL

- pgadmin4(Optional)

- vscode or other IDE

## Features of application

- 2-Factor Authentication

- Management of Todos List

- Responsive application

## Setup environment and use application

- setup your google account to allow it to send email see this link to do that : https://myaccount.google.com/apppasswords. <br>
  When you arrive on the link page your must create one application(todo_app for exemple) to get the `secret key` that you will use to send mail with google in your application.<br> This step is required to use application correctly.<br><br>
  **Very Important** : you must activate 2-step validation to use setup password application of google. for more information read this [help](https://support.google.com/mail/answer/185833?sjid=11845357661678490645-EU) on the section : `Create & use app passwords`

- After setup google account,create virtual env in the root of your project:

```cmd
   python -m venv .venv
```

<br> make sure that your python environment has not the name `.env`, because it is the name of the default environment that you will use in the future of this aplication.

- Clone the application in your project folder with link : [https://github.com/UlrichIvan/django_todos_list.git](https://github.com/UlrichIvan/django_todos_list.git)

- Create 4 files environment(.env, .env.local, .env.staging, .env.prod) and use the sample content file of `env.dist.sample` file at the root of this repository to fill `env.local, .env.staging, .env.prod` created,and use `env.sample` file to fill `.env` file created.

- To fill django `SECRET_KEY` use this [tool](https://djecrety.ir/) online.

- Create the database `todo_app` on your `local` or `staging` or `prod` environment database.

- make the migrations with django cli to create all necessaries tables to run application correctly.

```cmd
   python manage.py makemigrations
```

- Apply migrations with django cli

```cmd
   python manage.py migrate
```

- After migration created successfully, run application with django cli :

```cmd
   python manage.py runserver
```

- After running application, you can use it to manage your todo list with authentication.

if you have any questions or some needs, you can contact [me](https://www.linkedin.com/in/ulrich-chokomeny/) in linkedin platform by message.<br>

Thank you for your attention, and i am avalaible if you have an appreciation about this simple projet,thank you.

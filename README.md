# FAT CAT (An Expense and Income Tracker App)

## About
This web application is created using [**Django**](https://docs.djangoproject.com/en/4.1/), [**PostgreSQL**](https://www.postgresql.org/) and [**Bootstrap**](https://getbootstrap.com/). Put it simply, it is a finance expenses tracker app that supports CRUD operations. Aptly named Fat Cat, this web app includes a variety of features including, but not limited to:
- custom user registration and sign-in, password strength validation, forgot password and reset password with email feature.
- update user preferences and personal information. (base currency, username, email and password)
- interactive line, bar and pie charts to view expenses/income data.
- view recent activity feature.
- search bar. (by querying database using ajax search)
- sort income and expenses tables chronological and alphabetically.
- export data as a CSV/Excel file.

The web app also allows users to set their base currency and modify their usernames, email and password. I also customed the style of the Django admin page using CSS. 

**Challenges faced:** Being the first time I used [ChartJS](https://www.chartjs.org/docs/latest/) together with Django, I faced some trouble integrating them together and getting the data to render on the charts properly. Another issue was using Bootstrap's modal as a `<form>`, which was not rendering properly. However, using a modal form as opposed to redirecting users to another page was a deliberate decision I made as I believed this improves the user experience.  

**Video:** A short video demonstrating the features and usage of the web app is available at: https://www.youtube.com/watch?v=6OWLcNuER6I

**What's next for Fat Cat:** In future versions of the web app, I hope to integrate a currency conversion API that delivers real time exchange rates to reflect user's expenses and income accurately. This feature may come across as extremely relevant to people who own multi-currency bank accounts. Another feature of interest is to implement a filter function (in addition to the existing search bar and chronological sort) for better user experience.


## Getting Started

To get started, follow the steps below:

1. Install the following dependencies
- python 3.8.2, django 4.1,
- packages (using `pip install`): validate_email, xlwt, django-chartjs, python-dateutil, psycopg2
2. Export environmental variables in bash
- Database: `export` DB_NAME=expensesdb, DB_USER=postgres, DB_PASSWORD, DB_HOST=localhost
- Email: `export` EMAIL_HOST (e.g smtp.gmail.com. Check `settings.py` for more information.), EMAIL_HOST_USER (your email), EMAIL_HOST_PASSWORD (your email password)

*Note: I recommend to enter all environmental variables in a file and then export the file. Remember to use the `gitignore` command on the file to prevent leaking your email and password if you intend to upload your files on a public Github repo.*

## Running the App
Once all dependencies are installed, run the app (in development mode) in the terminal using `py manage.py runserver`. And you are all set! 

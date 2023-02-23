# Yatube Blog

This is a simple blogging web application built with Django, where users can create and publish posts, follow other users, comment on posts, and like them. 

## Installation

1. Clone the repository to your local machine using the command: 
```bash
git clone https://github.com/PavelFil98/Yatube_blog.git
```
2. Create a virtual environment using `venv` or `conda` and activate it.
3. Install the required dependencies by running the following command:
```bash
pip install -r requirements.txt
```
4. Apply the migrations to create the database:
```bash
python manage.py migrate
```
5. To run the application, use the following command:
```bash
python manage.py runserver
```

Then, navigate to `http://localhost:8000` in your web browser to see the home page of the Yatube blog.

## Features

- User registration and login.
- Creating and publishing blog posts.
- Following other users and viewing their posts.
- Commenting on posts and viewing comments.
- Liking posts and viewing the number of likes.

## Contributing

Contributions are always welcome! If you have any suggestions, bug reports, or feature requests, please feel free to create an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.


## Pixie: AI-Generated Image Repository

***Pixie*** is an innovative application designed to generate images through artificial intelligence using the Stable Diffusion API. With Pixie, users can easily create unique images and make them available for public use, contributing to a vast image bank accessible to all.

## Main Features

- Image Generation with AI: Use the Stable Diffusion API to generate high-quality, unique images.
- Public Image Library: Share your creations with the community, allowing others to use your images for a variety of purposes.
- User Management: Each user can manage their own images, including the choice of making them public or private.
- Performance and Scalability: Built with Flask, PostgreSQL and Nginx, guaranteeing a fast, secure and scalable application.

## Technologies Used

- Flask: Micro-web framework used to develop the application's backend, providing flexibility and efficiency.
- SQLAlchemy: A SQL toolkit and object relational mapping (ORM) library for Python, used to interact with the database using the Python language.
- PostgreSQL: Relational database management system used to store user information and their generated images.
- Nginx: Web server used to manage requests, increasing the application's performance and security.

## How it Works

- Account creation: Users register on the platform and create a personal account.
- Image generation: With just a few clicks, users can generate images using the Stable Diffusion API.
- Sharing: Users can choose to share their generated images, contributing to a public image bank.
- Use of Images: Images in the public bank can be accessed and used by anyone, facilitating the exchange and use of visual resources.

## Installation and Configuration

To install and configure Pixie locally, follow the instructions below:

1. Clone this repository:
``` bash
git clone https://github.com/viniciuslopesgit/Pixie.git
cd pixie
```
2. Set up the virtual environment and install the dependencies:
```
python3 -m venv menv
source venv/bin/activate
pip install -r requirements.txt
```
4. Configure the PostgreSQL database with the necessary credentials and apply the migrations:
```
flask db upgrade
```
6. Run application:
```
run app.py
```

## Contributing
Contributions are welcome! Feel free to open issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

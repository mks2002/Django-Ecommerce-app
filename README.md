


# Shoppify Ecommerce Application

Welcome to Shoppify, an ecommerce application built with Python, Django, Ajax, and Bootstrap.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Shoppify is a robust ecommerce application developed using Django framework. It offers a user-friendly interface for both customers and administrators, ensuring smooth content management and shopping experience.

## Features

- **Efficient Database Queries**: Utilized Django’s query sets and subqueries for efficient and intricate database searches.
- **Admin Dashboard**: Created a robust, user-friendly admin dashboard for streamlined content management.
- **Enhanced Security**: Implemented email verification and seamless user authentication features for enhanced security.
- **Forgot Password Mechanism**: Developed a secure ’Forgot Password’ mechanism for an enhanced user experience.
- **Real-time Updates**: Enabled real-time content updates through AJAX, ensuring a seamless shopping cart experience.
- **Order Status Checking**: Implemented real-time order status checking for easy administration and efficient order management.

## Setup

To set up the Shoppify project locally, follow these steps:

1. First fork the repository in your github account and then Clone the repository:

```bash
git clone https://github.com/your-username/shoppify.git
```

2. Navigate to the project directory:

```bash
cd shoppify
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Perform database migrations:

```bash
python manage.py migrate
```

5. Run the development server:

```bash
python manage.py runserver
```

6. Access the application at `http://localhost:8000` in your web browser.

## Usage

Once the application is set up, you can use the admin dashboard to manage products, orders, and customers efficiently. Customers can browse products, add them to the cart, and proceed to checkout seamlessly.

## Contributing

Contributions are welcome! If you'd like to contribute to Shoppify, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/new-feature`).
6. Create a new Pull Request.


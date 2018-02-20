# Catalog Project


## About
This project is a website that provides a list of best summer reads within a variety of authors.
Registered google users will have the ability to post, edit and delete items created by that user.

## Requirements

* Code editor - Atom
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [VirtualBox](https://www.virtualbox.org/)
* [Google Developer Account](https://console.developers.google.com/)

## Installation

1. Clone the vagrant machine from Udacity(https://github.com/udacity/fullstack-nanodegree-vm)
2. Place these project files in the catalog folder
3. Run following commands to setup Vagrant, 'vagrant up' and 'vagrant ssh' to log in to your Vagrant VM.
4. Move to your catalog folder, 'cd /vagrant/catalog'
5. Run following command to setup you database and test data, 'python database_setup.py' then 'python test_data.py'
6. Run the application with the following command: 'python application.py'
7. App will start running on configured port, open 'http://localhost:5000' on your browser to view the application.

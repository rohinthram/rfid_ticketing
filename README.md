# RFID based Bus Ticketing System

This repository contains the project files for 
**RFID based Bus Ticketing System** using Arduino and Python

![Setup-of-project](/assets/setup.jpg)

## Overview
- To develop a system to overcome the trivial ticketing system
- The existing ticketing system in busy is very *time consuming*, *need for hard cash* and *use of paper*
- Use of digital way makes ticketing hastle free
- Reduces the use of paper ticket that goes waste after the journey
- A website for users to check their travel data

## Working
- The user account for each passenger gets created by an ADMIN using the webpage, mainly the *RFID tag* comes from the TAG that the ADMIN gives each passenger
![sign-up page](/assets/webpage_signup.png)
- The user can login to the webpage to check details
![user-dashboard](/assets/webpage_user.png)
    - User details
    - The balance in the card
    - Block the Card if card gets missed
- At bus, the user can use the card to get in
![boarding-bus](/assets/show_id.jpg)
- The driver changes updates the location of the bus in the database, hence when passenger gets down fare is calculated
![deboarding-bus](/assets/thank_you.jpg)

## Tech Stack
- Arduino: for programming the hardware
    - ESP32 interfaced with RFID reader and LCD display and a servo motor to mimic the gate/door
- Python: to manage the user and backend processing related to ticketing; Using flask framework
- Hosted using pythonanywhere.com
- More technical hints at [tech_readme.md](tech_readme.md)

## Future Work
- Updating location dynamicallys
- Make webpage UI better

---

If this inspires you in building your project, feel free to cite this repo

---
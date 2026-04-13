#  ABB GoFa Robot TCP Control

This project implements TCP/IP communication between a Python client and an ABB GoFa collaborative robot using RAPID.

##  Features

- TCP socket communication
- Custom command protocol
- Robot motion control:
  - MoveJ (joint motion)
  - MoveL (linear motion)
- Read TCP position
- Gripper control (digital I/O)
- Quaternion-based orientation

##  Architecture

Python (Client) ↔ TCP Socket ↔ ABB Robot (RAPID Server)

##  Command Protocol

| Command | Description |
|--------|------------|
| READ | Get current TCP pose |
| MOVEJ,x,y,z,q1,q2,q3,q4 | Joint movement |
| MOVEL,x,y,z,q1,q2,q3,q4 | Linear movement |
| IOONN | Close gripper |
| IOOFF | Open gripper |

## 📂 Project Structure










Author
Teo Bratkovic
Hackathon 2026 project
import socket
import time
import struct

#BINARNA KODA
CMD_MOVEJ = 1
CMD_MOVEL = 2



ROBOT_IP = "192.168.125.1"
ROBOT_PORT = 5000

#*************************** CONECTION ***********************************
def connect_robot():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.settimeout(15)
    s.connect((ROBOT_IP, ROBOT_PORT))

    handshake = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")
    print("Robot says:", handshake)

    return s


#****************************   READ POSITION  TCP *************************************
def read_tcp_pose(s):
    s.sendall(b"READ\0")
    data = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")
    print("Raw TCP:", data)

    if data == "NOK":
        raise RuntimeError("Robot returned NOK on READ")

    values = list(map(float, data.split(",")))
    if len(values) != 7:
        raise ValueError(f"Expected 7 values, got {len(values)}")

    tcp_xyz = values[0:3]
    tcp_quat = values[3:7]
    return tcp_xyz, tcp_quat



# ***********************************  MOVEMENT *************************************

def move_robotJ(s, x, y, z, q1, q2, q3, q4):
    payload = struct.pack(">B7f", CMD_MOVEJ, x, y, z, q1, q2, q3, q4)
    s.sendall(payload)
    response = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")
    print("MOVEJ:", response)


def move_robotL(s, x, y, z, q1, q2, q3, q4):
    payload = struct.pack(">B7f", CMD_MOVEL, x, y, z, q1, q2, q3, q4)
    s.sendall(payload)
    response = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")
    print("MOVEL:", response)



def home_position(s):
    move_robotJ(
        s,
        x=595.47,
        y=0,
        z=500,
        q1=0.5,
        q2=0,
        q3=0.866,
        q4=0
    )



#******************************     GRIPPER ***********************************

def GripperOpen(s):
    s.sendall(b"IOOFF\0")
    response = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")          #s.recv(1024) blokirajoč klic — program stoji tam, dokler iz robota ne pride odgovor ali pa povezava ne pade.
    print("GripperOpen response:", response)

    #if response != "OK_prijemalo_odprto":
       # raise RuntimeError(f"Gripper failed: {response}")


def GripperClose(s):
    s.sendall(b"IOONN\0")        # POŠLJE SPOROČILO ROBOTU
    response = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")          #s.recv(1024) blokirajoč klic — program stoji tam, dokler iz robota ne pride odgovor ali pa povezava ne pade.
    print("GripperClose response:", response)

    #if response != "OK_prijemalo_zaprto":
       # raise RuntimeError(f"Gripper failed: {response}")








#**************************** VISOK NIVO ********************************
#   naj bo tocka tako definirana:    tocka  = (x, y, z, q1, q2, q3, q4)

tocka_nad_pobiranjem = (453.12, -224.88, 346.89, 0.00045, 0.2323, -0.97265, 0.0001)
tocka_pobiranje = (453.12, -224.88, 396.46, 0.00045, 0.2323, -0.97265, 0.0001)
tocka_nad_odlaganjem = (453.12, -224.88, 457.38, 0.00315, -0.23379, 0.97229, -0.00066)
tocka_odlaganje = (435.93, 151.10, 362.03, 0.00315, -0.23379, 0.97229, -0.00066)

def move_to_point_Joints(s, zeljena_tocka):
   
   

    if len(zeljena_tocka) != 7:
        raise ValueError("Expected 7 values (x,y,z,q1,q2,q3,q4)")

    x, y, z, q1, q2, q3, q4 = zeljena_tocka

    move_robotJ(
        s,
        x=x,
        y=y,
        z=z,
        q1=q1,
        q2=q2,
        q3=q3,
        q4=q4
    )


def move_to_point_Linear(s, zeljena_tocka):
    """
    Premik robota z MoveL (linearno v prostoru)

    zeljena_tocka: (x, y, z, q1, q2, q3, q4)
    """

    if len(zeljena_tocka) != 7:
        raise ValueError("Expected 7 values (x,y,z,q1,q2,q3,q4)")

    x, y, z, q1, q2, q3, q4 = zeljena_tocka

    move_robotL(
        s,
        x=x,
        y=y,
        z=z,
        q1=q1,
        q2=q2,
        q3=q3,
        q4=q4
    )


def pobiranje_iz_znane_lege (s):
    
    home_position(s)
    move_to_point_Joints(s, tocka_nad_pobiranjem)
    move_to_point_Linear(s, tocka_pobiranje)
    GripperClose(s)
    move_to_point_Linear(s, tocka_nad_pobiranjem)
    move_to_point_Joints(s, tocka_nad_odlaganjem)
    move_to_point_Linear(s, tocka_odlaganje)
    GripperOpen(s) 
    move_to_point_Joints(s, tocka_nad_odlaganjem)
    home_position(s)









if __name__ == "__main__":
    s = connect_robot()

    #move_robotJ(s, x=595.47, y=0, z=500, q1=0.5, q2=0, q3=0.866, q4=0)
    #move_robotJ(s, x=595.47, y=0, z=400, q1=0.5, q2=0, q3=0.866, q4=0)

   

    move_robotJ(s, x=453.89, y=151.12, z=458.38, q1=0.0315, q2=-0.23379, q3=0.97229, q4=0.00066)



    s.close()






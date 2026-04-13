import socket
import time

#USE YOUR COSTUM SETTINGS
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

def move_robotJ(s, x, y, z, q1, q2, q3, q4,):
    robtarget_str = (
        f"{x},{y},{z},"
        f"{q1},{q2},{q3},{q4}"
    )

    cmd = f"MOVEJ,{robtarget_str}\0"  #\0  če ni tega, se ti ne pošlje celoten string (čuvaj)
    print("Sending:", cmd)

    s.sendall(cmd.encode()) #socket.sendall() pošilja byte podatke

    #s.settimeout(10)
    response = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")
    print("Move response:", response)
    

    """ DEBUG help
    if response != "OK":    
        raise RuntimeError(f"Move failed: {response}")
    """

def move_robotL(s, x, y, z, q1, q2, q3, q4):
    robtarget_str = (
        f"{x},{y},{z},"
        f"{q1},{q2},{q3},{q4}"
       
    )

    cmd = f"MOVEL,{robtarget_str}\0"     

    print("Sending:", cmd)

    s.sendall(cmd.encode())

    print("dolžina_poslanega_stringa",len(cmd))

    #s.settimeout(20)
    response = s.recv(1024).decode(errors="ignore").strip("\x00\r\n ")
    print("Move response:", response)

    """ DEBUG help
    if response != "OK":    
        raise RuntimeError(f"Move failed: {response}")
    """





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
#   naj bo tocka tako definirana:    tocka  = (x, y, z, q1, q2, q3, q4), position + quaternions


def move_to_point_Joints(s, zeljena_tocka):
    if len(zeljena_tocka) != 7:
        raise ValueError("Expected 7 values (x,y,z,q1,q2,q3,q4)")

    x, y, z, q1, q2, q3, q4 = zeljena_tocka

    move_robotJ( s, x=x, y=y, z=z, q1=q1, q2=q2, q3=q3, q4=q4)


def move_to_point_Linear(s, zeljena_tocka):
    if len(zeljena_tocka) != 7:
        raise ValueError("Expected 7 values (x,y,z,q1,q2,q3,q4)")

    x, y, z, q1, q2, q3, q4 = zeljena_tocka

    move_robotL(s, x=x, y=y, z=z, q1=q1, q2=q2, q3=q3, q4=q4)











if __name__ == "__main__":
    s = connect_robot()

    #example
    #move_robotJ(s, x=453.89, y=151.12, z=458.38, q1=0.0315, q2=-0.23379, q3=0.97229, q4=0.00066)

    

    s.close()






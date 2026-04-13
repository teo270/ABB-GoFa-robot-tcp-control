

def moveJ_robot(s, x, y, z, q1, q2, q3, q4, cf1=0, cf4=0, cf6=0, cfx=0):
    robtarget_str = (
        f"[[{x},{y},{z}],"
        f"[{q1},{q2},{q3},{q4}],"
        f"[{cf1},{cf4},{cf6},{cfx}],"
        f"[9E9,9E9,9E9,9E9,9E9,9E9]]"
    )
    print(robtarget_str)

    cmd = f"MOVE,{robtarget_str}\0"     #ABB obravnava \0 kot konec stringa bolj predvidljivo
                                        #na začetek prilepi MOVE,
    print("Sending:", cmd)


def moveJ_robot1(s, x, y, z, q1, q2, q3, q4, cf1=0, cf4=0, cf6=0, cfx=0):
    robtarget_str = (
        f"[[{x},{y},{z}],"
        f"[{q1},{q2},{q3},{q4}],"
        f"[{cf1},{cf4},{cf6},{cfx}],"
        )
    print(len(robtarget_str))
    cmd = f"MOVE,{robtarget_str}\0"     #ABB obravnava \0 kot konec stringa bolj predvidljivo
    print(len(robtarget_str))           
    print("Sending:", cmd)


def move_robotJ2(s, x, y, z, q1, q2, q3, q4,):
    robtarget_str = (
        f"{x},{y},{z},"
        f"{q1},{q2},{q3},{q4}"   )
    print(len(robtarget_str))

    cmd = f"MOVEJ,{robtarget_str}\0"     #ABB obravnava \0 kot konec stringa bolj predvidljivo
    print(len(robtarget_str))           
    print("Sending:", cmd)


if __name__ == "__main__":
    s =1
    
    move_robotJ2(
       s,
        x=450.0,
        y=0,
        z=500,
        q1=1,
        q2=0,
        q3=0,
      q4=0
   )
    




    

    
    

    

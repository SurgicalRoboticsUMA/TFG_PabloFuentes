#!/usr/bin/env python

import rospy
import math
import numpy as np
from std_msgs.msg import String
from std_msgs.msg import Float64MultiArray as FM
from pytransform3d.rotations import matrix_from_axis_angle 
from pytransform3d.rotations import axis_angle_from_matrix

i = 0
xi = 0
yi = 0
zi = 0
ox = 0
oy = 0
oz = 0
theta = 1
z = 0
Dt = 0.3
fi = 0.5
Pf = 0
Pt = 0
Ph1 = 0
Ph2 = 0
Ph3 = 0
Pd = 0
Rh = np.matrix([[1, 1, 1],[1, 1, 1],[1, 1, 1]])
Ks = 1.0
Ptn = 0
zn = 0
ro = 0
Pn = 0

def callback1(data):
    global xi, yi, zi, ox, oy, oz

    #Posicion y orientacion actual del robot
    xi = data.data[0]
    yi = data.data[1]
    zi = data.data[2]
    ox = data.data[3]
    oy = data.data[4]
    oz = data.data[5]

    rate = rospy.Rate(10)
    #rate.sleep()

def conversion():
    rospy.init_node('conversion', anonymous=True)
    pub = rospy.Publisher('/UR3_1/inputs/move_pose', FM, queue_size=10)
    rospy.Subscriber("UR3_1/outputs/pose", FM, callback1)
    #rospy.Subscriber('phantom', String, callback2)
    rate = rospy.Rate(10) # 10hz

    while not rospy.is_shutdown():
        
        #Introducimos el incremento de posiscion que queremos en cada eje
        Ph1 = float(raw_input("Introduce Ph1: "))
        Ph2 = float(raw_input("Introduce Ph2: "))
        Ph3 = float(raw_input("Introduce Ph3: "))
        #Ph = 0.05

        #Esto es para que se realicen los calculos solo en caso de introducir valores
        if not (Ph1 == 0):
            
            rate.sleep()
            #Convertimos la orientacion de la herramienta en matriz de orientacion para obtener
            #la direccion en el eje z
            angle = math.sqrt(ox*ox + oy*oy + oz*oz)
            axis = [ox/theta, oy/theta, oz/theta]

            a = np.hstack((axis, (angle,)))
            Rm = matrix_from_axis_angle(a)
            x = Rm[0]
            y = Rm[1]
            z = Rm[2]

            #Obtenemos el punto de fulcro y la posicion de la punta
            P = [xi, yi, zi]
            Pf = P + fi*Dt*z
            Pt = P + Dt*z

            #Nueva posicion de la punta con el incremento del Phantom
            Pd = Rh*Ks*np.array([[Ph1], [0], [0]])
            #Ptn = Pt + np.transpose(Pd)
            Ptn = Pt + [Ph1, Ph2, Ph3]

            #Nueva direccion en el eje z de la herramienta
            zn = Pf - Ptn

            #Distancia del punto de fulcro a la nueva posicion de la pinza
            Mzn = math.sqrt(zn[0]*zn[0] + zn[1]*zn[1] + zn[2]*zn[2])
            ro = Dt - Mzn

            #Nueva posicion del efector finalcdel robot
            Pn = Pf + ro*zn/Mzn
            
            Rm[2] = -zn
            r = Pn-Ptn
            print(math.sqrt(r[0]*r[0] + r[1]*r[1] + r[2]*r[2]))
            #a = axis_angle_from_matrix(Rm)
            #orientacion = [a[0]*a[3], a[1]*a[3], a[2]*a[3]]
            pose = FM()
            pose.data = [Pn[0], Pn[1], Pn[2], zn[0], zn[1], zn[2]]

            pub.publish(pose)

    rate.sleep()

    rospy.spin()

if __name__ == '__main__':
    try:
        conversion()
    except rospy.ROSInterruptException:
        pass

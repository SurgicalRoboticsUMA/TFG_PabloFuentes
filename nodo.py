#!/usr/bin/env python

import rospy
import math
import numpy as np
from std_msgs.msg import String
from std_msgs.msg import Float64MultiArray as FM
from pytransform3d.rotations import matrix_from_axis_angle 
from pytransform3d.rotations import axis_angle_from_matrix
from pytransform3d.rotations import matrix_from_euler_zyx

i = 0
j = 0
xi = 0
yi = 0
zi = 0
ox = 0
oy = 0
oz = 0
theta = 0
Dt = 0
Pf = 0
Pt = 0
Ph1 = 0
Ph2 = 0
Ph3 = 0
Ptn = 0
zn = 0
ro = 0
Pn = 0
iteracion = False


def callback1(data):
    global xi, yi, zi, ox, oy, oz

    #Recibimos la posicion y orientacion actual del robot
    xi = data.data[0]
    yi = data.data[1]
    zi = data.data[2]
    ox = data.data[3]
    oy = data.data[4]
    oz = data.data[5]

    rate = rospy.Rate(10)
    #rate.sleep()

def callback2(data):
    global vector, IP, fulcro, orientacion, longitud

    #Recibimos valores de configuracion de la interfaz y los separamos
    vector = data.data.split()

    fulcro = float(vector[0])
    longitud = float(vector[1])

def callback3(data):
    global Ph1,Ph2,Ph3,iteracion

    #Recibimos incrementos para mover la pinza
    Ph1 = data.data[0]
    Ph2 = data.data[1]
    Ph3 = data.data[2]

    #La variable iteracion nos servira para mover el robot en caso de que sea True
    iteracion = True

def eulerZYZ(v):
    global M

    #Esta funcion va a crear la matriz de orientacion para nuestro robot
    M = [[math.cos(v[0])*math.cos(v[1])*math.cos(v[2]) - math.sin(v[0])*math.sin(v[2]), -math.cos(v[0])*math.cos(v[1])*math.sin(v[2]) - math.sin(v[0])*math.cos(v[2]), math.cos(v[0])*math.sin(v[1])],
        [math.sin(v[0])*math.cos(v[1])*math.cos(v[2]) + math.cos(v[0])*math.sin(v[2]), -math.sin(v[0])*math.cos(v[1])*math.sin(v[2]) + math.cos(v[0])*math.cos(v[2]), math.sin(v[0])*math.sin(v[1])],
        [-math.sin(v[1])*math.cos(v[2]), math.sin(v[1])*math.sin(v[2]), math.cos(v[1])]]
    return M


def conversion():
    #Iniciamos el nodo y declaramos las suscripciones y publicaciones de topics
    rospy.init_node('conversion', anonymous=True)
    pub = rospy.Publisher('/UR3_1/inputs/move_pose', FM, queue_size=10)
    rospy.Subscriber("UR3_1/outputs/pose", FM, callback1)
    rospy.Subscriber("configuracion", String, callback2)
    rospy.Subscriber("movimiento", FM, callback3)
    rate = rospy.Rate(10) # 10hz

    while not rospy.is_shutdown():

        global iteracion

        #Si no hemos recibido ningun dato de movimiento no movemos el robot
        if (iteracion == True):

            print("NUEVO MOVIMIENTO")

            iteracion = False
            global j,ro,longitud
            Dt = longitud

            #-------------Vamos a transformar la orientacion recibida del robot--------------------
            #-------------en otra forma de orientacion que podemos manejar mas adelante------------
            
            #Primero calculamos el ANGULO y el EJE del vector de orientacion que recibimos 
            angle = math.sqrt(ox*ox + oy*oy + oz*oz)
            axis = [ox/angle, oy/angle, oz/angle]

            #Creamos una matriz de orientacion a partir del angulo y el eje anteriores
            a = np.hstack((axis, (angle,)))
            Rm = matrix_from_axis_angle(a)

            #Obtenemos el Eje Z de nuestra matriz, que es el que necesitamos para los calculos
            z = Rm[2]
            #Guardamos la posicion del robot en la variable P
            P = [xi,yi,zi]

            #-------------Una vez tenemos posicion y orientacion vamos a calcular la nueva--------------------
            #-------------posicion y orientacion segun el movimiento que queremos para la herramienta------------
            
            #Para la primera vez que realizamos las operaciones vamos a tomar
            #una serie de valores determinados
            if(j == 0):
                fi = float(fulcro/Dt) #Calculamos fi con el valor inicial recibido por la interfaz
                Pf = P + fi*Dt*z #El punto de fulcro lo calculamos al principio y no cambia
                print(Pf)

            #La posicion inicial de la herramienta se calcula a partir de los valores de posicion del robot mas la orientacion
            Pt = P + Dt*z

            #Nueva posicion de la punta con el incremento del Phantom
            Ptn = [Pt[0]+Ph1, Pt[1]+Ph2, Pt[2]+Ph3]

            #Nueva direccion en el eje z de la herramienta
            zn = Pf - Ptn

            #Distancia del punto de fulcro a la nueva posicion de la pinza
            Mzn = math.sqrt(zn[0]*zn[0] + zn[1]*zn[1] + zn[2]*zn[2])
            ro = Dt - Mzn

            #Nueva posicion del efector final del robot
            Pn = Pf + ro*zn/Mzn

            # El eje Z ya lo tnemos, pero lo hacemos unitario
            znn = [-zn[0]/Mzn, -zn[1]/Mzn, -zn[2]/Mzn]


            #-------------Para calcular la orientacion vamos a calcular los angulos de Euler--------------------
            #-------------a partir del eje Z de la matriz, el cual ya tenemos, y una vez tengamos---------------
            #-------------los amgulos, llamamos a la funcion que nos calcula la matriz de orientacion-----------

            b = math.atan2(math.sqrt(znn[0]**2 + znn[1]**2), znn[2])
            a = 0
            g = math.atan2((znn[1]/math.sin(b)),(-znn[0]/math.sin(b)))

            M = eulerZYZ([a,b,g])

            #Pasamos la orientacion a axis-angle, que es la que entiende nuestro simulador
            a = axis_angle_from_matrix(M)
            orientacion = [a[0]*a[3], a[1]*a[3], a[2]*a[3]]

            r = Pn-Ptn
            print("Incremento", [Ph1, Ph2, Ph3])
            print(" ")
            print('Nueva posicion efector Pn', Pn)
            print('Nueva posicion herramienta Ptn', Ptn)
            print(' ')
            print("Comprobaciones")
            print(' ')
            print('Actual posicion herramienta Pt', Pt) 
            print('Longitud herramienta Dt', math.sqrt(r[0]*r[0] + r[1]*r[1] + r[2]*r[2]))
            print(' ')
            print(' ')
        
            #Creamos la variable que contiene la posicion y orientacion que le vamos a dar a nuestro robot
            pose = FM()
            pose.data = [Pn[0], Pn[1], Pn[2], orientacion[0], orientacion[1], orientacion[2]]
            #pose.data = [Pn[0], Pn[1], Pn[2], ox, oy, oz]

            #Publicamos la pose
            pub.publish(pose)

            #Aumentamos la iteracion
            j = j+1

    rate.sleep()

    rospy.spin()

if __name__ == '__main__':
    try:
        conversion()
    except rospy.ROSInterruptException:
        pass

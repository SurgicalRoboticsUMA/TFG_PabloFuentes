#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Float64MultiArray as FM
from Tkinter import *
root = Tk()


fulcro = StringVar()
longitud = StringVar()
ejex = StringVar()
ejey = StringVar()
ejez = StringVar()
x = 0
y = 0
z = 0

miFrame = Frame(root, width = 500, height = 400)
miFrame.pack()

def interfaz():
    rospy.init_node('interfaz', anonymous=True)
    pub = rospy.Publisher("configuracion", String, queue_size=30)
    pub1 = rospy.Publisher("movimiento", FM, queue_size=30)
    rate = rospy.Rate(10) # 10hz

    while not rospy.is_shutdown():

        #--------------CONFIGURACION----------------------

        Titulo1 = Label(miFrame, text = "CONFIGURACION", font = 20)
        Titulo1.grid(row = 0, column = 0, columnspan=4, pady = 20)

        PFentry = Entry(miFrame, textvariable=fulcro)
        PFentry.grid(row = 2, column = 1, padx = 10, pady = 10)

        PFLabel = Label(miFrame, text = "Punto de fulcro", font = 12)
        PFLabel.grid(row = 2, column = 0, padx = 10, pady = 10)

        LHentry = Entry(miFrame, textvariable=longitud)
        LHentry.grid(row = 4, column = 1, padx = 10, pady = 10)

        LHLabel = Label(miFrame, text = "Longitud herramienta", font = 12)
        LHLabel.grid(row = 4, column = 0, padx = 10, pady = 10)

        def variables():
            global configuracion

            configuracion = fulcro.get() + " " + longitud.get()

            pub.publish(configuracion)
            confifuracion = ""

        enviar = Button(miFrame, text="enviar", command=variables)
        enviar.grid(row=5, column=1)

        #--------------MOVIMIENTO----------------------

        Titulo2 = Label(miFrame, text = "MOVIMIENTO", font = 20)
        Titulo2.grid(row = 0, column = 10, columnspan=4, pady = 20)

        def Sumx():
            global x
            x = x + 0.01
            e = str(x)
            ejex.set(x)

        def Resx():
            global x
            x = x - 0.01
            e = str(x)
            ejex.set(x)

        def Sumy():
            global y
            y = y + 0.01
            e = str(y)
            ejey.set(y)

        def Resy():
            global y
            y = y - 0.01
            e = str(y)
            ejey.set(y)

        def Sumz():
            global z
            z = z + 0.01
            e = str(z)
            ejez.set(z)

        def Resz():
            global z
            z = z - 0.01
            e = str(z)
            ejez.set(z)

        #----------EjeX------------

        Ejex = Label(miFrame, text = "x", font = 8)
        Ejex.grid(row = 2, column = 10, padx = 5, pady = 5)

        XEntry = Entry(miFrame, textvariable=ejex)
        XEntry.grid(row = 2, column = 12, padx = 10, pady = 10)

        Izquierdax = Button(miFrame, text="<---", command=Resx)
        Izquierdax.grid(row=2, column=11)

        Derechax = Button(miFrame, text="--->", command=Sumx)
        Derechax.grid(row=2, column=13)

        #----------EjeY------------

        Ejey = Label(miFrame, text = "y", font = 8)
        Ejey.grid(row = 3, column = 10, padx = 5, pady = 5)

        YEntry = Entry(miFrame, textvariable=ejey)
        YEntry.grid(row = 3, column = 12, padx = 10, pady = 10)

        Izquierday = Button(miFrame, text="<---", command=Resy)
        Izquierday.grid(row=3, column=11)

        Derechay = Button(miFrame, text="--->", command=Sumy)
        Derechay.grid(row=3, column=13)

        #----------EjeZ------------

        Ejez = Label(miFrame, text = "z", font = 8)
        Ejez.grid(row = 4, column = 10, padx = 5, pady = 5)

        ZEntry = Entry(miFrame, textvariable=ejez)
        ZEntry.grid(row = 4, column = 12, padx = 10, pady = 10)

        Izquierdaz = Button(miFrame, text="<---", command=Resz)
        Izquierdaz.grid(row=4, column=11)

        Derechaz = Button(miFrame, text="--->", command=Sumz)
        Derechaz.grid(row=4, column=13)

        ex = str(x)
        ey = str(y)
        ez = str(z)
        ejex.set(ex)
        ejey.set(ey)
        ejez.set(ez)

        def movimiento():
            global x,y,z

            movimiento = FM()
            
            x = float(ejex.get())
            y = float(ejey.get())
            z = float(ejez.get())

            movimiento.data = [x,y,z]
            print(movimiento.data)
            pub1.publish(movimiento)
            x = 0
            y = 0
            z = 0
            rate.sleep()
            ex = str(x)
            ey = str(y)
            ez = str(z)
            ejex.set(ex)
            ejey.set(ey)
            ejez.set(ez)
            movimiento.data = [x,y,z]

        enviar1 = Button(miFrame, text="enviar", command=movimiento)
        enviar1.grid(row=5, column=12)

        root.mainloop()

if __name__ == '__main__':
    try:
        interfaz()
    except rospy.ROSInterruptException:
        pass

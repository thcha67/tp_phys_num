#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TP reconstruction TDM (CT)
# Prof: Philippe Després
# programme: Dmitri Matenine (dmitri.matenine.1@ulaval.ca)


# libs
import numpy as np
import time
import matplotlib.pyplot as plt

# local files
import geo as geo
import util as util
import CTfilter as CTfilter

## créer l'ensemble de données d'entrée à partir des fichiers
def readInput():
    # lire les angles
    [nbprj, angles] = util.readAngles(geo.dataDir+geo.anglesFile)

    print("nbprj:",nbprj)
    print("angles min and max (rad):")
    print("["+str(np.min(angles))+", "+str(np.max(angles))+"]")

    # lire le sinogramme
    [nbprj2, nbpix2, sinogram] = util.readSinogram(geo.dataDir+geo.sinogramFile)

    if nbprj != nbprj2:
        print("angles file and sinogram file conflict, aborting!")
        exit(0)

    if geo.nbpix != nbpix2:
        print("geo description and sinogram file conflict, aborting!")
        exit(0)

    return [nbprj, angles, sinogram]


## reconstruire une image TDM en mode rétroprojection
def laminogram():
    
    [nbprj, angles, sinogram] = readInput()
    # initialiser une image reconstruite
    image = np.zeros((geo.nbvox, geo.nbvox))

    mid_ray = geo.nbpix/2 # indice du rayon central
    mid_vox = geo.nbvox/2 # indice du voxel central en x et en y

    # "etaler" les projections sur l'image
    # ceci sera fait de façon "voxel-driven"
    # pour chaque voxel, trouver la contribution du signal reçu
    for j in range(geo.nbvox): # colonnes de l'image
        print("working on image column: "+str(j+1)+"/"+str(geo.nbvox))
        for i in range(geo.nbvox): # lignes de l'image
            for a in range(0, len(angles), 1):

                angle = angles[a]
                proj = sinogram[a]

                # déterminer si le rayon est dirigé vers la gauche ou la droite
                # l'algorithme est fait pour les rayons dirigés vers la gauche
                # on peut corriger à la fin pour les rayons dirigés vers la droite
                ray_dir = "left" if angle < np.pi else "right"

                # angle entre 0 et pi
                angle %= np.pi

                # position en voxels relative au centre de la grille de reconstruction
                current_vox_x = j - mid_vox
                current_vox_y = mid_vox - i

                # paramètre d'une droite passant par le voxel courant et la pente du rayon actuel
                m = np.tan(angle + np.pi/2)
                b = current_vox_y - m * current_vox_x

                # vecteur perpendiculaire à la droite mx+b et allant vers le centre de la grille
                perp_vector = [m*b/(m**2 + 1), -b/(m**2 + 1)]

                # norme et angle du vecteur perpendiculaire
                norm_to_center = np.linalg.norm(perp_vector)
                angle_to_center = np.arctan2(perp_vector[1], perp_vector[0])

                # décalage en pixels (détecteur) à partir du centre du détecteur pour avoir le rayon
                # croisant le voxel courant
                if np.isnan(angle_to_center): # si le courant est au centre de la grille, le vecteur est nul
                    ray_index = mid_ray
                
                else: # on ajuste le décalage en fonction de si le vecteur perpendiculaire
                    # pointe dans la même direction que le l'axe du détecteur ou non
                    # Si les angles sont opposés, le décalage doit être inversé 
                    # (sens contraire de t dans la figure 2 de l'énoncé)

                    n_ray_shift = norm_to_center * geo.pixsize/geo.voxsize

                    if int(angle_to_center) == int(angle):
                        factor = 1
                    else:
                        factor = -1
                    
                    if ray_dir == "right": # si le rayon est dirigé vers la droite (angle initial > pi avant le modulo)
                                        # on flip l'image dans les deux axes pour garder le même algorithme
                        i = geo.nbvox - i - 1
                        j = geo.nbvox - j - 1
                    
                    ray_index = int(mid_ray + n_ray_shift * factor)

                image[i, j] += proj[ray_index]


    util.saveImage(image, "lam")


## reconstruire une image TDM en mode retroprojection filtrée
def backproject():
    
    [nbprj, angles, sinogram] = readInput()
    
    # initialiser une image reconstruite
    image = np.zeros((geo.nbvox, geo.nbvox))
    
    ### option filtrer ###
    CTfilter.filterSinogram(sinogram)
    ######
    
    # "etaler" les projections sur l'image
    # ceci sera fait de façon "voxel-driven"
    # pour chaque voxel, trouver la contribution du signal reçu
    for j in range(geo.nbvox): # colonnes de l'image
        print("working on image column: "+str(j+1)+"/"+str(geo.nbvox))
        for i in range(geo.nbvox): # lignes de l'image
            for a in range(len(angles)):
                pass
                #votre code ici
               #pas mal la même chose que prédédemment
            #mais avec un sinogramme qui aura été préalablement filtré
    
    util.saveImage(image, "fbp")


## reconstruire une image TDM en mode retroprojection
def reconFourierSlice():
    
    [nbprj, angles, sinogram] = readInput()

    # initialiser une image reconstruite, complexe
    # pour qu'elle puisse contenir sa version FFT d'abord
    IMAGE = np.zeros((geo.nbvox, geo.nbvox), 'complex')
    
    # conteneur pour la FFT du sinogramme
    SINOGRAM = np.zeros(sinogram.shape, 'complex')

    #image reconstruite
    image = np.zeros((geo.nbvox, geo.nbvox))
    #votre code ici
   #ici le défi est de remplir l'IMAGE avec des TF des projections (1D)
   #au bon angle.
   #La grille de recon est cartésienne mais le remplissage est cylindrique,
   #ce qui fait qu'il y aura un bon échantillonnage de IMAGE
   #au centre et moins bon en périphérie. Un TF inverse de IMAGE vous
   #donnera l'image recherchée.

   
    
    util.saveImage(image, "fft")


## main ##
start_time = time.time()
laminogram()
#backproject()
#reconFourierSlice()
print("--- %s seconds ---" % (time.time() - start_time))


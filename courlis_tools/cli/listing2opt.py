"""
Convert Courlis listing binary file to Opthyca file format
"""
import argparse
import scipy.io as spio
import numpy as np


def listing2opt(in_listing, out_opt):
    try:
        with spio.FortranFile(in_listing, 'r') as f:
            res = f.read_reals(float)
            while True:
                res = np.vstack((res, f.read_reals(float)))
    except TypeError:
        pass

    listePdt = np.unique(res[:, 0])

    nombrePdT = len(listePdt)
    nombreSection = sum(res[:, 0] == listePdt[0])
    nombreCouche = sum(res[:, 1] == 1999)//(nombrePdT-1)

    Uno = np.array([1 for i in range(nombreSection)])
    PdT = res[0:nombreSection, 0]
    NumeroSection = res[0:nombreSection, 1]
    variables = res[0:nombreSection, 2:17]
    Q = res[0:nombreSection, 5]*res[0:nombreSection, 6]

    print("%i frames, %i sections, %i couches" % (nombrePdT, nombreSection, nombreCouche))

    Resultats = np.insert(variables, 0, PdT, axis=1)
    Resultats = np.insert(Resultats, 1, Uno, axis=1)
    Resultats = np.insert(Resultats, 17, Q, axis=1)
    Resultats = np.insert(Resultats, 2, NumeroSection, axis=1)

    OPT = Resultats

    for i in range(1,nombrePdT):
        rangeIndex_1 = i*nombreSection + (i-1)*(nombreCouche+3)
        rangeIndex_2 = rangeIndex_1 + nombreSection

        PdT = res[rangeIndex_1:rangeIndex_2, 0]
        NumeroSection = res[rangeIndex_1:rangeIndex_2, 1]
        variables = res[rangeIndex_1:rangeIndex_2, 2:17]
        Q = res[rangeIndex_1:rangeIndex_2, 5]*res[rangeIndex_1:rangeIndex_2, 6]

        Resultats = np.insert(variables, 0, PdT, axis=1)
        Resultats = np.insert(Resultats, 1, Uno, axis=1)
        Resultats = np.insert(Resultats, 17, Q, axis=1)
        Resultats = np.insert(Resultats, 2, NumeroSection, axis=1)

        OPT = np.vstack((OPT, Resultats))

    with open(out_opt, 'w') as w:
        w.write('[variables]\n')
        w.write('\"Cote de l eau\";\"Z\";\"m\";3\n')
        w.write('\"Cote du fond\";\"ZREF\";\"m\";4\n')
        w.write('\"Vitesse mineure\";\"VMIN\";\"m/s\";4\n')
        w.write('\"Section mouillee mineure\";\"E1\";\"m2\";2\n')
        w.write('\"Concentration en vase\";\"CVas\";\"g/l\";4\n')
        w.write('\"Concentration en sable\";\"CSbl\";\"g/l\";4\n')
        w.write('\"Depot cumule\";\"DepT\";\"T\";3\n')
        w.write('\"Variation de surface cumulee\";\"Vsur\";\"m2\";3\n')
        w.write('\"Flux massique de vase\";\"FlVs\";\"kg/m/s\";3\n')
        w.write('\"Flux massique de sable\";\"FlSb\";\"kg/m/s\";3\n')
        w.write('\"Contrainte au fond maximale\";\"THMx\";\"N/m2\";3\n')
        w.write('\"Contrainte moyenne\";\"THMy\";\"N/m2\";3\n')
        w.write('\"Contrainte effective moyenne\";\"TEMy\";\"N/m2\";3\n')
        w.write('\"Concentration d''equilibre moy\";\"CeqM\";\"g/l\";3\n')
        w.write('\"Debit\";\"Q\";\"m3/s\";1\n')
        w.write('[resultats]\n')
        for i in range(np.size(OPT, 0)):
            j = 0
            w.write("{:16.8f}".format(OPT[i, j]))
            for j in range(1, np.size(OPT, 1)):
                w.write(";{:16.8f}".format(OPT[i, j]))
            w.write("\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_listing', help="Courlis listing binary file")
    parser.add_argument('out_opt', help="Opthyca file")
    args = parser.parse_args()
    listing2opt(args.in_listing, args.out_opt)

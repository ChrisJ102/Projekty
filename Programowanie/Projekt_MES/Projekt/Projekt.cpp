#include <iostream>
#include<fstream>
#include<sstream>
#include<iomanip>
#include<vector>
using namespace std;

struct Node {
    double x;
    double y;
    int t;
    int BC;
    Node(double x1, double y1, int temp) {
        x = x1;
        y = y1;
        t = temp;
        BC = 0;
    }
};

struct GlobalData {
    int SimulationTime; //t
    int SimulationStepTime; //delta t
    int Conductivity; //k
    int Alfa;
    int Tot; // temperatura otoczenia
    int InitialTemp; //temperatura
    int Density; // gestosc
    int SpecificHeat; // cieplo wlascite - cp
};

struct Element {
    int ID[4];
    Element(int i, int j, int k, int l) {
        ID[0] = i;
        ID[1] = j;
        ID[2] = k;
        ID[3] = l;
    }
};

struct Grid {
    int nN; // Nodes_number
    int nE; // Elements_number
    vector < Node > tab_node;
    vector < Element > tab_elements;

};



int ile_punktow = 2;


void pochodne(double** wyniketa, double** wynikksi, int wielkosc_tab, int ile_punktow, vector <double> punkty);

void wypisanie_zmienne(GlobalData zmienne, Grid grid1);

void wypisaniemacierz(double** macierz, int kolumny, int wiersze);

void obmacierzH(double** macierzH, double** wyniketa, double** wynikksi, int wielkosc_tab, int liczba_pochodnych, Grid grid1, GlobalData zmienne, vector<double> wagi, int element, vector<double> wagi_mnnozenie);

void agregacja(double** macierzH, double** macierzHGlobal, Grid grid1, int liczba_pochodnych, int element);

void macierzHPC(double** macierzHpc, double* detJ, double** macierzNx, double** macierzNy, int liczba_pochodnych, int element, GlobalData zmienne);

void macierzHpom(double** macierzH, double** macierzHpc, vector<double> wagi_mnnozenie, int liczba_pochodnych, int element);

void macierzwyzeruj(double** macierz, int liczba_pochodnych);

void obmacierzHBc_wekP(double** macierzH, int wielkosc_tab, int liczba_pochodnych, Grid grid1, GlobalData zmienne, vector<double> wagi, int element, vector <double> punkty, double* wektorPLokal);

void obmacierzpow(double** macierzpow, double detJHBc[4], int liczba_pochodnych, int bok, GlobalData zmienne, vector<double> wagi, vector <double> punkty);

void obmacierzpowpom(double** macierzpow, double** macierzPC, double detJHBc[4], int liczba_pochodnych, GlobalData zmienne, vector<double> wagi, int punkt);

void obmacierzHBcpom(double** macierzHBC, double** macierzpow, int liczba_pochodnych);

void obwekP(double* wektorP_bok, double detJHBc[4], int liczba_pochodnych, int bok, GlobalData zmienne, vector<double> wagi, vector <double> punkty);

void obmacierzPpom(double* wektorP_bok, double** macierzPC, double detJHBc[4], int liczba_pochodnych, GlobalData zmienne, vector<double> wagi, int punkt);

void obwekPel(double* wektorPLokal, double* wektorP_bok, int liczba_pochodnych);

void agregacjaP(double* wektorPGlobal, double* wektorPLokal, Grid grid1, int liczba_pochodnych, int element);

void wypisanieWekP(double* wektorPLokal, int wielkosc);

void PLokwyzeruj(double* wektorPLokal, int liczba_pochodnych);

void wypisaniemacierzWektor(double** macierz, double* wektor, int kolumny, int wiersze);

void Gauss(double** macierzHGLobal, double* wektorPGlobal, double* wynikiTemp, int wielkosc);

int main() {
    //cout << setprecision(11) << fixed;
    ifstream dane("Test1_4_4.txt");
    //ifstream dane("Test2_4_4_MixGrid.txt");
    //ifstream dane("Test3_31_31_kwadrat.txt");
    string temp;
    int tempint = 0;
    GlobalData zmienne = { NULL };
    dane >> temp >> zmienne.SimulationTime >> temp >> zmienne.SimulationStepTime >> temp >> zmienne.Conductivity >> temp >> zmienne.Alfa;
    dane >> temp >> zmienne.Tot >> temp >> zmienne.InitialTemp >> temp >> zmienne.Density >> temp >> zmienne.SpecificHeat >> temp >> temp;
    int Nodes_number;
    dane >> Nodes_number >> temp >> temp;
    int Elements_number;
    dane >> Elements_number;

    Grid grid1 = { NULL };
    grid1.nN = Nodes_number;
    grid1.nE = Elements_number;

    dane >> temp;
    double tempdouble_x;
    double tempdouble_y;

    vector < Node > tab_wezlow;

    for (int i = 0; i < grid1.nN; i++) {
        dane >> tempint >> temp >> tempdouble_x >> temp >> tempdouble_y;
        tab_wezlow.push_back(Node(tempdouble_x, tempdouble_y, zmienne.InitialTemp));
    }
    dane >> temp >> temp;
    vector < Element > tab_elementow;
    int tempint0, tempint1, tempint2, tempint3;
    for (int j = 0; j < grid1.nE; j++) {
        dane >> tempint >> temp >> tempint0 >> temp >> tempint1 >> temp >> tempint2 >> temp >> tempint3;
        tab_elementow.push_back(Element(tempint0 - 1, tempint1 - 1, tempint2 - 1, tempint3 - 1));
    }

    vector <int> tabBC;

    dane >> temp;
    while (!dane.eof()) {
        dane >> tempint;
        tabBC.push_back(tempint);
        dane >> temp;
    }

    for (int i = 0; i < tabBC.size(); i++) {
        tab_wezlow[tabBC[i] - 1].BC = 1;
    }

    grid1.tab_node = tab_wezlow;
    grid1.tab_elements = tab_elementow;

    //wypisanie_zmienne(zmienne, grid1);

    int wielkosc_tab = 0;
    int liczba_pochodnych = 4;
    vector <double> punkty;
    vector<double> wagi;
    vector<double> wagi_mnnozenie;

    if (ile_punktow == 2) {
        wielkosc_tab = 4;
        punkty = { -1. / sqrt(3), 1. / sqrt(3) };
        wagi = { 1., 1. };
        wagi_mnnozenie = { (wagi[0] * wagi[0]), (wagi[1] * wagi[0]),
                           (wagi[0] * wagi[1]), (wagi[1] * wagi[1]) };
    }
    else if (ile_punktow == 3) {
        wielkosc_tab = 9;
        punkty = { -sqrt(3.0 / 5.0), 0., sqrt(3.0 / 5.0) };
        wagi = { (5. / 9.), (8. / 9.), (5. / 9.) };
        wagi_mnnozenie = { (wagi[0] * wagi[0]), (wagi[1] * wagi[0]), (wagi[2] * wagi[0]),
                           (wagi[0] * wagi[1]), (wagi[1] * wagi[1]), (wagi[2] * wagi[1]),
                           (wagi[0] * wagi[2]), (wagi[1] * wagi[2]), (wagi[2] * wagi[2]) };
    }
    else if (ile_punktow == 4) {
        wielkosc_tab = 16;
        punkty = { -sqrt((3. / 7.) + 2. / 7. * sqrt(6. / 5.)), -sqrt((3. / 7.) - 2. / 7. * sqrt(6. / 5.)), sqrt((3. / 7.) - 2. / 7. * sqrt(6. / 5.)), sqrt((3. / 7.) + 2. / 7. * sqrt(6. / 5.)) };
        wagi = { 1. / 36. * (18. - sqrt(30.)), 1. / 36. * (18. + sqrt(30.)), 1. / 36. * (18. + sqrt(30.)), 1. / 36. * (18. - sqrt(30.)) };
        wagi_mnnozenie = { (wagi[0] * wagi[0]), (wagi[1] * wagi[0]), (wagi[2] * wagi[0]), (wagi[3] * wagi[0]),
                           (wagi[0] * wagi[1]), (wagi[1] * wagi[1]), (wagi[2] * wagi[1]), (wagi[3] * wagi[1]),
                           (wagi[0] * wagi[2]), (wagi[1] * wagi[2]), (wagi[2] * wagi[2]), (wagi[3] * wagi[2]),
                           (wagi[0] * wagi[3]), (wagi[1] * wagi[3]), (wagi[2] * wagi[3]), (wagi[3] * wagi[3]) };
    }

    double** wyniketa = new double* [wielkosc_tab];
    double** wynikksi = new double* [wielkosc_tab];

    for (int i = 0; i < wielkosc_tab; i++) {
        wyniketa[i] = new double[liczba_pochodnych];
        wynikksi[i] = new double[liczba_pochodnych];
    }

    pochodne(wyniketa, wynikksi, wielkosc_tab, ile_punktow, punkty);

    double** macierzH = new double* [liczba_pochodnych];

    for (int i = 0; i < liczba_pochodnych; i++) {
        macierzH[i] = new double[liczba_pochodnych];
    }

    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzH[i][j] = 0.;
        }
    }

    double** macierzHGlobal = new double* [grid1.nN];

    for (int i = 0; i < grid1.nN; i++) {
        macierzHGlobal[i] = new double[grid1.nN];
    }

    for (int i = 0; i < grid1.nN; i++) {
        for (int j = 0; j < grid1.nN; j++) {
            macierzHGlobal[i][j] = 0.;
        }
    }

    double* wektorPLokal = new double[liczba_pochodnych];
    for (int i = 0; i < liczba_pochodnych; i++) {
        wektorPLokal[i] = 0.;
    }

    double* wektorPGlobal = new double[grid1.nN];
    for (int i = 0; i < grid1.nN; i++) {
        wektorPGlobal[i] = 0.;
    }

    for (int i = 0; i < grid1.nE; i++) {
        cout << "Element " << i + 1 << endl;
        obmacierzH(macierzH, wyniketa, wynikksi, wielkosc_tab, liczba_pochodnych, grid1, zmienne, wagi, i, wagi_mnnozenie);
        obmacierzHBc_wekP(macierzH, wielkosc_tab, liczba_pochodnych, grid1, zmienne, wagi, i, punkty, wektorPLokal);
        wypisaniemacierz(macierzH, liczba_pochodnych, liczba_pochodnych);
        cout << "Wektor elementu" << endl;
        wypisanieWekP(wektorPLokal, liczba_pochodnych);
        cout << endl;
        agregacja(macierzH, macierzHGlobal, grid1, liczba_pochodnych, i);
        agregacjaP(wektorPGlobal, wektorPLokal, grid1, liczba_pochodnych, i);
        macierzwyzeruj(macierzH, liczba_pochodnych);
        PLokwyzeruj(wektorPLokal, liczba_pochodnych);
    }

    cout << endl;
    //cout << setprecision(5);
    wypisaniemacierz(macierzHGlobal, grid1.nN, grid1.nN);
    cout << endl;
    wypisaniemacierzWektor(macierzHGlobal, wektorPGlobal, grid1.nN, grid1.nN);
    cout << endl;

    double* wynikiTemp = new double[grid1.nN];
    for (int i = 0; i < grid1.nN; i++) {
        wynikiTemp[i] = 0.;
    }

    Gauss(macierzHGlobal, wektorPGlobal, wynikiTemp, grid1.nN);

    for (int i = 0; i < grid1.nN; i++) {
        cout << wynikiTemp[i] << endl;
    }
    cout << endl;

    //usuwanie tablic dynamicznych
    for (int i = 0; i < wielkosc_tab; i++) {
        delete[] wyniketa[i];
        delete[] wynikksi[i];
    }
    for (int i = 0; i < liczba_pochodnych; i++) {
        delete[] macierzH[i];
    }
    for (int i = 0; i < grid1.nN; i++) {
        delete[] macierzHGlobal[i];
    }
    delete[] macierzHGlobal;
    delete[] wyniketa;
    delete[] wynikksi;
    delete[] macierzH;
    delete[] wektorPGlobal;
    delete[] wektorPLokal;
    delete[] wynikiTemp;
    return 0;
}


void pochodne(double** wyniketa, double** wynikksi, int wielkosc_tab, int ile_punktow, vector <double> punkty) {
    vector<double> tabeta;
    vector<double> tabksi;
    for (int i = 0; i < wielkosc_tab; i++) {
        if (ile_punktow == 2) {
            tabeta = { punkty[0], punkty[0], punkty[1], punkty[1] };
            tabksi = { punkty[0], punkty[1], punkty[0], punkty[1] };
        }
        else if (ile_punktow == 3) {
            tabeta = { punkty[0], punkty[0], punkty[0], punkty[1], punkty[1], punkty[1], punkty[2], punkty[2], punkty[2] };
            tabksi = { punkty[0], punkty[1], punkty[2], punkty[0], punkty[1], punkty[2], punkty[0], punkty[1], punkty[2] };
        }
        else if (ile_punktow == 4) {
            tabeta = { punkty[0], punkty[0], punkty[0], punkty[0], punkty[1], punkty[1], punkty[1], punkty[1], punkty[2], punkty[2], punkty[2], punkty[2], punkty[3], punkty[3], punkty[3], punkty[3] };
            tabksi = { punkty[0], punkty[1], punkty[2], punkty[3], punkty[0], punkty[1], punkty[2], punkty[3], punkty[0], punkty[1], punkty[2], punkty[3], punkty[0], punkty[1], punkty[2], punkty[3] };
        }
    }
    for (int i = 0; i < wielkosc_tab; i++) {
        wynikksi[i][0] = -1. / 4. * (1 - tabeta[i]);
        wynikksi[i][1] = 1. / 4. * (1 - tabeta[i]);
        wynikksi[i][2] = 1. / 4. * (1 + tabeta[i]);
        wynikksi[i][3] = -1. / 4. * (1 + tabeta[i]);

        wyniketa[i][0] = -1. / 4. * (1 - tabksi[i]);
        wyniketa[i][1] = -1. / 4. * (1 + tabksi[i]);
        wyniketa[i][2] = 1. / 4. * (1 + tabksi[i]);
        wyniketa[i][3] = 1. / 4. * (1 - tabksi[i]);

    }

    /* cout << "eta" << endl;
     for (int i = 0; i < wielkosc_tab; i++) {
         cout << tabeta[i] << "\t";
         for (int j = 0; j < 4; j++) {
             cout << wynikksi[i][j] << "\t";
         }
         cout << endl;
     }

     cout << endl;
     cout << "ksi" << endl;
     for (int i = 0; i < wielkosc_tab; i++) {
         cout << tabksi[i] << "\t";
         for (int j = 0; j < 4; j++) {
             cout << wyniketa[i][j] << "\t";
         }
         cout << endl;
     }
     cout << endl;*/
}

void wypisaniemacierz(double** macierz, int kolumny, int wiersze) {
    for (int i = 0; i < kolumny; i++) {
        for (int j = 0; j < wiersze; j++) {
            cout << macierz[i][j] << " ";
        }
        cout << endl;
    }
}

void wypisanieWekP(double* wektorPLokal, int wielkosc) {
    for (int i = 0; i < wielkosc; i++) {
        cout << wektorPLokal[i] << endl;
    }
}

void wypisanie_zmienne(GlobalData zmienne, Grid grid1) {
    cout << "SimulationTime " << zmienne.SimulationTime << "\nSimulationStepTime " << zmienne.SimulationStepTime <<
        "\nConductivity " << zmienne.Conductivity << "\nAlfa " << zmienne.Alfa << "\nTot " << zmienne.Tot << "\nInitialTemp " <<
        zmienne.InitialTemp << "\nDensity " << zmienne.Density << "\nSpecificHeat " << zmienne.SpecificHeat <<
        "\nNodes number " << grid1.nN << "\nElements number " << grid1.nE << endl;

    for (int i = 0; i < grid1.nN; i++) {
        cout << i + 1 << " " << grid1.tab_node[i].x << " " << grid1.tab_node[i].y << " " << grid1.tab_node[i].t << " " << grid1.tab_node[i].BC << endl;
    }

    for (int j = 0; j < grid1.nE; j++) {
        cout << "Element " << j + 1 << ": ";
        for (int k = 0; k < 4; k++) {
            cout << grid1.tab_elements[j].ID[k] + 1 << " ";
        }
        cout << endl;
    }
    cout << endl;
}

void obmacierzH(double** macierzH, double** wyniketa, double** wynikksi, int wielkosc_tab, int liczba_pochodnych, Grid grid1, GlobalData zmienne, vector<double> wagi, int element, vector<double> wagi_mnnozenie) {
    double** macierz = new double* [wielkosc_tab];
    int liczba_punktow = ile_punktow;
    for (int i = 0; i < wielkosc_tab; i++) {
        macierz[i] = new double[4];
    }
    for (int i = 0; i < wielkosc_tab; i++) {
        for (int j = 0; j < 4; j++) {
            macierz[i][j] = 0.;
        }
    }
    for (int i = 0; i < wielkosc_tab; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierz[i][0] += wynikksi[i][j] * grid1.tab_node[grid1.tab_elements[element].ID[j]].x;
            macierz[i][1] += wynikksi[i][j] * grid1.tab_node[grid1.tab_elements[element].ID[j]].y;
            macierz[i][2] += wyniketa[i][j] * grid1.tab_node[grid1.tab_elements[element].ID[j]].x;
            macierz[i][3] += wyniketa[i][j] * grid1.tab_node[grid1.tab_elements[element].ID[j]].y;
        }
    }

    double* detJ = new double[wielkosc_tab];
    double* detJodw = new double[wielkosc_tab];
    for (int i = 0; i < wielkosc_tab; i++) {
        detJ[i] = (macierz[i][0] * macierz[i][3]) - (macierz[i][1] * macierz[i][2]);
        detJodw[i] = 1. / detJ[i];
    }

    for (int i = 0; i < wielkosc_tab; i++) {
        swap(macierz[i][0], macierz[i][3]);
        macierz[i][1] *= -1.;
        macierz[i][2] *= -1.;
    }

    for (int i = 0; i < wielkosc_tab; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierz[i][j] *= detJodw[i];
        }
    }

    double** macierzNx = new double* [wielkosc_tab];
    double** macierzNy = new double* [wielkosc_tab];
    for (int i = 0; i < wielkosc_tab; i++) {
        macierzNx[i] = new double[liczba_pochodnych];
        macierzNy[i] = new double[liczba_pochodnych];
    }

    for (int i = 0; i < wielkosc_tab; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzNx[i][j] = 0.;
            macierzNy[i][j] = 0.;
        }
    }

    for (int i = 0; i < wielkosc_tab; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzNx[i][j] = macierz[i][0] * wynikksi[i][j] + macierz[i][1] * wyniketa[i][j];
            macierzNy[i][j] = macierz[i][2] * wynikksi[i][j] + macierz[i][3] * wyniketa[i][j];
        }
    }


    double** macierzHpc = new double* [liczba_pochodnych];
    for (int i = 0; i < liczba_pochodnych; i++) {
        macierzHpc[i] = new double[liczba_pochodnych];
    }
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzHpc[i][j] = 0.;
        }
    }

    for (int el = 0; el < wielkosc_tab; el++) {
        macierzHPC(macierzHpc, detJ, macierzNx, macierzNy, liczba_pochodnych, el, zmienne);
        macierzHpom(macierzH, macierzHpc, wagi_mnnozenie, liczba_pochodnych, el);
    }

    for (int i = 0; i < wielkosc_tab; i++) {
        delete[] macierz[i];
    }
    for (int i = 0; i < liczba_pochodnych; i++) {
        delete[] macierzHpc[i];
    }
    delete[] macierz;
    delete[] detJ;
    delete[] detJodw;
    delete[] macierzHpc;
}

void macierzHPC(double** macierzHpc, double* detJ, double** macierzNx, double** macierzNy, int liczba_pochodnych, int element, GlobalData zmienne) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzHpc[i][j] = zmienne.Conductivity * detJ[element] * (macierzNx[element][i] * macierzNx[element][j] + macierzNy[element][i] * macierzNy[element][j]);
        }
    }
}

void macierzHpom(double** macierzH, double** macierzHpc, vector<double> wagi_mnnozenie, int liczba_pochodnych, int element) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzH[i][j] += macierzHpc[i][j] * wagi_mnnozenie[element];
        }
    }
}

void macierzwyzeruj(double** macierz, int liczba_pochodnych) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierz[i][j] = 0.;
        }
    }
}

void obmacierzHBc_wekP(double** macierzH, int wielkosc_tab, int liczba_pochodnych, Grid grid1, GlobalData zmienne, vector<double> wagi, int element, vector <double> punkty, double* wektorPLokal) {
    double detJHBc[4];
    bool temp1[4], temp2[4];
    for (int i = 0; i < 4; i++) {
        if (i == 3) {
            if (grid1.tab_node[grid1.tab_elements[element].ID[3]].BC == 1 && grid1.tab_node[grid1.tab_elements[element].ID[0]].BC == 1) {
                detJHBc[3] = sqrt(pow(grid1.tab_node[grid1.tab_elements[element].ID[3]].x - grid1.tab_node[grid1.tab_elements[element].ID[0]].x, 2) + pow(grid1.tab_node[grid1.tab_elements[element].ID[3]].y - grid1.tab_node[grid1.tab_elements[element].ID[0]].y, 2)) / 2.;
                temp1[3] = grid1.tab_node[grid1.tab_elements[element].ID[3]].BC;
                temp2[3] = grid1.tab_node[grid1.tab_elements[element].ID[0]].BC;
            }
            else {
                detJHBc[3] = 0.;
                temp1[3] = grid1.tab_node[grid1.tab_elements[element].ID[3]].BC;
                temp2[3] = grid1.tab_node[grid1.tab_elements[element].ID[0]].BC;
            }
        }
        else {
            if (grid1.tab_node[grid1.tab_elements[element].ID[i + 1]].BC == 1 && grid1.tab_node[grid1.tab_elements[element].ID[i]].BC == 1) {
                detJHBc[i] = sqrt(pow(grid1.tab_node[grid1.tab_elements[element].ID[i + 1]].x - grid1.tab_node[grid1.tab_elements[element].ID[i]].x, 2) + pow(grid1.tab_node[grid1.tab_elements[element].ID[i + 1]].y - grid1.tab_node[grid1.tab_elements[element].ID[i]].y, 2)) / 2.;
                temp1[i] = grid1.tab_node[grid1.tab_elements[element].ID[i + 1]].BC;
                temp2[i] = grid1.tab_node[grid1.tab_elements[element].ID[i]].BC;
            }
            else {
                detJHBc[i] = 0.;
                temp1[i] = grid1.tab_node[grid1.tab_elements[element].ID[i + 1]].BC;
                temp2[i] = grid1.tab_node[grid1.tab_elements[element].ID[i]].BC;
            }
        }
    }

    double** macierzpow = new double* [liczba_pochodnych];
    double** macierzHBC = new double* [liczba_pochodnych];

    for (int ii = 0; ii < liczba_pochodnych; ii++) {
        macierzpow[ii] = new double[liczba_pochodnych];
        macierzHBC[ii] = new double[liczba_pochodnych];
    }
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzpow[i][j] = 0.;
            macierzHBC[i][j] = 0.;
        }
    }

    for (int b = 0; b < 4; b++) {
        if (temp1[b] == 1 && temp2[b] == 1) {
            obmacierzpow(macierzpow, detJHBc, liczba_pochodnych, b, zmienne, wagi, punkty);
            obmacierzHBcpom(macierzHBC, macierzpow, liczba_pochodnych);
        }
    }
    double* wektorP_bok = new double[4];
    double* wektorP_el = new double[4];

    for (int bo = 0; bo < 4; bo++) {
        if (temp1[bo] == 1 && temp2[bo] == 1) {
            obwekP(wektorP_bok, detJHBc, liczba_pochodnych, bo, zmienne, wagi, punkty);
            obwekPel(wektorPLokal, wektorP_bok, liczba_pochodnych);
        }
    }

    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzH[i][j] += macierzHBC[i][j];
        }
    }
    for (int i = 0; i < 4; i++) {
        detJHBc[i] = 0.;
    }

    for (int i = 0; i < liczba_pochodnych; i++) {
        delete[] macierzpow[i];
        delete[] macierzHBC[i];
    }
    delete[] macierzHBC;
    delete[] macierzpow;
    delete[] wektorP_bok;
    delete[] wektorP_el;
}

void obmacierzpow(double** macierzpow, double detJHBc[4], int liczba_pochodnych, int bok, GlobalData zmienne, vector<double> wagi, vector <double> punkty) {
    double* ksi_x = new double[ile_punktow];
    double* eta_y = new double[ile_punktow];
    macierzwyzeruj(macierzpow, liczba_pochodnych);
    for (int ii = 0; ii < ile_punktow; ii++) {
        ksi_x[ii] = 0.;
        eta_y[ii] = 0.;
    }

    for (int i = 0; i < ile_punktow; i++) {
        if (bok == 0) {
            ksi_x[i] = punkty[i];
            eta_y[i] = -1.;
        }
        else if (bok == 1) {
            ksi_x[i] = 1.;
            eta_y[i] = punkty[i];
        }
        else if (bok == 2) {
            ksi_x[i] = punkty[ile_punktow - 1 - i];
            eta_y[i] = 1.;
        }
        else if (bok == 3) {
            ksi_x[i] = -1.;
            eta_y[i] = punkty[ile_punktow - 1 - i];
        }
    }


    double** macierzPC = new double* [ile_punktow];
    for (int i = 0; i < ile_punktow; i++) {
        macierzPC[i] = new double[4];
    }

    for (int ii = 0; ii < ile_punktow; ii++) {
        for (int j = 0; j < 4; j++) {
            macierzPC[ii][j] = 0.;
        }
    }
    for (int p = 0; p < ile_punktow; p++) {
        macierzPC[p][0] = 0.25 * (1 - ksi_x[p]) * (1 - eta_y[p]);
        macierzPC[p][1] = 0.25 * (1 + ksi_x[p]) * (1 - eta_y[p]);
        macierzPC[p][2] = 0.25 * (1 + ksi_x[p]) * (1 + eta_y[p]);
        macierzPC[p][3] = 0.25 * (1 - ksi_x[p]) * (1 + eta_y[p]);
    }

    for (int pu = 0; pu < ile_punktow; pu++) {
        obmacierzpowpom(macierzpow, macierzPC, detJHBc, liczba_pochodnych, zmienne, wagi, pu);
    }
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzpow[i][j] *= detJHBc[bok];
        }
    }

    for (int i = 0; i < ile_punktow; i++) {
        delete[] macierzPC[i];
    }
    delete[] macierzPC;
    delete[] ksi_x;
    delete[] eta_y;
}

void obmacierzpowpom(double** macierzpow, double** macierzPC, double detJHBc[4], int liczba_pochodnych, GlobalData zmienne, vector<double> wagi, int punkt) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzpow[i][j] += zmienne.Alfa * wagi[punkt] * macierzPC[punkt][i] * macierzPC[punkt][j];
        }
    }
}

void obmacierzHBcpom(double** macierzHBC, double** macierzpow, int liczba_pochodnych) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        for (int j = 0; j < liczba_pochodnych; j++) {
            macierzHBC[i][j] += macierzpow[i][j];
        }
    }
}

void obwekP(double* wektorP_bok, double detJHBc[4], int liczba_pochodnych, int bok, GlobalData zmienne, vector<double> wagi, vector <double> punkty) {
    double* ksi_x = new double[ile_punktow];
    double* eta_y = new double[ile_punktow];
    for (int i = 0; i < liczba_pochodnych; i++) {
        wektorP_bok[i] = 0.;
    }
    for (int ii = 0; ii < ile_punktow; ii++) {
        ksi_x[ii] = 0.;
        eta_y[ii] = 0.;
    }

    for (int i = 0; i < ile_punktow; i++) {
        if (bok == 0) {
            ksi_x[i] = punkty[i];
            eta_y[i] = -1.;
        }
        else if (bok == 1) {
            ksi_x[i] = 1.;
            eta_y[i] = punkty[i];
        }
        else if (bok == 2) {
            ksi_x[i] = punkty[ile_punktow - 1 - i];
            eta_y[i] = 1.;
        }
        else if (bok == 3) {
            ksi_x[i] = -1.;
            eta_y[i] = punkty[ile_punktow - 1 - i];
        }
    }

    double** macierzPC = new double* [ile_punktow];
    for (int i = 0; i < ile_punktow; i++) {
        macierzPC[i] = new double[4];
    }

    for (int ii = 0; ii < ile_punktow; ii++) {
        for (int j = 0; j < 4; j++) {
            macierzPC[ii][j] = 0.;
        }
    }
    for (int p = 0; p < ile_punktow; p++) {
        macierzPC[p][0] = 0.25 * (1 - ksi_x[p]) * (1 - eta_y[p]);
        macierzPC[p][1] = 0.25 * (1 + ksi_x[p]) * (1 - eta_y[p]);
        macierzPC[p][2] = 0.25 * (1 + ksi_x[p]) * (1 + eta_y[p]);
        macierzPC[p][3] = 0.25 * (1 - ksi_x[p]) * (1 + eta_y[p]);
    }

    for (int pu = 0; pu < ile_punktow; pu++) {
        obmacierzPpom(wektorP_bok, macierzPC, detJHBc, liczba_pochodnych, zmienne, wagi, pu);
    }
    for (int i = 0; i < liczba_pochodnych; i++) {
        wektorP_bok[i] *= detJHBc[bok];
    }

    for (int i = 0; i < ile_punktow; i++) {
        delete[] macierzPC[i];
    }
    delete[] macierzPC;
    delete[] ksi_x;
    delete[] eta_y;
}

void obmacierzPpom(double* wektorP_bok, double** macierzPC, double detJHBc[4], int liczba_pochodnych, GlobalData zmienne, vector<double> wagi, int punkt) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        wektorP_bok[i] += zmienne.Alfa * wagi[punkt] * macierzPC[punkt][i] * zmienne.Tot;
    }
}

void obwekPel(double* wektorPLokal, double* wektorP_bok, int liczba_pochodnych) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        wektorPLokal[i] += wektorP_bok[i];
    }
}

void agregacja(double** macierzH, double** macierzHGlobal, Grid grid1, int liczba_pochodnych, int element) {
    for (int k = 0; k < 4; k++) {
        for (int w = 0; w < 4; w++) {
            macierzHGlobal[grid1.tab_elements[element].ID[k]][grid1.tab_elements[element].ID[w]] += macierzH[k][w];
        }
    }
}

void agregacjaP(double* wektorPGlobal, double* wektorPLokal, Grid grid1, int liczba_pochodnych, int element) {
    for (int k = 0; k < 4; k++) {
        wektorPGlobal[grid1.tab_elements[element].ID[k]] += wektorPLokal[k];
    }
}

void PLokwyzeruj(double* wektorPLokal, int liczba_pochodnych) {
    for (int i = 0; i < liczba_pochodnych; i++) {
        wektorPLokal[i] = 0.;
    }
}

void wypisaniemacierzWektor(double** macierz, double* wektor, int kolumny, int wiersze) {
    for (int i = 0; i < kolumny; i++) {
        for (int j = 0; j < wiersze; j++) {
            cout << macierz[i][j] << " ";
        }
        cout << "\t" << wektor[i] << endl;
    }
}

void Gauss(double** macierzHGLobal, double* wektorPGlobal, double* wynikiTemp, int wielkosc) {
    double** macierzH_P = new double* [wielkosc];
    for (int i = 0; i < wielkosc; i++) {
        macierzH_P[i] = new double[wielkosc + 1];
    }

    for (int i = 0; i < wielkosc; i++) {
        for (int j = 0; j < wielkosc; j++) {
            macierzH_P[i][j] = macierzHGLobal[i][j];
        }
    }

    for (int i = 0; i < wielkosc; i++) {
        macierzH_P[i][wielkosc] = wektorPGlobal[i];
    }

    for (int i = 0; i < wielkosc - 1; i++) {
        for (int j = i + 1; j < wielkosc; j++) {
            double mnoznik = macierzH_P[j][i] / macierzH_P[i][i];
            for (int k = 0; k <= wielkosc; k++) {
                if (j == k && macierzH_P[j][k] == 0) {
                    cout << "0 na przekatnej!" << endl;
                }
                macierzH_P[j][k] = macierzH_P[j][k] - (mnoznik * macierzH_P[i][k]);
            }
        }
    }
    for (int i = wielkosc - 1; i >= 0; i--) {
        wynikiTemp[i] = macierzH_P[i][wielkosc];
        for (int j = 0; j < wielkosc; j++) {
            if (j != i) {
                wynikiTemp[i] = wynikiTemp[i] - (macierzH_P[i][j] * wynikiTemp[j]);
            }
        }
        wynikiTemp[i] = wynikiTemp[i] / macierzH_P[i][i];
    }

}


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 15:17:15 2021

@author: phil
"""
import csv
import itertools
from functools import reduce
import unicodedata
from shutil import copyfile
from random import randint
import os
import fitz
from collections import OrderedDict


def grouper(n, iterable, fillvalue=None):
    """
    Fonction permettant de diviser une liste en sous-listes de taille n

    Parameters
    ----------
    n : Int
        Entier donnant la taille du groupe.
    iterable : List ou tuple ...
        Liste que l'on souhaite divisée
    fillvalue :  optional
        Permet de remplir si besoin. The default is None.

    Returns
    -------
    Liste découpée en sous-listes de taille n

    """
    args = [iter(iterable)] * n
    return list(itertools.zip_longest(*args, fillvalue=fillvalue))


def write_warning(file):
    warning = """

    %=====================================
    %   WARNING
    %   FICHIER AUTOMATISE
    %   NE PAS MODIFIER
    %=====================================

    """

    file.write(warning)


def tableau_reviewer(filename_in, nbcol):
    """
    Fonction permettant de générer le tableau des reviewers à partir d'un
    fichier issue d'OpenConf

    Parameters
    ----------
    filename_in : String
        Fichier CSV issu de l'exportation d'OpenConf il est de la forme
        "Path_IMOC+ nom_de_fichier.csv"
    nbcol : Int
        Nombre de colonnes du tableau

    Returns
    -------
        Fichier TEX il est de la forme "Path_EXTEX+ filename_in.tex"


    Example
    -------
    Préparation du fichier csv

    >>> Test_csv =['"ID","FULL NAME","ORGANIZATION"',
    '"148","Bruce Wayne","Batcave - Gotham city"',
    '"149","Clark KENT","Planète Krypton - Smallville"',
    '"150","OBiwan Kenobi","La force"']
    >>> file_in=open("file_in.csv","w", encoding='utf-8')
    >>> for e in Test_csv :
            file_in.write(e+"\\n")
    >>> file_in.close()

    Utilisation de tableau_reviewer

    >>> Test = tableau_reviewer("file_in.csv",3,towrite = False)
    >>> for row in Test :
            print(row)
    \\begin{supertabular}{lll}
    Obiwan Kenobi & Clark Kent & Bruce Wayne \\
    \\end{supertabular}
    """
    # Path_IMOC = os.path.dirname(file_in)
    # file_in = os.path.basename(file_in)
    tab = []
    with open(Path_IMOC+filename_in, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count = line_count + 1
            else:
                reviewer_name = row[1].title()
                tab.append(reviewer_name)

    tab.sort(key=lambda x: x.split()[-1])
    tab = grouper(nbcol, tab, fillvalue='')

    text_output = ["\\begin{supertabular}{"+nbcol*"l"+"}"]
    for row in tab:
        text_output.append(reduce(lambda x, y: x+" & "+y, row)+" \\\\")

    text_output.append("\\end{supertabular}")
    copyfile(Path_EXTEX+"Tableau_Reviewer_start.tex",
             Path_EXTEX+"Tableau_Reviewer.tex")
    file_out = Path_EXTEX+"Tableau_Reviewer.tex"
    with open(file_out, mode='a+') as file_tex:
        write_warning(file_tex)
        file_tex.writelines('\n'.join(text_output))
        file_tex.write('\end{center}')


def clean_dict(d):
    """
    Fonction permettant de nettoyer un dictionnaire avec du texte
    ainsi certains caractères sont remplacés par du LateX et

    Parameters
    ----------
    d : Dict
        Dictionnaire d'entrée

    Returns
    -------
    d : Dict
        Dictionnaire de sortie

    """
    chars_tex = [("’", "'"), (" &", " \&"), (" %", " \%"), ("μ", "$\mu$"),
                 ("≤", "$\leqslant$"), ("φ", "$\\varphi$"), ("mm2",
                                                             "\si{\square \milli\metre}"),
                 ("m2", "\si{\square m}"), ("m3",
                                            "\si{\cubic m}"), ("κ", "$\kappa$"),
                 ("Δ", "$\Delta$"), ("ν", "$\\nu$"),
                 ("W.m-2", "\si{\watt\per\square\meter}"),
                 ("W m-2 K-1", "\si{\watt\per\square\meter\per\kelvin}"),
                 ("W.m-1.K-1", "\si{\watt\per\meter\per\kelvin}"),
                 ("W.m^(-1).K^(-1)", "\si{\watt\per\meter\per\kelvin}"),
                 ("µV.W-1.m-2", "\si{\micro\\volt\per\watt\per\square\metre}"),
                 ("cm-1", "\si{\per\centi\metre}"),
                 ("µm", "\si{\micro\metre}"), ("τ", "$\\tau$"),
                 ("α", "$\\alpha$"), ("ρ", "$\\rho$"),
                 ("_", "\_"), ("CO2",
                               "\chemform{CO_2}"), ("CH4", "\chemform{CH_4}"),
                 ("Li4Br(OH)3", "\chemform{Li_4Br(OH)_3}"),
                 ("LiOH", "\chemform{LiOH}"), ("LiBR", "\chemform{LiBr}"),
                 ("Al2O3", "\chemform{Al_2O_3}"), ("Fe2O3",
                                                   "\chemform{Fe_2O_3}"),
                 ("Fe2Ti", "\chemform{Fe_2Ti}"), ("FeTi", "\chemform{F eTi}"),
                 ("NH3", "\chemform{NH_3}"), ("H2O", "\chemform{H_2O}"),
                 ("Cr7Fe17Ti5", "\chemform{Cr_7Fe_17Ti_5}"),
                 ("\n", "\n\n"), ("Tm", "$T_m$"), ("T0", "$T_0$"),
                 ("TC", "$T_C$"), ("ε", "$\\varepsilon$"),
                 ("TWh.an-1", "\si{TWH \per an}"),
                 ("µ", "$\mu$"), ("−", "-"), ("°", "$^{\circ}$")
                 # ("\n[","\\\\\n["),("\n-","\\\\\n-"),
                 ]
    d = dict([(k.strip(), v.strip()) for k, v in d.items() if len(v) > 0])
    for k in d.keys():
        for ch in chars_tex:
            d[k] = d[k].replace(ch[0], ch[1])
    return d


def clean_string(ch, accents=True, spaces=True):
    """
    Fonction permettant de nettoyer une chaîne de caractères avec l'option
    de supprimer les blancs et/ou les espaces

    Parameters
    ----------
    ch : String
        chaine de caractères d'entrée
    accents : Boolean, optional
        Si vrai alors on supprime les accents. The default is True.
    spaces : Boolean, optional
        Si vrai alors on supprime les espaces. The default is True.

    Returns
    -------
    ch : String
        Chaîne de carctères en sortie.

    """
    if accents:
        ch = unicodedata.normalize('NFKD', ch)
    if spaces:
        ch = ch.replace(' ', '')
    return ch.encode('ASCII', 'ignore').decode("utf-8")


def extract_authors(d):
    """
    Fonction permettant d'extraire la liste des auteurs d'un dictionnaire
    correspondant à un seul article

    Parameters
    ----------
    d : Dict
        Dictionnaire avec toutes les infos

    Returns
    -------
    List_author : List
        List avec tous les auteurs. Le format est le suivant
        [(name1,surname1),(name2,surname2),(name3,surname3)]

    """
    List_author = []
    for k in d.keys():
        chaine = str(k)
        if chaine.endswith('NOM') and not(chaine.endswith('PRÉNOM')) and chaine.startswith('AUTHOR'):
            name = d[k].title().strip()
        if chaine.endswith('PRÉNOM') and chaine.startswith('AUTHOR'):
            surname = d[k].title().strip()
        try:
            List_author.append((name, surname))
            del(name)
            del(surname)
        except UnboundLocalError:
            pass
    return List_author


def extract_affiliation(d):
    """
    Fonction permettant d'extraire la liste des affiliations d'un dictionnaire
    correspondant à un seul article

    Parameters
    ----------
    d : Dict
        Dictionnaire avec toutes les infos

    Returns
    -------
    List_aff : List
        Liste des affiliations le résultat est du type
        ['affiliation1,'affiliation2','affiliation3']

    """
    List_aff = []
    for k in d.keys():
        chaine = str(k)
        if chaine.endswith('AFFILIATION'):
            aff = d[k]
        try:
            List_aff.append(aff)
            del(aff)
        except UnboundLocalError:
            pass
    return List_aff


def unique(L):
    """
    Fonction permettant de ne retenir que les éléments uniques d'une liste

    Parameters
    ----------
    L : List
        liste d'entrée
    Returns
    -------
    list : List
        Liste de sortoe

    """
    return [x for i, x in enumerate(L) if L.index(x) == i]


def Abstract(filename_abs_tex, dict_abs, overwrite=False):
    """
    Fonction permettant d'écrire un abstract au format LateX

    Parameters
    ----------
    filename_abs_tex : String
        Nom du fichier TeX que l'on désire.
    dict_abs : Dict
        Dictionnaire correspondant à un papier
    overwrite : Boolean
        Permet de lancer la fonction sans écraser les fichiers abstracts .tex

    Returns
    -------
    Des fichiers LaTeX (.tex) stockés dans Path_EXTEX/Abstrats

    """
    dict_abs = clean_dict(dict_abs)
    if overwrite:
        with open(Path_EXTEX + 'Abstracts/' + filename_abs_tex, 'w') as file_export_latex:
            num_id = dict_abs['SUBMISSION ID']
            title = dict_abs['TITRE']
            keywords = dict_abs['MOTS CLÉS']
            abstract = dict_abs['RÉSUMÉ']
            contact_auth_email = dict_abs['CONTACT AUTHOR EMAIL']
            if 'DOI' in dict_abs.keys():
                doi = dict_abs['DOI']

            List_author = extract_authors(dict_abs)
            List_aff = unique(extract_affiliation(dict_abs))

            write_warning(file_export_latex)
            file_export_latex.write("\\newpage\n\n")

            if 'DOI' not in dict_abs.keys():
                print("WIP : ", num_id)
                file_export_latex.write(
                    "\\backgroundsetup{contents={Work In Progress},scale=7}\n")
                file_export_latex.write("\\BgThispage\n")

            file_export_latex.write(
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            file_export_latex.write("%% Papier "+num_id+"\n")
            file_export_latex.write(
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n")
            file_export_latex.write("% Indexations\n")

            for z in List_author:
                name, surname = z
                name_clean = clean_string(name)
                surname_clean = clean_string(surname)

                file_export_latex.write("\\index{" + name_clean + surname_clean
                                        + "@"+name+", " + surname+"}\n")
            file_export_latex.write("%\n% Titre\n")
            file_export_latex.write("\\begin{flushleft}\n")
            file_export_latex.write(
                "\\phantomsection\\addtocounter{section}{1}\n")
            file_export_latex.write(
                "\\addcontentsline{toc}{section}{"+title+"}\n")
            # if 'DOI' in dict_abs.keys():
            #     pass
            # else :
            #     file_export_latex.write("\\backgroundsetup{contents=Work In Progress}")

            file_export_latex.write("{\\Large \\textbf{"+title+"}}\\label{ref:" +
                                    num_id+"}\n")
            # enclosed to be removed
            # file_export_latex.write("{\\Large \\textbf{ NUM :"+num_id+"}}\n")
            # enclosed to be removed
            file_export_latex.write("\\end{flushleft}\n")
            file_export_latex.write("%\n% Auteurs\n")

            ch_authors = ''
            for i, z in enumerate(List_author, start=1):
                name, surname = z
                if name == dict_abs['CONTACT AUTHOR NOM']:
                    mark = ',\star'
                else:
                    mark = ''
                ind_aff = List_aff.index(dict_abs['AUTHOR '+str(i) +
                                                  ' AFFILIATION']) + 1

                ch_authors += surname + ' ' + name + '$^{' + str(ind_aff) + \
                    mark + '}$, '

            ch_authors = ch_authors[:-2]
            ch_authors += "\\\\[2mm]\n"
            file_export_latex.write(ch_authors)
            file_export_latex.write("$^{\\star}$ \\Letter : \\url{" +
                                    contact_auth_email + "}\\\\[2mm]\n")
            for i, aff in enumerate(List_aff, start=1):
                file_export_latex.write(
                    "{\\footnotesize $^{"+str(i)+"}$ "+aff+"}\\\\\n")

            file_export_latex.write("[4mm]\n%\n% Mots clés\n")
            file_export_latex.write("\\noindent \\textbf{Mots clés : } "+keywords +
                                    "\\\\[4mm]\n")
            file_export_latex.write("%\n% Résumé\n")
            file_export_latex.write("\\noindent \\textbf{Résumé : } \n\n")
            file_export_latex.write("{\\normalsize\n")
            # Tcoloorbox pour les abstracts trops longs
            # file_export_latex.write("\\begin{tcolorbox}[oversize,height fill=true,"+\
            #                            "notitle,halign=justify,boxrule=0pt,colback=white,"+\
            #                            "frame empty,before upper={\parindent10mm}]\n")
            file_export_latex.write(abstract)

            if 'DOI' in dict_abs.keys():
                file_export_latex.write(
                    "\n\n \\vfill doi : \\url{https://doi.org/"+doi+"}\n")
            else:
                file_export_latex.write("\n\n \\vfill Work In Progress\n")

            # Tcoloorbox pour les abstracts trops longs
            # file_export_latex.write("\n\\end{tcolorbox}")
            file_export_latex.write("\n}\n \n")


def All_Abstracts(filename_export_OpenConf, overwrite=False):
    """
    Fonction permettant de boucler sur tous les papiers d'OpenConf. On va donc
    traiter tous les abstracts

    Parameters
    ----------
    filename_export_OpenConf : String
        Fichier exportés d'OpenConf.
    overwrite : Boolean
        Permet de lancer la fonction sans écraser les fichiers abstracts .tex
    Returns
    -------
    List_files_abs_tex : List
        Liste des fichiers TeX en sortie.
    D : Dict
        Dictionnaire avec tous les abstracts avec en clé le numéro id

    """
    List_files_abs_tex = []
    D = {}

    with open(Path_IMOC+filename_export_OpenConf, 'r') as file_export_OpenConf:
        csv_reader = csv.DictReader(
            file_export_OpenConf, delimiter=',', dialect='unix')
        for dict_abs in csv_reader:
            filename_abs_tex = 'p'+dict_abs['SUBMISSION ID']+'.tex'
            List_files_abs_tex.append(int(dict_abs['SUBMISSION ID']))
            dict_abs = clean_dict(dict_abs)
            # TODO Add WIP, Status, DOI keys to dict_abs
            # dummy DOI added to abstract
            if os.path.isfile(Path_IMOC+'PDF_articles/'+dict_abs['SUBMISSION ID']+'.pdf'):
                dict_abs['DOI'] = "10.25855/SFT2021-" + \
                    dict_abs['SUBMISSION ID'].zfill(3)
            D[int(dict_abs['SUBMISSION ID'])] = dict_abs
            Abstract(filename_abs_tex, dict_abs, overwrite)

    return List_files_abs_tex, D


def distrib_theme(filename_list_theme):
    """
    Fonction permettant de distribuer les thèmes à partir d'un fichier CSV
    donné

    Parameters
    ----------
    filename_list_theme : String
        Nom du fichier d'entrée au format CSV il doît se présenter ainsi :

            +------------+------------------------------+
            | num_id     | name_theme                   |
            +============+==============================+
            | 4          | Thermique de l'habitat       |
            +------------+------------------------------+
            | 5          | Métrologie - Identification  |
            +------------+------------------------------+
            | ...        | ...                          |
            +------------+------------------------------+

    avec ";" comme délimiteur

    Returns
    -------
    dict_theme : Dict
        Dictionnaire avec tous les papiers par thème. Chaque clé du dictionaire
        est un thème

    """

    with open(Path_IMOC+filename_list_theme) as file_list_theme:
        csv_reader = csv.DictReader(file_list_theme, delimiter=';')
        dict_theme = {}
        for line in csv_reader:
            if not(line['name_theme'] in dict_theme):
                dict_theme[line['name_theme']] = [int(line['num_id'])]
            else:
                dict_theme[line['name_theme']].append(int(line['num_id']))

    return OrderedDict(sorted(dict_theme.items(), key=lambda t: t[0]))


def write_recueil_resume(filename_choix_theme):
    """
    Fonction permettant d'écrire le recueil des résumés avec l'inclusion des
    différents abstract.inc.tex. Un dictionnaire est récupéré en sortie qui
    contient les articles par thème.

    Parameters
    ----------
    filename_choix_theme : String
        Nom du fichier d'entrée au format CSV il doît se présenter ainsi :

            +------------+------------------------------+
            | num_id     | name_theme                   |
            +============+==============================+
            | 4          | Thermique de l'habitat       |
            +------------+------------------------------+
            | 5          | Métrologie - Identification  |
            +------------+------------------------------+
            | ...        | ...                          |
            +------------+------------------------------+

        avec ";" comme délimiteur

    Returns
    -------
    dict_theme : Dict
        Dictionnaire avec tous les papiers par thème. Chaque clé du dictionaire
        est un thème

    """

    D = distrib_theme(filename_choix_theme)
    theme_number = 0
    copyfile(Path_EXTEX+"Recueil_Resume/Recueil_Resume_start.tex",
             Path_EXTEX+"Recueil_Resume/Recueil_Resume.tex")
    Recueil_Resume = open(
        Path_EXTEX+"Recueil_Resume/Recueil_Resume.tex", "a+", encoding='utf-8')
    write_warning(Recueil_Resume)
    for di in D:
        theme_number += 1
        Recueil_Resume.write('\chapter{' + di + '}\n')
        Recueil_Resume.write('\minitoc\n')
        Recueil_Resume.write(
            '\input{abstract.'+str(theme_number)+'.inc.tex}\n')
        Recueil_Resume.write('\cleardoublepage\n')
        Recueil_Resume.write('\n')
        with open(Path_EXTEX+'Recueil_Resume/abstract.'+str(theme_number)+'.inc.tex', 'w', encoding='utf-8') as file_abs_by_theme:
            file_abs_by_theme.write("%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            file_abs_by_theme.write(
                "% Theme numéro "+str(theme_number)+" : "+di+"\n")
            file_abs_by_theme.write("%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            for num_id in D[di]:
                # file_abs_by_theme.write('\\SetBgContents{Work In Progress}\n')
                file_abs_by_theme.write(
                    '\\input{../Abstracts/p'+str(num_id)+".tex}\n")
                # file_abs_by_theme.write('\\SetBgContents{}\n')

    Recueil_Resume.write('\\backmatter\n')
    Recueil_Resume.write('\part{Annexes}\n')
    Recueil_Resume.write('\phantomsection\n')
    Recueil_Resume.write('\\addtocounter{chapter}{1}\n')
    Recueil_Resume.write(
        '\\addcontentsline{toc}{chapter}{Liste des auteurs}\n')
    Recueil_Resume.write('\printindex\n')
    Recueil_Resume.write('\end{document}\n')
    Recueil_Resume.close()
    return D


def tag_doi(num_id, DictPaper, overwrite=True):
    """
    Fonction permettant de modifier les PDF (ou pas) afin d'y insérer le
    n° DOI et le lien. On renvoie un booléen pour savoir si il y a un DOI

    Parameters
    ----------
    num_id : Int
        Entier qui correspond au numéro de soumission.
    DictPaper : Dict
        Dictionnaire qui contient l'abstract.
    overwrite : Bool, optional
        Booleen qui permet de contrôler si on tague les PDF ou pas.
        The default is True.

    Returns
    -------
    bool
        On renvoie vrai si il y a un DOI.

    """
    if 'DOI' not in DictPaper.keys():
        return False  # Pas de DOI en général c'est un WIP
    filename = Path_IMOC+"PDF_articles/"+str(num_id)+".pdf"
    filename_doi = Path_IMOC+"PDF_articles/"+str(num_id)+"_doi.pdf"
    if os.path.isfile(filename_doi) and not(overwrite):
        return True  # DOI déjà fait
    if os.path.isfile(filename):
        doc = fitz.open(filename)
        page = doc[0]
        page.clean_contents()
        text_position = fitz.Point(85, page.rect.height - 30)
        rc = page.insert_text(text_position,
                              "https://doi.org/"+DictPaper['DOI'].zfill(3),
                              fontname="helv",
                              fontsize=11,
                              rotate=0,
                              color=(0, 0, 0))
        doc.save(filename_doi)
        return True
    else:
        return False


def write_recueil_actes(Dtheme):
    """
    Fonction permettant d'écrire le recueil des actes (i.e. actes.tex) avec l'inclusion des
    différents papers.inc.tex.

    Parameters
    ----------
    Dtheme : Dict
        Dictionnaire avec les thèmes en clés et les n° papiers en valeurs
        ainsi on peut avoir :

        >>> Dtheme['Milieux poreux']
        [36, 50, 92, 93, 177]
    """

    copyfile(Path_EXTEX+"Recueil_Actes/actes_start.tex",
             Path_EXTEX+"Recueil_Actes/actes.tex")
    file_recueil_acte = open(
        Path_EXTEX+"Recueil_Actes/actes.tex", "a+", encoding='utf-8')
    # nb_paper = len(List_files_abs_tex)
    nb_paper = len(os.listdir(Path_IMOC+"PDF_articles/"))//2
    count_paper = 0
    pass_tome = True
    for num_theme, theme in enumerate(Dtheme):
        file_recueil_acte.write("\n\chapter{"+theme+"}\n")
        file_recueil_acte.write("\minitoc \n")
        file_recueil_acte.write(
            "\\input{paper."+str(num_theme+1)+".inc.tex} \n")
        if count_paper > nb_paper//2 and pass_tome:
            file_recueil_acte.writelines(["\n%%%%%%% T2 %%%%% \n", "\cleardoublepage \n",
                                          "\phantomsection \n",
                                          "\\addcontentsline{toc}{part}{Tome 2} \n\n"])
            pass_tome = False

        file_theme = open(Path_EXTEX+"Recueil_Actes/paper." +
                          str(num_theme+1)+".inc.tex", "w", encoding='utf-8')
        file_theme.write("%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        file_theme.write("% Theme numéro "+str(num_theme+1) +
                         " | Nom : "+theme+"\n")
        file_theme.write("%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

        for num_id in Dtheme[theme]:
            if tag_doi(num_id, D_abs[num_id], overwrite=True):
                count_paper = count_paper + 1
                file_theme.write("\\input{../Actes/p"+str(num_id)+".tex}\n")
                filein = open(Path_EXTEX+"Abstracts/p" +
                              str(num_id)+".tex", "r", encoding='utf-8')
                linesin = filein.readlines()
                filein.close()
                linesin[8] = "\\cleardoublepage\n"
                index = linesin.index('\\begin{flushleft}\n')
                linesin = linesin[:index]+linesin[index+1:index+3]
                linesin.append("\\label{ref:"+str(num_id)+"}\n")
                linesin.append("\\includepdf[pages=-,pagecommand={\\thispagestyle{fancyplain}},width=1.05\paperwidth]{" +
                               "../."+Path_IMOC+"PDF_articles/"+str(num_id)+"_doi.pdf}\n")
                fileout = open(Path_EXTEX+"Actes/p"+str(num_id) +
                               ".tex", "w", encoding='utf-8')
                fileout.writelines(linesin)
                fileout.close()

        file_theme.close()

    file_recueil_acte.writelines(open(
        Path_EXTEX+"Recueil_Actes/actes_end.tex", "r", encoding='utf-8').readlines())
    file_recueil_acte.close()


def write_index_html(Dtheme, Dall, base_url):
    """
    Fonction permettant de générer le fichier de la table des matières en
    markdown 'Table_of_contents.md'

    Parameters
    ----------
    Dtheme : Dict
        Dictionnaire avec les thèmes en clés et les n° papiers en valeurs
        ainsi on peut avoir :

        >>> Dtheme['Milieux poreux']
        [36, 50, 92, 93, 177]

    Dall : Dict
        Dictionnaire de tous les abstracts avec les id en clé
        ainsi on a :

        >>> D_abs[1]
        {'SUBMISSION ID': '1',
         'SUBMISSION DATE': '2020-11-16',
         'LAST UPDATED': '2021-03-26',
         ...
         'CHAIR NOTES': 'Résumé bien structuré. Merci de corriger les coupures de mots.',
         'DOI': '10.25855/SFT2021-001'}

    base_url : Str
        Chaîne de caractères avec l'URL sur le site de la SFT.

    Returns
    -------
    None.

    """
    fileheader = open(Path_HTML+"Table_of_contents_start.md",
                      "r", encoding='utf-8')
    header = ''.join(fileheader.readlines())
    fileheader.close()
    with open(Path_HTML+"Table_of_contents.md", "w", encoding='utf-8') as index_md:
        index_md.write(header)
        for theme in Dtheme:
            index_md.write("### "+theme+'\n\n')
            for num_id in Dtheme[theme]:
                index_md.write("["+Dall[num_id]['TITRE']+"]")
                index_md.write("("+base_url+"p"+str(num_id)+".html)<br>")
                auteurs = extract_authors(Dall[num_id])
                index_md.write(
                    ', '.join(list(map(lambda x: x[1]+" "+x[0], auteurs))))
                index_md.write('\n')
                index_md.write('\n')
    current_path = os.getcwd()
    os.chdir(Path_HTML)
    # print(title)
    Mesg = '/usr/bin/pandoc --quiet -s -t html5 -c markdown-pandoc.css' +\
        ' --metadata charset="utf-8" Table_of_contents.md ' +\
        ' -o Table_of_contents.html'
    print("\n"+20*"="+"\n")
    print("""
          Pour générer l'index HTML des articles il faut taper les commandes
          suivantes
          """)
    print(Mesg)
    os.system(Mesg)
    os.chdir(current_path)


if __name__ == "__main__":
    Path_EXF = './Export_Files/'
    Path_EXTEX = './Export_Tex/'
    Path_IMOC = './Imports_OpenConf/'
    Path_HTML = './Export_HTML/'
# %% Tableau reviewers

    tableau_reviewer("Tableau_Reviewer.csv", 3)

# %% Traitement Abstract
    filename_export_OpenConf = 'openconf-SFT2021-submissions-all'+'.csv'
    List_files_abs_tex, D_abs = All_Abstracts(
        filename_export_OpenConf, overwrite=False)

# %% Initialisation des themes et des Biot-Fourier

    Biot_Fourier = [8, 12, 31, 35, 48, 71]

# %% Création du recueil des résumés

    Dtheme = write_recueil_resume('choix_theme.csv')

    print("""
          Pour générer le recueil des résumés il faut vérifier
          tous les abstracts et ensuite lancer les commandes

          cd """+Path_EXTEX+"Recueil_Resume"+"""
          latexmk -CA
          latexmk -CF --silent -pdf -jobname=Resumes_SFT2021 Recueil_Resume.tex
          """)

# %% Création de l'index HTML des articles
    base_URL = "https://www.sft.asso.fr/DOIeditions/CFT2021/Abstracts/"
    write_index_html(Dtheme, D_abs, base_URL)


# %% Création des actes*
    print("\n"+20*"="+"\n")
    write_recueil_actes(Dtheme)
    print("""
          Pour générer le recueil des actes il faut vérifier
          lancer les commandes

          cd """+Path_EXTEX+"Recueil_Actes"+"""
          latexmk -CA
          latexmk -CF --silent -jobname=Actes_SFT2021 -pdf actes.tex
          """)

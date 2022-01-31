#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:05:06 2021

@author: phil
"""
# from io import StringIO
import os
import re
from lxml import etree
from xml.dom import minidom
import unicodedata
import csv

import fitz


def commentline(L, nums_row):
    """
    Fonction permettant de commenter des lignes de texte en ajoutant
    un % au début

    Parameters
    ----------
    L : List
        Liste avec les lignes.
    nums_row : List
        Liste d'entiers qui correspondent aux numéros des lignes.

    Returns
    -------
    L : Liste
        Liste avec les commentaires.

    """
    if type(nums_row) == int:
        nums_row = [nums_row]
    for num in nums_row:
        L[num] = '%'+L[num]
    return L


def uncommentline(L, nums_row):
    """
    Fonction permettant de décommenter des lignes de texte en supprimant
    un % au début

    Parameters
    ----------
    L : List
        Liste avec les lignes.
    nums_row : List
        Liste d'entiers qui correspondent aux numéros des lignes.

    Returns
    -------
    L : Liste
        Liste sans les commentaires.

    """
    if type(nums_row) == int:
        nums_row = [nums_row]

    for num in nums_row:
        L[num] = L[num][1:]
    return L


def textohtml(filename_abstex):
    """
    Fonction permettant de générer un fichier LaTex et HTML d'un abstract donné.
    Le fichier TeX est différent de celui du recueil des résumés. On charge le 
    fichier initial que l'on modifie pour en faire un document complet qui peut
    ensuite compilé en HTML à l'aide de pandoc

    Parameters
    ----------
    filename_abstex : Str
        Nom du fichier TeX d'un abstract qui se trouve dans le recueil des
        résumés.

    Returns
    -------
    None.
        Création de fichiers .tex et. html

    """
    testtex = open(path+filename_abstex, "r", encoding='utf-8')
    L_text = testtex.readlines()
    testtex.close()
    ind_title = L_text.index('\\phantomsection\\addtocounter{section}{1}\n')+1
    title = L_text[ind_title][31:-2]
    ind_affiliation = L_text.index("[4mm]\n")
    ind_auteurs = L_text.index('% Auteurs\n')+1
    L_affiliation = L_text[ind_auteurs+2:ind_affiliation]
    L_affiliation = [(el[18], el[22:-4]) for el in L_affiliation]
    auteurs = L_text[ind_auteurs].split('}$, ')
    L = []
    for s in auteurs:
        pos = s.index("$^{")
        aff_num = s[pos+3]
        if s.count("\\star") > 0:
            L.append((aff_num, s[:pos], "ref"))
        else:
            L.append((aff_num, s[:pos]))
    auteurs = L
    # print(auteurs)
    del(L)
    num_id = filename_abstex[1:-4]
    L_text = commentline(L_text, list(range(ind_title+1)))
    L_text = uncommentline(L_text, ind_title-2)
    L_text[ind_title+1] = L_text[ind_title +
                                 1][:L_text[ind_title+1].find("label{")-1]+'\n'
    L_text = ["\\begin{document}\n"] + L_text
    L_text = ["\input{../config_html.tex}\n"] + L_text
    L_text = ["\documentclass[a4paper]{article}\n"] + L_text
    if os.path.isfile(path_pdf+num_id+'_doi.pdf'):
        L_text = L_text + ["\\vfill PDF : \\href{https://www.sft.asso.fr/DOIeditions/CFT2021/PDF/" +
                           num_id+"_doi.pdf}{download}"]
    L_text = L_text + ["\end{document}\n"]

    with open(path_tex_html + filename_abstex, 'w') as file_export_latex:
        file_export_latex.writelines(L_text)
    os.chdir(path_tex_html)
    # print(title)

    os.system('/usr/bin/pandoc --quiet -s -f latex -t html5 ' +
              ' -c markdown-pandoc.css ' +
              ' --metadata charset="utf-8" ' +
              filename_abstex+' -o '+path_html+filename_abstex[:-3]+'html')


def extractdata_abs(filename_abstex_for_html):
    """
    Fonction permettant d'extraire les données d'un fichier TeX d'un abstract 
    pour HTML.  

    Parameters
    ----------
    filename_abstex_for_html : Str
        Nom du fichier TeX d'un abstract qui se trouve dans le répertoire 
        des fichiers TeX pour le HTML.

    Returns
    -------
    list
        On renvoie une liste avec les données suivantes.
        [filename_abstex_for_html, title, auteurs, resume, keywords].

    """
    testtex = open(path_tex_html+filename_abstex_for_html,
                   "r", encoding='utf-8')
    L_text = testtex.readlines()
    testtex.close()
    ind_auteurs = list(
        range(L_text.index('%% Indexations\n')+1, L_text.index('%% Titre\n')-1))
    auteurs = []
    for ind in ind_auteurs:
        auteurs.append(L_text[ind].split('@')[1][:-2].split(','))
        auteurs[-1][1] = auteurs[-1][1].strip()
    ind_affiliation = list(
        range(L_text.index('% Auteurs\n')+3, L_text.index("[4mm]\n")))
    title = L_text[ind_affiliation[0]-6]
    title = title[16:title.rindex('}')-1]
    line_auteurs = L_text[ind_affiliation[0]-2]
    # print(line_auteurs)
    try:
        resume_start_ind = L_text.index("{\\normalsize\n")+1
    except ValueError:
        resume_start_ind = L_text.index("{\\small\n")+1
    resume_end_ind = len(L_text)-5
    resume = ''.join(L_text[resume_start_ind:resume_end_ind])

    keywords = re.split(";|,", L_text[L_text.index("% Résumé\n")-2][32:-8])

    for auteur in auteurs:
        # print(auteur)
        aff_num = int(line_auteurs[line_auteurs.index(
            auteur[0]+"$")+len(auteur[0])+3])
        aff = L_text[ind_affiliation[aff_num-1]].split('}$ ')[1][:-4]
        auteur.append(aff)
    return [filename_abstex_for_html, title, auteurs, resume, keywords]


def writexml(filename_abstex_for_html):
    """
    Fonction qui crée un fichier XML à partir d'un fichier TeX

    Parameters
    ----------
    filename_abstex_for_html : Str
        Nom du fichier TeX d'un abstract qui se trouve dans le répertoire 
        des fichiers TeX pour le HTML.

    Returns
    -------
    None.
        Création d'un fichier XML.

    """
    rawdata = extractdata_abs(filename_abstex_for_html)
    num_id = rawdata[0][1:-4].zfill(3)
    schemaLocation = "http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.3/metadata.xsd"
    xmlns = "http://datacite.org/schema/kernel-4"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    metadata = etree.Element("{" + xmlns + "}resource",
                             attrib={
                                 "{" + xsi + "}schemaLocation": schemaLocation},
                             nsmap={'xsi': xsi, None: xmlns})
    comment = etree.Comment('Generated for SFT by P. Baucour with Python')
    metadata.append(comment)

    identifier = etree.SubElement(metadata, "identifier", attrib={
                                  'identifierType': 'DOI'})
    identifier.text = '10.25855/SFT2021-'+num_id
    auteurs = etree.SubElement(metadata, "creators")
    for auteur in rawdata[2]:
        creator = etree.SubElement(auteurs, "creator")
        creatorName = etree.SubElement(creator, "creatorName", attrib={
                                       'nameType': 'Personal'})
        creatorName.text = auteur[0]+', '+auteur[1]
        givenName = etree.SubElement(creator, 'givenName')
        givenName.text = auteur[1]
        familyName = etree.SubElement(creator, 'familyName')
        familyName.text = auteur[0]
        affiliation = etree.SubElement(creator, "affiliation")
        affiliation.text = auteur[2]

    titles = etree.SubElement(metadata, "titles")
    title = etree.SubElement(titles, "title")
    title.text = rawdata[1]
    publisher = etree.SubElement(metadata, "publisher")
    publisher.text = "Société Française de Thermique"
    publicationYear = etree.SubElement(metadata, "publicationYear")
    publicationYear.text = '2021'
    subjects = etree.SubElement(metadata, "subjects")
    for sub in rawdata[-1]:
        subject = etree.SubElement(subjects, "subject")
        subject.text = sub

    lang = etree.SubElement(metadata, "language")
    lang.text = 'FR'
    ress_type = etree.SubElement(metadata, 'resourceType', attrib={
                                 'resourceTypeGeneral': 'Text'})
    ress_type.text = 'Acte de congrès'

    descriptions = etree.SubElement(metadata, "descriptions")
    description = etree.SubElement(descriptions, "description",
                                   attrib={'descriptionType': "Abstract"})
    description.text = rawdata[-2]

    # print(etree.tostring(metadata, pretty_print=True, encoding='utf-8',
    #                     xml_declaration=True).decode("utf-8"))

    xmlfile = open(path_xml+filename_abstex_for_html[:-4]+".xml", "w")
    xmlfile.write(etree.tostring(metadata).decode('utf-8'))
    xmlfile.close()


if __name__ == '__main__':

    rootpath = os.getcwd()
    path = rootpath+'/Export_Tex/Abstracts/'
    path_tex_html = rootpath+'/Export_Tex/Abstracts_Tex_HTML/'
    path_html = rootpath+'/Export_HTML/Abstracts/'
    path_pdf = rootpath+'/Imports_OpenConf/PDF_articles/'
    path_xml = rootpath+'/Export_XML/'
    path_actes = rootpath+'/Export_Tex/Actes/'

    print('========= TeX for HTML ===========')
    for filetex in os.listdir(path):
        # print(filetex)
        textohtml(filetex)

    print('========= XML ===========')
    for filetex in os.listdir(path_tex_html):
        if os.path.isfile(path_actes+filetex):  # check si doi
            writexml(filetex)

    list_xml = os.listdir(path_xml)
    try:
        list_xml.remove('listing_SFT2021_xml.txt')
    except ValueError:
        pass
    list_url = list(map(lambda xml_file: "https://www.sft.asso.fr/DOIeditions/CFT2021/Abstracts/p" +
                        xml_file[1:-4]+".html", list_xml))
    list_doi = list(map(lambda xml: '10.25855/SFT2021-' +
                    xml[1:-4].zfill(3), list_xml))
    # textohtml('p97.tex')
    Tab = list(zip(list_doi, list_url))
    Tab = list(map(list, Tab))

    os.chdir(rootpath)
    with open(path_xml+'listing_SFT2021_xml.txt', 'w', newline="") as myfile:
        wr = csv.writer(myfile, dialect='excel', delimiter='\t')
        wr.writerows(Tab)

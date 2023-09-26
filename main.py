import streamlit as st

import HCurve as HC
import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime as dt
import plotly.graph_objects as go



############################################ Streamlit Settings ############################################

Title = "Plantonio"
st.set_page_config(page_title= Title,
                   page_icon= ":hot_pepper",
                   layout = "wide") 

############################################ Utilitaires ############################################
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "What's Antonio's plant name? No Caps", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "What's Antonio's plant name? No Caps", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True
    

    
def date_diff(date,starting_date):
    #format "years-months-days hours:min:sec"
    d1 = dt.strptime(starting_date, "%Y-%m-%d %H:%M:%S")
    d2 = dt.strptime(date, "%Y-%m-%d %H:%M:%S")
    st.write(d1-d2)
    return (d2-d1).seconds

############################################ Variables Globales ############################################
PV_Quantities = HC.PV_Quantities #["V","pH","DO","T","N","Default","Pump.F","Pump.V","Gas.OF","X","Gas.F","TR"]
SP_Quantities = HC.SP_Quantities #["pH","DO","T","N","Default","Pump.F","Gas.OF","X","Gas.F"]
PV_Quantities_to_display = HC.PV_Quantities_to_display
SP_Quantities_to_display = []
markers=[15,101,102,100,142,134,135,129,130,132,127,128]

colorset = [(244,184,52),
            (56,194,176),
            (242,138,118),
            (148,126,112),
            (6,178,210),
            (152,116,174),
            (152,116,174),
            (18,138,138),
            (218,142,218),
            (188,84,94),
            (102,144,196),
            (168,90,174),
            (248,158,148),
            (8,172,120),
            (146,254,148),
            (24,230,140),
            (154,204,50),
            (134,206,234),
            (62,114,64),
            (240,128,128),
            (210,180,140),
            (254,104,180),
            (150,62,68),
            (6,28,62),
            (170,230,242),
            (148,126,112)
         ]

# Colors= {"T" : (244,184,52),
#          "DO" : (56,194,176),
#          "pH" : (242,138,118),
#          "RD" : (148,126,112),
#          "Gas.F" : (6,178,210),
#          "Pump.F" : (152,116,174),
#          "Pump.V" : (152,116,174),
#          "X" : (18,138,138),
#          "V" : (218,142,218),
#          "N" : (188,84,94),
#          "AU" : (102,144,196),
#          "CX" : (168,90,174),
#          "G" : (248,158,148),
#          "M" : (8,172,120),
#          "U" : (146,254,148),
#          "I" : (24,230,140),
#          "R" : (154,204,50),
#          "MT" : (134,206,234),
#          "Gas.V" : (62,114,64),
#          "PF" : (240,128,128),
#          "PFT" : (210,180,140),
#          "TR" : (254,104,180),
#          "VT" : (150,62,68),
#          "Pr" : (6,28,62),
#          "Gas.OF" : (170,230,242),
#          "Default": (148,126,112)
#          }

Colors= {"T" : "#f4b834",
         "DO" : "#38c2b0",
         "pH" : "#f28a76",
         "RD" : "#947e70",
         "Gas.F" : "#06b2d2",
         "Pump.F" : "#9874ae",
         "Pump.V" : "#9874ae",
         "X" : "#128a8a",
         "V" : "#da8eda",
         "N" : "#bc545e",
         "AU" : "#6690c4",
         "CX" : "#a85aae",
         "G" : "#f89e94",
         "M" : "#08ac78",
         "U" : "#92fe94",
         "I" : "#18e68c",
         "R" : "#9acc32",
         "MT" : "#86ceea",
         "Gas.V" : "#3e7240",
         "PF" :"#f08080",
         "PFT" : "#d2b48c",
         "TR" :"#fe68b4",
         "VT" : "#963e44",
         "Pr" : "#061c3e",
         "Gas.OF" : "#aae6f2",
         "Default": "#947e70"
         }



EU= {"T" : "°C",
     "DO" : "%DO",
     "pH" : "pH",
     "RD" : "mV",
     "Gas.F" : "sL/h",
     "Pump.F" : "mL/h",
     "Pump.V" : "mL",
     "X" : "%",
     "V" : "mL/h",
     "N" : "rpm",
     "AU" : "AU",
     "CX" : "CX",
     "G" : "\u03BCS",
     "M" : "g",
     "U" : "mV",
     "I" : "nA",
     "R" : "Ohm",
     "MT" : "mNm",
     "Gas.V" : "sL",
     "PF" : "\u03BCmol/s",
     "PFT" : "\u03BCmol",
     "TR" : "mMol/h",
     "VT" : "mMol",
     "Pr" : "bar",
     "Gas.OF" : "sL/h",
     "Default": ""
     }

############################################ Data Processing #############################################
@st.cache_data
def CSV_read(csv_file):
    
    ## Conversion du fichier depuis Streamlit ##
    # La conversion en dataframe est évitée, en effet elle n'apprécie pas que le nombre de colonnes fluctue autant et supprime le fichier sous forme de bytes_data
    # On passe par une conversion classique en lignes
    
    bytes_data = csv_file.read()
    lines= bytes_data.decode("utf-8").splitlines() 
    
    ## Recensement des indexs associés à chaque section ##
    Cat_idx = {} # Dictionnaire qui associe à chaque titre de section de type "[Section]" le numéro de la ligne associée
    for i in range(len(lines)):
        if lines[i][:2] == '"[':
            Cat_idx[lines[i].strip("\"")] = i
            
    ## Initialisation
    Units_OnOff = {} # dictionnaire qui associe à chaque unité un booléen pour savoir si cette dernière est active ou pas  
    
    TrackDatas=[] # liste contenant les différents dictionnaires associés à chaque TrackData
    
    TrackInfo= pd.DataFrame([]) # DataFrame de la section grâce à laquelle les associations et la sélection des colonnes sont faites
    
    ## Completing Active Units ##
    if "[Unit]" in Cat_idx.keys() and "[Units]" in Cat_idx.keys() and "[Sensors]" in Cat_idx.keys() and "[Requirements]" in Cat_idx.keys():
        Units = [(line.replace("\"",'').split(";"))[0] for line in lines[Cat_idx["[Units]"]+2:Cat_idx["[Sensors]"]-1]] ## Sans headers, [Units] et [Sensors]  (type: List of Strings)
        # on initialise avec des False en entrant les noms des unités comme clés du dictionnaire 
        for Unit in Units: 
            Units_OnOff[Unit]=False
        # Dans la section requirements, on relève les unités actives
        for Unit in [(line.replace("\"",'').split(";"))[0] for line in lines[Cat_idx["[Unit]"]+2:Cat_idx["[Requirements]"]-1]]:
            Units_OnOff[Unit] = True
    
    ## Completing TrackInfo ##
    if "[TrackInfo]" in Cat_idx.keys() and"[TrackData]" in Cat_idx.keys():
        ## méthode plus archaïque car des colonnes sont vides et un problème de dimensionnement apparait entre les headers et les datas
        TrackInfo=pd.DataFrame([], columns=lines[Cat_idx["[TrackInfo]"]+1].replace("\"",'').split(";"))
        for line in [line.replace("\"",'').split(";") for line in lines[Cat_idx["[TrackInfo]"]+2:Cat_idx["[TrackData]"]-1]]:
            TrackInfo.loc[len(TrackInfo)] = line+[None for i in range(len(TrackInfo.keys())-(len(line)))]

    ## Extracting & Completing Datas
    if "[TrackData]" in Cat_idx.keys() and "[TrackInfo]" in Cat_idx.keys() and "[Events]" in Cat_idx.keys():
        iTrackInfo = list(Cat_idx).index("[TrackInfo]") # numéro de la section TrackIngo
        iTrackData = list(Cat_idx).index("[TrackData]") # numéro de la section TrackData
        iTrackEvents = list(Cat_idx).index("[Events]") # numéro de la section Events
        nTrackData = iTrackEvents - iTrackData -1 # nombre de sous sections i.e. de TrackData
        
        TrackData_names=["[TrackData"+ str(1+i) + "]" for i in range(nTrackData) ] # liste des "sous-sections" à chercher

        for i in range(nTrackData):
            data_srow = Cat_idx[TrackData_names[i]]+1 # ligne ou le tableau commence
            # on détermine la ligne de fin
            data_erow = 0 ## initialisation 
            if i+1==nTrackData: ## Cas du dernier TrackDatas
                data_erow = Cat_idx["[Events]"] -1  #Sans [TrackData1], les headers, et le saut de ligne à la fin
            else: ## Cas si la prochaine section est aussi un TrackData
                data_erow = Cat_idx[TrackData_names[i+1]] - 1 #Idem avec [TrackDatai] et [Trackdatai+1] et le saut de ligne à la fin
            # on extrait et formate le tableau sous forme de liste
            TrackDatai = [(line.replace("\"",'').split(";")) for line in lines[data_srow:data_erow]]
            # on l'ajoute à la liste TrackDatas sous forme de DataFrame
            TrackDatas.append(pd.DataFrame(TrackDatai[1:], columns = TrackDatai[0]))
    
    if "[Internal Values]" in Cat_idx.keys():
        # Inutile pour l'instant
        test = [line.replace("\"",'').split(";") for line in lines[Cat_idx["[Internal Values]"]+1:Cat_idx["[Setups]"]-1]]


    ## Extracting Events
    
    if "[Events]" in Cat_idx.keys() and "[End]" in Cat_idx.keys():
        Events = pd.DataFrame(data= [line.replace("\"",'').split(";") for line in lines[Cat_idx["[Events]"]+2:Cat_idx["[End]"]]], 
                              columns = lines[Cat_idx["[Events]"]+1].replace("\"",'').split(";")
                              )
       
    return Units_OnOff, TrackInfo, TrackDatas, Events

############################################### Streamlit ################################################

## Initialisations
def Init_st_TrackData(TrackData_i : str, TrackInfo: object, Units_On: list, df: object):
    if TrackData_i not in st.session_state:
        st.session_state[TrackData_i] = HC.TrackData(TrackInfo,Units_On,df)
    return

def Init_st_PV_Display(TrackData_i : str, Unit : str):
    if TrackData_i+"/"+Unit+"/PV/Display" not in st.session_state:
        PV_D = {}
        for Quantity in PV_Quantities :
            if Quantity in PV_Quantities_to_display:
                PV_D[Quantity]=True
            else:
                PV_D[Quantity]=False
        st.session_state[TrackData_i+"/"+Unit+"/PV/Display"]=PV_D
    return

def Init_st_SP_Display(TrackData_i : str, Unit : str):
    if TrackData_i+"/"+Unit+"/SP/Display" not in st.session_state:
        SP_D = {}
        for Quantity in SP_Quantities:
            if Quantity in SP_Quantities_to_display:
                SP_D[Quantity]=True
            else:
                SP_D[Quantity]=False
        st.session_state[TrackData_i+"/"+Unit+"/SP/Display"]=SP_D
    return

def Init_st_Display_Settings(TrackData_i : str, Unit : str):
    ## [{TrackData_i}/{Unit}/PV/Display] est une liste de booléen pour savoir si la quantité en PV est à afficher ou pas
    ## [{TrackData_i}/{Unit}/SP/Display] est une liste de booléen pour savoir si la quantité en PV est à afficher ou pas
    ## [{TrackData_i}/{Unit}/PV/Display/{CurveName}] est un booléen pour savoir si la courbe PV en question est à afficher ou pas
    ## [{TrackData_i}/{Unit}/SP/Display/{CurveName}] est un booléen pour savoir si la courbe SP en question est à afficher ou pas
    ### Le booléen sur la quantité est prioritaire sur le booléen de la courbe
    ## [Show_markers] est un booléen selon lequel on affiche ou pas les markers sur la courbes
    
    Init_st_PV_Display(TrackData_i, Unit)
    Init_st_SP_Display(TrackData_i, Unit)
    
    for Quantity in PV_Quantities :
        for Curve in st.session_state[TrackData_i].Units[Unit].PV[Quantity]:
            if TrackData_i+"/"+Unit+"/PV/Display/"+ Curve.display_name not in st.session_state:
                st.session_state[TrackData_i+"/"+Unit+"/PV/Display/" + Curve.display_name]= True
    
    for Quantity in SP_Quantities :
        for Curve in st.session_state[TrackData_i].Units[Unit].SP[Quantity]:
            if TrackData_i+"/"+Unit+"/SP/Display/"+ Curve.display_name not in st.session_state:
                st.session_state[TrackData_i+"/"+Unit+"/SP/Display/" + Curve.display_name]= True
    
    if "Show_markers" not in st.session_state:
        st.session_state.Show_markers = False
    
    return

def Init_st_Colors():
    for Quantity in Colors.keys():
        if Quantity+"/Color" not in st.session_state:
            st.session_state[Quantity+"/Color"] = Colors[Quantity]
    return


## Updates: 
    
def Update_st_PV_switch(TrackData_i : str, Unit : str, Quantity_to_update: str):
    Init_st_PV_Display(TrackData_i, Unit)
    if TrackData_i+"/"+Unit+"/PV/Display" in st.session_state:
        st.session_state[TrackData_i+"/"+Unit+"/PV/Display"][Quantity_to_update] = not st.session_state[TrackData_i+"/"+Unit+"/PV/Display"][Quantity_to_update]

def Update_st_SP_switch(TrackData_i : str, Unit : str, Quantity_to_update: str):
    Init_st_SP_Display(TrackData_i, Unit)
    if TrackData_i+"/"+Unit+"/SP/Display" in st.session_state:
        st.session_state[TrackData_i+"/"+Unit+"/SP/Display"][Quantity_to_update]= not st.session_state[TrackData_i+"/"+Unit+"/SP/Display"][Quantity_to_update]
    return

## Display
def Display_st_sidebar(TrackData_i : str, Unit: str, TrackInfo: object, Units_On: list, df: object):
    ## La fenêtre latérale présente en un bouton à bascule pour l'affichage des marqueurs (courbes)
    ## 2 colonnes (st.columns()) avec d'une part les couleurs associées à chaque grandeur et d'autre part
    ## deux onglets "PV - On/Off" et "SP - On/Off" pour choisir l'affichage des Quantités et des courbes
    
    Init_st_TrackData(TrackData_i, TrackInfo, Units_On, df)
    Init_st_Colors()
    
    with st.sidebar:
        st.title("Editor")
        ## Markers ##
        if "Show_markers" not in st.session_state:
            st.session_state.Show_markers = False
        st.toggle("Show Markers", key="Show_markers")#,bool=st.session_state.Show_markers)
        
        ## Colonnes
        sb_col1, sb_col2 = st.columns([2,4])
        
        ## Colors ##
        with sb_col1:
            st.header("Colors")
            for Quantity in Colors.keys():
                st.color_picker(label = Quantity + " ["+ EU[Quantity]+ "]",
                                            key = Quantity + "/Color",
                                            # disabled=True,
                                            label_visibility="visible")
            # couleurs = [st.color_picker(label = Quantity,
            #                             key = Quantity + "/Color",
            #                             disabled=True,
            #                             label_visibility="visible")
            #             for Quantity in PV_Quantities]
            
        ## On/Off PV ##
        with sb_col2:
            sb_tabs1, sb_tabs2 = st.tabs(["PV","SP"])
            
            with sb_tabs1:
                st.header("PV - On/Off")
                
                for Quantity in PV_Quantities:
                    ## Checkbox pour afficher ou pas la Quantité en question 
                    st.checkbox(label= Quantity,
                                key="PV_On/Off"+ Quantity,
                                value=st.session_state[TrackData_i+"/"+Unit+"/PV/Display"][Quantity],
                                on_change=Update_st_PV_switch,
                                args= (TrackData_i,Unit,Quantity)
                            )
                    ## dessous, un onglet déroulant contenant des checkbox concernant l'affichage des courbes
                    with st.expander("Curves to show"):
                        for Curve in st.session_state[TrackData_i].Units[Unit].PV[Quantity]:
                                # st.write(Curve.display_name)
                                st.checkbox(label = Curve.display_name,
                                            key = TrackData_i+"/"+Unit+"/PV/Display/" + Curve.display_name)
                                
            with sb_tabs2:              
                st.header("SP - On/Off")
                
                for Quantity in SP_Quantities:
                    ## Checkbox pour afficher ou pas la Quantité en question
                    st.checkbox(label= Quantity,
                                key="SP_On/Off"+ Quantity,                       
                                value=st.session_state[TrackData_i+"/"+Unit+"/SP/Display"][Quantity],
                                on_change=Update_st_SP_switch,
                                args= (TrackData_i,Unit,Quantity)
                                )
                    ## dessous, un onglet déroulant contenant des checkbox concernant l'affichage des courbes
                    with st.expander("Curves to show"):
                        for Curve in st.session_state[TrackData_i].Units[Unit].SP[Quantity]:
                                # st.write(Curve.display_name)
                                st.checkbox(label = Curve.display_name,
                                            key = TrackData_i+"/"+Unit+"/SP/Display/" + Curve.display_name)
    return

def Bool_to_markers_mode(Bool):
    if Bool:
        return "lines+markers"
    else:
        return "lines"

def PV_Which_yaxis(TrackData_i: str, Unit:str, Quantity:str):
    #retourne "y" si la quantité est la première à être affichée
    #retourne "y{numéro}" sinon (numéro>=2)
    Init_st_PV_Display(TrackData_i, Unit)
    number = 0
    for Q in PV_Quantities:
        if st.session_state[TrackData_i+"/"+Unit+"/PV/Display"][Q]:
            number +=1
        if Q == Quantity:
            if number ==1:
                return "y"
            else:
                return "y"+str(number)
    return "y"

def SP_Which_yaxis(TrackData_i: str, Unit:str, Quantity:str):
    #retourne "y" si la quantité est la première à être affichée
    #retourne "y{numéro}" sinon (numéro>=2)
    Init_st_SP_Display(TrackData_i, Unit)
    number = 0
    for Q in SP_Quantities:
        if st.session_state[TrackData_i+"/"+Unit+"/SP/Display"][Q]:
            number +=1
        if Q == Quantity:
            if number ==1:
                return "y"
            else:
                return "y"+str(number)
    return "y"

def Display_st_PV_plots(TrackData_i : str, Unit :str, PV_fig: object):
    
    Init_st_Display_Settings(TrackData_i, Unit)
    Init_st_Colors()
    for Quantity in PV_Quantities:    
        if st.session_state[TrackData_i+"/"+Unit+"/PV/Display"][Quantity]:
            ynumber = PV_Which_yaxis(TrackData_i, Unit, Quantity)
            Qcolor = st.session_state[Quantity+"/Color"]
            j=0
            
            for Curve in st.session_state[TrackData_i].Units[Unit].PV[Quantity]:
                if st.session_state[TrackData_i+"/"+Unit+"/PV/Display/" + Curve.display_name]:
                    PV_fig.add_trace(go.Scatter(
                        mode= Bool_to_markers_mode(st.session_state.Show_markers),
                        x=Curve.XY.Timestamp,
                        y=Curve.XY[Curve.name],
                        name = Curve.display_name,
                        marker_symbol=markers[j%len(markers)],
                        line = dict(color = Qcolor),
                        showlegend=False,
                        yaxis=ynumber
                        )
                    )
                j+=1
            if  ynumber == "y":
                PV_fig.layout['yaxis'] = dict(title=Quantity + "["+ EU[Quantity]+ "]",
                                              titlefont = dict(
                                                  color = Qcolor
                                                  ),
                                              tickfont = dict(
                                                  color = Qcolor
                                                  )
                                          )
            else: 
                PV_fig.layout['yaxis'+ ynumber[1:]]= dict(title=Quantity + " ["+ EU[Quantity]+ "]",
                                                          titlefont = dict(
                                                          color = Qcolor
                                                          ),
                                                          tickfont = dict(
                                                          color = Qcolor
                                                          ),
                                                          side=["left","right"][(int(ynumber[1:])-1)%2],
                                                          anchor="free",
                                                          overlaying="y",
                                                          autoshift = True,
                                                          shift=[-15,15][(int(ynumber[1:])-1)%2]                                                          
                                                      )
    PV_fig.update_layout(height=800)
    st.plotly_chart(PV_fig,
                    use_container_width=True,
                    config ={'scrollZoom': True,
                                    'toImageButtonOptions': {
                                        'format': 'svg', # one of png, svg, jpeg, webp
                                        'filename': 'custom_image',
                                        'height': 500,
                                        'width': 700,
                                        'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
                                      }
                                    }
                    )
    return

def Display_st_SP_plots(TrackData_i : str, Unit :str, SP_fig: object):
    
    Init_st_Display_Settings(TrackData_i, Unit)
    
    for Quantity in SP_Quantities:    
        if st.session_state[TrackData_i+"/"+Unit+"/SP/Display"][Quantity]:
            ynumber = SP_Which_yaxis(TrackData_i, Unit, Quantity)
            Qcolor = st.session_state[Quantity + "/Colors"]   
            j=0
            
            for Curve in st.session_state[TrackData_i].Units[Unit].SP[Quantity]:
                if st.session_state[TrackData_i+"/"+Unit+"/SP/Display/" + Curve.display_name]:
                    SP_fig.add_trace(go.Scatter(
                        mode= Bool_to_markers_mode(st.session_state.Show_markers),
                        x=Curve.XY.Timestamp,
                        y=Curve.XY[Curve.name],
                        name = Curve.display_name,
                        marker_symbol=markers[j%len(markers)],
                        line = dict(color = Qcolor),
                        showlegend=False,
                        yaxis=ynumber
                        )
                    )
                j+=1
            if  ynumber == "y":
                SP_fig.layout['yaxis'] = dict(title=Quantity + "["+ EU[Quantity]+ "]",
                                              titlefont = dict(
                                                  color = Qcolor
                                                  ),
                                              tickfont = dict(
                                                  color = Qcolor
                                                  )
                                          )
            else: 
                SP_fig.layout['yaxis'+ ynumber[1:]]= dict(title=Quantity + " ["+ EU[Quantity]+ "]",
                                                          titlefont = dict(
                                                          color = Qcolor
                                                          ),
                                                          tickfont = dict(
                                                          color = Qcolor
                                                          ),
                                                          side=["left","right"][(int(ynumber[1:])-1)%2],
                                                          anchor="free",
                                                          overlaying="y",
                                                          autoshift = True,
                                                          shift=[-15,15][(int(ynumber[1:])-1)%2]                                                          
                                                      )
    SP_fig.update_layout(height=800)
    st.plotly_chart(SP_fig,
                    use_container_width=True,
                    config ={'scrollZoom': True,
                             'toImageButtonOptions': {
                                 'format': 'svg', # one of png, svg, jpeg, webp
                                 'filename': 'custom_image',
                                 'height': 500,
                                 'width': 700,
                                 'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
                                 },
                             }
                    )
    return

def Display_Events(Events):
    st.dataframe(data= Events, 
                 use_container_width= True,
                 hide_index=True)
    return
                                
################################################## Main ##################################################


def main():
    ######################## Title ########################
    st.title(Title)
    st.markdown("""---""") 
    
    ################## Download section ###################
    ## On upload le CSV file avant de le lire avec la fonction CSV_read()
    uploaded_file = st.file_uploader("Upload your CSV file",accept_multiple_files=False,type="csv")
    st.markdown("""---""") 

    ################### Extracting Data ###################
    ## Read_CSV(file) renvoie:
    ## - Units_OnOff, dictionnaire qui à une Unit renvoie un booléen sur son utilisation
    ## - TrackInfo, la section TrackInfo sous forme de dataframe
    ## - TrackDatas, Tableau de dataframes chacun associé à un TrackData (Units non scindés)
    ## - Events, la section TrackInfo sous forme de dataframe
       
    if uploaded_file != None:
        Units_OnOff, TrackInfo, TrackDatas, Events = CSV_read(uploaded_file)
        
    ################### Formating Data ####################
        ## TrackData Selection ##
        select_TrackData = st.selectbox(label="Which TrackData do you want to display", 
                                        options= [1+k for k in range(len(TrackDatas))],
                                        index=0)
        
        ## Initialisation des TrackDatas ##
        df=TrackDatas[select_TrackData-1]
        TrackData_i = 'TrackData '+str(select_TrackData) # nom du trackdata
        tab_labels=[Unit for Unit,Bool in Units_OnOff.items() if Bool] # Intitulé pour chaque fenêtre 
        Units_On=tab_labels.copy() # list contenant uniquement les unités actives
        
        Init_st_TrackData(TrackData_i,TrackInfo,Units_On,df) 
        
    ################### Displaying Data ###################        
        ## Fenêtres 
        # Chaque Unit a sa fenêtre, une fenêtre de comparatif est ajoutée
        
        ntabs = len(tab_labels)
        tab_labels.append("Compare")
        
        itab=0
        tabs = st.tabs(tab_labels)
        for tab in tabs :
            Unit = tab_labels[itab]
            with tab:
                if itab< ntabs:
    #################### Display Editor ###################
                    ## Initialization color,on/off (display or not) and curves##
                    Init_st_Display_Settings(TrackData_i, Unit)
                    ## Affichage et mise à jour de la fenêtre latérale
                    Display_st_sidebar(TrackData_i, Unit, TrackInfo, Units_On, df)
                
    #################### Display Graph ####################
                    PV_fig= go.Figure()
                    Display_st_PV_plots(TrackData_i, Unit,PV_fig)
                    SP_fig= go.Figure()
                    Display_st_SP_plots(TrackData_i, Unit, SP_fig)
                                
                    itab+=1
        with tabs[-1]:
            colcompare1,colcompare2 = st.columns(2)
            choices = []
            for Unit in Units_On:
                choices.append(TrackData_i+"/"+Unit + "/PV")
                choices.append(TrackData_i+"/"+Unit + "/SP")
            with colcompare1:
                choice1= st.selectbox(label="First Choice",
                                      key = TrackData_i+ "/Compare/1" , 
                                      options= choices,
                                      # index = None
                                      )
                fig1 = go.Figure()
                if choice1 != None:
                    if choice1.split("/")[2] == "PV":
                        Display_st_PV_plots(TrackData_i, choice1.split("/")[1],fig1)
                    elif choice1.split("/")[2] == "SP":
                        Display_st_SP_plots(TrackData_i, choice1.split("/")[1],fig1)
            with colcompare2:
                choice2= st.selectbox(label="Second Choice",
                                      key = TrackData_i+ "/Compare/2" , 
                                      options= choices,
                                      # index = None
                                      )
                fig2 = go.Figure()
                if choice2 != None:
                    if choice2.split("/")[2] == "PV":
                        Display_st_PV_plots(TrackData_i, choice2.split("/")[1],fig2)
                    elif choice2.split("/")[2] == "SP":
                        Display_st_SP_plots(TrackData_i, choice2.split("/")[1],fig2)
                            
                
        

                
        with st.expander("Events"):
            Display_Events(Events)
        with st.expander("Check Data"):
            st.dataframe(TrackInfo)
            st.dataframe(df)
    return

if check_password():
  main()



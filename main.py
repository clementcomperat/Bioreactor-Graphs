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
            "What's Antiono's plant's name ? No CAPS nor Spaces", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "What's Antiono's plant's name ? No CAPS nor Spaces", type="password", on_change=password_entered, key="password"
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
def Init_st_TrackData(FileName: str, TrackData_i : str, TrackInfo: object, Units_On: list, df: object):
    if FileName + "/" +TrackData_i not in st.session_state:
        st.session_state[FileName + "/" + TrackData_i] = HC.TrackData(TrackInfo,Units_On,df)
    return

def Init_st_PV_Display(FileName: str,TrackData_i : str, Unit : str):
    for Quantity in PV_Quantities:
        if FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Quantity not in st.session_state:
            if Quantity in PV_Quantities_to_display:
                st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Quantity] = True
            else:
                st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Quantity] = False
    return

def Init_st_SP_Display(FileName: str,TrackData_i : str, Unit : str):
    for Quantity in SP_Quantities:
        if FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/"+Quantity not in st.session_state:
            if Quantity in SP_Quantities_to_display:
                st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/"+Quantity] = True
            else:
                st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/"+Quantity] = False
    return

def Init_st_PV_Display_Curves(FileName: str,TrackData_i : str, Unit : str):
    for Quantity in PV_Quantities :
        for Curve in st.session_state[FileName + "/" +TrackData_i].Units[Unit].PV[Quantity]:
            if FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+ Quantity +"/"+ Curve.display_name not in st.session_state:
                st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/" + Quantity +"/"+ Curve.display_name]= True
    return

def Init_st_SP_Display_Curves(FileName: str,TrackData_i : str, Unit : str):
    for Quantity in SP_Quantities :
        for Curve in st.session_state[FileName + "/" +TrackData_i].Units[Unit].SP[Quantity]:
            if FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/"+Quantity +"/"+ Curve.display_name not in st.session_state:
                st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/" +Quantity +"/"+ Curve.display_name]= True
    return

def Init_st_Display_Settings(FileName: str,TrackData_i : str, Unit : str):
    ## [{TrackData_i}/{Unit}/PV/Display/{Quantity}] est un booléen pour savoir si la quantité en PV est à afficher ou pas
    ## [{TrackData_i}/{Unit}/SP/Display/{Quantity}] est un booléen pour savoir si la quantité en PV est à afficher ou pas
    ## [{TrackData_i}/{Unit}/PV/Display/{CurveName}] est un booléen pour savoir si la courbe PV en question est à afficher ou pas
    ## [{TrackData_i}/{Unit}/SP/Display/{CurveName}] est un booléen pour savoir si la courbe SP en question est à afficher ou pas
    ### Le booléen sur la quantité est prioritaire sur le booléen de la courbe
    ## [Show_markers] est un booléen selon lequel on affiche ou pas les markers sur la courbes
    
    Init_st_PV_Display(FileName,TrackData_i, Unit)
    Init_st_SP_Display(FileName,TrackData_i, Unit)
    Init_st_PV_Display_Curves(FileName,TrackData_i, Unit)
    Init_st_SP_Display_Curves(FileName,TrackData_i, Unit)
    
    if "Show_markers" not in st.session_state:
        st.session_state.Show_markers = False
    
    return

def Init_st_Colors():
    for Quantity in Colors.keys():
        if Quantity+"/Color" not in st.session_state:
            st.session_state[Quantity+"/Color"] = Colors[Quantity]
    return

## Display
def Display_st_sidebar(FileName: str,TrackData_i : str, Unit: str): #, TrackInfo: object, Units_On: list, df: object):
    ## La fenêtre latérale présente en un bouton à bascule pour l'affichage des marqueurs (courbes)
    ## 2 colonnes (st.columns()) avec d'une part les couleurs associées à chaque grandeur et d'autre part
    ## deux onglets "PV - On/Off" et "SP - On/Off" pour choisir l'affichage des Quantités et des courbes
    
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
                                            label_visibility="visible")
            
        ## On/Off PV ##
        with sb_col2:
            sb_tabs1, sb_tabs2 = st.tabs(["PV","SP"])
            
            with sb_tabs1:
                st.header("PV - On/Off")
                
                for Quantity in PV_Quantities:
                    ## Checkbox pour afficher ou pas la Quantité en question 
                    st.checkbox(label= Quantity,
                                key=FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Quantity,
                                value = st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Quantity]
                            )
                    ## dessous, un onglet déroulant contenant des checkbox concernant l'affichage des courbes
                    with st.expander("Curves to show"):
                        for Curve in st.session_state[FileName+"/"+TrackData_i].Units[Unit].PV[Quantity]:
                                # st.write(Curve.display_name)
                                st.checkbox(label = Curve.display_name,
                                            key = FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/" +Quantity +"/"+ Curve.display_name,
                                            value = st.session_state[FileName + "/" + TrackData_i+"/"+Unit+"/PV/Display/" +Quantity +"/"+ Curve.display_name]
                                            )
                                
            with sb_tabs2:              
                st.header("SP - On/Off")
                
                for Quantity in SP_Quantities:
                    ## Checkbox pour afficher ou pas la Quantité en question
                    st.checkbox(label= Quantity,
                                key=FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/"+Quantity,
                                value = st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Quantity]
                                )
                    ## dessous, un onglet déroulant contenant des checkbox concernant l'affichage des courbes
                    with st.expander("Curves to show"):
                        for Curve in st.session_state[FileName + "/" +TrackData_i].Units[Unit].SP[Quantity]:
                                # st.write(Curve.display_name)
                                st.checkbox(label = Curve.display_name,
                                            key =FileName + "/" + TrackData_i+"/"+Unit+"/SP/Display/" +Quantity +"/"+ Curve.display_name,
                                            value = st.session_state[FileName + "/" + TrackData_i+"/"+Unit+"/SP/Display/" +Quantity +"/"+ Curve.display_name]
                                            )
    return

def Bool_to_markers_mode(Bool):
    if Bool:
        return "lines+markers"
    else:
        return "lines"

def PV_Which_yaxis(FileName: str,TrackData_i: str, Unit:str, Quantity:str):
    #retourne "y" si la quantité est la première à être affichée
    #retourne "y{numéro}" sinon (numéro>=2)
    # Init_st_PV_Display(FileName,TrackData_i, Unit)
    number = 0
    for Q in PV_Quantities:
        if st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Q]:
            number +=1
        if Q == Quantity:
            if number ==1:
                return "y"
            else:
                return "y"+str(number)
    return "y"

def SP_Which_yaxis(FileName: str,TrackData_i: str, Unit:str, Quantity:str):
    #retourne "y" si la quantité est la première à être affichée
    #retourne "y{numéro}" sinon (numéro>=2)
    # Init_st_SP_Display(FileName,TrackData_i, Unit)
    number = 0
    for Q in SP_Quantities:
        if st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/"+Q]:
            number +=1
        if Q == Quantity:
            if number ==1:
                return "y"
            else:
                return "y"+str(number)
    return "y"

def Display_st_PV_plots(FileName: str,TrackData_i : str, Unit :str, PV_fig: object):
    
    # Init_st_Display_Settings(FileName, TrackData_i, Unit)
    # Init_st_Colors()
    # date_mode = st.selectbox(label="Date Mode",
    #                          options=st.session[])
    for Quantity in PV_Quantities:    
        if st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/"+Quantity]:
            ynumber = PV_Which_yaxis(FileName,TrackData_i, Unit, Quantity)
            Qcolor = st.session_state[Quantity+"/Color"]
            j=0
            if len(st.session_state[FileName + "/" +TrackData_i].Units[Unit].PV[Quantity])==0:
                st.write(st.session_state[FileName + "/" +TrackData_i].Units[Unit].PV[Quantity])
            for Curve in st.session_state[FileName + "/" +TrackData_i].Units[Unit].PV[Quantity]:
                if st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/" +Quantity +"/"+ Curve.display_name]:
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
                
    PV_fig.update_layout(height=650)
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
                                    },
                    )
    return

def Display_st_SP_plots(FileName:str,TrackData_i : str, Unit :str, SP_fig: object):
    
    # Init_st_Display_Settings(FileName,TrackData_i, Unit)
    # Init_st_Colors()
    for Quantity in SP_Quantities:    
        if st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/"+Quantity]:
            ynumber = SP_Which_yaxis(FileName,TrackData_i, Unit, Quantity)
            Qcolor = st.session_state[Quantity + "/Color"]   
            j=0
            if len(st.session_state[FileName + "/" +TrackData_i].Units[Unit].SP[Quantity]) !=  0: 
                for Curve in st.session_state[FileName + "/" +TrackData_i].Units[Unit].SP[Quantity]:
                    if st.session_state[FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/" +Quantity +"/"+ Curve.display_name]:
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
    SP_fig.update_layout(height=650)
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

def Display_st_Compare_Display_Settings():
    st.header("On/Off")
    colPV,colSP = st.tabs(["PV - On/Off","SP - On/Off"])
    with colPV:
        for Quantity in PV_Quantities:
            if Quantity in PV_Quantities_to_display:
                st.checkbox(label= Quantity,
                            key="Compare///PV/Display/"+Quantity,
                            value = True
                            )
            else:
                st.checkbox(label= Quantity,
                            key="Compare///PV/Display/"+Quantity,
                            value = False
                            )
    with colSP:
        for Quantity in SP_Quantities:
            if Quantity in SP_Quantities_to_display:
                st.checkbox(label= Quantity,
                            key="Compare///SP/Display/"+Quantity,
                            value = True
                            )
            else:
                st.checkbox(label= Quantity,
                            key="Compare///SP/Display/"+Quantity,
                            value = False
                            )
    return


def Display_st_Compare_Display_Curves(fig,FileName: str,TrackData_i : str, Unit :str, mode : str):
    container = st.container()
    
    
    if mode == "PV":
        for Quantity in PV_Quantities:
            with st.expander(Quantity+" - Curves to show"):
                for Curve in st.session_state[FileName+"/"+TrackData_i].Units[Unit].PV[Quantity]:
                        # st.write(Curve.display_name)
                        st.checkbox(label = Curve.display_name,
                                    key = "Compare/"+FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/" +Quantity +"/"+ Curve.display_name,
                                    value = True)
        with container:
            # Init_st_Display_Settings(FileName,TrackData_i, Unit)
            # Init_st_Colors()
            for Quantity in SP_Quantities:    
                if st.session_state["Compare///PV/Display/"+Quantity]:
                    ynumber = PV_Which_yaxis("Compare","", "", Quantity)
                    Qcolor = st.session_state[Quantity + "/Color"]   
                    j=0
                    if len(st.session_state[FileName + "/" +TrackData_i].Units[Unit].PV[Quantity]) !=  0: 
                        for Curve in st.session_state[FileName + "/" +TrackData_i].Units[Unit].PV[Quantity]:
                            if st.session_state["Compare/"+FileName + "/" +TrackData_i+"/"+Unit+"/PV/Display/" +Quantity +"/"+ Curve.display_name]:
                                fig.add_trace(go.Scatter(
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
                        fig.layout['yaxis'] = dict(title=Quantity + "["+ EU[Quantity]+ "]",
                                                      titlefont = dict(
                                                          color = Qcolor
                                                          ),
                                                      tickfont = dict(
                                                          color = Qcolor
                                                          )
                                                  )
                    else: 
                        fig.layout['yaxis'+ ynumber[1:]]= dict(title=Quantity + " ["+ EU[Quantity]+ "]",
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
            fig.update_layout(height=650)
            st.plotly_chart(fig,
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
    
            
            
    if mode == "SP":
        for Quantity in SP_Quantities:
            with st.expander(Quantity+" - Curves to show"):
                for Curve in st.session_state[FileName+"/"+TrackData_i].Units[Unit].SP[Quantity]:
                    st.checkbox(label = Curve.display_name,
                                    key = "Compare/"+FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/" +Quantity +"/"+ Curve.display_name,
                                    value = True)
    
        with container:
            # Init_st_Display_Settings(FileName,TrackData_i, Unit)
            # Init_st_Colors()
            for Quantity in SP_Quantities:    
                if st.session_state["Compare///SP/Display/"+Quantity]:
                    ynumber = SP_Which_yaxis("Compare","", "", Quantity)
                    Qcolor = st.session_state[Quantity + "/Color"]   
                    j=0
                    if len(st.session_state[FileName + "/" +TrackData_i].Units[Unit].SP[Quantity]) !=  0: 
                        for Curve in st.session_state[FileName + "/" +TrackData_i].Units[Unit].SP[Quantity]:
                            if st.session_state["Compare/"+FileName + "/" +TrackData_i+"/"+Unit+"/SP/Display/" +Quantity +"/"+ Curve.display_name]:
                                fig.add_trace(go.Scatter(
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
                        fig.layout['yaxis'] = dict(title=Quantity + "["+ EU[Quantity]+ "]",
                                                      titlefont = dict(
                                                          color = Qcolor
                                                          ),
                                                      tickfont = dict(
                                                          color = Qcolor
                                                          )
                                                  )
                    else: 
                        fig.layout['yaxis'+ ynumber[1:]]= dict(title=Quantity + " ["+ EU[Quantity]+ "]",
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
            fig.update_layout(height=650)
            st.plotly_chart(fig,
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
    
                        





def Display_Events(Events):
    st.dataframe(data= Events, 
                 use_container_width= True,
                 hide_index=True)
    return
                                
################################################## Main ##################################################

def Init_st_session_state(uploaded_files):
    Init_st_Colors()
    for uploaded_file in uploaded_files:
        Units_OnOff, TrackInfo, TrackDatas, Events = CSV_read(uploaded_file)
        Units_On = [Unit for Unit,Bool in Units_OnOff.items() if Bool]
        if uploaded_file.name + "/Trackdata/Units_On" not in st.session_state:
            st.session_state[uploaded_file.name + "/Units_On"]=Units_On
            
        for k in range(len(TrackDatas)):
            TrackData_i = 'TrackData '+str(k+1)
            df=TrackDatas[k]
            Init_st_TrackData(uploaded_file.name,TrackData_i,TrackInfo,Units_On,df)
            for Unit in Units_On:
                Init_st_Display_Settings(uploaded_file.name,TrackData_i, Unit)
                
        if uploaded_file.name + "/nTrackDatas" not in st.session_state:
            st.session_state[uploaded_file.name + "/nTrackDatas"] =len(TrackDatas)
            st.balloons()
    return 
    


def main():
    ######################## Title ########################
    st.title(Title)
    st.markdown("""---""") 
    
    ################## Download section ###################
    ## On upload le CSV file avant de le lire avec la fonction CSV_read()
    uploaded_files = st.file_uploader("Upload your CSV file(s)",accept_multiple_files=True,type="csv")
    st.markdown("""---""") 
    # Sidebar = st.sidebar
    
    
    
    ################### Initialization ####################
    
    ## Extracting Data 
    ### Read_CSV(file) renvoie:
    ### - Units_OnOff, dictionnaire qui à une Unit renvoie un booléen sur son utilisation
    ### - TrackInfo, la section TrackInfo sous forme de dataframe
    ### - TrackDatas, Tableau de dataframes chacun associé à un TrackData (Units non scindés)
    ### - Events, la section TrackInfo sous forme de dataframe
    
    
    if len(uploaded_files) != 0:
        Init_st_session_state(uploaded_files)
        # for key in st.session_state.keys():
        #     st.write(key)
        nFiles = len(uploaded_files)
        FileList = [uploaded_files[i].name for i in range(nFiles)]
        
        tab1,tab2 = st.tabs(["Simple","Compare"])
        
        with tab1:
        ################### File of interest ###################
            
            # iFile = st.radio("Which file you want to display ?", options=range(nFiles), format_func=lambda x:FileList[x])
            iFile = st.selectbox("Which file you want to display ?", options=range(nFiles), format_func=lambda x:FileList[x])
            FileName = FileList[iFile]
  
            ## TrackData Selection ##

            n = st.session_state[FileName + "/nTrackDatas"] 
            ################### Selecting Graphs ####################
            select_TrackData = st.selectbox(label="Which TrackData do you want to display", 
                                            options= [1+k for k in range(n)],
                                            index=0)
            TrackData_i = 'TrackData '+str(select_TrackData)
            Units_On=[Unit for Unit in st.session_state[FileName+"/Units_On"]] # Intitulé pour chaque fenêtre 
        
            ################### Displaying Data ###################        
                ## Fenêtres 
                # Chaque Unit a sa fenêtre, une fenêtre de comparatif est ajoutée
                
            
               
            itab=0
            # if FileName+"/"+TrackData_i not in st.session_state:
            tabs = st.tabs(Units_On)
            for tab in tabs :
                Unit = Units_On[itab]
                Display_st_sidebar(FileName,TrackData_i, Unit)
                with tab:
                    
                    col1,col2,col3 = st.columns([1,10,1])
                    with col2:
                        PV_fig= go.Figure()
                        Display_st_PV_plots(FileName,TrackData_i, Unit,PV_fig)
                        SP_fig= go.Figure()
                        Display_st_SP_plots(FileName,TrackData_i, Unit, SP_fig)
                            
                                
                itab+=1
        with tab2:
            options_to_compare = []
            for file in FileList:
                for TrackData_i in ["TrackData "+str(k+1) for k in range(st.session_state[file + "/nTrackDatas"] )]:
                    for Unit in st.session_state[file+"/Units_On"]:
                        options_to_compare.append(file+"/"+TrackData_i+"/"+Unit+"/PV")
                        options_to_compare.append(file+"/"+TrackData_i+"/"+Unit+"/SP")
            options = st.multiselect("To compare",options = options_to_compare,default=None)
            noptions=len(options)
            if noptions !=0:
                Display_st_Compare_Display_Settings()
                cols_compare = st.columns(noptions)
                
                icol=0
                for col in cols_compare:
                    with col:
                        fig=go.Figure()
                        Display_st_Compare_Display_Curves(fig, options[icol].split("/")[0], options[icol].split("/")[1], options[icol].split("/")[2], options[icol].split("/")[-1])
                        
                    icol+=1
            
            
                        
                    
            # with tabs[-1]:
            #     colcompare1,colcompare2 = st.columns(2)
            #     choices = []
            #     for Unit in Units_On:
            #         choices.append(FileName+"/"+TrackData_i+"/"+Unit + "/PV")
            #         choices.append(FileName+"/"+TrackData_i+"/"+Unit + "/SP")
            #     with colcompare1:
            #         choice1= st.selectbox(label="First Choice",
            #                               key = TrackData_i+ "/Compare/1" , 
            #                               options= choices,
            #                               # index = None
            #                               )
            #         fig1 = go.Figure()
            #         if choice1 != None:
            #             if choice1.split("/")[2] == "PV":
            #                 Display_st_PV_plots(TrackData_i, choice1.split("/")[1],fig1)
            #             elif choice1.split("/")[2] == "SP":
            #                 Display_st_SP_plots(TrackData_i, choice1.split("/")[1],fig1)
            #     with colcompare2:
            #         choice2= st.selectbox(label="Second Choice",
            #                               key = TrackData_i+ "/Compare/2" , 
            #                               options= choices,
            #                               # index = None
            #                               )
            #         fig2 = go.Figure()
            #         if choice2 != None:
            #             if choice2.split("/")[2] == "PV":
            #                 Display_st_PV_plots(TrackData_i, choice2.split("/")[1],fig2)
            #             elif choice2.split("/")[2] == "SP":
            #                 Display_st_SP_plots(TrackData_i, choice2.split("/")[1],fig2)
                                
                    
            
    
                    
            # with st.expander("Events"):
            #     Display_Events(Events)
            # with st.expander("Check Data"):
            #     st.dataframe(TrackInfo)
            #     st.dataframe(df)
        
                
    # for key in st.session_state.keys():
    #     st.write(key)
    return

if check_password():
  main()  



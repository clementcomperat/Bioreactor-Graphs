PV_Quantities = ["V","pH","DO","T","N","Default","Pump.F","Pump.V","Gas.OF","X","Gas.F","TR"]
SP_Quantities = ["pH","DO","T","N","Default","Pump.F","Gas.OF","X","Gas.F"]
PV_Quantities_to_display = ["pH","DO","T","N"]



class Curve:
    def __init__(self,Name,Display_name,XY):
        self.name = Name
        self.display_name = Display_name 
        self.XY = XY
        

class UnitCurves:
    def __init__(self,df,Unit,TrackInfo):
        self.PV = {}
        for Quantity in PV_Quantities:
            self.PV[Quantity]=[]
        self.SP = {}
        for Quantity in SP_Quantities:
            self.SP[Quantity]=[]
        for i in range(TrackInfo.shape[0]):
            
            if "LocComment" in TrackInfo.keys():
                ## Afin de prévoir des variantes comme le nom des pompes, on regarde en premier le LocComment pui le LocNameet enfon le LocNamePar 
                LocName = TrackInfo.LocName[i]
                LocComment= TrackInfo.LocComment[i]
                LocNamePar= TrackInfo.LocNamePar[i]
                key_to_search = LocNamePar + " ["+str(TrackInfo.Unit[i])+"]"
                
                ## V Section ##
                if "Vessel volume process value" == LocComment :
                    if Unit in LocNamePar and ".VPV" in LocNamePar:
                        key_to_search = LocNamePar + " " + "["+str(TrackInfo.Unit[i])+"]"
                        displayed_name = Unit + "/Vessel/VPV"
                        XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                        self.PV["V"].append(Curve(key_to_search,displayed_name,XY))
 
                        
                ## pH Section ##
                elif "pH" in LocComment:
                    if Unit in LocNamePar:
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/pH/Sensor/PV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["pH"].append(Curve(key_to_search,displayed_name,XY))
                        elif ".SP" in LocNamePar:
                            displayed_name = Unit + "/pH/Sensor/SP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["pH"].append(Curve(key_to_search,displayed_name,XY))
                ## DO Section ##
                elif "DO" in LocComment:
                    if Unit in LocNamePar:
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/Do/Sensor/PV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["DO"].append(Curve(key_to_search,displayed_name,XY))
                            
                        elif ".SP" in LocNamePar:
                            displayed_name = Unit + "/Do/Sensor/SP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["DO"].append(Curve(key_to_search,displayed_name,XY))
                
                ## T Section ##
                elif "Temperature" in LocComment:
                    if Unit in LocNamePar:
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/Temperature/Sensor/PV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["T"].append(Curve(key_to_search,displayed_name,XY))
                        elif ".SP" in LocNamePar:
                            displayed_name = Unit + "/Temperature/SP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["T"].append(Curve(key_to_search,displayed_name,XY))
                
                ## N Section ##
                elif "Agitation" in LocComment:
                    if Unit in LocNamePar :
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/Agitation/Controller/PV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["N"].append(Curve(key_to_search,displayed_name,XY))
                        elif ".SP" in LocNamePar:
                            displayed_name = Unit + "/Agitation/Controller/SP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["N"].append(Curve(key_to_search,displayed_name,XY))
                ## Default Section ##
                elif "Controller" in LocComment:
                    if Unit in LocNamePar and TrackInfo.Unit[i] == "":
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/User" + LocName.split(".")[1] + "/Controller/PV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["Default"].append(Curve(key_to_search,displayed_name,XY))
                        if ".SP" in LocNamePar:
                            displayed_name = Unit + "/User" + LocName.split(".")[1] + "/Controller/SP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["Default"].append(Curve(key_to_search,displayed_name,XY))
                    
                elif "Respiration ration" == LocComment:
                    if Unit in LocNamePar:
                        displayed_name = Unit + "/Gasanalyzer/Sensor/RQ"
                        XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                        self.PV["Default"].append(Curve(key_to_search,displayed_name,XY))
                        
                        
                ## Pump.F Section ##
                elif "Flow" in LocComment: # Flow apparait dans d'autres commentaires locaux cependant sans Majuscule 
                    if TrackInfo.Unit[i] == "mL/h" and Unit in LocNamePar: # and "Unit.F" in TrackInfo.LocName[i]: # pour plus de conditions
                        letter = LocNamePar.split(".")[1][1:-1]
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/Pump"+ letter + "/Controller/FPV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["Pump.F"].append(Curve(key_to_search,displayed_name,XY))
                        elif ".SP" in LocNamePar:
                            displayed_name = Unit + "/Pump"+ letter + "/Controller/FSP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["Pump.F"].append(Curve(key_to_search,displayed_name,XY))
                            

                # internal en standby
                        
                ## Pump.V Section ##depend de l'unite
                elif "Volume process value" == LocComment:
                    if TrackInfo.Unit[i] == "mL" and Unit in LocNamePar:
                        letter = LocNamePar.split(".")[1][1:-1]
                        displayed_name = Unit + "/Pump"+ letter + "/Controller/VPV"
                        XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                        self.PV["Pump.V"].append(Curve(key_to_search,displayed_name,XY))
                
                ## Gas.OF ## utilise  LocName
                elif "Unit.OF." in LocName: 
                    if Unit in LocNamePar:
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/Overlay/Controller/FPV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["Gas.OF"].append(Curve(key_to_search,displayed_name,XY))

                        elif ".SP" in LocNamePar:
                            displayed_name = Unit + "/Overlay/Controller/FSP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["Gas.OF"].append(Curve(key_to_search,displayed_name,XY))
                            
                ## X Section
                elif "concentration" in LocComment:
                    if Unit in LocNamePar:
                        if ".PV" in LocNamePar:
                            if LocNamePar.split(".")[1][0] == "O":
                                molecule = LocName.split(".")[1][2:]
                                displayed_name = Unit + "/Overlay/Controller/X"+molecule+"PV"
                                XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                                self.PV["X"].append(Curve(key_to_search,displayed_name,XY))
                            elif LocNamePar.split(".")[1][0] == "X":
                                molecule = LocName.split(".")[1][1:]
                                displayed_name = Unit + "/Gassing/Controller/X"+molecule+"PV"
                                XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                                self.PV["X"].append(Curve(key_to_search,displayed_name,XY))
                                
                        elif ".Out" in LocNamePar: #"Vessel output gas flow"
                                molecule = LocName.split(".")[1][1:]
                                displayed_name = Unit + "/Gasanalyzer/Controller/X"+molecule+"Out"
                                XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                                self.PV["X"].append(Curve(key_to_search,displayed_name,XY))
                        
                        elif ".SP" in LocNamePar:
                            if LocNamePar.split(".")[1][0] == "O":
                                molecule = LocName.split(".")[1][2:]
                                displayed_name = Unit + "/Overlay/Controller/X"+molecule+"SP"
                                XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                                self.SP["X"].append(Curve(key_to_search,displayed_name,XY))
                            elif LocNamePar.split(".")[1][0] == "X":
                                molecule = LocName.split(".")[1][1:]
                                displayed_name = Unit + "/Gassing/Controller/X"+molecule+"SP"
                                XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                                self.SP["X"].append(Curve(key_to_search,displayed_name,XY))
                                
                ## GasF Section
                elif "Unit.F." in LocName: 
                    if Unit in LocNamePar:
                        if ".PV" in LocNamePar:
                            displayed_name = Unit + "/Gassing/Controller/FPV"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["Gas.F"].append(Curve(key_to_search,displayed_name,XY))
                        if ".Out" in LocNamePar:
                            displayed_name = Unit + "/Gasanalyzer/Sensor/FOut"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.PV["Gas.F"].append(Curve(key_to_search,displayed_name,XY))  
                        elif ".SP" in LocNamePar:
                            displayed_name = Unit + "/Gassing/Controller/FSP"
                            XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                            self.SP["Gas.F"].append(Curve(key_to_search,displayed_name,XY))
                            
                ## TR Section depend de l'unité, 
                elif "transfer rate" in LocComment:
                    if TrackInfo.Unit[i] == "mMol/h" and Unit in LocNamePar: 
                        displayed_name = Unit + "Gasanalyzer/Sensor/"+ LocName.split(".")[1]
                        XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
                        self.PV["TR"].append(Curve(key_to_search,displayed_name,XY))
                        
                ## P Section 
                
        return
    
    
            
class TrackData:
    def __init__(self,TrackInfo,Active_Units_lbls,Data):
        self.Units= {}
        for name in Active_Units_lbls:
            self.Units[name]= UnitCurves(Data,name,TrackInfo)
        





# class ProcessValue:
#     def __init__(self):
#         self.V = []
#         self.pH = []
#         self.DO = []
#         self.T = []
#         self.N = []
#         self.Default = []
#         self.PumpF= []
#         self.PumpV = []
#         self.GasOF = []
#         self.X = []
#         self.GasF = []
#         self.TR = []
    
# class SetPoint:
#     def __init__(self):
#         self.pH = []
#         self.DO = []
#         self.T = []
#         self.N = []
#         self.Default = []
#         self.PumpF= []
#         self.GasOF = []
#         self.X = []
#         self.GasF = []

# class UnitCurves:
#     def __init__(self,df,Unit,TrackInfo):
#         self.PV = ProcessValue()
#         self.SP = SetPoint()
#         for i in range(TrackInfo.shape[0]):
            
#             if "LocComment" in TrackInfo.keys():
#                 ## Afin de prévoir des variantes comme le nom des pompes, on regarde en premier le LocComment pui le LocNameet enfon le LocNamePar 
#                 LocName = TrackInfo.LocName[i]
#                 LocComment= TrackInfo.LocComment[i]
#                 LocNamePar= TrackInfo.LocNamePar[i]
#                 key_to_search = LocNamePar + " ["+str(TrackInfo.Unit[i])+"]"
                
#                 ## V Section ##
#                 if "Vessel volume process value" == LocComment :
#                     if Unit in LocNamePar and ".VPV" in LocNamePar:
#                         key_to_search = LocNamePar + " " + "["+str(TrackInfo.Unit[i])+"]"
#                         displayed_name = Unit + "/Vessel/VPV"
#                         XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                         self.PV.V.append(Curve(key_to_search,displayed_name,XY))
 
                        
#                 ## pH Section ##
#                 elif "pH sensor process value" in LocComment:
#                     if Unit in LocNamePar:
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/pH/Sensor/PV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.pH.append(Curve(key_to_search,displayed_name,XY))
#                         elif ".SP" in LocNamePar:
#                             displayed_name = Unit + "/pH/Sensor/SP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.pH.append(Curve(key_to_search,displayed_name,XY))
#                 ## DO Section ##
#                 elif "DO" in LocComment:
#                     if Unit in LocNamePar:
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/Do/Sensor/PV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.DO.append(Curve(key_to_search,displayed_name,XY))
                            
#                         elif ".SP" in LocNamePar:
#                             displayed_name = Unit + "/Do/Sensor/SP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.DO.append(Curve(key_to_search,displayed_name,XY))
                
#                 ## T Section ##
#                 elif "Temperature" in LocComment:
#                     if Unit in LocNamePar:
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/Temperature/Sensor/PV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.T.append(Curve(key_to_search,displayed_name,XY))
#                         elif ".SP" in LocNamePar:
#                             displayed_name = Unit + "/Temperature/SP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.T.append(Curve(key_to_search,displayed_name,XY))
                
#                 ## N Section ##
#                 elif "Agitation" in LocComment:
#                     if Unit in LocNamePar :
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/Agitation/Controller/PV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.N.append(Curve(key_to_search,displayed_name,XY))
#                         elif ".SP" in LocNamePar:
#                             displayed_name = Unit + "/Agitation/Controller/SP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.N.append(Curve(key_to_search,displayed_name,XY))
#                 ## Default Section ##
#                 elif "Controller" in LocComment:
#                     if Unit in LocNamePar and TrackInfo.Unit[i] == "":
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/User" + LocName.split(".")[1] + "/Controller/PV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.Default.append(Curve(key_to_search,displayed_name,XY))
#                         if ".SP" in LocNamePar:
#                             displayed_name = Unit + "/User" + LocName.split(".")[1] + "/Controller/SP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.Default.append(Curve(key_to_search,displayed_name,XY))
                    
#                 elif "Respiration ration" == LocComment:
#                     if Unit in LocNamePar:
#                         displayed_name = Unit + "/Gasanalyzer/Sensor/RQ"
#                         XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                         self.PV.Default.append(Curve(key_to_search,displayed_name,XY))
                        
                        
#                 ## Pump.F Section ##
#                 elif "Flow" in LocComment: # Flow apparait dans d'autres commentaires locaux cependant sans Majuscule 
#                     if TrackInfo.Unit[i] == "mL/h" and Unit in LocNamePar: # and "Unit.F" in TrackInfo.LocName[i]: # pour plus de conditions
#                         letter = LocNamePar.split(".")[1][2:-1]
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/Pump"+ letter + "/Controller/FPV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.PumpF.append(Curve(key_to_search,displayed_name,XY))
#                         elif ".SP" in LocNamePar:
#                             displayed_name = Unit + "/Pump"+ letter + "/Controller/FSP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.PumpF.append(Curve(key_to_search,displayed_name,XY))
                            

#                 # internal en standby
                        
#                 ## Pump.V Section ##depend de l'unite
#                 elif "Volume process value" == LocComment:
#                     if TrackInfo.Unit[i] == "mL" and Unit in LocNamePar:
#                         letter = LocNamePar.split(".")[1][2:-1]
#                         displayed_name = Unit + "/Pump"+ letter + "/Controller/VPV"
#                         XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                         self.PV.PumpV.append(Curve(key_to_search,displayed_name,XY))
                
#                 ## Gas.OF ## utilise  LocName
#                 elif "Unit.OF." in LocName: 
#                     if Unit in LocNamePar:
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/Overlay/Controller/FPV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.GasOF.append(Curve(key_to_search,displayed_name,XY))

#                         elif ".SP" in LocNamePar:
#                             displayed_name = Unit + "/Overlay/Controller/FSP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.GasOF.append(Curve(key_to_search,displayed_name,XY))
                            
#                 ## X Section
#                 elif "concentration" in LocComment:
#                     if Unit in LocNamePar:
#                         if ".PV" in LocNamePar:
#                             if LocNamePar.split(".")[1][0] == "O":
#                                 molecule = LocName.split(".")[1][2:]
#                                 displayed_name = Unit + "/Overlay/Controller/X"+molecule+"PV"
#                                 XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                                 self.PV.X.append(Curve(key_to_search,displayed_name,XY))
#                             elif LocNamePar.split(".")[1][0] == "X":
#                                 molecule = LocName.split(".")[1][1:]
#                                 displayed_name = Unit + "/Gassing/Controller/X"+molecule+"PV"
#                                 XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                                 self.PV.X.append(Curve(key_to_search,displayed_name,XY))
                                
#                         elif ".Out" in LocNamePar: #"Vessel output gas flow"
#                                 molecule = LocName.split(".")[1][1:]
#                                 displayed_name = Unit + "/Gasanalyzer/Controller/X"+molecule+"Out"
#                                 XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                                 self.PV.X.append(Curve(key_to_search,displayed_name,XY))
                        
#                         elif ".SP" in LocNamePar:
#                             if LocNamePar.split(".")[1][0] == "O":
#                                 molecule = LocName.split(".")[1][2:]
#                                 displayed_name = Unit + "/Overlay/Controller/X"+molecule+"SP"
#                                 XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                                 self.SP.X.append(Curve(key_to_search,displayed_name,XY))
#                             elif LocNamePar.split(".")[1][0] == "X":
#                                 molecule = LocName.split(".")[1][1:]
#                                 displayed_name = Unit + "/Gassing/Controller/X"+molecule+"SP"
#                                 XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                                 self.SP.X.append(Curve(key_to_search,displayed_name,XY))
                                
#                 ## GasF Section
#                 elif "Unit.F." in LocName: 
#                     if Unit in LocNamePar:
#                         if ".PV" in LocNamePar:
#                             displayed_name = Unit + "/Gassing/Controller/FPV"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.GasF.append(Curve(key_to_search,displayed_name,XY))
#                         if ".Out" in LocNamePar:
#                             displayed_name = Unit + "/Gasanalyzer/Sensor/FOut"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.PV.GasF.append(Curve(key_to_search,displayed_name,XY))  
#                         elif ".SP" in LocNamePar:
#                             displayed_name = Unit + "/Overlay/Controller/FSP"
#                             XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                             self.SP.GasF.append(Curve(key_to_search,displayed_name,XY))
                            
#                 ## TR Section depend de l'unité, 
#                 elif "transfer rate" in LocNamePar:
#                     if TrackInfo.Unit[i] == "mMol/h" and Unit in LocNamePar: 
#                         displayed_name = Unit + "Gasanalyzer/Sensor/"+ LocName.split(".")[1]
#                         XY=df.loc[df[key_to_search] != "",["Timestamp",key_to_search]]
#                         self.PV.TR.append(Curve(key_to_search,displayed_name,XY))
                        
#                 ## P Section 
                
#         return
    
    
            
# class TrackData:
#     def __init__(self,TrackInfo,Active_Units_lbls,Data):
#         self.Units= {}
#         for name in Active_Units_lbls:
#             self.Units[name]= UnitCurves(Data,name,TrackInfo)
        
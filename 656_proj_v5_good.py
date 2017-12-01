import numpy as np
import numpy.random as rnd
import math
import random

radius=10000          #radius in m
Lambda=6              #average number of calls that can be made in an hour in 6
avg_dur=60            #average duration of the call is 60s
cdma_BW=1.25          #Carrier Bandwidth in MHz
bitRate=12.5          #bit rate in kbps

EIRP_Pilot_check=[]

call_yes=[]
call=[]
call_no=[]
shadow=[]
call_dur={}
position={}
channel_num={}
channel_total=56
channel=1
min_sinr=6
count_no_retry=0
x_coord=0
y_coord=0
x_shadow=0
y_shadow=0

EIRP_init=42
#EIRP_Pilot=0
EIRP_min=30
EIRP_max=52
Cd=57
Ci=0
delta_EIRP_Pilot=0.5


def rsl_calc(yes_call):
    hBase=50              #Basestation height in m
    baseMTU=42            #Basestation MTU in dBm
    loss=2.1              #Connector loss in dB
    gain=12.1             #Antenna gain in dB
    freq=1900             #Carrier frequency in MHz
    RSL={}
    blocked=0
    x_shadow=0
    y_shadow=0
    EIRP_Pilot=EIRP_init-loss+gain
    if(len(active_call)>Cd and EIRP_Pilot>EIRP_min):
      EIRP_Pilot=EIRP_Pilot-delta_EIRP_Pilot
    elif(len(active_call)<Ci and EIRP_Pilot<EIRP_max):
      EIRP_Pilot=EIRP_Pilot+delta_EIRP_Pilot
    x_coord=int(yes_call[0]/10.0)
    y_coord=int(yes_call[1]/10.0)
    d=math.sqrt((yes_call[0])**2+(yes_call[1])**2)
    PL=46.3+(33.9*math.log10(freq))-(13.82*math.log10(hBase))+((44.9-6.55*math.log10(hBase))*math.log10(d/1000.0))
    ###### Checking the quadrant in which the point lies for shadow value calculation ########
    if(x_coord>0 and y_coord>0):
        x_shadow=1000+x_coord
        y_shadow=1000-y_coord
    elif(x_coord<0 and y_coord>0):
        x_shadow=1000-x_coord
        y_shadow=1000-y_coord
    elif(x_coord<0 and y_coord<0):
        x_shadow=1000+x_coord
        y_shadow=1000+y_coord
    elif(x_coord>0 and y_coord<0):
        x_shadow=1000+x_coord
        y_shadow=1000-y_coord
    elif(x_coord==0 and y_coord==0):
        x_shadow=1000+x_coord
        y_shadow=1000+y_coord
    S=shadow[x_shadow,y_shadow]
    x = np.random.rayleigh(1)
    F=20*math.log10(x)
    rsl=EIRP_Pilot-PL+S+F
    return rsl
    
def position_calc():
    pos_dict={}
    t=(2*np.pi)*rnd.random();
    u=(rnd.random()+rnd.random())
    if (u >= 1):
        u=u-1
    else:
        u=u
    x=u*np.cos(t)*radius
    y=u*np.sin(t)*radius
    point=[x,y]
    return point

def sinr_calc(active_list,n):
    n=len(channel_num)
    hBase=50              #Basestation height in m
    baseMTU=42            #Basestation MTU in dBm
    loss=2.1              #Connector loss in dB
    gain=12.1             #Antenna gain in dB
    PG=25                 #Processing gain in dB
    freq=1900             #Carrier frequency in MHz
    min_sinr=6            #minimum sinr is 6dB
    noise=-110            #noise level is -110dB
    x_shadow=0
    y_shadow=0
    EIRP=42-loss+gain
    x_coord=int(active_list[0]/10)
    y_coord=int(active_list[1]/10)
    d=math.sqrt((active_list[0])**2+(active_list[1])**2)
    PL=46.3+(33.9*math.log10(freq)-13.82*math.log10(hBase))+((44.9-6.55*math.log10(hBase))*math.log10(d/1000.0))
    #### Checking in which quadrant the point lies in ####
    if(x_coord>0 and y_coord>0):
        x_shadow=1000+x_coord
        y_shadow=1000-y_coord
    elif(x_coord<0 and y_coord>0):
        x_shadow=1000-x_coord
        y_shadow=1000-y_coord
    elif(x_coord<0 and y_coord<0):
        x_shadow=1000+x_coord
        y_shadow=1000+y_coord
    elif(x_coord>0 and y_coord<0):
        x_shadow=1000+x_coord
        y_shadow=1000-y_coord
    elif(x_coord==0 and y_coord==0):
        x_shadow=1000+x_coord
        y_shadow=1000+y_coord
    S=shadow[x_shadow,y_shadow]
    x = np.random.rayleigh(1)
    F=20*np.log10(x)
    RSL=EIRP-PL+S+F
    sig_level=RSL+PG
    if(n==1): #if there is only 1 active user
        sinr=sig_level-10*math.log10(10**(noise/10))
    else:
        interference=RSL+10*math.log10(n-1)
        sinr=sig_level-10*math.log10(10**(interference/10)+(10**(noise/10)))
    return sinr

#shadow values
num_squares=int((20*20*1000*1000)/(10*10)) #calculating the number of shadow values to be calculted for the square region of size 20km*20km
shadow_val=[]
shadow_val=rnd.normal(0,2,num_squares)
shadow_val=np.array(shadow_val)
shadow=shadow_val.reshape(2000,2000)       #reshaping shadow values as a 2000*2000 matrix

sinr_values={}
re_attempt_sinr={}
re_attempt_rsl={}
position={}
pos={}
active_call={}
num=1000
ind=0
user=()
rsl={}
active_users={}
rsl_value={}
sinr_value={}
rsl_recalc={}
sinr_recalc={}
blocked_sinr=0
success_call=0
blocked_trchannel=0
blocked_rsl=0
count_retry=0
active=[]
val_sinr=[]
val_x=[]
val_active_call=[]
for g in range(num):
    user+=(g,)
    
for j_count in range(7200):
  #### Checking if the user wants to make a call using call probability ####
  for w in user:
      a=rnd.random();
      if(a<(1/600)):
          active.append(w)
          user_list=list(user)
          user_list.remove(w)
          user=tuple(user_list)
  n=len(active_call)
  #### Check if SINR is to be re-calculated for any user ###
  if(len(sinr_recalc) is not 0):
      for x in sinr_recalc:
          sinr_recalc[x]=sinr_recalc[x]+1
          sinr_value=sinr_calc(position[x],n)
          if(sinr_value>=min_sinr):
              val_sinr.append(x)
              call_dur[x]=call_dur[x]-1
              if(call_dur[x]<=0):                            #if the call has successfully ended
                    success_call=success_call+1
                    del position[x]
                    del channel_num[x]
                    del call_dur[x]
                    del rsl[x]
                    user+=(x,)
          elif(sinr_value<min_sinr and sinr_recalc[x]==3):   #if the call fails due to SINR even after re-calculation
              blocked_sinr=blocked_sinr+1
              del position[x]
              del channel_num[x]
              del call_dur[x]
              del rsl[x]
              val_sinr.append(x)
              user+=(x,)
          #elif(sinr_value<min_sinr and sinr_recalc[x]<3):    #if the re-calculation value for SINR for the user is to be updated
              #sinr_recalc[x]=sinr_recalc[x]+1
  for x2 in range(len(val_sinr)):                            # remove SINR recalculation count 
      del sinr_recalc[val_sinr[x2]]
  val_sinr=[]
  #### Check for SINR value of new active user ####
  if(len(active_call)is not 0):
      n=len(active_call)
      for d in active_call:
          sinr_value=sinr_calc(position[d],n)
          if(sinr_value>min_sinr):
              call_dur[d]=call_dur[d]-1
              if(call_dur[d]<=0):
                  success_call=success_call+1
                  del position[d]
                  del rsl[d]
                  del channel_num[d]
                  del call_dur[d]
                  val_active_call.append(d)
                  user+=(d,)
          elif(sinr_value<min_sinr):
              val_active_call.append(d)                       #if the re-calculation value for SINR for the user is needed
              sinr_recalc[d]=0
  for g1 in range(len(val_active_call)):
      del active_call[val_active_call[g1]]
  val_active_call=[]

  if(len(rsl_recalc)is not 0):
      count_retry=count_retry+1
      for x in rsl_recalc:
          rsl_recalc[x]=rsl_recalc[x]+1
          rsl_value=rsl_calc(position[x])
          if(rsl_value>=-107):
              active_call[x]=x
              call_dur[x]=rnd.exponential(avg_dur)
              channel_num[x]=1
              val_x.append(x)
          elif(rsl_value<-107 and rsl_recalc[x]==3):        #if RSL value has failed after 3 consecutive tries
              blocked_rsl=blocked_rsl+1
              del position[x]
              del rsl[x]
              val_x.append(x)
              user+=(x,)
          elif(rsl_value<-107 and rsl_recalc[x]<3):         #if the re-calculation value for RSL for the user is to be updated
              rsl_recalc[x]=rsl_recalc[x]+1
  for x1 in range(len(val_x)):
      del rsl_recalc[val_x[x1]]
  val_x=[]
  #### Checking RSL for a new user ####
  for p in active:
      active.remove(p)
      if(len(active_call)<=55):
          count_no_retry=count_no_retry+1
          position[p]=position_calc()
          rsl[p]=rsl_calc(position[p])
          if(rsl[p]>=-107):
              active_call[p]=p
              call_dur[p]=rnd.exponential(avg_dur)
              channel_num[p]=1    
          elif(rsl[p]<-107):
              rsl_recalc[p]=0
          elif(len(active_call)>56):
              blocked_trchannel=blocked_trchannel+1
              user+=(p,)
  #### Calculating the radius of the fathest active user ####
  rad=0
  for j in rsl:
      if(len(rsl) is not 0):
          ind=min(rsl, key=rsl.get)
          rad=math.sqrt((position[ind][0])**2+(position[ind][1])**2)
      else:
          rad=0

  if(j_count>=120 and j_count%120==0):
      print('Number of call attempts excluding retry',count_no_retry)
      print('Number of call attempts including retry',(count_no_retry+count_retry))
      print('Number of blocked calls due to traffic capacity',blocked_trchannel)
      print('Number of blocked calls due to signal strength', blocked_rsl)
      print('Number of dropped calls', blocked_sinr)
      print('Number of successfully completed calls', success_call)
      print('Number of calls in progress at a given time',len(active_call)+len(sinr_recalc))
      print('Number of failed calls',blocked_sinr+blocked_trchannel+blocked_rsl)
      print('Current cell radius in meters',rad)
      print(" ")

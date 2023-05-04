""" 
HELPER FUNCTION - Skip to line 173
STAGE 1 - FETCH - Skip to line 730
STAGE 2 - DECODE - Skip to line 737
STAGE 3 - EXECUTE - Skip to line 750
"""

import os
import argparse
import subprocess
from pathlib import Path

class Config(object):
    def __init__(self, iodir):
        self.filepath = os.path.abspath(os.path.join(iodir, "Config.txt"))
        self.parameters = {} # dictionary of parameter name: value as strings.

        try:
            with open(self.filepath, 'r') as conf:
                self.parameters = {line.split('=')[0].strip(): line.split('=')[1].split('#')[0].strip() for line in conf.readlines() if not (line.startswith('#') or line.strip() == '')}
            print("Config - Parameters loaded from file:", self.filepath)
            print("Config parameters:", self.parameters)
        except:
            print("Config - ERROR: Couldn't open file in path:", self.filepath)
            raise

class IMEM(object):
    def __init__(self, iodir,filename):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, filename))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions=[ins.split('#')[0].strip() for ins in insf.readlines() if not (ins.startswith('#'))]
                #self.instructions = [ins.strip() for ins in insf.readlines()]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)

    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            return self.instructions[idx]
        else:
            print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

class DMEM(object):
    # Word addressible - each address contains 32 bits.
    def __init__(self, name, iodir, addressLen):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.ipfilepath = os.path.abspath(os.path.join(iodir, name + ".txt"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = []

        try:
            with open(self.ipfilepath, 'r') as ipf:
                self.data = [int(line.strip()) for line in ipf.readlines()]
            print(self.name, "- Data loaded from file:", self.ipfilepath)
            # print(self.name, "- Data:", self.data)
            self.data.extend([0x0 for i in range(self.size - len(self.data))])
        except:
            print(self.name, "- ERROR: Couldn't open input file in path:", self.ipfilepath)

    def Read(self, idx): # Use this to read from DMEM.
        pass # Replace this line with your code here.

    def Write(self):#, idx, val): # Use this to write into DMEM.
        f = open(self.opfilepath ,"w")
        for i in self.data:
            f.write(str(i) + "\n")



    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)


class RegisterFile(object):
    def __init__(self, name, count, length = 1, size = 32):
        self.name       = name
        self.reg_count  = count
        self.vec_length = length # Number of 32 bit words in a register.
        self.reg_bits   = size
        self.min_value  = -pow(2, self.reg_bits-1)
        self.max_value  = pow(2, self.reg_bits-1) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        pass # Replace this line with your code.

    def Write(self,name):#, idx, val):
        f = open(name ,"w")
        for i in self.registers:
            converted_list = [str(element) for element in i]
            resultString = ','.join(converted_list)
            f.write(resultString+"\n")

        

    def dump(self, iodir):
        opfilepath = os.path.abspath(os.path.join(iodir, self.name + ".txt"))
        try:
            with open(opfilepath, 'w') as opf:
                row_format = "{:<13}"*self.vec_length
                lines = [row_format.format(*[str(i) for i in range(self.vec_length)]) + "\n", '-'*(self.vec_length*13) + "\n"]
                lines += [row_format.format(*[str(val) for val in data]) + "\n" for data in self.registers]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", opfilepath)
    
    
class Core():
    def __init__(self, imem, sdmem, vdmem, modified_imem):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem
        self.IMEM = modified_imem
                                        #defining variables
        self.pc = 0
        # self.vlr = 10
        self.vmr = [1]*64
        self.srf = [0]*8

        self.busy_board_v = [0]*8
        self.busy_board_s = [0]*8
        self.data_q_depth = int(config.parameters['dataQueueDepth'])
        self.compute_q_depth = int(config.parameters['computeQueueDepth'])
        self.scalar_only_q_depth = int(config.parameters['computeQueueDepth'])
        self.data_q =[]
        self.compute_q =[]
        self.scalar_only_q=[]
        self.chumma_q=[]
        self.fetch_flag=0
        self.decode_flag=1
        self.queue_flag=1
        self.pipeline_flag=1
        self.terminate_flag=0
       

        self.vls_depth = int(config.parameters['vlsPipelineDepth'])
        self.add_depth = int(config.parameters['pipelineDepthAdd'])
        self.mul_depth = int(config.parameters['pipelineDepthMul'])
        self.div_depth = int(config.parameters['pipelineDepthDiv'])
        self.num_lanes=int(config.parameters['numLanes'])
        self.num_banks=int(config.parameters['vdmNumBanks'])
        # self.bankbusytime=int(config.parameters['bankBusyTime'])
        self.vls_q=['0']*self.vls_depth
        self.add_q=['0']*self.add_depth
        self.mul_q=['0']*self.mul_depth
        self.div_q=['0']*self.div_depth
        self.vls_qy='0'
        self.add_qy='0'
        self.mul_qy='0'
        self.div_qy='0'
        self.dq_full_flag=0
        self.cq_full_flag=0
        
        self.countd=0
        self.counta=0
        self.countm=0
        self.countdiv=0
        self.cycles=0
        self.halt_flag=0
        self.bankconflictflag=0
    
#----------------------------------------------------HELPER FUNCTION---------------------------------------------------------------------------

        #We are calling helper_function which outputs a list of destination register,  source registers, vlr and aswell instruction

        def helper_function(fetch):
            i=fetch
            self.vlr = int(fetch.split(" ")[-1])
            
         
            if(i[:6]=='SUBVV '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1


                
                    
                # list1=[]
                # for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                #     if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                #          list1.append(int(i-j))
                     
                #     else:
                #         list1.append(vr.registers[op][i])
                # vr.registers[op]=list1
           
            elif(i[:6]=='ADDVV '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i) 
                self.pc+=1   
                # list1=[]
                # for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                #     if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                #         list1.append(int(i+j))

                     
                #     else:
                #         list1.append(vr.registers[op][i])
                # vr.registers[op]=list1
            elif(i[:6]=='MULVV '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i) 
                self.pc+=1   
                # list1=[]
                # for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                #     print(i)
                #     if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                #         list1.append(int(i*j))

                     
                #     else:
                #         list1.append(vr.registers[op][i])
                        
                # vr.registers[op]=list1
            elif(i[:6]=='DIVVV '):
                flag=0
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
                # list1=[]
                # for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                #     if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                #         if(j==0):
                #             print("divide by zero")
                #             break
                #         list1.append(int(i/j))
                     
                #     else:
                #         list1.append(vr.registers[op][i])
                # vr.registers[op]=list1
            elif(i[:6]=='ADDVS '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                #list1=[int(p) + int(sr.registers[ip2][0])  if vmr.registers[0][vr.registers[ip1].index(p)]==1  else p for p in vr.registers[ip1]]
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SUBVS '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                #list1=[int(p) - int(sr.registers[ip2][0])  if vmr.registers[0][vr.registers[ip1].index(p)]==1 else p for p in vr.registers[ip1]]
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='MULVS '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                list1=[]
                #list1=[int(p) * int(sr.registers[ip2][0])  if vmr.registers[0][vr.registers[ip1].index(p)]==1 else p for p in vr.registers[ip1]]
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='DIVVS '):
                
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                sim=[]
                sim.append('VR'+str(op))
                sim.append('VR'+ str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:3]=='CVM'):
                
                
                sim=[]
                sim.append[i]
                self.pc+=1
            elif(i[:4]=='POP '):
                op=int(i[6])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('VMR')
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SEQVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SNEVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SGTVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SLTVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SGEVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SLEVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('VR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SEQVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SNEVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SGTVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SLTVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SGEVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:6]=='SLEVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                sim=[]
                sim.append('VMR')
                sim.append('VR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(i)
                self.pc+=1
            elif(i[:5]=='MTCL '):
                ip=int(i[7])
                sim=[]
                sim.append('blank')
                sim.append('SR'+str(ip))
                sim.append(i)
                self.pc+=1
            elif(i[:5]=='MFCL '):
                ip=int(i[7])
                sim=[]
                sim.append('SR'+str(ip))
                sim.append('VLR')
                sim.append(i)
                self.pc+=1
            elif(i[:3]=='LV '):
                self.address_list=" ".join(fetch.split(" ")[-(self.vlr+1):][:-1])
                ip=int(i[9])
                op=int(i[5])
                sim=[]
                sim.append('VR'+str(op))
                sim.append('SR'+str(ip))
                sim.append(self.address_list)
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:3]=='SV '):
                self.address_list=" ".join(fetch.split(" ")[-(self.vlr+1):][:-1])
                ip=int(i[9])
                op=int(i[5])
                sim=[]
                sim.append('blank')
                sim.append('VR'+str(ip))
                sim.append('SR'+str(op))
                sim.append(self.address_list)
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:5]=='LVWS '):
                
                self.address_list=" ".join(fetch.split(" ")[-(self.vlr+1):][:-1])
                ip1=int(i[11])
                ip2=int(i[15])
                op=int(i[7])
                sim=[]
                sim.append('VR'+ str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(self.address_list)
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:5]=='SVWS '):
                
                self.address_list=" ".join(fetch.split(" ")[-(self.vlr+1):][:-1])
                ip1=int(i[11])
                ip2=int(i[15])
                op=int(i[7])
                sim=[]
                sim.append('blank')
                sim.append('VR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append('SR'+str(op))
                sim.append(self.address_list)
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1
            elif(i[:4]=='LVI '):
                self.address_list=" ".join(fetch.split(" ")[-(self.vlr+1):][:-1])
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sim=[]
                sim.append('VR'+str(op))
                sim.append('SR' +str(ip1))
                sim.append('VR'+ str(ip2))
                sim.append(self.address_list)
                sim.append(self.vlr)
                sim.append(i)
                self.pc+=1

                
            elif(i[:4]=='SVI '):
                self.address_list=" ".join(fetch.split(" ")[-(self.vlr+1):][:-1])
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=int(i[14])
                sim=[]
                sim.append('blank')
                sim.append('VR'+str(ip1))
                sim.append('SR'+ str(ip2))
                sim.append('VR'+str(ip3))
                sim.append(self.address_list)
                sim.append(self.vlr)
                sim.append(i)
                self.pc=self.pc+1
            elif(i[:3]=='LS '):
                
                
                ip1=int(i[9])
                
                op=int(i[5])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append(1)
                
                sim.append(i)
                self.pc+=1
            elif(i[:3]=='SS '):
                
                ip1=int(i[5])
                ip2=int(i[9])
                sim=[]
                sim.append('blank')
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                
                sim.append(i)
                self.pc+=1
            elif(i[:4]=='ADD ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1
            elif(i[:4]=='SUB ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                #print(sr.registers[ip1][0])
                #print(sr.registers[ip2][0])
                
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1
                #print(sr.registers[op][0])
            elif(i[:4]=='AND ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1
            elif(i[:3]=='OR ' ):
                
                ip1=int(i[9])
                ip2=int(i[13])
                op=int(i[5])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1
            elif(i[:4]=='XOR ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1
            elif(i[:4]=='SRL '):
                
               
                ip1=int(i[10])
                ip2=int(i[14])
                
                
                op=int(i[6])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1
                
            elif(i[:4]=='SLL '):
               
                ip1=int(i[10])
                ip2=int(i[14])
                
                op=int(i[6])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1
            elif(i[:4]=='SRA '):
               
                ip1=int(i[10])
                ip2=int(i[14])
                
                op=int(i[6])
                sim=[]
                sim.append('SR'+str(op))
                sim.append('SR'+str(ip1))
                sim.append('SR'+str(ip2))
                sim.append(1)
                sim.append(i)
                self.pc+=1

            elif(i[:4]=='BEQ ' ):
                ip1=int(i[6])
                ip2=int(i[10])
                sim=[]
                sim.append('blank')
                sim.append('SR'+ str(ip1))
                sim.append('SR'+ str(ip2))
                sim.append(i)
                self.fetch_flag=1
               
            elif(i[:4]=='BNE '):
                ip1=int(i[6])
                ip2=int(i[10])
                sim=[]
                sim.append('blank')
                sim.append('SR'+ str(ip1))
                sim.append('SR'+ str(ip2))
                sim.append(i)
                self.fetch_flag=1
            elif(i[:4]=='BGT '):
                ip1=int(i[6])
                ip2=int(i[10])
                sim=[]
                sim.append('blank')
                sim.append('SR'+ str(ip1))
                sim.append('SR'+ str(ip2))
                sim.append(i)
                self.fetch_flag=1
            elif(i[:4]=='BLT '):
                ip1=int(i[6])
                ip2=int(i[10])
                sim=[]
                sim.append('blank')
                sim.append('SR'+ str(ip1))
                sim.append('SR'+ str(ip2))
                sim.append(i)
                self.fetch_flag=1
            elif(i[:4]=='BGE '):
                ip1=int(i[6])
                ip2=int(i[10])
                sim=[]
                sim.append('blank')
                sim.append('SR'+ str(ip1))
                sim.append('SR'+ str(ip2))
                sim.append(i)
                self.fetch_flag=1
            elif(i[:4]=='BLE '):
                ip1=int(i[6])
                ip2=int(i[10])
                sim=[]
                sim.append('blank')
                sim.append('SR'+ str(ip1))
                sim.append('SR'+ str(ip2))
                sim.append(i)
                self.fetch_flag=1
            elif(i[:5]=='HALT '):
                sim=[]
                sim.append('blank')
                sim.append(i)

            return sim


#----------------------------------------------------STAGE 1 FETCH---------------------------------------------------------------------------
        def fetch(pc):
            if(self.fetch_flag==0):                            #if the fetch_flag is 0, then only the fetch function is executed
                self.decode_flag=0 
                return modified_imem.instructions[pc]          #returns instructions from modified_imem (Modified_imem takes care of branching) 


#----------------------------------------------------STAGE 2 DECODE---------------------------------------------------------------------------
        def decode(fetch):
            if(self.decode_flag==0):                            #if the decode_flag is 0, then only the decode function is executed
                sim = helper_function(fetch)                    #Sim is an array of destinaton, source registers, vlr and the whole instruction
                # print("simm", sim)
                ins = " ".join(sim[-1].split(" ")[:-1])
                sim = sim[:-1]+ [ins]
                self.pipeline_flag=0                            #sets pipeline_flag as 0 if decode is done !
                # print("simm", sim)
                return sim               
            else: 
                self.fetch_flag=1                               #else, decode function is not executed and also sets fetch_flag 1 

#----------------------------------------------------STAGE 3 EXECUTE---------------------------------------------------------------------------

        def pipeline(decode):             
            if(self.pipeline_flag==0):                                                     #only if pipeline_flag is zero, the following code is executed
                if(self.dq_full_flag==1 and len(self.data_q)<self.data_q_depth ):          
                    self.dq_full_flag=0
                    self.decode_flag=0
                    self.fetch_flag=0
                if(self.cq_full_flag==1 and len(self.compute_q)<self.compute_q_depth ):
                    self.cq_full_flag=0
                    self.decode_flag=0
                    self.fetch_flag=0

#---------------------------Dispatch Queue logic for load store type instructions-----------------------          
                sources=[]
                dest=decode[0]
                if(decode[-1][0:2]=='SV' or decode[-1][0:2]=='SS' or decode[-1][0:1]=='L' ):     #data queue for load and store instructions
                    flag=0
                    sources=decode[1:-3]
                    for regs in sources:
                        type=regs[0]
                        index=int(regs[2])
                        if(type=='V'):
                            if(self.busy_board_v[index]==1):                                     #BUSY BOARD checking for sources
                                flag=1                                                           #if busy board corresponding to source indices are 1, 
                                break                                                                   #sets local flag to 1 and 
                        if(type=='S'):                                                 
                            if(self.busy_board_s[index]==1):                            
                                flag=1                                                  
                                break

                    if(flag==1 or len(self.data_q)>=self.data_q_depth):             
                        # self.queue_flag=1                                                             OR data queue is almost full
                        if(len(self.data_q)==self.data_q_depth):
                            self.dq_full_flag=1                                                         #sets dq_full_flag to 1
                        self.decode_flag=1                                                              #sets decode_flag to 1
                        self.fetch_flag=1                                                               #sets fetch_flag to 1 

                    elif(flag==0 and len(self.data_q)<self.data_q_depth):
                        if(decode[-1][0:2]=='LV' or decode[-1][0:2]=='SV'):
                            self.data_q.append(decode)                                          #else append instruction in the data queue
                        
                        if(dest[0]=='V'):                            
                            self.busy_board_v[int(dest[-1])]=1                                          #and set busy board of destination index to 1  
                            self.pipeline_flag=0                                                        #and also set rest of the stage flags 0
                            self.decode_flag=0
                            self.fetch_flag=0

                #scalar instructions are taken care separately. It accesses memory from SDMEM . They are executed in one cycle after decode stage. 

                    elif(flag==0 and len(self.scalar_only_q)<self.scalar_only_q_depth):         #if busy board corresponding to source indices are 0,then
                        if(decode[-1][0:2]=='LS' or decode[-1][0:2]=='SS'):
                            self.scalar_only_q.append(decode)                        
                        if(dest[0]=='S'):
                            self.busy_board_s[int(dest[-1])]=1                                          #busy board updation for scalar
                            self.pipeline_flag=0                                                        #set busy board to 1 and also set rest of the stage flags 0 
                            self.decode_flag=0
                            self.fetch_flag=0

            #HALT instructions set all stage flags as 1 indicating halting of operation
                elif(decode[-1]=='HALT'):
                    self.fetch_flag=1
                    self.decode_flag=1
                    self.halt_flag=1                #halt_flag set to 1 - stop operation
                        
            #MTCL instructions change the value of vlr -  length of vector. Executed in one cycle after decode
                elif(decode[-1]=='MTCL'):
                    if(len(self.scalar_only_q)==0):
                        self.scalar_only_q.append(decode)
                          
#---------------------------Dispatch Queue logic for Computational Instructions-----------------------   
            #Remaining Instructions are Arithmetic and logical instructions 
                else:
                    
                    flag=0 
                    sources=decode[1:-2]                                                       #compute queue for arithmetic instructions
                    for regs in sources:
                        type=regs[0]
                        index=int(regs[2])
                        if(type=='V'):
                            if(self.busy_board_v[index]==1):                                        #BUSY BOARD checking for sources
                                flag=1                                                              #if busy board corresponding to source indices are 1,
                                break                                                                       #sets local flag to 1 and
                        if(type=='S'):
                            if(self.busy_board_s[index]==1):
                                flag=1
                                break
                    if(flag==1 or len(self.compute_q)>=self.compute_q_depth):                               #OR compute queue is almost full
                        if(len(self.compute_q)==self.compute_q_depth):
                            self.cq_full_flag=1                                                             #sets dq_full_flag to 1
                        self.decode_flag=1                                                                  #sets decode_flag to 1
                        self.fetch_flag=1                                                                   #sets fetch_flag to 1
                        

                    elif(flag==0 and len(self.compute_q)<self.compute_q_depth and dest[0]=='V'):    #else append instruction in the compute queue
                        self.busy_board_v[int(dest[-1])]=1                                                  #and set busy board of destination index to 1 
                        self.compute_q.append(decode)                                                       #and also set rest of the stage flags 0
                        self.pipeline_flag=0
                        self.decode_flag=0
                        self.fetch_flag=0

                #busy board updation for scalar Computational Instructions
                    elif(flag==0 and len(self.scalar_only_q)<self.scalar_only_q_depth and dest[0]=='S'):                  
                        self.busy_board_s[int(dest[-1])]=1
                        self.scalar_only_q.append(decode)
                        self.pipeline_flag=0
                        self.decode_flag=0
                        self.fetch_flag=0



#---------------------------Pipelining logic---------------------------------------------------------------------------------

            """ Pipelining logic
            for load store type -
                if data queue is not empty
                    1) check the bank conflicts at pipe-end(vls)
                    2) set corresponding busy board destination index to 0
                    3) shift the pipeline(vls)
                    4) delete the instruction from the queue
                else
                    step 1 + 2 + 3
                    
            for arithmetic type instructions - 
                if compute queue is not empty
                    1) set corresponding busy board destination index to 0
                    2) shift the pipeline(mul + add + div)
                    3) delete the instruction from the queue
                else
                    step 1 + 2
                    
            if all queues and pipelines are 0 and halt flag is 1 then terminate flag is set to 1 
            
            DJ FORMULA is used to calculate number of elements gets into the pipeline per lane
                if number of elements(m) are less than the number of lanes(l) - executes in 1 cycles
                else m/l + (m mod l)"""

#check report for neat explanation 
            dq_f=0
            cq_f=0                  #local flags
                        
        #For scalar instructions only
            if(len(self.scalar_only_q)>0):
                scalar = self.scalar_only_q[0]
                dest=scalar[0]
                index=int(dest[2])
                
                self.busy_board_s[index]=0                                      #set busy board of destination index to 0
                del self.scalar_only_q[0]                                       #delete that instrution out of the pipeline - execution done
                self.queue_flag=0                                               #set stage flags 0 for continued execution
                self.decode_flag=0
                self.fetch_flag=0

        #If there is an instruction in data queue - push to pipeline - check conditions(busy board updation and delete instruction in queue)
        #also check for Bank conflicts
            if(len(self.data_q)>0 ):
               
               dq_f=1
               length=int(self.data_q[0][-2]) 
               banknum=0

               if(length<self.num_lanes):                                                                           # DJ FORMULA GIVES number of elements per lane
                banknum=1
               else:
                banknum=int((length/self.num_lanes)) + min(1,int((length % self.num_lanes)))

               self.vls_qy=self.vls_q[-1]
               
               pipend=self.vls_qy
               
               if(pipend!='0' and self.bankconflictflag==0):
                finnum=0
                if(int(self.vls_qy.split(" ")[-1])<self.num_lanes):
                    finnum=1
                else:
                    finnum=int(int(self.vls_qy.split(" ")[-1])/self.num_lanes)+ min(1,int(int(self.vls_qy.split(" ")[-1])%self.num_lanes))

                
                splitinst=pipend.split(" ")
                #print(splitinst)
                if(int(splitinst[-int(splitinst[-1])-2])==finnum-1):
                    dest=splitinst[1]
                    type=dest[0]
                    index=int(dest[2])
                    if(type=='V'):
                         self.busy_board_v[index]=0                                                 #busy board updation

               var=self.data_q[0][-1]
               ele=[var+" "+str(i) + " "+ str(self.data_q[0][-3])+" " + str(self.data_q[0][-2]) for i in range(banknum)]
                
            # check Bank conflicts and shift
               if(self.bankconflictflag!=0):
                    
                    self.bankconflictflag-=1
                    if(self.bankconflictflag==0):
                        #self.vls_qy=self.vls_q[-1]
                        self.vls_q= [ele[self.countd]] + self.vls_q[0:-1]                                #shift (deletion of last element basically)
                        self.countd+=1

               else:
                    conflict_no=0   
                    fl=0
                    finsize=0
                    if(self.vls_q[-1]!='0'):
                        
                        splitter=self.vls_q[-1].split(" ")
                        
                        eleno=int(splitter[-int(splitter[-1])-2])
                        #print(splitter)
                        conflict_list=[]
                        finnum=0
                        if(int(self.vls_qy.split(" ")[-1])<self.num_lanes):
                            finnum=1
                        else:
                            finnum=int(int(self.vls_qy.split(" ")[-1])/self.num_lanes)+ int(int(self.vls_qy.split(" ")[-1])%self.num_lanes)
                        
                        if(finnum==1 and int(self.vls_qy.split(" ")[-1])!=64):
                            finsize=finnum
                        else:
                            finsize=self.num_lanes
                        eleno=int(splitter[-int(splitter[-1])-2])
                        conflict_list=[]
                        for i in range(finsize):
                            addrlist=self.vls_q[-1].split(" ")
                            addr=0
                            index=addrlist[-int(addrlist[-1])-1:][:-1]
                            
                            addr=int(index[(eleno*finsize)+i])
                            
                            
                            bank=addr%self.num_banks
                            conflict_list.append(bank)
                        if(len(conflict_list) != len(set(conflict_list))): 
                           
                                conflict_no=len(conflict_list)/len(set(conflict_list))
                                fl=1
                                                                 # checking for the number of bank conflicts
                            
                    if(fl==1):
                        self.bankconflictflag=conflict_no-1

                    
                    else:                            
                        #self.vls_qy=self.vls_q[-1]
                        self.vls_q= [ele[self.countd]] + self.vls_q[0:-1]                                #shift (deletion of last element basically)
                        self.countd+=1
            
            #deletion of instruction from data queue
               if(self.countd>=banknum):                   
                    del self.data_q[0]   
                    self.countd=0

        #Compute Queue is not empty - push to pipeline - check conditions(busy board updation and delete instruction in queue)
            if(len(self.compute_q)>0):
                
                cq_f=1
                length=int(self.compute_q[0][-2]) 
                lanenum=0
                if(length<self.num_lanes):
                    lanenum=1
                else:
                    lanenum=int((length/self.num_lanes)) + min(1,int((length % self.num_lanes)))                 
                
                
            #if it is div instruction
                self.div_qy=self.div_q[-1]
                pipenddiv=self.div_qy
                if(pipenddiv!='0'):
                 splitinst=pipenddiv.split(" ")
                 finnum=0
                 if(int(self.div_qy.split(" ")[-1])<self.num_lanes):
                    finnum=1
                 else:
                    finnum=int(int(self.div_qy.split(" ")[-1])/self.num_lanes)+ min(1,int(int(self.div_qy.split(" ")[-1])%self.num_lanes))

                 
                 if(int(splitinst[-2])==finnum-1):
                    dest=splitinst[1]
                    type=dest[0]
                    index=int(dest[2])
                    if(type=='V'):
                         self.busy_board_v[index]=0

            #if it is mul instruction
                self.mul_qy=self.mul_q[-1]
                pipendmul=self.mul_qy
                if(pipendmul!='0'):
                 splitinst=pipendmul.split(" ")
                 finnum=0
                 if(int(self.mul_qy.split(" ")[-1])<self.num_lanes):
                    finnum=1
                 else:
                    finnum=int(int(self.mul_qy.split(" ")[-1])/self.num_lanes)+ min(1,int(int(self.mul_qy.split(" ")[-1])%self.num_lanes))

                 
                 if(int(splitinst[-2])==finnum-1):
                    dest=splitinst[1]
                    type=dest[0]
                    index=int(dest[2])
                    if(type=='V'):
                         self.busy_board_v[index]=0

            #if it is add instruction
                self.add_qy=self.add_q[-1]
                pipendadd=self.add_qy                
                if(pipendadd!='0'):
                  
                  splitinst=pipendadd.split(" ")
                  if(int(self.add_qy.split(" ")[-1])<self.num_lanes):
                    finnum=1
                  else:
                    finnum=int(int(self.add_qy.split(" ")[-1])/self.num_lanes)+ min(1,int(int(self.add_qy.split(" ")[-1])%self.num_lanes))

                  
                  if(int(splitinst[-2])==finnum-1):
                     
                    
                     dest=splitinst[1]
                     type=dest[0]
                     index=int(dest[2])
                     if(type=='V'):
                          
                          self.busy_board_v[index]=0
                          
            #shifting process
                if(self.compute_q[0][-1][0:3]=='MUL'):
                    var=self.compute_q[0][-1]
                    ele=[var+" "+str(i) + " " + str(self.compute_q[0][-2]) for i in range(lanenum)]
                    
               
                    
                    #self.div_qy=self.div_q[-1]
                    self.div_q= ['0'] + self.div_q[0:-1]                                #shift div lane
                    
                    #self.mul_qy=self.mul_q[-1]
                    self.mul_q= [ele[self.countm]] + self.mul_q[0:-1]                   #shift mul lane
                    
                    #self.add_qy=self.add_q[-1]
                    self.add_q= ['0'] + self.add_q[0:-1]                                #shift add lane
                    
                    self.countm+=1
                elif(self.compute_q[0][-1][0:3]=='DIV'):
                    
                    var=self.compute_q[0][-1]
                    ele=[var+" "+str(i) + " " + str(self.compute_q[0][-2]) for i in range(lanenum)]
               
                    
                    #self.div_qy=self.div_q[-1]
                    self.div_q= [ele[self.countdiv]] + self.div_q[0:-1]
                    
                    #self.mul_qy=self.mul_q[-1]
                    self.mul_q= ['0'] + self.mul_q[0:-1]
                    
                    #self.add_qy=self.add_q[-1]
                    self.add_q= ['0'] + self.add_q[0:-1]
                    self.countdiv+=1
                else:
                    var=self.compute_q[0][-1]
                    ele=[var+" "+str(i) + " " + str(self.compute_q[0][-2]) for i in range(lanenum)]
               
                    #self.add_qy=self.add_q[-1]
                    
                    self.add_q= [ele[self.counta]] + self.add_q[0:-1]
                    
                    #self.mul_qy=self.mul_q[-1]
                    self.mul_q= ['0'] + self.mul_q[0:-1]
                    
                    #self.div_qy=self.div_q[-1]
                    self.div_q= ['0'] + self.div_q[0:-1]
                    self.counta+=1

            #deletion of instruction from queue   
                if(self.counta>=lanenum):                    
                    del self.compute_q[0]                    
                    self.counta=0
                
                if(self.countm>=lanenum):
                    del self.compute_q[0]                    
                    self.countm=0

                if(self.countdiv>=lanenum):
                    del self.compute_q[0]
                    self.countdiv=0

        #if both data and compute queues are empty - check instructions in pipeline - push  ; else - check for halt flag and terminate_flag is set
            if(len(self.data_q)==0 and len(self.compute_q)==0 and cq_f==0 and dq_f==0 ):

            #if vls pipeline is not empty and no bank conflicts
                self.vls_qy=self.vls_q[-1]
                pipend=self.vls_qy
                if(pipend!='0' and self.bankconflictflag==0):
                    splitinst=pipend.split(" ")
                    banknum=0
                                                                                                    # DJ FORMULA GIVES number of elements per lane
                    if(int(self.vls_qy.split(" ")[-1])<self.num_lanes):
                        banknum=1
                    else:
                        banknum=int((int(splitinst[-1])/self.num_lanes)) + min(1,int((int(splitinst[-1]) % self.num_lanes)))

                    if(int(splitinst[-int(splitinst[-1])-2])==banknum-1):
                        dest=splitinst[1]
                        type=dest[0]
                        index=int(dest[2])
                        if(type=='V'):
                            self.busy_board_v[index]=0                                              #set busy board dest index to 0

            #if div pipeline is not empty
                self.div_qy=self.div_q[-1]
                pipenddiv=self.div_qy            
                if(pipenddiv!='0'):
                  splitinst=pipenddiv.split(" ")
                  lanenum=0
                  if(int(self.div_qy.split(" ")[-1])<self.num_lanes):                               # DJ FORMULA GIVES number of elements per lane
                    lanenum=1
                  else:
                    lanenum=int((int(splitinst[-1])/self.num_lanes)) + min(1,int((int(splitinst[-1]) % self.num_lanes)))
                  

                  if(int(splitinst[-2])==lanenum-1):
                     dest=splitinst[1]
                     type=dest[0]
                     index=int(dest[2])
                     if(type=='V'):
                          self.busy_board_v[index]=0                                                #set busy board dest index to 0

            #if mul pipeline is not empty
                self.mul_qy=self.mul_q[-1]
                pipendmul=self.mul_qy
                if(pipendmul!='0'):
                  splitinst=pipendmul.split(" ")
                  lanenum=0
                  if(int(self.mul_qy.split(" ")[-1])<self.num_lanes):                               #DJ FORMULA GIVES number of elements per lane
                    lanenum=1
                  else:
                    lanenum=int((int(splitinst[-1])/self.num_lanes)) + min(1,int((int(splitinst[-1]) % self.num_lanes)))
                  
                  if(int(splitinst[-2])==lanenum-1):
                     dest=splitinst[1]
                     type=dest[0]
                     index=int(dest[2])
                     if(type=='V'):
                          self.busy_board_v[index]=0                                                #set busy board dest index to 0

            #if add pipeline is not empty
                self.add_qy=self.add_q[-1]
                pipendadd=self.add_qy
                if(pipendadd!='0'):       
                   splitinst=pipendadd.split(" ")                  
                   lanenum=0
                   if(int(self.add_qy.split(" ")[-1])<self.num_lanes):                              # DJ FORMULA GIVES number of elements per lane
                    lanenum=1
                   else:
                    lanenum=int((int(splitinst[-1])/self.num_lanes)) + min(1,int((int(splitinst[-1]) % self.num_lanes)))
                   if(int(splitinst[-2])==lanenum-1):
                     
                      dest=splitinst[1]
                    
                      type=dest[0]
                      index=int(dest[2])
                      if(type=='V'):
                          
                          self.busy_board_v[index]=0                                                  #set busy board dest index to 0

            #Bank conflicts  
                if(self.bankconflictflag!=0):
                    self.bankconflictflag-=1
                    if(self.bankconflictflag==0):
                        #self.vls_qy=self.vls_q[-1]
                        self.vls_q= ['0'] + self.vls_q[0:-1]                                #shift (deletion of last element basically)
                else:                
                    conflict_no=0
                    fl=0
                    finsize=0
                    if(self.vls_q[-1]!='0'):
                        splitter=self.vls_q[-1].split(" ")
                        finnum=0
                        #print(self.vls_qy)
                        if(int(self.vls_qy.split(" ")[-1])<self.num_lanes):                 # DJ formula
                            finnum=1
                        else:
                            finnum=int(int(self.vls_qy.split(" ")[-1])/self.num_lanes)+ min(1,int(int(self.vls_qy.split(" ")[-1])%self.num_lanes))

                        
                        if(finnum==1 and int(self.vls_qy.split(" ")[-1])!=64):
                            finsize=finnum
                        else:
                            finsize=self.num_lanes
                        
                        eleno=int(splitter[-int(splitter[-1])-2])
                        conflict_list=[]
                        for i in range(finsize):
                            addrlist=self.vls_q[-1].split(" ")
                            addr=0
                            index=addrlist[-int(addrlist[-1])-1:][:-1]
                            
                            addr=int(index[(eleno*finsize)+i])
                            bank=addr%self.num_banks
                            conflict_list.append(bank)
                        if(len(conflict_list) != len(set(conflict_list))):
                            
                                conflict_no=len(conflict_list)/len(set(conflict_list))
                                fl=1                                  # checking for the number of bank conflicts
                            
                    if(fl==1):
                        self.bankconflictflag=conflict_no-1

                    
                    else:
                        #self.vls_qy=self.vls_q[-1]
                        self.vls_q= ['0'] + self.vls_q[0:-1]                                #shift (deletion of last element basically)
                          
                        
            #shifting across pipeline    
                #self.mul_qy=self.mul_q[-1]
                self.mul_q= ['0'] + self.mul_q[0:-1]                                    #shift (deletion of last element basically)
                
                #self.add_qy=self.add_q[-1]
                self.add_q= ['0'] + self.add_q[0:-1]                                    #shift (deletion of last element basically)
                
                #self.div_qy=self.div_q[-1]
                self.div_q= ['0'] + self.div_q[0:-1]                                    #shift (deletion of last element basically)
                cq_f=1
                dq_f=1

                #if both data and compute queues are empty and also halt falg is 1 and also pipelines are empty, terminate flag set to 1
                if(all(element == '0' for element in self.vls_q) and all(element == '0' for element in self.add_q) and all(element == '0' for element in self.mul_q) and all(element == '0' for element in self.div_q) and self.halt_flag==1):
                    self.terminate_flag=1

        #only if data queue is empty
            if(len(self.data_q)==0 and  dq_f==0 ):
                
                self.vls_qy=self.vls_q[-1]
                pipend=self.vls_qy
                if(pipend!='0' and self.bankconflictflag==0):
                 splitinst=pipend.split(" ")
                 
                 banknum=0
                 if(int(self.vls_qy.split(" ")[-1])<self.num_lanes):
                    banknum=1
                 else:

                   banknum=int((int(splitinst[-1])/self.num_lanes)) + min(1,int((int(splitinst[-1]) % self.num_lanes)))
                 if(int(splitinst[-int(splitinst[-1])-2])==banknum-1):
                    dest=splitinst[1]
                    type=dest[0]
                    index=int(dest[2])
                    if(type=='V'):
                         self.busy_board_v[index]=0
                
            #check Bank conflict     
                if(self.bankconflictflag!=0):
                    self.bankconflictflag-=1
                    if(self.bankconflictflag==0):
                        #self.vls_qy=self.vls_q[-1]
                        self.vls_q= ['0'] + self.vls_q[0:-1]                                #shift (deletion of last element basically)
                  
                else:
                        conflict_no=0
                        fl=0
                        finsize=0
                        if(self.vls_q[-1]!='0'):
                            splitter=self.vls_q[-1].split(" ")
                            finnum=0
                            if(int(self.vls_qy.split(" ")[-1])<self.num_lanes):
                               finnum=1
                            else:
                              finnum=int(int(self.vls_qy.split(" ")[-1])/self.num_lanes)+ min(int(int(self.vls_qy.split(" ")[-1])%self.num_lanes),1)
                            
                            if(finnum==1 and int(self.vls_qy.split(" ")[-1])!=64):
                                finsize=finnum
                            else:
                                finsize=self.num_lanes
                            
                            eleno=int(splitter[-int(splitter[-1])-2])
                            conflict_list=[]
                            for i in range(finsize):
                              addrlist=self.vls_q[-1].split(" ")
                              addr=0
                              index=addrlist[-int(addrlist[-1])-1:][:-1]
                              
                                
                              addr=int(index[(eleno*finsize)+i])
                              bank=addr%self.num_banks
                              conflict_list.append(bank)
                            if(len(conflict_list) != len(set(conflict_list))):
                                
                                   conflict_no=len(conflict_list)/len(set(conflict_list))
                                   fl=1
                                                                  # checking for the number of bank conflicts
                               
                        if(fl==1):
                            self.bankconflictflag=conflict_no-1

                        
                        else:
                          #self.vls_qy=self.vls_q[-1]
                          self.vls_q= ['0'] + self.vls_q[0:-1]     
                
        #only if compute queue is empty   
            if(len(self.compute_q)==0 and   cq_f==0):
                
                self.div_qy=self.div_q[-1]
                pipenddiv=self.div_qy
                if(pipenddiv!='0'):
                  
                  splitinst=pipenddiv.split(" ")
                
                  lanenum=0
                  if(int(self.div_qy.split(" ")[-1])<self.num_lanes):
                    lanenum=1
                  else:
                    lanenum=int((int(splitinst[-1])/self.num_lanes)) + int((int(splitinst[-1]) % self.num_lanes))
                  if(int(splitinst[-2])==lanenum-1):
                     dest=splitinst[1]
                     type=dest[0]
                     index=int(dest[2])
                     if(type=='V'):
                          self.busy_board_v[index]=0
                
                self.mul_qy=self.mul_q[-1]
                pipendmul=self.mul_qy
                if(pipendmul!='0'):
                  splitinst=pipendmul.split(" ")
                
                  lanenum=0
                  if(int(self.mul_qy.split(" ")[-1])<self.num_lanes):
                    lanenum=1
                  else:
                    lanenum=int((int(splitinst[-1])/self.num_lanes)) + int((int(splitinst[-1]) % self.num_lanes))
                  if(int(splitinst[-2])==lanenum-1):
                     dest=splitinst[1]
                     type=dest[0]
                     index=int(dest[2])
                     if(type=='V'):
                          self.busy_board_v[index]=0
                
                
                self.add_qy=self.add_q[-1]
                pipendadd=self.add_qy
                if(pipendadd!='0'):
                    

                   splitinst=pipendadd.split(" ")
                  
                   lanenum=0
                   if(int(self.add_qy.split(" ")[-1])<self.num_lanes):
                    lanenum=1
                   else:
                    lanenum=int((int(splitinst[-1])/self.num_lanes)) + int((int(splitinst[-1]) % self.num_lanes))
                   
                   if(int(splitinst[-2])==lanenum-1):
                     
                      dest=splitinst[1]
                    
                      type=dest[0]
                      index=int(dest[2])
                      if(type=='V'):
                        #    print(self.cycles+1)
                           self.busy_board_v[index]=0

                #self.add_qy=self.add_q[-1]
                self.add_q= ['0'] + self.add_q[0:-1]
                #self.mul_qy=self.mul_q[-1]
                self.mul_q= ['0'] + self.mul_q[0:-1]
                #self.div_qy=self.div_q[-1]
                self.div_q= ['0'] + self.div_q[0:-1]



    #CALL THE STAGE FUNCTIONS 
        while(self.terminate_flag!=1):
            
            if(self.pipeline_flag==0):
                pipeline(decode1)  
            
            if(self.decode_flag==0):                
                decode1=decode(fetch1)
                
            if(self.fetch_flag==0):
                fetch1=fetch(self.pc)              

            self.cycles+=1
        print(self.cycles)
        print("The total number of cycles taken for execution is ", self.cycles)
       
    
            
    def run(self):
        while(True):
            break # Replace this line with your code.

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    try:
        #parse arguments for input file location
        parser = argparse.ArgumentParser(description='Vector Core Performance Model')
        parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
        args = parser.parse_args()

        iodir = os.path.abspath(args.iodir)
        print("IO Directory:", iodir)

        # Parse Config
        config = Config(iodir)

        # Parse IMEM
        imem=IMEM(iodir,'Code.asm')

        sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.

        vdmem = DMEM("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

        my_file = Path(iodir+"\Modified_code.asm")
        print(my_file)
        if my_file.is_file():
            modified_imem = IMEM(iodir, "Modified_code.asm")
        else:
            print("If Modified_code.asm file is not found, Please run Functional Simulator first.")


        # Create Vector Core
        vcore = Core(imem, sdmem, vdmem, modified_imem)

    except:
        print("Please run Functional Simulator first. Command:  python js12891_and_ds6992_funcsimulator.py --iodir <path/to/the/directory/containing/your/io/files>")

    # THE END

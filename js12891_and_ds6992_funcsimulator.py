import os
import argparse

class IMEM(object):
    def __init__(self, iodir,filename):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, filename))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions=[ins.split('#')[0].strip() for ins in insf.readlines() if not (ins.startswith('#')or ins.strip()=='')]
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
    def __init__(self, imem, sdmem, vdmem):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem
        modified_imem =[]
        #self.RFs = {"SRF": RegisterFile("SRF", 8),
        #            "VRF": RegisterFile("VRF", 8, 64)}
        sr=RegisterFile("SRF",8)
        vr=RegisterFile("VRF",8,64)
        vlr=RegisterFile("VLR",1)
        vlr.registers[0]=64 # MVL of register
        vmr=RegisterFile("VMR",1,64)
        for i in range(64):
            vmr.registers[0][i]=1


       
        

        # #Vector Operations test
        # for i in range(64):
        #     vr.registers[1][i]=2
        #     vr.registers[2][i]=1
        #     vr.registers[4][i]=22
        # sr.registers[5]=[12]
        # sr.registers[4]=[11]



   

        # Your code here.
        pc=0
        i=imem.instructions[pc]
        
        
        print(imem.instructions)
        while(i!='HALT'):
            address_list=""
            
            
            
            if(i[:6]=='SUBVV '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                for i in range(64):
                    if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                        vr.registers[op][i]=vr.registers[ip1][i]-vr.registers[ip2][i]
                    
                # list1=[]
                # for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                #     if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                #          list1.append(int(i-j))
                     
                #     else:
                #         list1.append(vr.registers[op][i])
                # vr.registers[op]=list1
            elif(i==''):
                pc=pc+1
                i=imem.instructions[pc]
                continue
            elif(i[:6]=='ADDVV '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                for i in range(64):
                    if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                        vr.registers[op][i]=vr.registers[ip1][i]+vr.registers[ip2][i]
                    
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
                for i in range(64):
                    if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                        vr.registers[op][i]=vr.registers[ip1][i]*vr.registers[ip2][i]
                    
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
                for i in range(64):
                    if(vr.registers[ip2][i]==0):
                        flag=1
                        print("Divide by zero error")
                        break
                    if(vmr.registers[0][i]==1 and i<vlr.registers[0]):
                        vr.registers[op][i]=int(vr.registers[ip1][i]/vr.registers[ip2][i])
                if(flag==1):
                    break
                
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
                list1=[]
                for i in range(64):
                    if(i<vlr.registers[0] and vmr.registers[0][i]==1):
                        ele=int(sr.registers[ip2][0])+int(vr.registers[ip1][i])
                        list1.append(ele)
                    else:
                        list1.append(vr.registers[op][i])

                
                vr.registers[op]=list1
            elif(i[:6]=='SUBVS '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                #list1=[int(p) - int(sr.registers[ip2][0])  if vmr.registers[0][vr.registers[ip1].index(p)]==1 else p for p in vr.registers[ip1]]
                list1=[]
                for i in range(64):
                    if(i<vlr.registers[0] and vmr.registers[0][i]==1):
                        ele=int(vr.registers[ip1][i]) - int(sr.registers[ip2][0])
                        list1.append(ele)
                    else:
                        list1.append(vr.registers[op][i])

                
                vr.registers[op]=list1
            elif(i[:6]=='MULVS '):
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                list1=[]
                #list1=[int(p) * int(sr.registers[ip2][0])  if vmr.registers[0][vr.registers[ip1].index(p)]==1 else p for p in vr.registers[ip1]]
                for i in range(64):
                    
                    if(i<vlr.registers[0] and vmr.registers[0][i]==1):
                        ele=int(vr.registers[ip1][i]) * int(sr.registers[ip2][0])
                        
                        list1.append(ele)
                        
                    else:
                        
                        list1.append(vr.registers[op][i])
                
                vr.registers[op]=list1
            elif(i[:6]=='DIVVS '):
                
                ip1=int(i[12])
                ip2=int(i[16])
                op=int(i[8])
                list1=[]
                if(sr.registers[ip2][0])==0:
                    print("divide by zero error ")
                    break
                #list1=[(int(int(p) / int(sr.registers[ip2][0])) ) if vmr.registers[0][vr.registers[ip1].index(p)]==1 else p for p in vr.registers[ip1]]
                for i in range(64):
                    if(i<vlr.registers[0] and vmr.registers[0][i]==1):
                        
                        ele=int(int(vr.registers[ip1][i]) / int(sr.registers[ip2][0]))
                        list1.append(ele)
                    else:
                        list1.append(vr.registers[op][i])
                
                vr.registers[op]=list1
            elif(i[:3]=='CVM'):
                
                for i in range(64):
                    vmr.registers[0][i]=1
            elif(i[:4]=='POP '):
                op=int(i[6])
                sum=0
                for i in vmr.registers[0]:
                    sum=sum+int(i)
                sr.registers[op]=[sum]
            elif(i[:6]=='SEQVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                    if(i==j):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SNEVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                    if(i!=j):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SGTVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                    if(i>j):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SLTVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                    if(i<j):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SGEVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                    if(i>=j):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SLEVV '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i,j in zip(vr.registers[ip1],vr.registers[ip2]):
                    if(i<=j):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SEQVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i in vr.registers[ip1]:
                    if(i==sr.registers[ip2][0]):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SNEVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i in vr.registers[ip1]:
                    if(i!=sr.registers[ip2][0]):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SGTVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i in vr.registers[ip1]:
                    if(i>sr.registers[ip2][0]):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SLTVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i in vr.registers[ip1]:
                    if(i<sr.registers[ip2][0]):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SGEVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i in vr.registers[ip1]:
                    if(i>=sr.registers[ip2][0]):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:6]=='SLEVS '):
                ip1=int(i[8])
                ip2=int(i[12])
                list1=[]
                for i in vr.registers[ip1]:
                    if(i<=sr.registers[ip2][0]):
                        list1.append(1)
                    else:
                        list1.append(0)
                vmr.registers[0]=list1
            elif(i[:5]=='MTCL '):
                ip=int(i[7])
                vlr.registers[0]=sr.registers[ip][0]
            elif(i[:5]=='MFCL '):
                ip=int(i[7])
                sr.registers[ip][0]=vlr.registers[0]
            elif(i[:3]=='LV '):
                
                alist=[]
                flag=0
                ip=int(i[9])
                op=int(i[5])
                address=(sr.registers[ip][0])
                index=address
                count=0
                if address<0 or address>=131072:
                    print("invalid address")
                    break
                while(index<=(address+vlr.registers[0]-1)):
                    if(vmr.registers[0][count]==1):
                        vr.registers[op][count]=vdmem.data[index]
                        alist.append(str(index))
                        
                       
                    
                    index=index+1
                    count=count+1
                    if index>=131072:
                        print("invalid address")
                        flag=1
                        break
                if flag==1:
                    break
                address_list=' '.join(alist)
            elif(i[:3]=='SV '):
                
                alist=[]
                flag=0
                ip=int(i[9])
                op=int(i[5])
                address=sr.registers[ip][0]
                if address<0 or address>=131072:
                    print("invalid address")
                for i in range(vlr.registers[0]):
                    if address+i >=131072:
                        flag=1
                        print("invalid address")
                        break
                    if(vmr.registers[0][i]==1):
                        vdmem.data[(address+i)]=vr.registers[op][i]
                        alist.append(str(address+i))
                    


                    
                if(flag==1):
                     break
                address_list=' '.join(alist)
            elif(i[:5]=='LVWS '):
                
                alist=[]
                flag=0
                ip1=int(i[11])
                ip2=int(i[15])
                op=int(i[7])
                stride=sr.registers[ip2][0]
                address=(sr.registers[ip1][0])
                index=address
                count=0
                if address<0 or address>=131072:
                    print("invalid address")
                    break
                while(index<=((address+vlr.registers[0]*stride)-1)):
                    if(vmr.registers[0][count]==1):
                        vr.registers[op][count]=vdmem.data[index]
                        alist.append(str(index))
                    index=index+stride
                    count=count+1
                    if index>=131072:
                        flag=1
                        print("invalid address")
                        break
                if(flag==1):
                    break
                address_list=' '.join(alist)
            elif(i[:5]=='SVWS '):
                
                alist=[]
                flag=0
                ip1=int(i[11])
                ip2=int(i[15])
                op=int(i[7])
                stride=sr.registers[ip2][0]
                address=(sr.registers[ip1][0])
                if address<0 or address>=131072:
                    print("invalid address")
                    break
                for i in range(vlr.registers[0]):
                    if address+(stride*i) >=131072:
                        print("invalid address")
                        flag=1
                        break
                    if(vmr.registers[0][i]==1):
                        vdmem.data[(address+(stride*i))]=vr.registers[op][i]
                        alist.append(str(address+(stride*i)))
                    
                
                if(flag==1):
                    break
                address_list=' '.join(alist)
            elif(i[:4]=='LVI '):
                
                alist=[]
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                base=int(sr.registers[ip1][0])
                flag=0
                if base <0 or base>=131072:
                    print("invalid address")
                    break
                for i in range(vlr.registers[0]):
                    
                    val=base+vr.registers[ip2][i]
                    
                    if(val<0 or val>131072):
                        print("invalid address")
                        flag=1
                        break
                    if(vmr.registers[0][i]==1):
                        
                        vr.registers[op][i]=vdmem.data[val]
                        alist.append(str(val))
                if(flag==1):
                    break
                address_list=' '.join(alist)
            elif(i[:4]=='SVI '):
                
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=int(i[14])
                base=int(sr.registers[ip2][0])
                flag=0
                if base<0 or base>=131072:
                    print("invalid address")
                for i in range(vlr.registers[0]):
                    val=base + vr.registers[ip3][i]
                    if(val<0 or val>131072):
                        print("invalid address")
                        flag=1
                        break
                    if(vmr.registers[0][i]):
                        vdmem.data[val]=vr.registers[ip1][i]
                        address_list=address_list+" "+ str(val)
                if(flag==1):
                    break
                address_list=address_list[:-1]
            elif(i[:3]=='LS '):
                
                ip1=int(i[9])
                ip2=''
                j=11
                while(j<len(i)):
                    ip2=ip2+i[j]
                    j=j+1
                ip2=int(ip2)
                op=int(i[5])
                print(op)
                address=sr.registers[ip1][0]+ip2
            
                if(address<0 or address> 8992):
                    print("invalid address")
                    break
                sr.registers[op][0]=sdmem.data[address]
            elif(i[:3]=='SS '):
                ip1=int(i[5])
                ip2=int(i[9])
                ip3=''
                j=11
                while(j<len(i)):
                    ip3=ip3+i[j]
                    j=j+1
                ip3=int(ip3)
                address=sr.registers[ip2][0]+ip3
                if(address<0 or address>8992):
                    print("invalid address")
                    break
                sdmem.data[address]=sr.registers[ip1][0]
            elif(i[:4]=='ADD ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sr.registers[op][0]=sr.registers[ip1][0]+sr.registers[ip2][0]
            elif(i[:4]=='SUB ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sr.registers[op][0]=sr.registers[ip1][0]-sr.registers[ip2][0]
            elif(i[:4]=='AND ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sr.registers[op][0]=sr.registers[ip1][0]&sr.registers[ip2][0]
            elif(i[:3]=='OR ' ):
                
                ip1=int(i[9])
                ip2=int(i[13])
                op=int(i[5])
                sr.registers[op][0]=sr.registers[ip1][0]|sr.registers[ip2][0]
            elif(i[:4]=='XOR ' ):
                ip1=int(i[10])
                ip2=int(i[14])
                op=int(i[6])
                sr.registers[op][0]=sr.registers[ip1][0]^sr.registers[ip2][0]
            elif(i[:4]=='SRL '):
                print("test")
               
                ip1=int(i[10])
                ip2=int(i[14])
                val=sr.registers[ip1][0]
                print(val)
                by=sr.registers[ip2][0]
                val=(val % 0x100000000) >> by
                print(val)
                op=int(i[6])
                
                sr.registers[op][0]=val
            elif(i[:4]=='SLL '):
               
                ip1=int(i[10])
                ip2=int(i[14])
                val=sr.registers[ip1][0]
                by=sr.registers[ip2][0]
                val=(val % 0x100000000) << by
                op=int(i[6])
                
                sr.registers[op][0]=val
            elif(i[:4]=='SRA '):
               
                ip1=int(i[10])
                ip2=int(i[14])
                val=sr.registers[ip1][0]
                by=sr.registers[ip2][0]
                val=val >> by
                op=int(i[6])
                
                sr.registers[op][0]=val

            elif(i[:4]=='BEQ ' ):
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=''
                j=12
                
                while(j<len(i)):
                    ip3=ip3+i[j]
                    j=j+1
                if(sr.registers[ip1][0]==sr.registers[ip2][0]):
                    
                    pc=pc+int(ip3)
                    i=imem.instructions[pc]
                    continue
            elif(i[:4]=='BNE '):
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=''
                j=12
                while(j<len(i)):
                    ip3=ip3+i[j]
                    j=j+1
                if(sr.registers[ip1][0]!=sr.registers[ip2][0]):
                    pc=pc+int(ip3)
                    i=imem.instructions[pc]
                    continue
            elif(i[:4]=='BGT '):
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=''
                j=12
                while(j<len(i)):
                    ip3=ip3+i[j]
                    j=j+1
                if(sr.registers[ip1][0]>sr.registers[ip2][0]):
                    pc=pc+int(ip3)
                    i=imem.instructions[pc]
                    continue
            elif(i[:4]=='BLT '):
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=''
                j=12
                while(j<len(i)):
                    ip3=ip3+i[j]
                    j=j+1
                if(sr.registers[ip1][0]<sr.registers[ip2][0]):
                    pc=pc+int(ip3)
                    i=imem.instructions[pc]
                    continue
            elif(i[:4]=='BGE '):
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=''
                j=12
                while(j<len(i)):
                    ip3=ip3+i[j]
                    j=j+1
                if(sr.registers[ip1][0]>=sr.registers[ip2][0]):
                    pc=pc+int(ip3)
                    i=imem.instructions[pc]
                    continue
            elif(i[:4]=='BLE '):
                ip1=int(i[6])
                ip2=int(i[10])
                ip3=''
                j=12
                while(j<len(i)):
                    ip3=ip3+i[j]
                    j=j+1
                if(sr.registers[ip1][0]<=sr.registers[ip2][0]):
                    pc=pc+int(ip3)
                    i=imem.instructions[pc]
                    continue
           
            if imem.instructions[pc][0]!='B':
                modified_imem.append(imem.instructions[pc] +" "+ address_list+" "+str(vlr.registers[0]))



            pc=pc+1
            # print(vlr.registers[0])
            i=imem.instructions[pc]
            #print(i)
        modified_imem.append(i + " "+str(vlr.registers[0]))
     
        print(vr.registers[0])
        print(vr.registers[1])
        print(vr.registers[2])
        print(vr.registers[3])
        print(vr.registers[4])
        print(vr.registers[5])
        print(vr.registers[6])
        print(vr.registers[7])
        print(sr.registers[0][0])
        print(sr.registers[1][0])
        print(sr.registers[2][0])
        print(sr.registers[3][0])
        print(sr.registers[4][0])
        print(sr.registers[5][0])
        print(sr.registers[6][0])
        print(sr.registers[7][0])
        
        print(pc)      
        print("the contents of the vector mask register are"+ '\n'+str(vmr.registers))
        print("the vector length register value is "+str(vlr.registers[0]))
        print(vlr.registers[0])
        sdmem.Write()
        vdmem.Write()
        print(vdmem.data[2048])
        
        vr.Write(iodir+"/VRF.txt")
        sr.Write(iodir+"/SRF.txt")
        with open('Modified_code.asm', 'w') as f:
            for line in modified_imem:
                f.write("%s\n" % line)
        



            
    def run(self):
        while(True):
            break # Replace this line with your code.

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Performance Model')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse IMEM
    imem = IMEM(iodir,'Code.asm')  
    # print(imem.instructions)
    # print("\n")
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # print(len(sdmem.data))
    # print("\n")
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 
    # print(len(vdmem.data))
    # print("\n")
    # print(vdmem.data[:32])

    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem)

    # Run Core
    #vcore.run()   
   # vcore.dumpregs(iodir)

    #sdmem.dump()
    #vdmem.dump()

    # THE END
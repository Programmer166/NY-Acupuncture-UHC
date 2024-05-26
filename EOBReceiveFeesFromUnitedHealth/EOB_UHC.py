#!/usr/bin/env python
#encoding: utf-8

import logging.handlers
import re

import EOB_CLAIM

OPTUM_PAY_TAG="Optum Pay"
TIN_TAG="TIN:*****"
NPI_TAG="NPI:"
PAYMENT_NUMBER_TAG="Payment Number:"
MEMBER_NAME_TAG="/ --"
PAYMENT_INFO_TAG="Subtotal "
DOS_TAG="HC:"

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')





def PARSING_EOB(filePath):
    DOS_LIST = []
    ID_LIST = []
    CLAIM_LIST = []
    NAME_LIST = []
    CHARGE_LIST = []
    EOB_LIST = []
    PAID_LIST = []
    ALLOW_LIST = []
    DED_LIST = []
    TOPT_LIST = []
    NPI_LIST = []
    Payment_Number = ""
    Payment_Total = ""

    claim_info = EOB_CLAIM.CLAIM_INFO()

    data = ""
    with open(filePath, 'rt') as f:
        data = f.readlines()
    f.close()

    record_num = 0

    for i in range(len(data)):
        '''
        if data[i] == "SUBTOTAL\n":
            if len(NAME_LIST) != len(DOS_LIST):
                temp_name = NAME_LIST[-1]
                NAME_LIST.append(temp_name)
            record_num = record_num + 1
        '''
        if len( re.findall("^(?=PATIENT:).*" ,data[i]))>0:    #name
            temp_info = data[i]
            info = temp_info.split(":", temp_info.count(":"))
            info_name_temp = info[-1].split("(", info[-1].count("("))
            info_name = info_name_temp[0].replace("\n", "").lstrip(" ").rstrip(" ")
            if len(NAME_LIST) == record_num + 1:
                NAME_LIST[record_num] = info_name
            else:
                NAME_LIST.append(info_name)


        if data[i] == "CD\n":   #paid
            temp_i = i + 2
            if len(PAID_LIST) == record_num + 1:
                PAID_LIST[record_num] = data[temp_i].replace("\n", "")
            else:
                PAID_LIST.append(data[temp_i].replace("\n", ""))
            if len(NAME_LIST) != len(DOS_LIST):
                temp_name = NAME_LIST[-1]
                NAME_LIST.append(temp_name)
            record_num = record_num + 1
            #print(data[temp_i])


        if data[i] == "SUBSCRIBER ID: CLAIM DATE: REND PROV ID:\n":    #dos
            #print(i)
            temp_i = i + 2
            temp_date = data[temp_i]
            temp_dos = temp_date.split("-", temp_date.count("-"))
            sp_dos = temp_dos[1].replace("\n", "").lstrip(" ").rstrip(" ")
            sp_dos_two = sp_dos.split(" ", sp_dos.count(" "))
            p_dos = sp_dos_two[0]
            #print(p_dos)
            if len(DOS_LIST) == record_num + 1:
                #print("1111111111111111111111111111111111111111111111111111111111")
                DOS_LIST[record_num] = p_dos
            else:
                #print("2222222222222222222222222222222222222222222222222222222222")
                DOS_LIST.append(p_dos)



        if data[i] == "DRG DRG WEIGHT CLAIM CHARGE CLM ADJ AMT AMOUNT\n":     #charge
            temp_i = i + 1
            if len(CHARGE_LIST) == record_num + 1:
                CHARGE_LIST[record_num] = data[temp_i].replace("\n", "")
            else:
                CHARGE_LIST.append(data[temp_i].replace("\n", ""))


        if len( re.findall("PAYMENT NUMBER:" ,data[i]))>0 and len( re.findall("PAYMENT AMOUNT:" ,data[i]))>0:
            temp_row = data[i]
            temp_num = temp_row.split(":")
            Payment_Total = temp_num[-1]
            temp_paynum = temp_num[-2].rstrip(" ")
            str_length = len(temp_paynum) - 14
            Payment_Number = temp_paynum[:str_length]

        if len( re.findall("TRACE NUMBER:" ,data[i]))>0 and len( re.findall("PAYMENT:" ,data[i]))>0:
            temp_row = data[i]
            temp_num = temp_row.split(":")
            Payment_Total = temp_num[-1]
            temp_paynum = temp_num[-2].rstrip(" ")
            str_length = len(temp_paynum) - 7
            Payment_Number = temp_paynum[:str_length]
        elif len( re.findall("TRACE NUMBER:" ,data[i]))>0:
            temp_row = data[i]
            temp_num = temp_row.split(":")
            Payment_Number = temp_num[-1]
        elif len( re.findall("PAYMENT:" ,data[i]))>0:
            temp_row = data[i]
            temp_num = temp_row.split(":")
            temp_total = temp_num[1].split(" ")
            Payment_Total = temp_total[1]
        else:
            pass




    #print(len(NAME_LIST),len(CHARGE_LIST),len(DOS_LIST), len(PAID_LIST))
    min_len = min(len(CHARGE_LIST), len(PAID_LIST), len(NAME_LIST), len(DOS_LIST))
    for index in range(0, min_len, 1):
        #print(NAME_LIST[index], DOS_LIST[index], CHARGE_LIST[index], PAID_LIST[index])
        EOB_CLAIM.reset(claim_info)
        #claim_info["ID"] = ID_LIST[index]
        claim_info["CHARGE"] = CHARGE_LIST[index]
        #print(claim_info["CHARGE"])
        claim_info["PAID"] = PAID_LIST[index]
        #claim_info["CLAIM"] = CLAIM_LIST[index]
        #claim_info['EOB'] = EOB
        info = NAME_LIST[index].split(" ", NAME_LIST[index].count(" "))
        claim_info['LAST'] = info[-1]
        claim_info['FIRST'] = info[0]
        claim_info["DOS"] = DOS_LIST[index]
        print("Payment number and payment toal is ",Payment_Number, Payment_Total)
        claim_info["NOTE"] = Payment_Number + " " + Payment_Total
        #print(claim_info["NOTE"])
        #print(claim_info['LAST'],claim_info['FIRST'],claim_info["DOS"],claim_info["CHARGE"],claim_info["PAID"])


        claim_info["ID"], claim_info["CLAIM"], claim_info["ALLOW"], claim_info["DED"], claim_info['TOPT'], \
        claim_info["TAX"], claim_info["NPI"], claim_info["MAX"], claim_info["TERMINATED"], \
        claim_info["NO COVER"], claim_info['EOB']
        EOB_CLAIM.save_csv(claim_info)





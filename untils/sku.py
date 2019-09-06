import time

def composesku(code, sizegroupid, skulist, brandid, partClassId, partclassname):

    # JSON信息拼接开始
    ptiPartDtSkuDtos = 'jsonData={"orderFlag":0,"statusId":10010305,"statusCode":"D_MASPARTSTATUS5","partCode":"' \
                       + code + '","partName":"' + code + '","partClassId":"' + str(partClassId) + '","partClassName":"' + partclassname \
                       + '","brandId":' + brandid + ',"sizeGroupId":' + sizegroupid + ','

    # 拼接sku信息
    ptiPartDtSkuDtos = ptiPartDtSkuDtos + '"ptiPartDtSkuDtos": ['

    firstflag = True
    for i in range(len(skulist)):
        if firstflag == True:
            firstflag = False
        else:
            ptiPartDtSkuDtos = ptiPartDtSkuDtos + ','

        ptiPartDtSkuDtos = ptiPartDtSkuDtos + '{"colorId":' + skulist[i][4] + ',"colorCode":"' + skulist[i][5] + '","colorName":"' + skulist[i][6] \
                           + '","sizeId":' + skulist[i][1] + ',"sizeCode":"' + skulist[i][2] + '","sizeName":"' + skulist[i][3] + '","ptiPartSkuCode":"' \
                           + code + skulist[i][5] + skulist[i][2] +'","deleteFlag":0}'

    ptiPartDtSkuDtos = ptiPartDtSkuDtos + '],"gctPartDtMeasureVos": [],"ptiPartDttStseVos": ['

    # 拼接颜色id
    # 去重，新建一个颜色list
    colorlist = []
    colorlist0 = [skutmp[4:7] for skutmp in skulist]
    for colortmp in colorlist0:
        if colortmp not in colorlist:
            colorlist.append(colortmp)
    print(colorlist)

    # 拼接颜色信息
    firstflag = True
    for coli in range(len(colorlist)):
        if firstflag == True:
            firstflag = False
        else:
            ptiPartDtSkuDtos = ptiPartDtSkuDtos + ','
        ptiPartDtSkuDtos = ptiPartDtSkuDtos + '{"colorId":' + colorlist[coli][0] + ',"colorCode":"' + colorlist[coli][1] + \
                           '","colorName":"' + colorlist[coli][2] + '","deleteFlag":0}'

    # 拼接信息
    ptiPartDtSkuDtos = ptiPartDtSkuDtos + '],"ptiPartDtPropVos":[],"ptiPartDtListedVos":[],"colorIds": ['

    firstflag = True
    for coli in range(len(colorlist)):
        if firstflag == True:
            firstflag = False
        else:
            ptiPartDtSkuDtos = ptiPartDtSkuDtos + ','
        ptiPartDtSkuDtos = ptiPartDtSkuDtos + colorlist[coli][0]

    ptiPartDtSkuDtos = ptiPartDtSkuDtos + ']}'
    return ptiPartDtSkuDtos

# 拼接商品定价json
def composeproductprice(pid, pcode, pprice):
    jsonData='jsonData={"partStpDate":"' + str(time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())) \
             + '","statusId":10250301,"brandId":null,"pricingLatId":10260201,"pricingId":10260101,"memo":"' + pcode +' price is ' + pprice \
             + '","psmPartStpDtList":[{"fk":' + pid + ',"ptiPartHdId":' + pid +',"ptiPartHdCode":"' + pcode \
             + '","ptiPartHdName":"' + pcode + '","price":' + pprice +',"isCheckedModel":"checked"}],"psmPartStpDtObjList":[]}'
    return jsonData

# 拼接调整单json,增加库存
def composestock(stockupid, stockupname, stockrepid, stockrepname ,stockstorageid, adjusttypeid, pcode, pid, adjid, skulist, pprice):
    fdsStkadjHdSaveDto='fdsStkadjHdSaveDto={"brandId":-1,"stateId":10290506,"sourceId":10290601,"upGrpId":' + stockupid \
                       + ',"upGrpName":"' + stockupname + '","whsHdId":' + stockrepid + ',"whsHdName":"' + stockrepname \
                       + '","locId":' + stockstorageid + ',"adjTypeId":' + adjusttypeid + ',"memo":"' + pcode +'","fdsStkadjDtSaveDtos":['
    firstflag = True
    for i in range(len(skulist)):
        if firstflag == True:
            firstflag = False
        else:
            fdsStkadjHdSaveDto = fdsStkadjHdSaveDto + ','
        fdsStkadjHdSaveDto = fdsStkadjHdSaveDto + '{"adjQty":' + adjid + ',"ptiPartHdId":' + pid + ',"partName":"' + pcode \
                             + '","partCode":"' + pcode + '","sizeId":' + skulist[i][1] + ',"sizeName":"' + skulist[i][3]\
                             + '","sizeCode":"' + skulist[i][2] + '","colorId":' + skulist[i][4] + ',"colorCode":"' + skulist[i][5] \
                             + '","colorName":"' + skulist[i][6] + '","deliveryDate":"","memo":"","ptiPartDtSkuId":' + skulist[i][0] \
                             + ',"salePrice":0,"discount":1,"adjPrice":' + pprice + ',"crtLog":"' + str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))\
                             + '","totalSalePrice":"0.00","totalDisPrice":"' + str(int(adjid) * float(pprice)) + '","isCheckedModel":"unchecked","isSelectedModel":"unselected"}'

    fdsStkadjHdSaveDto = fdsStkadjHdSaveDto + '],"fdsStkadjDtCodeSaveDtos":[],"stkAdjDate":"' + str(time.strftime("%Y-%m-%d", time.gmtime())) \
                         + '","confirmDate":"' + str(time.strftime("%Y-%m-%d", time.gmtime())) + '"}'
    print(fdsStkadjHdSaveDto)
    return fdsStkadjHdSaveDto





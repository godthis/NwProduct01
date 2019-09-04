import copy
import os
import re
import tkinter
from tkinter import ttk
import tkinter.messagebox

import xlsxwriter

from untils.httputil import httppost, httpget, httpupload
from untils.searchDB import searchmysql
from untils.sku import composesku, composeproductprice, composestock


# 树状图窗口
def TreesPre():
    classvalue=''
    names = locals()
    win=tkinter.Tk(className='商品分类')
    # 树状图
    Treeviewpclass = ttk.Treeview(win)
    # 获取树状图内容
    def treetool(treeid):
        # 判断节点是否存在上级节点
        treeup = searchmysql("select up_pti_part_class_id from qs_iss_mas.pti_part_class where own_company_id = 562 "
                             "and id = %s;" % treeid,'(.*)?')
        # 节点不存在父节点，即该节点已经是root节点,将root节点加入tree
        if treeup == "['((None,),)', '']":
            # 获取分类名称
            treerootname = searchmysql("select pti_part_class_name from qs_iss_mas.pti_part_class where own_company_id = 562 "
                                    "and id = %s;" % treeid, '(.*)?')
            treerootname = re.search("(?<=[(]').*?(?=',)", treerootname).group()
            names['tree' + str(treeid)] = Treeviewpclass.insert("", 0, str(treerootname) + str(treeid),
                                                            text=str(treerootname), values=str(treeid))
            #记录加入的节点
            treeall.append(treeid)
        # 节点还存在上层的节点
        else:
            # 获取上层节点
            treeupid = re.search("(?<=[(][(]).*?(?=,[)])", treeup).group()
            # 判断上级节点是否存在于list中
            # 上级节点已经存在于list中，将节点加入tree
            if treeupid in treeall:
                # 获取分类名称
                treename = searchmysql(
                    "select pti_part_class_name from qs_iss_mas.pti_part_class where own_company_id = 562 "
                    "and id = %s;" % treeid, '(.*)?')
                treename = re.search("(?<=[(]').*?(?=',)", treename).group()
                # 节点加入tree
                names['tree' + str(treeid)] = Treeviewpclass.insert(names['tree' + str(treeupid)], len(treeall),
                                                                    str(treename) + str(treeid), text=str(treename), values=str(treeid))
                # 记录加入的节点
                treeall.append(treeid)
            # 上级节点不在list中,more
            else:
                treetool(treeupid)
    # 商品分类确定按钮
    def btnok1():
        global varpclassvalue
        # 获取选择的值
        varpclassvalue = Treeviewpclass.item(Treeviewpclass.selection(),"values")
        if varpclassvalue:
            # 商品分类标签赋值
            classname = searchmysql(
                    "select pti_part_class_name from qs_iss_mas.pti_part_class where own_company_id = 562 "
                    "and id = %s;" % varpclassvalue[0], '(.*)?')
            classname = re.search("(?<=[(]').*?(?=',)", classname).group()
            varpclass.set(classname)
            # 关闭窗口
            win.destroy()
        else:
            print('未选择商品分类')
    # 商品分类取消按钮
    def btncan1():
        win.destroy()

    treeall=[]
    # 获取所有最底层节点
    treeF0list = searchmysql("select id,up_pti_part_class_id from qs_iss_mas.pti_part_class where own_company_id = 562 "
                           "and id not in (select up_pti_part_class_id from qs_iss_mas.pti_part_class "
                             "where own_company_id = 562 and up_pti_part_class_id is not null) "
                           "and up_pti_part_class_id is not null;","(.*)?")
    treeF0list=re.findall('(?<=[(]).*?(?=[)],)',treeF0list)
    # 获取所有最底层节点数量
    treelistlen = len(treeF0list)
    # 定个计数器
    i=0
    # 遍历所有最底层节点
    while(i < treelistlen):
        treeF0tmp = re.findall('[0-9]+', treeF0list[i])
        # print(treeF0tmp)
        # 将底层节点或者底层节点的某个上级节点加入tree
        treetool(treeF0tmp[0])
        # print(treeall[-1])
        # 当加入的是底层节点时，计数器加1
        if treeall[-1] == treeF0tmp[0]:
            i = i + 1

    #按钮
    btnok = tkinter.Button(win, text='确定', command=btnok1)
    btncan = tkinter.Button(win, text='取消', command=btncan1)
    # 树状图
    Treeviewpclass.pack()
    btnok.pack(side='left')
    btncan.pack()

    # 维持窗口
    win.mainloop()
    return classvalue

if __name__ == '__main__':
    def inputint():

        # 查询数据库获取需要的各种数据
        # 获取商品分类name
        partclassname = searchmysql(
            "select pti_part_class_name from qs_iss_mas.pti_part_class where own_company_id = 562 and id = '%s';" % varpclassvalue[0],
            "(.*)?")
        partclassname = re.search("(?<=[(][(]').*?(?=',[)])", partclassname).group()

        # 获取品牌id
        brandid = searchmysql(
            "select id from qs_iss_mas.pti_brand where own_company_id = 562 and brand_name = '%s';" % str(varpbrand.get()),
            "(.*)?")
        brandid = re.search('(?<=[(][(]).*?(?=,[)])', brandid).group()

        # 获取尺码组id，再根据尺码组获取对应尺码list
        sizegroupid = searchmysql(
            "select id from qs_iss_mas.pti_size_group_hd where own_company_id = 562 and size_group_name = '%s';" % str(varpsizegroup.get()),
            "(.*)?")
        sizegroupid = re.search('(?<=[(][(]).*?(?=,[)])', sizegroupid).group()

        sizeidlist = searchmysql(
            "select size_id from qs_iss_mas.pti_size_group_dt where own_company_id = 562 and size_group_hd_id = '%s';" % sizegroupid,
            "(.*)?")
        sizeidlist = re.findall("(?<=[(])[0-9]+(?=,[)])", sizeidlist)

        #定义一个list来存储sku相关信息
        skulist=[]
        # 获取每个尺码id对应的尺码code和尺码name
        # sizecodelist = [''] * len(sizeidlist)
        # sizenamelist = [''] * len(sizeidlist)
        # 获取选择的颜色
        colornamelist = re.findall("(?<=')[^,].*?(?=')", varlistboxpcolor.get())
        # 声明颜色id和颜色code
        # coloridlist = [''] * len(colornamelist)
        # colorcodelist = [''] * len(colornamelist)

        for sizei in range(len(sizeidlist)):
            skutmp=['']*7
            sizetmp = searchmysql(
                "select size_code,size_name from qs_iss_mas.pti_size where own_company_id = 562 and id = '%s';" % sizeidlist[sizei],
                "(.*)?")
            #sizecodelist[sizei] = re.search("(?<=[(]')(.*?)(?=',)", sizetmp).group()
            #sizenamelist[sizei] = re.search("(?<= ')(.*?)(?='[)])", sizetmp).group()
            skutmp[1] = sizeidlist[sizei]
            skutmp[2] = re.search("(?<=[(]')(.*?)(?=',)", sizetmp).group()
            skutmp[3] = re.search("(?<= ')(.*?)(?='[)])", sizetmp).group()

            # 根据颜色名称列表获取颜色id列表
            # 颜色名称列表

            for coli in range(len(colornamelist)):
                # 获取颜色id
                colortmp = searchmysql(
                    "select id, color_code from qs_iss_mas.pti_color where own_company_id = 562 and color_name = '%s';" % colornamelist[coli],
                    "(.*)?")
                # coloridlist[coli] = re.search("(?<=[(][(])(.*?)(?=,)", colortmp).group()
                # colorcodelist[coli] = re.search("(?<= ')(.*?)(?='[)])", colortmp).group()
                skutmp[4] = re.search("(?<=[(][(])(.*?)(?=,)", colortmp).group()
                skutmp[5] = re.search("(?<= ')(.*?)(?='[)])", colortmp).group()
                skutmp[6] = colornamelist[coli]
                skulist.append(copy.deepcopy(skutmp))

        # 计算组合json,创建商品档案
        datavalue = composesku(str(varpcode.get()), sizegroupid, skulist, brandid, varpclassvalue[0], partclassname)
        print(datavalue)

        # 发送post消息,创建商品档案
        httppost('http://issx.bl.test2.qs.com/ISSX/ptiPartHd/saveOrUpdateAsJson', datavalue)

        # 创建完成后获取商品档案id
        pid = searchmysql(
            "select id from qs_iss_mas.pti_part_hd where own_company_id = 562 and part_code ='%s' and part_code ='%s'" % (str(varpcode.get()), str(varpcode.get())), "(.*)?")
        pid = re.search("(?<=[(][(]).*?(?=,[)])", pid).group()
        # 拼接商品定价JSON
        datavalue = composeproductprice(pid,varpcode.get(),varpprice.get())
        print(datavalue)
        # 发送post消息,商品定价
        httppost('http://issx.bl.test2.qs.com/ISSX/psmPartStpHd/saveAsJson', datavalue)

        # 获取商品定价id
        ppriceid = searchmysql("select part_stp_hd_id from qs_iss_acc.psm_partstp_dt where own_company_id = 562 and pti_part_hd_id ='%s';" % pid,"(.*)?")
        ppriceid = re.search("(?<=[(][(]).*?(?=,[)])",ppriceid).group()
        datavalue = 'id=%s&statusId=10250302' % ppriceid
        # 审核商品定价
        httppost('http://issx.bl.test2.qs.com/ISSX/psmPartStpHd/updateStatus', datavalue)

        # 获取上级id,code,name
        stockupcode = re.search(".*?(?=', ')", str(varstockup.get())).group()
        stockupname = re.search("(?<=', ').*", str(varstockup.get())).group()
        stockupid = searchmysql("select id from qs_iss_bas.cud_dpt where own_company_id = 562 and eff_flag = 1 "
                                "and dpt_class_id = 10030208 and dpt_code='%s' and dpt_name ='%s';" % (stockupcode, stockupname),"(.*)?")
        stockupid = re.search("(?<=[(][(]).*?(?=,[)])", stockupid).group()
        # 获取仓库id,code,name
        stockrepcode = re.search(".*?(?=', ')", str(varstockrep.get())).group()
        stockrepname = re.search("(?<=', ').*", str(varstockrep.get())).group()
        stockrepid = searchmysql("select id from qs_iss_bas.whs_dpt_whse_hd where own_company_id = 562 and eff_flag = 1 "
                                "and whs_hd_code='%s' and whs_hd_name ='%s';" % (stockrepcode, stockrepname), "(.*)?")
        stockrepid = re.search("(?<=[(][(]).*?(?=,[)])", stockrepid).group()
        # 获取库位id,code,name
        stockstoragecode = re.search(".*?(?=', ')", str(varstockstorage.get())).group()
        stockstoragename = re.search("(?<=', ').*", str(varstockstorage.get())).group()
        sql="select id from qs_iss_bas.whs_loccode where own_company_id = 562 and eff_flag = 1 and loc_code = '%s' and loc_name = '%s' and whs_hd_id = '%s';" \
            % (stockstoragecode, stockstoragename, stockrepid)
        stockstorageid = searchmysql(sql, "(.*)?")
        stockstorageid = re.search("(?<=[(][(]).*?(?=,[)])", stockstorageid).group()

        # 获取调整类型id
        adjusttypeid = searchmysql(
            "select id from qs_iss_bas.bil_dpt_dict where own_company_id = 562 and eff_flag = 1 and up_dict_id = 102902 and dict_name = '%s';" % varstockAdjustType.get() ,
            "(.*)?")

        # 二维skulist表,补充partdtskuid
        for i in range(len(skulist)):
            sql = "select id from qs_iss_mas.pti_part_dt_sku where own_company_id = 562 and eff_flag = 1 and pti_part_hd_id = '%s' and size_id = '%s' and color_id = '%s';" % (
                pid, skulist[i][1], skulist[i][4])
            # print(sql)
            skudtidtmp = searchmysql(sql, "(.*)?")
            skudtidtmp = re.search("(?<=[(][(]).*?(?=,[)])", skudtidtmp).group()
            skulist[i][0] = skudtidtmp
        # 获取要增加的库存数量
        adjusttypeid = re.search("(?<=[(][(]).*?(?=,[)])",adjusttypeid).group()
        datavalue = composestock(stockupid, stockupname ,stockrepid, stockrepname, stockstorageid ,adjusttypeid, varpcode.get(), pid, varstocknum.get(), skulist, varpprice.get())
        # 发送post消息增加商品库存
        httppost('http://issx.bl.test2.qs.com/ISSX/fdsStkadjHd/saveAsJson', datavalue)

        # 平台商品列表,上架商品
        # 生成excle文件
        if os.path.exists(r'C:\temp\a.xlsx'):
            os.remove(r'C:\temp\a.xlsx')
        workbook = xlsxwriter.Workbook(r'C:\temp\a.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, '商品货号')
        worksheet.write(1, 0, varpcode.get())
        workbook.close()
        # 获取平台id
        if varpbusconts.get() == '全平台':
            buscontsId = ''
        else:
            sql="select id from qs_iss_stm.glb_dict where eff_flag = 1 and up_dict_id = 100420 and dict_name ='%s'" % varpbusconts.get()
            buscontsId = searchmysql(sql, "(.*)?")
            buscontsId = re.search("(?<=[(][(]).*?(?=,[)])", buscontsId).group()
        # 上传文件
        httpupload('http://issx.bl.test2.qs.com/ISSX/spPartGoods/importExcel',r'C:\temp\a.xlsx',buscontsId)

        # 上架
        sql="select id from qs_iss_sal.sp_part_goods where goods_code = '%s' and goods_name = '%s'" % (varpcode.get(), varpcode.get())
        sppartgoodid = searchmysql(sql, "(.*)?")
        sppartgoodid = re.search("(?<=[(][(]).*?(?=,[)])", sppartgoodid).group()
        datavalue = 'id=&batchHandleCode=D_LABEL_O6&batchHandleValue=1&text=批量设置上架&ids=%s' % sppartgoodid
        httppost('http://issx.bl.test2.qs.com/ISSX/spPartGoods/batchHandle', datavalue)

        # print(datavalue)
        # except:
            # tkinter.messagebox.showinfo("不是一个有效值")

    # 颜色增加按钮
    def btncoloradd():
        # 获取选择的颜色值
        colortmp = str(varpcolor.get())
        # 判断颜色值是否存在
        if colortmp in varlistboxpcolor.get():
            tkinter.messagebox.showerror("ERROR", message='不是一个有效值')
        else:
            listboxpcolor.insert(0, colortmp)
            #print(varlistboxpcolor.get())

    # 颜色删除按钮
    def butcolordel():
        try:
            colortmp = listboxpcolor.curselection()
            listboxpcolor.delete(colortmp)
        except:
            print("未选择要删除的元素")

    # 弹出分类选择窗口
    def btnpclass():
        TreesPre()

    # 库存调整-仓库
    def funstockup(event):
        stockupcode = re.search(".*?(?=', ')", str(varstockup.get())).group()
        stockupname = re.search("(?<=', ').*", str(varstockup.get())).group()
        replist = searchmysql(
            "select whs_hd_code,whs_hd_name from qs_iss_bas.whs_dpt_whse_hd where own_company_id = 562 and id in "
            "(select whs_hd_id from qs_iss_bas.cud_dpt_dt_whse where dpt_id = (select id from qs_iss_bas.cud_dpt "
            "where own_company_id = 562 and eff_flag = 1 and dpt_class_id = 10030208 and dpt_code='%s' and dpt_name ='%s'));" % (stockupcode, stockupname),
            "(.*)?")
        comboboxstockrep["value"] = re.findall("(?<=[(]').*?(?='[)])", replist)
        varstockrep.set('')
        varstockstorage.set('')

    def funstockrep(event):
        stockrepcode = re.search(".*?(?=', ')", str(varstockrep.get())).group()
        stockrepname = re.search("(?<=', ').*", str(varstockrep.get())).group()
        storagelist = searchmysql(
            "select loc_code,loc_name from qs_iss_bas.whs_loccode where whs_hd_id =(select id from qs_iss_bas.whs_dpt_whse_hd "
            "where own_company_id = 562 and whs_hd_code ='%s' and whs_hd_name ='%s');" % (stockrepcode, stockrepname),
            "(.*)?")
        comboboxstockstorage["value"] = re.findall("(?<=[(]').*?(?='[)])", storagelist)
        varstockstorage.set('')

    # 正整数校验
    def checknum(content):
        if content.isdigit() or (content == ""):
            return True
        else:
            return False

    # 定价格式校验
    # 先写成正整数吧，后面再说
    def checkprice(content):
        if content.isdigit() or (content == ""):
            return True
        else:
            return False

    # 弹出窗口名称
    root = tkinter.Tk(className='新建商品')
    root.geometry('300x565')  # 设置弹出框的大小 w x h


    # 商品编码和商品名称
    varpcode = tkinter.StringVar()  # 这即是输入框中的内容
    varpcode.set('')  # 通过var.get()/var.set() 来 获取/设置var的值
    Framepcode = tkinter.Frame(root)
    entrypcode = tkinter.Entry(Framepcode, textvariable=varpcode, width=25)  # 设置"文本变量"为var
    # lable文本设置
    lablepcode = tkinter.Label(Framepcode, text="编码/名称", font=('宋体', 10), width=10, height=2)
    Framepcode.pack(side='top')
    lablepcode.pack(side='left', ipadx='0')
    entrypcode.pack(side='right')

    # 商品分类
    Framepclass = tkinter.Frame(root)
    btnpclass = tkinter.Button(Framepclass, text='商品分类', command=btnpclass)
    varpclass = tkinter.StringVar()
    lablepclass = tkinter.Label(Framepclass, textvariable=varpclass, font=('宋体', 10), height=2, width=14)
    Framepclass.pack()
    btnpclass.pack(side='left')
    lablepclass.pack()

    # 商品品牌
    Framepbrand = tkinter.Frame(root)
    lablepbrand = tkinter.Label(Framepbrand, text="商品品牌", font=('宋体', 10), width=10, height=2)
    varpbrand = tkinter.StringVar() #获取下拉框选择的内容
    comboboxpbrand = ttk.Combobox(Framepbrand, textvariable=varpbrand)
    brandlist=searchmysql("select brand_name from qs_iss_mas.pti_brand where own_company_id = 562 and eff_flag = 1;", "(.*)?")
    comboboxpbrand["value"] = re.findall("(?<=[(]').*?(?=',[)])",brandlist)

    Framepbrand.pack(side='top')
    lablepbrand.pack(side='left')
    comboboxpbrand.pack()

    # 是否定制
        # 再说再说

    # 颜色
    Framepcolor = tkinter.Frame(root , background='#FFE4B5')
    lablepcolor = tkinter.Label(Framepcolor, text="颜色", font=('宋体', 10), width=10, height=2, background='#FFE4B5')
    varpcolor = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxpcolor = ttk.Combobox(Framepcolor, textvariable=varpcolor, height=6)
    colorlist = searchmysql("select color_name from qs_iss_mas.pti_color where own_company_id = 562;","(.*)?")
    comboboxpcolor["value"] = re.findall("(?<=[(]').*?(?=',[)])", colorlist)

    btncoloradd = tkinter.Button(Framepcolor, text='Add', command=btncoloradd)
    btncolordel = tkinter.Button(Framepcolor, text='Del', command=butcolordel)

    varlistboxpcolor = tkinter.StringVar()
    listboxpcolor = tkinter.Listbox(root, listvariable=varlistboxpcolor,height=6)

    Framepcolor.pack(side='top')
    lablepcolor.pack(side='left')
    comboboxpcolor.pack()
    btncoloradd.pack(side='left')
    btncolordel.pack(side='left')
    listboxpcolor.pack()

    # 尺码组
    Framepsizegroup = tkinter.Frame(root)
    lablepsizegroup = tkinter.Label(Framepsizegroup, text="尺码组", font=('宋体', 10), width=10, height=2)
    varpsizegroup = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxpsizegroup = ttk.Combobox(Framepsizegroup, textvariable=varpsizegroup)
    sizegrouplist = searchmysql("select size_group_name from qs_iss_mas.pti_size_group_hd where own_company_id = 562;",
                                "(.*)?")
    comboboxpsizegroup["value"] = re.findall("(?<=[(]').*?(?=',[)])", sizegrouplist)
    Framepsizegroup.pack(side='top')
    lablepsizegroup.pack(side='left')
    comboboxpsizegroup.pack()

    # 商品定价
    recheckprice = root.register(checkprice)
    Framepprice = tkinter.Frame(root)
    lableppprice = tkinter.Label(Framepprice, text="商品定价", font=('宋体', 10), width=10, height=2)
    varpprice = tkinter.StringVar()  # 这即是输入框中的内容
    entrypprice = tkinter.Entry(Framepprice, textvariable=varpprice, width=25, validate='key', validatecommand=(recheckprice, '%P'))  # 设置"文本变量"为var

    Framepprice.pack()
    lableppprice.pack(side='left')
    entrypprice.pack()

    # 库存调整

    # 库存调整-上级组织
    Framestockup = tkinter.Frame(root)
    lablestockup = tkinter.Label(Framestockup, text="上级组织", font=('宋体', 10), width=10, height=2)
    varstockup = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockup = ttk.Combobox(Framestockup, textvariable=varstockup, height=6)
    dptlist = searchmysql("select dpt_code,dpt_name from qs_iss_bas.cud_dpt where own_company_id = 562 and eff_flag = 1 and dpt_class_id = 10030208;", "(.*)?")
    comboboxstockup["value"] = re.findall("(?<=[(]')[^,].*?(?='[)])", dptlist)
    comboboxstockup.bind("<<ComboboxSelected>>", funstockup)
    Framestockup.pack()
    lablestockup.pack(side='left')
    comboboxstockup.pack(side='left')

    # 库存调整-仓库
    Framestockrep = tkinter.Frame(root)
    lablestockrep = tkinter.Label(Framestockrep, text="仓库", font=('宋体', 10), width=10, height=2)
    varstockrep = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockrep = ttk.Combobox(Framestockrep, textvariable=varstockrep, height=6)
    comboboxstockrep.bind("<<ComboboxSelected>>", funstockrep)
    Framestockrep.pack()
    lablestockrep.pack(side='left')
    comboboxstockrep.pack(side='left')

    # 库存调整-库位
    Framestockstorage = tkinter.Frame(root)
    lablestockstorage = tkinter.Label(Framestockstorage, text="库位", font=('宋体', 10), width=10, height=2)
    varstockstorage = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockstorage = ttk.Combobox(Framestockstorage, textvariable=varstockstorage, height=6)

    Framestockstorage.pack()
    lablestockstorage.pack(side='left')
    comboboxstockstorage.pack(side='left')

    # 库存调整-调整类型
    FramestockAdjustType = tkinter.Frame(root)
    lablestockAdjustType = tkinter.Label(FramestockAdjustType, text="调整类型", font=('宋体', 10), width=10, height=2)
    varstockAdjustType = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockAdjustType = ttk.Combobox(FramestockAdjustType, textvariable=varstockAdjustType, height=6)
    adjusttypelist = searchmysql("select dict_name from qs_iss_bas.bil_dpt_dict where own_company_id = 562 and eff_flag = 1 and up_dict_id = 102902;", "(.*)?")
    #print(re.findall("(?<=[(][(]').*?(?=',[)])", adjusttypelist))
    comboboxstockAdjustType["value"] = re.findall("(?<=[(][(]').*?(?=',[)])", adjusttypelist)

    FramestockAdjustType.pack(side='top')
    lablestockAdjustType.pack(side='left')
    comboboxstockAdjustType.pack(side='left')

    # 库存调整-商品库存数
    rechecknum = root.register(checknum)
    Framestocknum = tkinter.Frame(root)
    lablestocknum = tkinter.Label(Framestocknum, text="调整库存数", font=('宋体', 10), width=10, height=2)
    varstocknum = tkinter.StringVar()
    entrystocknum = tkinter.Entry(Framestocknum, textvariable=varstocknum, width=25, validate='key', validatecommand=(rechecknum, '%P'))  # 设置"文本变量"为var

    Framestocknum.pack()
    lablestocknum.pack(side='left')
    entrystocknum.pack()

    # 上架平台
    Framepbusconts = tkinter.Frame(root)
    lablepbusconts = tkinter.Label(Framepbusconts, text="上架平台", font=('宋体', 10), width=10, height=2)
    varpbusconts = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxpbusconts = ttk.Combobox(Framepbusconts, textvariable=varpbusconts)
    buscontslist = searchmysql("select dict_name from qs_iss_stm.glb_dict where dict_code like 'D_BUSCONTS%' and eff_flag = 1 and up_dict_id = 100420;",
                               "(.*)?")
    comboboxpbuscontslist=['全平台']
    combolisttmp = re.findall("(?<=[(]').*?(?=',[)])", buscontslist)
    for i in combolisttmp:
        comboboxpbuscontslist.append(i)
    comboboxpbusconts["value"] = comboboxpbuscontslist
    Framepbusconts.pack(side='top')
    lablepbusconts.pack(side='left')
    comboboxpbusconts.pack()


    # 按钮效果
    btn1 = tkinter.Button(root, text='确定', command=inputint)
    # 显示按钮
    btn1.pack()

    # 维持窗口
    root.mainloop()


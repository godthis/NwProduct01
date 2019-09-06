import copy
import os
import re
import tkinter
from tkinter import ttk
import tkinter.messagebox
import xlsxwriter
from untils.httputil import httppost, httpupload, loginandgetcookie, httpget
from untils.myconfig import choiceEnv
from untils.searchDB import searchmysql
from untils.sku import composesku, composeproductprice, composestock

# 没有选择环境时默认用第一个巴龙环境的companyid
owncompanyid = '562'

def rootwin():

    # 给各个控件赋值
    def initvalue(owncompanyid):
        print(owncompanyid)
        # 商品品牌下拉框赋值
        brandlist = searchmysql(
            "select brand_name from qs_iss_mas.pti_brand where own_company_id = '%s' and eff_flag = 1;" % owncompanyid)
        comboboxpbrand["value"] = re.findall("(?<=[(]').*?(?=',[)])", brandlist)
        # 颜色下拉框赋值
        colorlist = searchmysql(
            "select color_name from qs_iss_mas.pti_color where own_company_id = '%s';" % owncompanyid)
        comboboxpcolor["value"] = re.findall("(?<=[(]').*?(?=',[)])", colorlist)
        # 尺码组下拉框赋值
        sizegrouplist = searchmysql(
            "select size_group_name from qs_iss_mas.pti_size_group_hd where own_company_id = '%s';" % owncompanyid)
        comboboxpsizegroup["value"] = re.findall("(?<=[(]').*?(?=',[)])", sizegrouplist)
        # 库存调整-上级组织赋值
        dptlist = searchmysql(
            "select dpt_code,dpt_name from qs_iss_bas.cud_dpt where own_company_id = '%s' and eff_flag = 1 and dpt_class_id = 10030208;" % owncompanyid)
        comboboxstockup["value"] = re.findall("(?<=[(]')[^,].*?(?='[)])", dptlist)
        # 库存调整-调整类型赋值
        adjusttypelist = searchmysql(
            "select dict_name from qs_iss_bas.bil_dpt_dict where own_company_id = '%s' and eff_flag = 1 and up_dict_id = 102902;" % owncompanyid)
        comboboxstockAdjustType["value"] = re.findall("(?<=[(][(]').*?(?=',[)])", adjusttypelist)
        # 商品上架平台赋值
        buscontslist = searchmysql(
            "select dict_name from qs_iss_stm.glb_dict where dict_code like 'D_BUSCONTS%' and eff_flag = 1 and up_dict_id = 100420;")
        comboboxpbuscontslist = ['全平台']
        combolisttmp = re.findall("(?<=[(]').*?(?=',[)])", buscontslist)
        for i in combolisttmp:
            comboboxpbuscontslist.append(i)
        comboboxpbusconts["value"] = comboboxpbuscontslist

    # 选择环境并给各个控件赋值
    def setenvfun(event):
        global owncompanyid
        envname = varenv.get()
        envlist = choiceEnv(envname)
        baseurl = envlist[2]
        # 获取userid
        loginresultlist = loginandgetcookie(baseurl, envlist[0], envlist[1])
        # 通过useri查询own_company_id
        owncompanyid = searchmysql(
            "select own_company_id from qs_iss_bas.per_usr where id = '%s';" % loginresultlist[0])
        owncompanyid = str(re.search('(?<=[(][(]).*?(?=,[)])', owncompanyid).group())
        initvalue(owncompanyid)

    # 树状图窗口
    def TreesPre():
        global owncompanyid
        classvalue = ''
        names = locals()
        # 一个list记录已经加入树状图的节点
        listcheck = []
        listlevel = []

        # 商品分类确定按钮
        def btnok1():
            global varpclassvalue
            # 获取选择的值
            varpclassvalue = Treeviewpclass.item(Treeviewpclass.selection(), "values")
            if varpclassvalue:
                # 商品分类标签赋值
                classname = searchmysql(
                    "select pti_part_class_name from qs_iss_mas.pti_part_class where own_company_id = '%s' and id = %s;" % (
                    owncompanyid, varpclassvalue[0]))
                classname = re.search("(?<=[(]').*?(?=',)", classname).group()
                varpclass.set(classname)
                # 关闭窗口
                win.destroy()
                winpclass.set(0)
            else:
                print('未选择商品分类')

        # 商品分类取消按钮
        def btncan1():
            win.destroy()
            winpclass.set(0)

        def closingfun():
            win.destroy()
            winpclass.set(0)

        def getnode(upnodeid, owncompanyid):
            listcheck.append(str(upnodeid))
            # 获取下级节点
            sql = "select id,pti_part_class_name from qs_iss_mas.pti_part_class where own_company_id = '%s' and up_pti_part_class_id = '%s'" % (
            owncompanyid, upnodeid)
            nodelist = searchmysql(sql)
            if nodelist:
                nodelist = re.search('(?<=[(])(.*)?', nodelist).group()
                nodelist = re.findall('(?<=[(]).*?(?=[)])', nodelist)
                listlevel2 = []
                for nodei in range(len(nodelist)):
                    nodetmp = [''] * 2
                    nodetmp[0] = re.search(".*?(?=, ')", nodelist[nodei]).group()
                    nodetmp[1] = re.search("(?<=, ').*?(?=')", nodelist[nodei]).group()
                    listlevel2.append(nodetmp)
                for i in range(len(listlevel2)):
                    names['tree' + str(listlevel2[i][0])] = Treeviewpclass.insert(names['tree' + str(upnodeid)],
                                                                                  str(listlevel2[i][0]),
                                                                                  str(listlevel2[i][1]) + str(
                                                                                      listlevel2[i][0]),
                                                                                  text=str(listlevel2[i][1]),
                                                                                  values=str(listlevel2[i][0]))
                    listsave.append(listlevel2[i][0])

        win = tkinter.Tk(className='商品分类')
        Treeviewpclass = ttk.Treeview(win)
        # 获取root节点
        sql = "select id,pti_part_class_name from qs_iss_mas.pti_part_class where up_pti_part_class_id is null and own_company_id = '%s' and pti_part_class_code = 10" % owncompanyid
        roottmp = searchmysql(sql)
        rootclassid = re.search('(?<=[(][(]).*?(?=,)', roottmp).group()
        rootclassname = re.search("(?<=, ').*?(?='[)])", roottmp).group()
        # 添加root节点到树状图
        names['tree' + str(rootclassid)] = Treeviewpclass.insert("", 0, str(rootclassname) + str(rootclassid),
                                                                 text=str(rootclassname), values=str(rootclassid))
        listsave = []
        listsave.append(rootclassid)
        # 遍历下级节点
        getnode(rootclassid, owncompanyid)
        # 加入树状图
        for savei in listsave:
            if savei not in listcheck:
                getnode(savei, owncompanyid)

        # 按钮
        btnok = tkinter.Button(win, text='确定', command=btnok1)
        btncan = tkinter.Button(win, text='取消', command=btncan1)

        Treeviewpclass.pack()
        btnok.pack(side='left')
        btncan.pack()
        win.protocol("WM_DELETE_WINDOW", closingfun)
        win.mainloop()

    # 按钮功能-弹出选择商品分类窗口
    def btnpclassfun():
        if winpclass.get() == 0:
            winpclass.set(1)
            TreesPre()
            winpclass.set(0)

    # 按钮功能-颜色增加按钮
    def btncoloraddfun():
        # 获取选择的颜色值
        colortmp = str(varpcolor.get())
        # 判断颜色值是否存在
        if colortmp in varlistboxpcolor.get():
            tkinter.messagebox.showinfo("ERROR", message='该颜色已经选择')
        else:
            listboxpcolor.insert(0, colortmp)

    # 按钮功能-颜色删除按钮
    def butcolordelfun():
        try:
            colortmp = listboxpcolor.curselection()
            listboxpcolor.delete(colortmp)
        except:
            print("未选择要删除的元素")

    # 输入校验-正整数校验
    def checknum(content):
        if content.isdigit() or (content == ""):
            return True
        else:
            return False

    # 输入校验-商品定价
    # 先写成正整数吧，后面再说
    def checkprice(content):
        if content.isdigit() or (content == ""):
            return True
        else:
            return False

    # 库存调整-选择上级后仓库下拉框赋值
    def funstockup(event):
        stockupcode = re.search(".*?(?=', ')", str(varstockup.get())).group()
        stockupname = re.search("(?<=', ').*", str(varstockup.get())).group()
        replist = searchmysql(
            "select whs_hd_code,whs_hd_name from qs_iss_bas.whs_dpt_whse_hd where own_company_id = '%s' and id in "
            "(select whs_hd_id from qs_iss_bas.cud_dpt_dt_whse where dpt_id = (select id from qs_iss_bas.cud_dpt "
            "where own_company_id = '%s' and eff_flag = 1 and dpt_class_id = 10030208 and dpt_code='%s' and dpt_name ='%s'));" % (
            owncompanyid, owncompanyid, stockupcode, stockupname))
        comboboxstockrep["value"] = re.findall("(?<=[(]').*?(?='[)])", replist)
        varstockrep.set('')
        varstockstorage.set('')

    # 库存调整-选择仓库后给库位赋值
    def funstockrep(event):
        stockrepcode = re.search(".*?(?=', ')", str(varstockrep.get())).group()
        stockrepname = re.search("(?<=', ').*", str(varstockrep.get())).group()
        storagelist = searchmysql(
            "select loc_code,loc_name from qs_iss_bas.whs_loccode where whs_hd_id =(select id from qs_iss_bas.whs_dpt_whse_hd "
            "where own_company_id = '%s' and whs_hd_code ='%s' and whs_hd_name ='%s');" % (
            owncompanyid, stockrepcode, stockrepname))
        comboboxstockstorage["value"] = re.findall("(?<=[(]').*?(?='[)])", storagelist)
        varstockstorage.set('')
    # 确认按钮功能
    def inputint():
        # 认证并获取cookie
        envname = varenv.get()
        if envname:
            envlist = choiceEnv(envname)
            logincookie = (loginandgetcookie(envlist[2], envlist[0], envlist[1]))[1]
            baseurl = envlist[2]
            # 检查是否有重复的商品code
            sql = "select part_code from qs_iss_mas.pti_part_hd where own_company_id = '%s';" % owncompanyid
            checkpcode = searchmysql(sql)
            if varpcode.get() in checkpcode:
                tkinter.messagebox.showerror('ERROR', message='重复的商品名称')
                return 0

            # 获取商品分类name
            partclassname = searchmysql(
                "select pti_part_class_name from qs_iss_mas.pti_part_class where own_company_id = '%s' and id = '%s';" % (
                owncompanyid, varpclassvalue[0]))
            partclassname = re.search("(?<=[(][(]').*?(?=',[)])", partclassname).group()

            # 获取品牌id
            brandid = searchmysql(
                "select id from qs_iss_mas.pti_brand where own_company_id = '%s' and brand_name = '%s';" % (
                owncompanyid, str(varpbrand.get())))
            brandid = re.search('(?<=[(][(]).*?(?=,[)])', brandid).group()

            # 获取尺码组id，再根据尺码组获取对应尺码list
            sizegroupid = searchmysql(
                "select id from qs_iss_mas.pti_size_group_hd where own_company_id = '%s' and size_group_name = '%s';" % (
                owncompanyid, str(varpsizegroup.get())))
            sizegroupid = re.search('(?<=[(][(]).*?(?=,[)])', sizegroupid).group()

            sizeidlist = searchmysql(
                "select size_id from qs_iss_mas.pti_size_group_dt where own_company_id = '%s' and size_group_hd_id = '%s';" % (
                owncompanyid, sizegroupid))
            sizeidlist = re.findall("(?<=[(])[0-9]+(?=,[)])", sizeidlist)

            # 定义一个list来存储sku相关信息
            skulist = []
            # 获取选择的颜色
            colornamelist = re.findall("(?<=')[^,].*?(?=')", varlistboxpcolor.get())

            for sizei in range(len(sizeidlist)):
                skutmp = [''] * 7
                sizetmp = searchmysql(
                    "select size_code,size_name from qs_iss_mas.pti_size where own_company_id = '%s' and id = '%s';" % (
                    owncompanyid, sizeidlist[sizei]))
                skutmp[1] = sizeidlist[sizei]
                skutmp[2] = re.search("(?<=[(]')(.*?)(?=',)", sizetmp).group()
                skutmp[3] = re.search("(?<= ')(.*?)(?='[)])", sizetmp).group()

                # 根据颜色名称列表获取颜色id列表
                # 颜色名称列表
                for coli in range(len(colornamelist)):
                    # 获取颜色id
                    colortmp = searchmysql(
                        "select id, color_code from qs_iss_mas.pti_color where own_company_id = '%s' and color_name = '%s';" % (
                        owncompanyid, colornamelist[coli]))
                    skutmp[4] = re.search("(?<=[(][(])(.*?)(?=,)", colortmp).group()
                    skutmp[5] = re.search("(?<= ')(.*?)(?='[)])", colortmp).group()
                    skutmp[6] = colornamelist[coli]
                    skulist.append(copy.deepcopy(skutmp))

            # 计算组合json,创建商品档案
            datavalue = composesku(str(varpcode.get()), sizegroupid, skulist, brandid, varpclassvalue[0],
                                   partclassname)
            print(datavalue)

            # 发送post消息,创建商品档案
            httppost('%s/ISSX/ptiPartHd/saveOrUpdateAsJson' % baseurl, logincookie, datavalue)

            # 创建完成后获取商品档案id
            pid = searchmysql(
                "select id from qs_iss_mas.pti_part_hd where own_company_id = '%s' and part_code ='%s' and part_code ='%s'" % (
                owncompanyid, str(varpcode.get()), str(varpcode.get())))
            pid = re.search("(?<=[(][(]).*?(?=,[)])", pid).group()
            # 拼接商品定价JSON
            datavalue = composeproductprice(pid, varpcode.get(), varpprice.get())
            print(datavalue)

            # 发送post消息,商品定价
            httppost('%s/ISSX/psmPartStpHd/saveAsJson' % baseurl, logincookie, datavalue)

            # 获取商品定价id
            ppriceid = searchmysql(
                "select part_stp_hd_id from qs_iss_acc.psm_partstp_dt where own_company_id = '%s' and pti_part_hd_id ='%s';" % (
                owncompanyid, pid))
            ppriceid = re.search("(?<=[(][(]).*?(?=,[)])", ppriceid).group()
            datavalue = 'id=%s&statusId=10250302' % ppriceid
            # 审核商品定价
            httppost('%s/ISSX/psmPartStpHd/updateStatus' % baseurl, logincookie, datavalue)

            # 获取上级id,code,name
            stockupcode = re.search(".*?(?=', ')", str(varstockup.get())).group()
            stockupname = re.search("(?<=', ').*", str(varstockup.get())).group()
            stockupid = searchmysql("select id from qs_iss_bas.cud_dpt where own_company_id = '%s' and eff_flag = 1 "
                                    "and dpt_class_id = 10030208 and dpt_code='%s' and dpt_name ='%s';" % (
                                    owncompanyid, stockupcode, stockupname))
            stockupid = re.search("(?<=[(][(]).*?(?=,[)])", stockupid).group()
            # 获取仓库id,code,name
            stockrepcode = re.search(".*?(?=', ')", str(varstockrep.get())).group()
            stockrepname = re.search("(?<=', ').*", str(varstockrep.get())).group()
            stockrepid = searchmysql(
                "select id from qs_iss_bas.whs_dpt_whse_hd where own_company_id = '%s' and eff_flag = 1 "
                "and whs_hd_code='%s' and whs_hd_name ='%s';" % (owncompanyid, stockrepcode, stockrepname))
            stockrepid = re.search("(?<=[(][(]).*?(?=,[)])", stockrepid).group()
            # 获取库位id,code,name
            stockstoragecode = re.search(".*?(?=', ')", str(varstockstorage.get())).group()
            stockstoragename = re.search("(?<=', ').*", str(varstockstorage.get())).group()
            sql = "select id from qs_iss_bas.whs_loccode where own_company_id = '%s' and eff_flag = 1 and loc_code = '%s' and loc_name = '%s' and whs_hd_id = '%s';" \
                  % (owncompanyid, stockstoragecode, stockstoragename, stockrepid)
            stockstorageid = searchmysql(sql)
            stockstorageid = re.search("(?<=[(][(]).*?(?=,[)])", stockstorageid).group()

            # 获取调整类型id
            adjusttypeid = searchmysql(
                "select id from qs_iss_bas.bil_dpt_dict where own_company_id = '%s' and eff_flag = 1 and up_dict_id = 102902 and dict_name = '%s';" % (
                owncompanyid, varstockAdjustType.get()))

            # 二维skulist表,补充partdtskuid
            for i in range(len(skulist)):
                sql = "select id from qs_iss_mas.pti_part_dt_sku where own_company_id = '%s' and eff_flag = 1 and pti_part_hd_id = '%s' and size_id = '%s' and color_id = '%s';" \
                      % (owncompanyid, pid, skulist[i][1], skulist[i][4])
                # print(sql)
                skudtidtmp = searchmysql(sql)
                skudtidtmp = re.search("(?<=[(][(]).*?(?=,[)])", skudtidtmp).group()
                skulist[i][0] = skudtidtmp
            # 获取要增加的库存数量
            adjusttypeid = re.search("(?<=[(][(]).*?(?=,[)])", adjusttypeid).group()
            datavalue = composestock(stockupid, stockupname, stockrepid, stockrepname, stockstorageid, adjusttypeid,
                                     varpcode.get(), pid, varstocknum.get(), skulist, varpprice.get())
            # 发送post消息增加商品库存
            httppost('%s/ISSX/fdsStkadjHd/saveAsJson' % baseurl, logincookie, datavalue)

            sql="select stkadj_hd_id from qs_iss_dtb.fds_stkadj_dt where own_company_id = '%s' and pti_part_dt_sku_id = '%s'" % (owncompanyid, skulist[0][0])
            stkadjid = searchmysql(sql)
            stkadjid = re.search("(?<=[(][(]).*?(?=,[)])", stkadjid).group()
            # 确认调整单
            httpget('%s/ISSX/fdsStkadjHd/updateStatus?id=%s' % (baseurl, stkadjid), logincookie)

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
                sql = "select id from qs_iss_stm.glb_dict where eff_flag = 1 and up_dict_id = 100420 and dict_name ='%s'" % varpbusconts.get()
                buscontsId = searchmysql(sql)
                buscontsId = re.search("(?<=[(][(]).*?(?=,[)])", buscontsId).group()
            # 上传文件
            httpupload('%s/ISSX/spPartGoods/importExcel' % baseurl, logincookie, r'C:\temp\a.xlsx', buscontsId)

            # 上架
            sql = "select id from qs_iss_sal.sp_part_goods where own_company_id = '%s' and goods_code = '%s' and goods_name = '%s'" % (
            owncompanyid, varpcode.get(), varpcode.get())
            sppartgoodid = searchmysql(sql)
            sppartgoodid = re.search("(?<=[(][(]).*?(?=,[)])", sppartgoodid).group()
            datavalue = 'id=&batchHandleCode=D_LABEL_O6&batchHandleValue=1&text=批量设置上架&ids=%s' % sppartgoodid
            httppost('%s/ISSX/spPartGoods/batchHandle' % baseurl, logincookie, datavalue)


    # 弹出窗口名称
    root = tkinter.Tk(className='新建商品')
    root.geometry('300x580')  # 设置弹出框的大小 w x h
    winpclass = tkinter.IntVar(root, value=0)

    # 环境选择
    Frameenv = tkinter.Frame(root)
    lableenv = tkinter.Label(Frameenv, text="测试环境", font=('宋体', 10), width=10, height=2)
    varenv = tkinter.StringVar()  # 获取下拉框选择的内容

    comboboxenv = ttk.Combobox(Frameenv, textvariable=varenv, state="readonly")
    comboboxenv.bind("<<ComboboxSelected>>", setenvfun)
    comboboxenvvalue = ["巴龙"]
    comboboxenv["value"] = comboboxenvvalue
    varenv.set(comboboxenvvalue[0])
    Frameenv.pack(side='top')
    lableenv.pack(side='left')
    comboboxenv.pack()

    # 商品编码和商品名称
    varpcode = tkinter.StringVar()  # 这即是输入框中的内容
    varpcode.set('')  # 通过var.get()/var.set() 来 获取/设置var的值
    Framepcode = tkinter.Frame(root)
    entrypcode = tkinter.Entry(Framepcode, textvariable=varpcode, width=25)  # 设置"文本变量"为var
    lablepcode = tkinter.Label(Framepcode, text="编码/名称", font=('宋体', 10), width=10, height=2)
    Framepcode.pack(side='top')
    lablepcode.pack(side='left', ipadx='0')
    entrypcode.pack(side='right')

    # 商品分类
    winpclass = tkinter.IntVar(root, value=0) # 防止窗口重复弹出标志位
    Framepclass = tkinter.Frame(root)
    btnpclass = tkinter.Button(Framepclass, text='商品分类', command=btnpclassfun)
    varpclass = tkinter.StringVar()
    lablepclass = tkinter.Label(Framepclass, textvariable=varpclass, font=('宋体', 10), height=2, width=14)
    Framepclass.pack()
    btnpclass.pack(side='left')
    lablepclass.pack()

    # 商品品牌
    Framepbrand = tkinter.Frame(root)
    lablepbrand = tkinter.Label(Framepbrand, text="商品品牌", font=('宋体', 10), width=10, height=2)
    varpbrand = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxpbrand = ttk.Combobox(Framepbrand, textvariable=varpbrand, state="readonly")
    Framepbrand.pack(side='top')
    lablepbrand.pack(side='left')
    comboboxpbrand.pack()

    # 是否定制
    # 再说再说

    # 颜色
    Framepcolor = tkinter.Frame(root, background='#FFE4B5')
    lablepcolor = tkinter.Label(Framepcolor, text="颜色", font=('宋体', 10), width=10, height=2, background='#FFE4B5')
    varpcolor = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxpcolor = ttk.Combobox(Framepcolor, textvariable=varpcolor, height=6, state="readonly")
    btncoloradd = tkinter.Button(Framepcolor, text='Add', command=btncoloraddfun)
    btncolordel = tkinter.Button(Framepcolor, text='Del', command=butcolordelfun)
    varlistboxpcolor = tkinter.StringVar()
    listboxpcolor = tkinter.Listbox(root, listvariable=varlistboxpcolor, height=6)
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
    comboboxpsizegroup = ttk.Combobox(Framepsizegroup, textvariable=varpsizegroup, state="readonly")
    Framepsizegroup.pack(side='top')
    lablepsizegroup.pack(side='left')
    comboboxpsizegroup.pack()

    # 商品定价
    recheckprice = root.register(checkprice)
    Framepprice = tkinter.Frame(root)
    lableppprice = tkinter.Label(Framepprice, text="商品定价", font=('宋体', 10), width=10, height=2)
    varpprice = tkinter.StringVar()  # 这即是输入框中的内容
    entrypprice = tkinter.Entry(Framepprice, textvariable=varpprice, width=25, validate='key',
                                validatecommand=(recheckprice, '%P'))
    Framepprice.pack()
    lableppprice.pack(side='left')
    entrypprice.pack()

    # 库存调整-上级组织
    Framestockup = tkinter.Frame(root)
    lablestockup = tkinter.Label(Framestockup, text="上级组织", font=('宋体', 10), width=10, height=2)
    varstockup = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockup = ttk.Combobox(Framestockup, textvariable=varstockup, height=6, state="readonly")
    comboboxstockup.bind("<<ComboboxSelected>>", funstockup)
    Framestockup.pack()
    lablestockup.pack(side='left')
    comboboxstockup.pack(side='left')

    # 库存调整-仓库
    Framestockrep = tkinter.Frame(root)
    lablestockrep = tkinter.Label(Framestockrep, text="仓库", font=('宋体', 10), width=10, height=2)
    varstockrep = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockrep = ttk.Combobox(Framestockrep, textvariable=varstockrep, height=6, state="readonly")
    comboboxstockrep.bind("<<ComboboxSelected>>", funstockrep)
    Framestockrep.pack()
    lablestockrep.pack(side='left')
    comboboxstockrep.pack(side='left')

    # 库存调整-库位
    Framestockstorage = tkinter.Frame(root)
    lablestockstorage = tkinter.Label(Framestockstorage, text="库位", font=('宋体', 10), width=10, height=2)
    varstockstorage = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockstorage = ttk.Combobox(Framestockstorage, textvariable=varstockstorage, height=6, state="readonly")
    Framestockstorage.pack()
    lablestockstorage.pack(side='left')
    comboboxstockstorage.pack(side='left')

    # 库存调整-调整类型
    FramestockAdjustType = tkinter.Frame(root)
    lablestockAdjustType = tkinter.Label(FramestockAdjustType, text="调整类型", font=('宋体', 10), width=10, height=2)
    varstockAdjustType = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxstockAdjustType = ttk.Combobox(FramestockAdjustType, textvariable=varstockAdjustType, height=6,
                                           state="readonly")
    FramestockAdjustType.pack(side='top')
    lablestockAdjustType.pack(side='left')
    comboboxstockAdjustType.pack(side='left')

    # 库存调整-商品库存数
    rechecknum = root.register(checknum)
    Framestocknum = tkinter.Frame(root)
    lablestocknum = tkinter.Label(Framestocknum, text="调整库存数", font=('宋体', 10), width=10, height=2)
    varstocknum = tkinter.StringVar()
    entrystocknum = tkinter.Entry(Framestocknum, textvariable=varstocknum, width=25, validate='key',
                                  validatecommand=(rechecknum, '%P'))
    Framestocknum.pack()
    lablestocknum.pack(side='left')
    entrystocknum.pack()

    # 上架平台
    Framepbusconts = tkinter.Frame(root)
    lablepbusconts = tkinter.Label(Framepbusconts, text="上架平台", font=('宋体', 10), width=10, height=2)
    varpbusconts = tkinter.StringVar()  # 获取下拉框选择的内容
    comboboxpbusconts = ttk.Combobox(Framepbusconts, textvariable=varpbusconts, state="readonly")
    Framepbusconts.pack(side='top')
    lablepbusconts.pack(side='left')
    comboboxpbusconts.pack()

    # 确认按钮
    btn1 = tkinter.Button(root, text='确定', command=inputint)
    btn1.pack()

    # 赋予默认值
    choiceEnv('巴龙')
    initvalue(owncompanyid)
    # 窗口维持
    root.mainloop()

if __name__ == '__main__':
    rootwin()
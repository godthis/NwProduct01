import re
import tkinter

from untils.searchDB import searchmysql
from tkinter import ttk

#定义一个返回值

def TreesPre():
    classvalue=''
    names = locals()
    win=tkinter.Tk()
    #树状图
    Treeviewpclass = ttk.Treeview(win)

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
            #获取上层节点
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
                                                                    str(treename) + str(treeid),text=str(treename), values=str(treeid))
                # 记录加入的节点
                treeall.append(treeid)
            # 上级节点不在list中,more
            else:
                treetool(treeupid)

    def btnok1():
        # 使用全局变量作为返回值
        nonlocal classvalue
        # 获取选择的值
        classvalue = Treeviewpclass.item(Treeviewpclass.selection(),"values")
        if classvalue:

            # 关闭窗口
            win.destroy()
        else:
            print('未选择商品分类')

    def btncan1():
        win.destroy()

    treeall=[]
    #获取所有最底层节点
    treeF0list = searchmysql("select id,up_pti_part_class_id from qs_iss_mas.pti_part_class where own_company_id = 562 "
                           "and id not in (select up_pti_part_class_id from qs_iss_mas.pti_part_class "
                             "where own_company_id = 562 and up_pti_part_class_id is not null) "
                           "and up_pti_part_class_id is not null;","(.*)?")
    treeF0list=re.findall('(?<=[(]).*?(?=[)],)',treeF0list)
    #获取所有最底层节点数量
    treelistlen = len(treeF0list)
    #定个计数器
    i=0
    #遍历所有最底层节点
    while(i < treelistlen):
        treeF0tmp = re.findall('[0-9]+', treeF0list[i])
        #print(treeF0tmp)
        #将底层节点或者底层节点的某个上级节点加入tree
        treetool(treeF0tmp[0])
        #print(treeall[-1])
        #当加入的是底层节点时，计数器加1
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

#cc = TreesPre()
#print('cc ' + cc[0])
    '''
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
    '''


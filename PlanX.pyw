from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
from tkinter.colorchooser import askcolor
import mysql.connector
import hashlib
import tkinter.font as tkFont
import decimal
import math
import datetime as dt
from time import strftime
from kucoin.client import *
import threading as th

connection = mysql.connector.connect(host ='127.0.0.1',user='',password='',database='')
db = connection.cursor()

tk = Tk() 
tk.configure(background="#e0f0fd")
tk.geometry("800x500+200+100")
tk.resizable(False,False)
tk.title("PlanX")

# img = PhotoImage(file=r'D:/Pictures/d.png')
# background = Label(tk,image=img)
# background.place(x=0,y=0)

# def entry_check_create(event):
#     c_username = create_user_entry.get()
#     c_password = create_pass_entry.get() 
#     if c_username=='':
#         create_user_entry.configure(highlightbackground="#ff0000") 
#     else:
#         create_user_entry.configure(highlightbackground="#0000ff") 
#     if c_password == '':
#         create_pass_entry.configure(highlightbackground="#ff0000") 
#     else:
#         create_pass_entry.configure(highlightbackground="#0000ff") 

def entry_check_login(event):
    username = user_entry.get()
    password = pass_entry.get()
    if username=='':
        user_entry.configure(highlightbackground="#ff0000")
    else:
        user_entry.configure(highlightbackground="#0000ff")
    if password=='':
        pass_entry.configure(highlightbackground="#ff0000")
    else:
        pass_entry.configure(highlightbackground="#0000ff") 

def find_duplicate_username(username):
    db.execute(f"select * from users where username = '{username}'")
    dup = db.fetchall()
    if len(dup) != 0:
        return True
    return False

def create_account():
    username = user_entry.get()
    password = pass_entry.get()
    if username=='' or password=='':
        messagebox.showerror("Error",'enter username and password')
    elif find_duplicate_username(username):
        messagebox.showerror("Error","username taken")
    else: 
        db.execute(f"""insert into users(username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr)
                   values('{username}','{password}','0','0','0','0','0','0','0','0','0','0','0') """) 
        db.execute(f"""create table trades_{username}
        (no int auto_increment primary key,
        asset varchar(16),
        vol decimal(10,2),
        entry decimal(10,4),
        sl decimal(10,4),
        tp decimal(10,4),
        rr decimal(10,2),
        lev decimal(10,2),
        close decimal(10,2),
        pnlp decimal(10,4),
        pnl decimal(10,2))""") 
        connection.commit()  
        user_entry.delete(0,'end')
        pass_entry.delete(0,'end')
        login(username) 

def find_account():
    username = user_entry.get()
    password = pass_entry.get() 
    if username=='' or password=='':
        messagebox.showerror("Error",'Enter username and password')
    else:
        db.execute(f"select * from users where username = '{username}' and password = '{password}' ") 
        user = db.fetchall() 
        if len(user) == 0:
            messagebox.showerror("Error","no such user") 
        else:
            user_entry.delete(0,'end')
            pass_entry.delete(0,'end')
            login(username)

def login(username):
    db.execute(f"select * from users where username = '{username}'")
    account = db.fetchall()
    username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr = account[0] 
    db.execute(f"select * from trades_{username}")
    trades = db.fetchall() # A list of trades(tuple) 
    user_window = Toplevel(tk)
    user_window.geometry("802x500+200+100") 
    user_window.resizable(False,False)
    user_window.title(f"PlanX (user: {username})")
    user_window.grab_set()
    user_window.configure(bg="#ffffff") 

    date = dt.datetime.now()
    date_label = Label(user_window, text=f"{date:%A, %B %d, %Y}", font="Calibri, 8",bg="#ffffff")
    date_label.place(x=15,y=475) 

    def my_time():
        time_string = strftime('%H:%M:%S %p') # time format 
        time_label.config(text=time_string)
        time_label.after(1000,my_time) # time delay of 1000 milliseconds 

    time_string = strftime('%H:%M:%S %p')
    time_label = Label(user_window, text=f"{time_string}", font="Calibri, 8",bg="#ffffff")
    time_label.place(x=719,y=475) 
    my_time()

    def add_trade_(username):
        if close_entry.get()=='': close_entry.delete(0,'end'); close_entry.insert(END,0)
        if pnlp_entry.get()=='': pnlp_entry.delete(0,'end'); pnlp_entry.insert(END,0)
        if pnl_entry.get()=='': pnl_entry.delete(0,'end'); pnl_entry.insert(END,0) 
        db.execute(f"select * from users where username = '{username}'")
        account = db.fetchall()
        username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr = account[0]
        if asset_entry.get()=='' or vol_entry.get()=='' or entry_entry.get()=='' or sl_entry.get()=='' or tp_entry.get()=='' or rr_entry.get()=='':
            messagebox.showerror('Error','fill the necessary areas')
        elif float(vol_entry.get())>float(vpt):
            messagebox.showerror('Error',f'volume cannot be more than {vpt}')
        elif float(sl_entry.get())>mrpt*100:
            messagebox.showerror('Error',f'SL cannot be more than {mrpt*100}%')
        # elif float(tp_entry.get())/float(sl_entry.get())<2:
        #     messagebox.showerror("error",'TP gives RR<2') 
        # elif float(rr_entry.get())<2:
        #     messagebox.showerror("error",'RR below 2') 
        else:
            if position_type.get()==1:
                asset = asset_entry.get() + ' (L)'
            elif position_type.get()==2:
                asset = asset_entry.get() + ' (S)' 
            vol=float(vol_entry.get()); entry=float(entry_entry.get()); sl=float(sl_entry.get()); sl=sl/100; tp=float(tp_entry.get()); tp=tp/100
            rr = float(rr_entry.get()); lev=float(lev_entry.get()); close=float(close_entry.get()); pnlp=float(pnlp_entry.get()); pnlp=pnlp/100; pnl=float(pnl_entry.get())
            try:
                db.execute(f"""insert into trades_{username}(asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
                values('{asset}','{vol}','{entry}','{sl}','{tp}','{rr}','{lev}','{close}','{pnlp}','{pnl}')""")
                connection.commit()
            except:
                messagebox.showerror("Error",'error while adding record')
            else:
                db.execute(f"select * from trades_{username}")
                no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl1 = db.fetchall()[-1]
                if pnl1>0:
                    vol = '$' + str(vol)
                    entry = '$' + str(entry)
                    sl = str(sl*100) + '%'
                    tp = str(tp*100) + '%'
                    close = '$' + str(close)
                    pnlp = str(pnlp*100) + '%'
                    if pnl<0:
                        pnl = str(pnl1)
                        pnl = pnl[0] + '$' + pnl[1:]
                    else:
                        pnl = '$' + str(pnl1) 
                    trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
                    trade_view.insert('',index = -1, value=trade,tags='win')
                elif pnl1<0:
                    vol = '$' + str(vol)
                    entry = '$' + str(entry)
                    sl = str(sl*100) + '%'
                    tp = str(tp*100) + '%'
                    close = '$' + str(close)
                    pnlp = str(pnlp*100) + '%'
                    if pnl<0:
                        pnl = str(pnl)
                        pnl = pnl[0] + '$' + pnl[1:]
                    else:
                        pnl = '$' + str(pnl) 
                    trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
                    trade_view.insert('',index = -1, value=trade,tags='loss')
                else:
                    vol = '$' + str(vol)
                    entry = '$' + str(entry)
                    sl = str(sl*100) + '%'
                    tp = str(tp*100) + '%'
                    close = '$' + str(close)
                    pnlp = str(pnlp*100) + '%'
                    if pnl<0:
                        pnl = str(pnl1)
                        pnl = pnl[0] + '$' + pnl[1:]
                    else:
                        pnl = '$' + str(pnl1) 
                    trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
                    trade_view.insert('',index = -1, value=trade) 
                asset_entry.delete(0,'end'); vol_entry.delete(0,'end'); entry_entry.delete(0,'end'); 
                sl_entry.delete(0,'end'); pnl_entry.delete(0,'end'); tp_entry.delete(0,'end'); 
                rr_entry.delete(0,'end'); lev_entry.delete(0,'end'); close_entry.delete(0,'end'); pnlp_entry.delete(0,'end')
                close_entry.insert(END,0); pnlp_entry.insert(END,0); pnl_entry.insert(END,0); lev_entry.insert(END,1) 
                tp_sublabel.configure(text='')
                # db.execute(f"select equity from users where username = '{username}'")
                # equity = db.fetchall()[0][0]
                equity += pnl1
                vpt += pnl1 
                pnl_total += pnl1
                try:
                    db.execute(f"update users set equity = '{equity}' where username = '{username}'")
                    db.execute(f"update users set vpt = '{vpt}' where username = '{username}'")
                    db.execute(f"update users set pnl_total = '{pnl_total}' where username = '{username}'")
                except:
                    connection.rollback()
                    messagebox.showerror('Error','an error has occured while updating account!!')
                else:
                    connection.commit()
                    refresh(username) 

    account_frame = LabelFrame(user_window,width=770,height=60,highlightthickness=1,bg="#a6cfc2")
    account_frame.place(x=15,y=21) 

    saved_label = Label(user_window,text='Saved',bg="#a6cfc2")
    saved_label.place(x=25,y=30)
    balance_label = Label(user_window,text='Balance',bg="#a6cfc2")
    balance_label.place(x=90,y=30)
    emdd_label = Label(user_window,text='EMDD',bg="#a6cfc2")
    emdd_label.place(x=170,y=30)
    tolerance_label = Label(user_window,text='Tolerance',bg="#a6cfc2")
    tolerance_label.place(x=240,y=30)
    vpt_label = Label(user_window,text='VPT',bg="#a6cfc2")
    vpt_label.place(x=320,y=30)
    pnl_label = Label(user_window,text='PNL',bg="#a6cfc2")
    pnl_label.place(x=380,y=30)
    pnlp_label = Label(user_window,text='PNLP',bg="#a6cfc2")
    pnlp_label.place(x=440,y=30)
    equity_label = Label(user_window,text='Equity',bg="#a6cfc2")
    equity_label.place(x=510,y=30)
    mrpt_label = Label(user_window,text='MRPT',bg="#a6cfc2")
    mrpt_label.place(x=595,y=30)
    rr_label = Label(user_window,text='RR',bg="#a6cfc2")
    rr_label.place(x=665,y=30)
    wr_label = Label(user_window,text='WR',bg="#a6cfc2")
    wr_label.place(x=710,y=30) 
    
    saved_value = Label(user_window,text=f'${saved}',bg="#a6cfc2")
    saved_value.place(x=25,y=50) 
    balance_value = Label(user_window,text=f'${balance}',bg="#a6cfc2")
    balance_value.place(x=90,y=50) 
    emdd_value = Label(user_window,text=f'{emdd*100}%',bg="#a6cfc2")
    emdd_value.place(x=170,y=50)
    tolerance_value = Label(user_window,text=f'{tolerance}',bg="#a6cfc2")
    tolerance_value.place(x=240,y=50)
    vpt_value = Label(user_window,text=f'${vpt}',bg="#a6cfc2")
    vpt_value.place(x=320,y=50)
    if pnl_total<0:
        pnl_total = str(pnl_total)
        pnl_total = pnl_total[0] + 'S' + pnl_total[1:]
    else:
        pnl_total = '$' + str(pnl_total) 
    pnl_value = Label(user_window,text=f'{pnl_total}',bg="#a6cfc2")
    pnl_value.place(x=380,y=50)
    pnlp_value = Label(user_window,text=f'{pnlp_total*100}%',bg="#a6cfc2")
    pnlp_value.place(x=440,y=50)
    equity_value = Label(user_window,text=f'${equity}',bg="#a6cfc2")
    equity_value.place(x=510,y=50)
    mrpt_str = mrpt; mrpt_str *= 100; mrpt_str=str(mrpt_str); real,frac=mrpt_str.split('.'); mrpt_str = real + '.' + frac[0:2]
    mrpt_value = Label(user_window,text=f'{mrpt_str}%',bg="#a6cfc2")
    mrpt_value.place(x=595,y=50)
    rr_value = Label(user_window,text=f'{rr_total}',bg="#a6cfc2")
    rr_value.place(x=665,y=50)
    wr_value = Label(user_window,text=f'{wr*100}%',bg="#a6cfc2")
    wr_value.place(x=710,y=50) 

    def get_rr(username):
        db.execute(f"select * from trades_{username}")
        trades = db.fetchall()
        avg_rr = 0
        for i in range(len(trades)):
            avg_rr += trades[i][6]
        if len(trades)>0:
            avg_rr = float(avg_rr)/len(trades)
        else:
            avg_rr = 0
        return avg_rr

    def refresh(username):
        db.execute(f"select * from users where username = '{username}'")
        account = db.fetchall() #a list of tuples
        db.execute(f"select * from trades_{username}")
        trades = db.fetchall() #a list of tuples
        username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr = account[0]
        sum_pnlp = 0
        win = 0
        total_trades = len(trades) 
        gross_profit = 0
        gross_loss = 0
        for i in range(len(trades)):
            no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl = trades[i]
            sum_pnlp += pnlp
            if pnl>0: 
                gross_profit += pnl
                win += 1
            elif pnl<0: 
                gross_loss += math.fabs(pnl) 
        if total_trades>0:
            wr = win/total_trades
        else: wr = 0
        if gross_loss==0:
            rr = get_rr(username)
        else:
            rr = float(gross_profit)/float(gross_loss) 
        if tolerance>0:
            risk = pnl_total/vpt
            if float(float(risk)/float(tolerance))>float(tolerance):
                mrpt = risk/tolerance
            else:
                mrpt = tolerance/100
        try:
            db.execute(f"update users set pnlp_total = '{sum_pnlp}' where username = '{username}'")
            db.execute(f"update users set mrpt = '{mrpt}' where username = '{username}'")
            db.execute(f"update users set rr_total = '{rr}' where username = '{username}'")
            db.execute(f"update users set wr = '{wr}' where username = '{username}'")
        except:
            connection.rollback()
            messagebox.showerror('Error','An error has occured while updating account')
        else:
            connection.commit()
            db.execute(f"select * from users where username = '{username}'")
            account = db.fetchall()
            username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr = account[0]
            saved_value.configure(text=f'${saved}')
            balance_value.configure(text=f'${balance}')
            emdd_value.configure(text=f'{emdd*100}%')
            tolerance_value.configure(text=f'{tolerance}')    
            equity_value.configure(text=f'${equity}') 
            vpt_value.configure(text=f'${vpt}') 
            pnl_value.configure(text=f'${pnl_total}')
            pnlp_value.configure(text=f'{pnlp_total*100}%')
            mrpt *= 100; mrpt=str(mrpt); real,frac=mrpt.split('.'); mrpt = real + '.' + frac[0:2]
            mrpt_value.configure(text=f'{mrpt}%')
            rr_value.configure(text=f'{rr_total}')
            wr_value.configure(text=f'{wr*100}%') 
            vpt_sublabel.configure(text=f'VPT: ${vpt}')
            mrpt_sublabel.configure(text=f'MRPT: {mrpt}%')
            lev_sublabel.configure(text=f'max: 1') 
            user_window.grab_set()

    def deposit_(username):
        deposit_window = Toplevel(user_window)
        deposit_window.geometry("300x200+200+250") 
        deposit_window.resizable(False,False)
        deposit_window.title("Deposit")
        deposit_window.grab_set()
        deposit_window.configure(bg="#ffffff") 

        db.execute(f"select balance,equity,emdd,pnl_total,tolerance from users where username = '{username}'")
        fetch = db.fetchall()
        balance,equity,emdd,pnl_total,tolerance = fetch[0]

        current_balance_label = Label(deposit_window,text=f'current balance: ${balance}',bg="#ffffff",fg="#889589")
        current_balance_label.place(x=15,y=3)
        current_equity_label = Label(deposit_window,text=f'current equity: ${equity}',bg="#ffffff",fg="#889589")
        current_equity_label.place(x=15,y=24)

        amount_label = Label(deposit_window,text='Amount',bg="#ffffff",font=('Calibri',12))
        amount_label.place(x=15,y=70)
        amount_entry = Entry(deposit_window,width=20,highlightthickness=1,highlightbackground="#0000ff")
        amount_entry.place(x=75,y=73)
        amount_entry.insert(END,0)
        usd_label = Label(deposit_window,text='USD',bg="#ffffff")
        usd_label.place(x=205,y=72)

        def deposited(balance,equity,emdd,pnl_total,tolerance):
            if amount_entry.get()=='':
                pass
            else:
                amount = decimal.Decimal(amount_entry.get())
                if amount<=0:
                        pass
                else:
                    try:
                        balance = balance + amount
                        balance_value.configure(text=f'${balance}')
                        equity = equity + amount
                        equity_value.configure(text=f'${equity}')
                        vpt = equity*emdd; vpt=float(vpt); pnl_total=float(pnl_total); tolerance=float(tolerance)
                        mrpt = 0.00
                        if vpt != 0:
                            risk = pnl_total/vpt
                            if tolerance != 0:
                                if (risk/tolerance) > (tolerance/100):
                                    mrpt = risk/tolerance
                                else:
                                    mrpt = tolerance/100
                        db.execute(f"update users set balance = '{balance}' where username = '{username}' ")
                        db.execute(f"update users set equity = '{equity}' where username = '{username}' ")
                        db.execute(f"update users set vpt = '{vpt}' where username = '{username}' ")
                        db.execute(f"update users set mrpt = '{mrpt}' where username = '{username}' ")
                        connection.commit()
                    except Exception as e:
                        connection.rollback()
                        messagebox.showerror('Error','an error has occured')
                        print(e)
                    else:
                        db.execute(f"select vpt from users where username = '{username}'")
                        vpt = db.fetchall()
                        vpt = vpt[0][0]
                        vpt_value.configure(text=f'${vpt}')
                        mrpt1_str = mrpt; mrpt1_str *= 100; mrpt1_str=str(mrpt1_str); real,frac=mrpt1_str.split('.'); mrpt1_str = real + '.' + frac[0:2]
                        mrpt_value.configure(text=f'{mrpt1_str}%')
                        vpt_sublabel.configure(text=f'VPT: ${vpt}')
                        mrpt_sublabel.configure(text=f'MRPT: {mrpt1_str}%')
                        deposit_window.destroy()

        deposit_button = Button(deposit_window,text='Deposit',bg="#2a7e7f",fg="#ffffff",font=('Calibri',8),command=lambda:deposited(balance,equity,emdd,pnl_total,tolerance))
        deposit_button.place(x=117,y=112)
        user_window.grab_set()
        deposit_window.grab_set()
        
    def change_tolerance_(username):
        tolerance_window = Toplevel(user_window)
        tolerance_window.geometry("300x200+200+250") 
        tolerance_window.resizable(False,False)
        tolerance_window.title("Change Tolerance")
        tolerance_window.grab_set()
        tolerance_window.configure(bg="#ffffff") 

        db.execute(f"select tolerance,vpt,pnl_total from users where username = '{username}'")
        fetch = db.fetchall()
        tolerance,vpt,pnl_total = fetch[0]

        current_tolerance_label = Label(tolerance_window,text=f'current Tolerance: {tolerance}',bg="#ffffff",fg="#889589")
        current_tolerance_label.place(x=15,y=5)

        amount_label = Label(tolerance_window,text='Amount',bg="#ffffff",font=('Calibri',12))
        amount_label.place(x=15,y=70)
        amount_entry = Entry(tolerance_window,width=20,highlightthickness=1,highlightbackground="#0000ff")
        amount_entry.place(x=75,y=73)
        amount_entry.insert(END,0)
        tolerance_limit_label = Label(tolerance_window,text='limit=100',bg="#ffffff",fg="#889589",font=('Calibri',9)) 
        tolerance_limit_label.place(x=80,y=95)

        def tolerance_changed(vpt,pnl_total):
            if amount_entry.get()=='':
                pass
            else:
                amount = float(amount_entry.get())
                if amount<=0 or amount>100:
                        pass
                else:
                    db.execute(f"update users set tolerance = '{amount}' where username = '{username}'")
                    tolerance_value.configure(text=f'{amount}')
                    pnl_total = float(pnl_total); vpt = float(vpt)
                    if vpt != 0:
                        risk = pnl_total/vpt
                        if (risk/amount)>(amount/100):
                            mrpt = risk/amount
                        else:
                            mrpt = amount/100
                    db.execute(f"update users set mrpt = '{mrpt}' where username = '{username}'")
                    connection.commit()
                    tolerance_value.configure(text=f"{amount}")
                    mrpt = float(mrpt); mrpt *= 100; mrpt=str(mrpt); real,frac=mrpt.split('.'); mrpt = real + '.' + frac[0:2]
                    mrpt_value.configure(text=f"{mrpt}%")
                    mrpt_sublabel.configure(text=f"MRPT: {mrpt}%")
                    tolerance_window.destroy()

        confirm_button = Button(tolerance_window,text='Confirm Tolerance',bg="#2a7e7f",fg="#ffffff",font=('Calibri',8),command=lambda: tolerance_changed(vpt,pnl_total))
        confirm_button.place(x=100,y=130)
        user_window.grab_set()
        tolerance_window.grab_set()
    
    def change_password_(username):
        password_window = Toplevel(user_window)
        password_window.geometry("300x200+200+250") 
        password_window.resizable(False,False)
        password_window.title("Change Password")
        password_window.grab_set()
        password_window.configure(bg="#ffffff") 

        db.execute(f"select password from users where username = '{username}'")
        fetch = db.fetchall()
        password= fetch[0][0]

        current_password_label = Label(password_window,text=f'current password: {password}',bg="#ffffff",fg="#889589")
        current_password_label.place(x=15,y=5)

        new_password_label = Label(password_window,text='New password',bg="#ffffff",font=('Calibri',12))
        new_password_label.place(x=15,y=70)
        new_password_entry = Entry(password_window,width=25,highlightthickness=1,highlightbackground="#0000ff")
        new_password_entry.place(x=125,y=73)  

        def new_password_():
            if new_password_entry.get()=='':
                pass
            else:
                db.execute(f"update users set password = '{new_password_entry.get()}' where username = '{username}'")
                connection.commit() 
                password_window.destroy() 

        confirm_new_password_button = Button(password_window,text='Confirm password',bg="#2a7e7f",fg="#ffffff",font=('Calibri',8),command=new_password_)
        confirm_new_password_button.place(x=100,y=130)
        user_window.grab_set()
        password_window.grab_set()

    def change_emdd_(username):
        emdd_window = Toplevel(user_window)
        emdd_window.geometry("300x200+200+250") 
        emdd_window.resizable(False,False)
        emdd_window.title("Change EMDD")
        emdd_window.grab_set()
        emdd_window.configure(bg="#ffffff") 

        db.execute(f"select equity,emdd,vpt from users where username = '{username}'")
        fetch = db.fetchall()
        equity,emdd,vpt = fetch[0]

        current_emdd_label = Label(emdd_window,text=f'current EMDD: {emdd*100}%',bg="#ffffff",fg="#889589")
        current_emdd_label.place(x=15,y=5)

        amount_label = Label(emdd_window,text='Amount',bg="#ffffff",font=('Calibri',12))
        amount_label.place(x=15,y=70)
        amount_entry = Entry(emdd_window,width=20,highlightthickness=1,highlightbackground="#0000ff")
        amount_entry.place(x=75,y=73)
        amount_entry.insert(END,0)
        percent_label = Label(emdd_window,text='%',bg="#ffffff")
        percent_label.place(x=205,y=72)

        def emdd_changed(equity,emdd,vpt):
            if amount_entry.get()=='':
                pass
            else:
                amount = decimal.Decimal(amount_entry.get())
                if amount<=0 or amount>100:
                        pass
                else:
                    try:
                        amount = amount/100
                        db.execute(f"update users set emdd = '{amount}' where username = '{username}'")
                        vpt = equity*amount
                        db.execute(f"update users set vpt = '{vpt}' where username = '{username}'")
                    except:
                        messagebox.showerror('Error','an error has occured')
                    else:
                        connection.commit()
                        db.execute(f"select emdd,vpt from users where username = '{username}'")
                        emdd,vpt = db.fetchall()[0] 
                        emdd_value.configure(text=f'{emdd*100}%')
                        vpt_value.configure(text=f'${vpt}')
                        vpt_sublabel.configure(text=f'VPT: ${vpt}')
                        emdd_window.destroy()

        emdd_confirm_button = Button(emdd_window,text='Confirm EMDD',bg="#2a7e7f",fg="#ffffff",font=('Calibri',8),command=lambda:emdd_changed(equity,emdd,vpt))
        emdd_confirm_button.place(x=100,y=112)
        user_window.grab_set()
        emdd_window.grab_set()

    def withdraw_(username):
        withdraw_window = Toplevel(user_window)
        withdraw_window.geometry("300x200+200+250") 
        withdraw_window.resizable(False,False)
        withdraw_window.title("Withdraw")
        withdraw_window.grab_set()
        withdraw_window.configure(bg="#ffffff") 

        db.execute(f"select saved,balance,equity,emdd,pnl_total,tolerance from users where username = '{username}'")
        fetch = db.fetchall()
        saved,balance,equity,emdd,pnl_total,tolerance = fetch[0]

        current_balance_label = Label(withdraw_window,text=f'current balance: ${balance}',bg="#ffffff",fg="#889589")
        current_balance_label.place(x=15,y=3)
        current_equity_label = Label(withdraw_window,text=f'current equity: ${equity}',bg="#ffffff",fg="#889589")
        current_equity_label.place(x=15,y=24)

        amount_label = Label(withdraw_window,text='Amount',bg="#ffffff",font=('Calibri',12))
        amount_label.place(x=15,y=70)
        amount_entry = Entry(withdraw_window,width=20,highlightthickness=1,highlightbackground="#0000ff")
        amount_entry.place(x=75,y=73)
        amount_entry.insert(END,0)
        usd_label = Label(withdraw_window,text='USD',bg="#ffffff") 
        usd_label.place(x=205,y=72)

        def withdrawn(saved,balance,equity,emdd,pnl_total,tolerance):
            if amount_entry.get()=='':
                pass
            else:
                amount = float(amount_entry.get())
                if amount<=0 or amount>equity:
                        pass
                else:
                    try:
                        equity=float(equity); saved=float(saved); balance=float(balance); pnl_total=float(pnl_total); tolerance=float(tolerance); emdd=float(emdd)
                        equity -= amount
                        saved += amount
                        balance -= amount
                        if balance<0: balance = 0
                        pnl_total -= amount
                        if pnl_total<=0: pnl_total = 0
                        vpt = equity*emdd
                        risk = pnl_total/vpt
                        if risk/tolerance>tolerance:
                            mrpt = risk/tolerance
                        else:
                            mrpt = tolerance/100
                        db.execute(f"update users set saved = '{saved}' where username = '{username}'")
                        db.execute(f"update users set balance = '{balance}' where username = '{username}'")
                        db.execute(f"update users set equity = '{equity}' where username = '{username}'")
                        db.execute(f"update users set vpt = '{vpt}' where username = '{username}'")
                        db.execute(f"update users set pnl_total = '{pnl_total}' where username = '{username}'")
                        db.execute(f"update users set mrpt = '{mrpt}' where username = '{username}'")
                        connection.commit()
                    except:
                        connection.rollback()
                        messagebox.showerror('Error','an error has occured') 
                    else:
                        db.execute(f"select saved,balance,equity,vpt,pnl_total,mrpt from users where username = '{username}'")
                        saved,balance,equity,vpt,pnl_total,mrpt = db.fetchall()[0]
                        saved_value.configure(text=f'${saved}')
                        balance_value.configure(text=f'${balance}')
                        equity_value.configure(text=f'${equity}')
                        vpt_value.configure(text=f'${vpt}')
                        pnl_value.configure(text=f'${pnl_total}')
                        mrpt1_str = mrpt; mrpt1_str *= 100; mrpt1_str=str(mrpt1_str); real,frac=mrpt1_str.split('.'); mrpt1_str = real + '.' + frac[0:2]
                        mrpt_value.configure(text=f'{mrpt1_str}%')
                        vpt_sublabel.configure(text=f'VPT: ${vpt}')
                        mrpt_sublabel.configure(text=f'MRPT: {mrpt1_str}%') 
                        withdraw_window.destroy() 

        withdraw_button = Button(withdraw_window,text='Withdraw',bg="#2a7e7f",fg="#ffffff",font=('Calibri',8),command=lambda:withdrawn(saved,balance,equity,emdd,pnl_total,tolerance))
        withdraw_button.place(x=117,y=112)
        user_window.grab_set()
        withdraw_window.grab_set()

    def kucoin_(username):
        kucoin_window = Toplevel(user_window)
        kucoin_window.geometry("300x200+200+250") 
        kucoin_window.resizable(False,False)
        kucoin_window.title("Kucoin")
        kucoin_window.grab_set()
        kucoin_window.configure(bg="#ffffff") 
        
        api_key = ''
        api_secret = ''
        passphrase = ''

        client = Client(api_key,api_secret,passphrase)

        def get_price():
            global bnb,bnb_price_label
            global xrp,xrp_price_label
            global ada,ada_price_label

            btc = client.get_ticker('BTC-USDT')
            btc_price_label.config(text=f"${btc['price']}")
    
            eth = client.get_ticker('ETH-USDT')
            eth_price_label.config(text=f"${eth['price']}")
    
            bnb = client.get_ticker('BNB-USDT')
            bnb_price_label = Label(kucoin_window,text=f"${bnb['price']}")

            xrp = client.get_ticker('XRP-USDT')
            xrp_price_label = Label(kucoin_window,text=f"${xrp['price']}")

            ada = client.get_ticker('ADA-USDT')
            ada_price_label = Label(kucoin_window,text=f"${ada['price']}")
    
            price_label.after(100,get_price)


        price_label = Label(kucoin_window,text='Prices',font=('Helvetica', 15, 'bold'),bg='#BBBBFF')
        price_label.place(x=20,y=20)

        btc = client.get_ticker('BTC-USDT')
        btc_label = Label(kucoin_window,text='Bitcoin: ',font=('Helvetica', 10, 'bold'),bg='#ffffff')
        btc_label.place(x=20,y=60)
        btc_price_label = Label(kucoin_window,text=f"${btc['price']}",bg='#ffffff')
        btc_price_label.place(x=100,y=60)

        eth = client.get_ticker('ETH-USDT')
        btc_label = Label(kucoin_window,text='Ethereum: ',font=('Helvetica', 10, 'bold'),bg='#ffffff')
        btc_label.place(x=20,y=80)
        eth_price_label = Label(kucoin_window,text=f"${eth['price']}",bg='#ffffff')
        eth_price_label.place(x=100,y=80)

        bnb = client.get_ticker('BNB-USDT')
        btc_label = Label(kucoin_window,text='Binance: ',font=('Helvetica', 10, 'bold'),bg='#ffffff')
        btc_label.place(x=20,y=100)
        bnb_price_label = Label(kucoin_window,text=f"${bnb['price']}",bg='#ffffff')
        bnb_price_label.place(x=100,y=100)

        xrp = client.get_ticker('XRP-USDT')
        btc_label = Label(kucoin_window,text='Ripple: ',font=('Helvetica', 10, 'bold'),bg='#ffffff')
        btc_label.place(x=20,y=120)
        xrp_price_label = Label(kucoin_window,text=f"${xrp['price']}",bg='#ffffff')
        xrp_price_label.place(x=100,y=120)

        ada = client.get_ticker('ADA-USDT')
        btc_label = Label(kucoin_window,text='Cardano: ',font=('Helvetica', 10, 'bold'),bg='#ffffff')
        btc_label.place(x=20,y=140)
        ada_price_label = Label(kucoin_window,text=f"${ada['price']}",bg='#ffffff')
        ada_price_label.place(x=100,y=140)

        get_price()       

        user_window.grab_set()
        kucoin_window.grab_set()


    
    def edit_trade(username):
        if len(trade_view.selection())>0:
            trade = trade_view.item(trade_view.selection()[0])
            selected_trade = trade_view.selection()[0]
            no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl = trade['values']
            close = close[1:]; close = float(close)
            if close==0:
                db.execute(f"select * from users where username = '{username}'")
                account = db.fetchall()
                username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr = account[0]
                mrpt1_str = mrpt; mrpt1_str *= 100; mrpt1_str=str(mrpt1_str); real,frac=mrpt1_str.split('.'); mrpt1_str = real + '.' + frac[0:2]
                edit_window = Toplevel(user_window)
                edit_window.geometry("800x200+140+400") 
                edit_window.resizable(False,False)
                edit_window.title("Edit trade")
                user_window.grab_set()
                edit_window.grab_set()
                edit_window.configure(bg="#ffffff") 
                def add_trade_entry_check1(event):
                    if asset1_entry.get()=='':
                        asset1_entry.configure(highlightbackground="#ff0000") 
                    else:
                        asset1_entry.configure(highlightbackground="#0000ff")
                    if vol1_entry.get()=='':
                        vol1_entry.configure(highlightbackground="#ff0000")
                    else:
                        vol1_entry.configure(highlightbackground="#0000ff")
                    if entry1_entry.get()=='':
                        entry1_entry.configure(highlightbackground="#ff0000")
                    else:
                        entry1_entry.configure(highlightbackground="#0000ff")
                    if sl1_entry.get()=='':
                        sl1_entry.configure(highlightbackground="#ff0000")
                        lev1_sublabel.configure(text='max: 1')
                        tp1_sublabel.configure(text='')
                    else:
                        sl1_entry.configure(highlightbackground="#0000ff")
                        try:
                            tp = decimal.Decimal(sl1_entry.get())*2
                            tp1_sublabel.configure(text=f'min: {tp}%')
                            lev = mrpt/decimal.Decimal(sl1_entry.get()); lev *= 100; lev=str(lev); real,frac=lev.split('.'); lev = real + '.' + frac[0:2]
                            lev1_sublabel.configure(text=f'max: {lev}') 
                        except:
                            tp1_sublabel.configure(text='')
                            lev1_sublabel.configure(text='max: 1')
                    if tp1_entry.get()=='':
                        tp1_entry.configure(highlightbackground="#ff0000")
                        rr1_entry.delete(0,'end')
                        rr1_entry.insert(END,0)
                    else:
                        tp1_entry.configure(highlightbackground="#0000ff")
                        try:
                            rr = float(tp1_entry.get())/float(sl1_entry.get())
                            rr=str(rr); real,frac=rr.split('.'); rr = real + '.' + frac[0:2]
                            rr1_entry.delete(0,'end')
                            rr1_entry.insert(END,rr)
                        except:
                            rr1_entry.delete(0,'end')
                            rr1_entry.insert(END,0)
                    if rr1_entry.get()=='':
                        rr1_entry.configure(highlightbackground="#ff0000")
                    else:
                        rr1_entry.configure(highlightbackground="#0000ff")
                    if close1_entry.get()=='' or close1_entry.get()=='0':
                        pnlp1_entry.delete(0,'end')
                        pnl1_entry.delete(0,'end')
                        pnlp1_entry.insert(END,0)
                        pnl1_entry.insert(END,0) 
                    else:
                        try:
                            pnlp1_entry.delete(0,'end')
                            pnl1_entry.delete(0,'end')
                            pnlp = ((float(close1_entry.get())-float(entry1_entry.get()))/float(entry1_entry.get()))*100; pnlp = pnlp*float(lev1_entry.get())
                            if position1_type.get()==2:
                                pnlp *= -1
                            pnlp1=str(pnlp); real,frac=pnlp1.split('.'); pnlp1 = real + '.' + frac[0:2]
                            pnlp1 = float(pnlp1)
                            pnlp1_entry.insert(END,pnlp1)
                            if vol1_entry.get()=='':
                                vol = 0
                            else:
                                vol = float(vol1_entry.get())
                            pnl = vol*(pnlp/100); pnl=str(pnl); real,frac=pnl.split('.'); pnl = real + '.' + frac[0:2]
                            pnl1_entry.insert(END,pnl) 
                        except:
                            pnlp1_entry.delete(0,'end')
                            pnl1_entry.delete(0,'end')
                            pnlp1_entry.insert(END,0)
                            pnl1_entry.insert(END,0) 

                def edited(username,no):
                    if close1_entry.get()=='': close1_entry.delete(0,'end'); close1_entry.insert(END,0)
                    if pnlp1_entry.get()=='': pnlp1_entry.delete(0,'end'); pnlp1_entry.insert(END,0)
                    if pnl1_entry.get()=='': pnl1_entry.delete(0,'end'); pnl1_entry.insert(END,0) 
                    db.execute(f"select * from users where username = '{username}'")
                    account = db.fetchall()
                    username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr = account[0]
                    if asset1_entry.get()=='' or vol1_entry.get()=='' or entry1_entry.get()=='' or sl1_entry.get()=='' or tp1_entry.get()=='' or rr1_entry.get()=='':
                        messagebox.showerror('Error','fill the necessary areas')
                    elif float(vol1_entry.get())>float(vpt):
                        messagebox.showerror('Error',f'volume cannot be more than {vpt}')
                    elif float(sl1_entry.get())>mrpt*100:
                        messagebox.showerror('Error',f'SL cannot be more than {mrpt*100}%')
                    # elif float(tp1_entry.get())/float(sl1_entry.get())<2:
                    #     messagebox.showerror("error",'TP gives RR<2') 
                    # elif float(rr1_entry.get())<2:
                    #     messagebox.showerror("error",'RR below 2') 
                    else:
                        if position1_type.get()==1:
                            asset = asset1_entry.get() + ' (L)'
                        elif position1_type.get()==2:
                            asset = asset1_entry.get() + ' (S)' 
                        vol=float(vol1_entry.get()); entry=float(entry1_entry.get()); sl=float(sl1_entry.get()); sl=sl/100; tp=float(tp1_entry.get()); tp=tp/100
                        rr = float(rr1_entry.get()); lev=float(lev1_entry.get()); close=float(close1_entry.get()); pnlp=float(pnlp1_entry.get()); pnlp=pnlp/100; pnl=float(pnl1_entry.get())
                        try:
                            db.execute(f"update trades_{username} set asset = '{asset}' where no = '{no}'")
                            db.execute(f"update trades_{username} set vol = '{vol}' where no = '{no}'")
                            db.execute(f"update trades_{username} set entry = '{entry}' where no = '{no}'")
                            db.execute(f"update trades_{username} set sl = '{sl}' where no = '{no}'")
                            db.execute(f"update trades_{username} set tp = '{tp}' where no = '{no}'")
                            db.execute(f"update trades_{username} set rr = '{rr}' where no = '{no}'")
                            db.execute(f"update trades_{username} set lev = '{lev}' where no = '{no}'")
                            db.execute(f"update trades_{username} set close = '{close}' where no = '{no}'")
                            db.execute(f"update trades_{username} set pnlp = '{pnlp}' where no = '{no}'")
                            db.execute(f"update trades_{username} set pnl = '{pnl}' where no = '{no}'")
                            connection.commit()
                        except Exception as e:
                            print(e)
                            connection.rollback()
                            messagebox.showerror("Error",'error while adding record')
                        else:
                            db.execute(f"select * from trades_{username} where no = '{no}'")
                            no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl1 = db.fetchall()[0] 
                            if pnl1>0:
                                vol = '$' + str(vol)
                                entry = '$' + str(entry)
                                sl = str(sl*100) + '%'
                                tp = str(tp*100) + '%'
                                close = '$' + str(close)
                                pnlp = str(pnlp*100) + '%'
                                if pnl<0:
                                    pnl = str(pnl1)
                                    pnl = pnl[0] + '$' + pnl[1:]
                                else:
                                    pnl = '$' + str(pnl1) 
                                trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
                                trade_view.item(selected_trade, value=trade,tags='win')
                            elif pnl1<0:
                                vol = '$' + str(vol)
                                entry = '$' + str(entry)
                                sl = str(sl*100) + '%'
                                tp = str(tp*100) + '%'
                                close = '$' + str(close)
                                pnlp = str(pnlp*100) + '%'
                                if pnl<0:
                                    pnl = str(pnl)
                                    pnl = pnl[0] + '$' + pnl[1:]
                                else:
                                    pnl = '$' + str(pnl) 
                                trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
                                trade_view.item(selected_trade, value=trade,tags='loss')
                            else:
                                vol = '$' + str(vol)
                                entry = '$' + str(entry)
                                sl = str(sl*100) + '%'
                                tp = str(tp*100) + '%'
                                close = '$' + str(close)
                                pnlp = str(pnlp*100) + '%'
                                if pnl<0:
                                    pnl = str(pnl1)
                                    pnl = pnl[0] + '$' + pnl[1:]
                                else:
                                    pnl = '$' + str(pnl1) 
                                trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
                                trade_view.item(selected_trade, value=trade) 
                            
                            equity += pnl1
                            vpt += pnl1 
                            pnl_total += pnl1
                            try:
                                db.execute(f"update users set equity = '{equity}' where username = '{username}'")
                                db.execute(f"update users set vpt = '{vpt}' where username = '{username}'")
                                db.execute(f"update users set pnl_total = '{pnl_total}' where username = '{username}'")
                                connection.commit()
                            except:
                                connection.rollback()
                                messagebox.showerror('Error','an error has occured while updating account!!')
                            else:
                                refresh(username) 
                                edit_window.destroy()
                
                edit_trade_frame = LabelFrame(edit_window,width=770,height=100,highlightthickness=1,bg="#e8e4e8")
                edit_trade_frame.place(x=15,y=44)

                edit_trade = Label(edit_window,text='Edit trade',width=10,bg="#400c43",fg="#ffffff")
                edit_trade.place(x=16,y=24)

                position1_type = IntVar(edit_window) 
                long1 = Radiobutton(edit_window,text="Long",variable = position1_type, value=1,fg="#51ae6a",bg='#ffffff',font=('Calibri',9))
                long1.place(x=100,y=20)
                short1 = Radiobutton(edit_window,text="Short",variable = position1_type, value=2,fg="#c73839",bg='#ffffff',font=('Calibri',9))
                short1.place(x=155,y=20) 

                asset1_label = Label(edit_window,text='Asset',bg="#e8e4e8",font=('Calibri',12)) 
                asset1_label.place(x=30,y=59) 
                asset1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                asset1_entry.place(x=30,y=89)
                asset1_entry.bind("<KeyRelease>",add_trade_entry_check1)
                vol1_label = Label(edit_window,text='Vol',bg="#e8e4e8",font=('Calibri',12))
                vol1_label.place(x=100,y=59) 
                vol1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                vol1_entry.place(x=100,y=89)
                vol1_entry.bind("<KeyRelease>",add_trade_entry_check1)
                entry1_label = Label(edit_window,text='Entry',bg="#e8e4e8",font=('Calibri',12))
                entry1_label.place(x=170,y=59) 
                entry1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                entry1_entry.place(x=170,y=89)
                entry1_entry.bind("<KeyRelease>",add_trade_entry_check1)
                sl1_label = Label(edit_window,text='SL',bg="#e8e4e8",font=('Calibri',12))
                sl1_label.place(x=240,y=59) 
                sl1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                sl1_entry.place(x=240,y=89)
                sl1_entry.bind("<KeyRelease>",add_trade_entry_check1)
                tp1_label = Label(edit_window,text='TP',bg="#e8e4e8",font=('Calibri',12))
                tp1_label.place(x=310,y=59) 
                tp1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                tp1_entry.place(x=310,y=89)
                tp1_entry.bind("<KeyRelease>",add_trade_entry_check1)
                rr1_label = Label(edit_window,text='RR',bg="#e8e4e8",font=('Calibri',12))
                rr1_label.place(x=380,y=59) 
                rr1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                rr1_entry.place(x=380,y=89)
                rr1_entry.bind("<KeyRelease>",add_trade_entry_check1)
                lev1_label = Label(edit_window,text='Lev',bg="#e8e4e8",font=('Calibri',12)) 
                lev1_label.place(x=450,y=59) 
                lev1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                lev1_entry.place(x=450,y=89)
                close1_label = Label(edit_window,text='Close',bg="#e8e4e8",font=('Calibri',12))
                close1_label.place(x=520,y=59) 
                close1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                close1_entry.place(x=520,y=89)
                close1_entry.bind("<KeyRelease>",add_trade_entry_check1)
                pnlp1_label = Label(edit_window,text='PNLP',bg="#e8e4e8",font=('Calibri',12))
                pnlp1_label.place(x=590,y=59) 
                pnlp1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
                pnlp1_entry.place(x=590,y=89)
                pnl1_label = Label(edit_window,text='PNL',bg="#e8e4e8",font=('Calibri',12))
                pnl1_label.place(x=660,y=59) 
                pnl1_entry = Entry(edit_window,width=10,highlightbackground="#0000ff",highlightthickness=1) 
                pnl1_entry.place(x=660,y=89)

                number_frame = Label(edit_window,text=f'{no}',highlightthickness=1,bg="#e8e4e8",highlightbackground="#000000")
                number_frame.place(x=17,y=150)

                asset,position = asset.split('('); position = position[0]; asset = asset[:-1]; asset1_entry.insert(END,asset)
                if position=='L': position1_type.set(1)
                elif position=='S': position1_type.set(2)
                vol = vol[1:]; vol = float(vol); vol1_entry.insert(END,vol)
                entry = entry[1:]; entry = float(entry); entry1_entry.insert(END,entry)
                sl,percent = sl.split('%'); sl = float(sl); sl1_entry.insert(END,sl)
                tp,percent = tp.split('%'); tp = float(tp); tp1_entry.insert(END,tp) 
                rr1_entry.insert(END,rr)
                lev1_entry.insert(END,lev)  
                close1_entry.insert(END,0)
                pnlp1_entry.insert(END,0)
                pnl1_entry.insert(END,0)

                mrpt1_sublabel = Label(edit_window,text=f'MRPT: {mrpt1_str}%',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                mrpt1_sublabel.place(x=235,y=110)
                asset1_ex_label = Label(edit_window,text='Ex: EUR/USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                asset1_ex_label.place(x=30,y=110)
                vpt1_sublabel = Label(edit_window,text=f'VPT: ${vpt}',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                vpt1_sublabel.place(x=95,y=110)
                tp1_sublabel = Label(edit_window,text='',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                tp1_sublabel.place(x=315,y=110)
                decimal1_label1 = Label(edit_window,text='min: 2',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                decimal1_label1.place(x=380,y=110)
                lev1_sublabel = Label(edit_window,text=f'max: 1',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                lev1_sublabel.place(x=450,y=110) 
                rr1_sublabel = Label(edit_window,text='%',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                rr1_sublabel.place(x=590,y=110)
                pnl1_sublabel = Label(edit_window,text='USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                pnl1_sublabel.place(x=660,y=110)
                entry1_sublabel = Label(edit_window,text='USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                entry1_sublabel.place(x=170,y=110)
                close1_sublabel = Label(edit_window,text='USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
                close1_sublabel.place(x=520,y=110)

                edit_trade_button = Button(edit_window,text='Edit',bg="#216263",fg="#ffffff",command=lambda:edited(username,no))
                edit_trade_button.place(x=736,y=84) 

                user_window.grab_set()
                edit_window.grab_set()

            else:
                user_window.grab_set()
                trade_view.selection_remove(trade_view.selection()) 

    def delete_trade(username):
        if len(trade_view.selection())>0:
            trade = trade_view.item(trade_view.selection()[0])
            selected_trade = trade_view.selection()[0]
            no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl = trade['values']
            db.execute(f"select * from users where username = '{username}'")
            account = db.fetchall()
            username,password,saved,balance,emdd,tolerance,vpt,pnl_total,pnlp_total,equity,mrpt,rr_total,wr = account[0]
            delete_window = Toplevel(user_window)
            delete_window.geometry("800x200+140+400") 
            delete_window.resizable(False,False)
            delete_window.title("Delete trade")
            user_window.grab_set()
            delete_window.grab_set()
            delete_window.configure(bg="#ffffff") 

            def deleted(username,no,pnl,equity,vpt,pnl_total):
                if pnl[0]=='$':
                    pnl = pnl[1:]; pnl = float(pnl)
                elif pnl[0]=='-':
                    pnl = pnl[2:]; pnl = float(pnl); pnl *= -1
                equity = float(equity); vpt = float(vpt); pnl_total = float(pnl_total)
                equity -= pnl
                vpt -= pnl
                pnl_total -= pnl
                try:
                    db.execute(f"update users set equity = '{equity}' where username = '{username}'")
                    db.execute(f"update users set vpt = '{vpt}' where username = '{username}'")
                    db.execute(f"update users set pnl_total = '{pnl_total}' where username = '{username}'")
                    db.execute(f"delete from trades_{username} where no = '{no}'") 
                    connection.commit()
                except:
                    connection.rollback()
                    messagebox.showerror('Error','an error has occured while deleting trade and updating account.')
                else:
                    trade_view.delete(selected_trade) 
                    refresh(username) 
                    delete_window.destroy()

            delete_trade_frame = LabelFrame(delete_window,width=770,height=100,highlightthickness=1,bg="#e8e4e8")
            delete_trade_frame.place(x=15,y=44)

            delete_trade = Label(delete_window,text='Delete trade',width=10,bg="#400c43",fg="#ffffff")
            delete_trade.place(x=16,y=24)

            asset,position = asset.split('('); position = position[0]; asset = asset[:-1] 
            if position=='L':
                long1 = Radiobutton(delete_window,text="Long",fg="#51ae6a",bg='#ffffff',font=('Calibri',9))
                long1.place(x=100,y=20)
            elif position=='S': 
                short1 = Radiobutton(delete_window,text="Short",fg="#c73839",bg='#ffffff',font=('Calibri',9))
                short1.place(x=100,y=20) 

            asset1_label = Label(delete_window,text='Asset',bg="#e8e4e8",font=('Calibri',12)) 
            asset1_label.place(x=30,y=59) 
            asset1_value = Label(delete_window,text=f"{asset}",highlightbackground="#400c43",highlightthickness=1)
            asset1_value.place(x=31,y=89)
            
            vol1_label = Label(delete_window,text='Vol',bg="#e8e4e8",font=('Calibri',12))
            vol1_label.place(x=98,y=59) 
            vol1_value = Label(delete_window,text=f"{vol}",highlightbackground="#400c43",highlightthickness=1)
            vol1_value.place(x=98,y=89)
            
            entry1_label = Label(delete_window,text='Entry',bg="#e8e4e8",font=('Calibri',12))
            entry1_label.place(x=165,y=59) 
            entry1_value = Label(delete_window,text=f"{entry}",highlightbackground="#400c43",highlightthickness=1)
            entry1_value.place(x=165,y=89)
            
            sl1_label = Label(delete_window,text='SL',bg="#e8e4e8",font=('Calibri',12))
            sl1_label.place(x=250,y=59) 
            sl1_value = Label(delete_window,text=f"{sl}",highlightbackground="#400c43",highlightthickness=1)
            sl1_value.place(x=250,y=89)
            
            tp1_label = Label(delete_window,text='TP',bg="#e8e4e8",font=('Calibri',12))
            tp1_label.place(x=315,y=59) 
            tp1_value = Label(delete_window,text=f"{tp}",highlightbackground="#400c43",highlightthickness=1)
            tp1_value.place(x=315,y=89)
            
            rr1_label = Label(delete_window,text='RR',bg="#e8e4e8",font=('Calibri',12))
            rr1_label.place(x=383,y=59) 
            rr1_value = Label(delete_window,text=f"{rr}",highlightbackground="#400c43",highlightthickness=1)
            rr1_value.place(x=383,y=89)
            
            lev1_label = Label(delete_window,text='Lev',bg="#e8e4e8",font=('Calibri',12)) 
            lev1_label.place(x=436,y=59) 
            lev1_value = Label(delete_window,text=f"{lev}",highlightbackground="#400c43",highlightthickness=1)
            lev1_value.place(x=436,y=89)

            close1_label = Label(delete_window,text='Close',bg="#e8e4e8",font=('Calibri',12))
            close1_label.place(x=490,y=59) 
            close1_value = Label(delete_window,text=f"{close}",highlightbackground="#400c43",highlightthickness=1)
            close1_value.place(x=490,y=89)
            
            pnlp1_label = Label(delete_window,text='PNLP',bg="#e8e4e8",font=('Calibri',12))
            pnlp1_label.place(x=575,y=59) 
            pnlp1_value = Label(delete_window,text=f"{pnlp}",highlightbackground="#400c43",highlightthickness=1)
            pnlp1_value.place(x=575,y=89)

            pnl1_label = Label(delete_window,text='PNL',bg="#e8e4e8",font=('Calibri',12))
            pnl1_label.place(x=652,y=59) 
            pnl1_value = Label(delete_window,text=f"{pnl}",highlightbackground="#400c43",highlightthickness=1) 
            pnl1_value.place(x=652,y=89)

            number_frame = Label(delete_window,text=f'{no}',bg="#e8e4e8",highlightthickness=1,highlightbackground="#000000")
            number_frame.place(x=17,y=150)
            if pnl[0]=='$':
                number_frame.configure(bg="#b8f6a9")
            elif pnl[0]=='-':
                number_frame.configure(bg="#f9b1ad")
            
            delete_trade_button = Button(delete_window,text='Delete',bg="#a23620",fg="#ffffff",font=('Calibri',10),command=lambda:deleted(username,no,pnl,equity,vpt,pnl_total)) 
            delete_trade_button.place(x=720,y=86) 

            user_window.grab_set()
            delete_window.grab_set()

        else:
            user_window.grab_set()
            trade_view.selection_remove(trade_view.selection()) 
    
    def reset_account(username):
        reset_window = Toplevel(user_window)
        reset_window.geometry("300x200+250+200") 
        reset_window.resizable(False,False)
        reset_window.title("Reset account")
        user_window.grab_set()
        reset_window.grab_set()
        reset_window.configure(bg="#ffffff") 

        def reset(username):
            if check_password_entry.get() != password:
                messagebox.showerror("Error","password isn't match")
            else:
                try:
                    db.execute(f"drop table trades_{username}")
                    db.execute(f"update users set saved = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set balance = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set emdd = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set tolerance = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set vpt = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set pnl_total = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set pnlp_total = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set equity = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set mrpt = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set rr_total = '{0.00}' where username = '{username}'")
                    db.execute(f"update users set wr = '{0.00}' where username = '{username}'")
                    db.execute(f"""create table trades_{username}
                    (no int auto_increment primary key,
                    asset varchar(16),
                    vol decimal(10,2),
                    entry decimal(10,4),
                    sl decimal(10,3),
                    tp decimal(10,3),
                    rr decimal(10,2),
                    lev decimal(10,2),
                    close decimal(10,2),
                    pnlp decimal(10,4),
                    pnl decimal(10,2))""") 
                    connection.commit()
                except:
                    connection.rollback()
                    messagebox.showerror('Error',"something went wrong")
                else:

                    for item in trade_view.get_children():
                        trade_view.delete(item)
                    refresh(username)
                    reset_window.destroy() 

        check_password_label = Label(reset_window,text='Enter password',bg="#ffffff",font=('Calibri',12))
        check_password_label.place(x=15,y=70)
        check_password_entry = Entry(reset_window,width=25,highlightthickness=1,highlightbackground="#0000ff")
        check_password_entry.place(x=125,y=73)  

        reset_button = Button(reset_window,text='Reset account',bg="#a23620",fg="#ffffff",font=('Calibri',10),command=lambda:reset(username))
        reset_button.place(x=100,y=130) 
        user_window.grab_set()
        reset_window.grab_set() 
    
    def delete_account(username):
        delete_account_window = Toplevel(user_window)
        delete_account_window.geometry("300x200+250+200") 
        delete_account_window.resizable(False,False)
        delete_account_window.title("Delete account")
        user_window.grab_set()
        delete_account_window.grab_set()
        delete_account_window.configure(bg="#ffffff") 

        def deleted_account(username):
            if check_password_entry.get() != password:
                messagebox.showerror("Error","password isn't match")
            else:
                try:
                    db.execute(f"drop table trades_{username}")
                    db.execute(f"delete from users where username = '{username}'")
                    connection.commit()
                except:
                    connection.rollback()
                    messagebox.showerror("Error","something went wrong while deleting account")
                else:
                    delete_account_window.destroy()
                    user_window.destroy()

        check_password_label = Label(delete_account_window,text='Enter password',bg="#ffffff",font=('Calibri',12))
        check_password_label.place(x=15,y=70)
        check_password_entry = Entry(delete_account_window,width=25,highlightthickness=1,highlightbackground="#0000ff")
        check_password_entry.place(x=125,y=73)  

        delete_account_button = Button(delete_account_window,text='Delete account',bg="#a23620",fg="#ffffff",font=('Calibri',10),command=lambda:deleted_account(username))
        delete_account_button.place(x=100,y=130) 
        user_window.grab_set()
        delete_account_window.grab_set()
        
        t1 = th.Thread(target=lambda: kucoin_(username))



    menubar =Menu(user_window) 
    menubar.add_cascade(label='Withdraw',command=lambda: withdraw_(username))
    menubar.add_cascade(label='Deposit',command=lambda: deposit_(username)) 
    menubar.add_cascade(label='Change EMDD',command=lambda: change_emdd_(username))
    menubar.add_cascade(label='Change Tolerance',command=lambda: change_tolerance_(username))
    menubar.add_cascade(label='Change Password',command=lambda: change_password_(username))
    menubar.add_cascade(label='Refresh',command=lambda: refresh(username)) 
    menubar.add_cascade(label='Reset account',command=lambda: reset_account(username))
    menubar.add_cascade(label='Delete account',command=lambda: delete_account(username))
    menubar.add_cascade(label='Kucoin',command=lambda: kucoin_(username))


    user_window.config(menu = menubar) 
    user_window.configure() 

    edit_trade_button = Button(user_window,text="Edit trade",font=('Calibri',9),command=lambda:edit_trade(username))
    edit_trade_button.place(x=718,y=340)
    delete_trade_button = Button(user_window,text="Delete trade",font=('Calibri',9),command=lambda:delete_trade(username))
    delete_trade_button.place(x=638,y=340)

    trade_columns = ('No','Asset','Vol','Entry','SL','TP','RR','Lev','Close','PNLP','PNL')
    trade_view = ttk.Treeview(user_window, show='headings',columns=trade_columns)  
    trade_view.heading("No", text='No') 
    trade_view.column('No',minwidth=0,width=20)
    trade_view.heading("Asset", text='Asset')
    trade_view.column('Asset',minwidth=0,width=50)
    trade_view.heading("Vol", text='Vol')
    trade_view.column('Vol',minwidth=0,width=50)
    trade_view.heading("Entry", text='Entry')
    trade_view.column('Entry',minwidth=0,width=50)
    trade_view.heading("SL", text='SL')
    trade_view.column('SL',minwidth=0,width=50)
    trade_view.heading("TP", text='TP')
    trade_view.column('TP',minwidth=0,width=50)
    trade_view.heading("RR", text='RR')
    trade_view.column('RR',minwidth=0,width=50)
    trade_view.heading("Lev", text='Lev')
    trade_view.column('Lev',minwidth=0,width=50)
    trade_view.heading("Close", text='Close')
    trade_view.column('Close',minwidth=0,width=50)
    trade_view.heading("PNLP", text='PNLP')
    trade_view.column('PNLP',minwidth=0,width=50)
    trade_view.heading("PNL", text='PNL')
    trade_view.column('PNL',minwidth=0,width=50) 

    trades_bar = Label(user_window,text='Trade bar',width=109,bg="#400c43",fg="#ffffff")
    trades_bar.place(x=15,y=97)

    scroll_frame = LabelFrame(user_window,width=16,height=245,highlightbackground="#400c43")
    scroll_frame.place(x=780,y=97)

    scrollbar = Scrollbar(user_window,orient=VERTICAL,width=13) 
    scrollbar.config(command=trade_view.yview) 
    scrollbar.place(x=781,y=200) 

    trade_view.tag_configure("win", background="#b8f6a9")
    trade_view.tag_configure("loss", background="#f9b1ad")

    for i in range(len(trades)):
        no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl = trades[i]
        if pnl>0: 
            vol = '$' + str(vol)
            entry = '$' + str(entry)
            sl = str(sl*100) + '%'
            tp = str(tp*100) + '%'
            close = '$' + str(close)
            pnlp = str(pnlp*100) + '%'
            if pnl<0:
                pnl = str(pnl)
                pnl = pnl[0] + '$' + pnl[1:]
            else:
                pnl = '$' + str(pnl) 
            trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
            trade_view.insert('',index = -1, value=trade,tags='win') 
        elif pnl<0:
            vol = '$' + str(vol)
            entry = '$' + str(entry)
            sl = str(sl*100) + '%'
            tp = str(tp*100) + '%'
            close = '$' + str(close)
            pnlp = str(pnlp*100) + '%'
            if pnl<0:
                pnl = str(pnl)
                pnl = pnl[0] + '$' + pnl[1:]
            else:
                pnl = '$' + str(pnl) 
            trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
            trade_view.insert('',index = -1, value=trade,tags='loss')
        else:
            vol = '$' + str(vol)
            entry = '$' + str(entry)
            sl = str(sl*100) + '%'
            tp = str(tp*100) + '%'
            close = '$' + str(close)
            pnlp = str(pnlp*100) + '%'
            if pnl<0:
                pnl = str(pnl)
                pnl = pnl[0] + '$' + pnl[1:]
            else:
                pnl = '$' + str(pnl) 
            trade = (no,asset,vol,entry,sl,tp,rr,lev,close,pnlp,pnl)
            trade_view.insert('',index = -1, value=trade)
    
    trade_view.place(x = 15,y = 115,width=770)

    add_trade_frame = LabelFrame(user_window,width=770,height=95,highlightthickness=1,bg="#e8e4e8")
    add_trade_frame.place(x=15,y=375)

    add_trade = Label(user_window,text='Add a trade',width=10,bg="#400c43",fg="#ffffff")
    add_trade.place(x=16,y=355)

    def add_trade_entry_check(event):
        if asset_entry.get()=='':
            asset_entry.configure(highlightbackground="#ff0000") 
        else:
            asset_entry.configure(highlightbackground="#0000ff")
        if vol_entry.get()=='':
            vol_entry.configure(highlightbackground="#ff0000")
        else:
            vol_entry.configure(highlightbackground="#0000ff")
        if entry_entry.get()=='':
            entry_entry.configure(highlightbackground="#ff0000")
        else:
            entry_entry.configure(highlightbackground="#0000ff")
        if sl_entry.get()=='':
            sl_entry.configure(highlightbackground="#ff0000")
            lev_sublabel.configure(text='max: 1')
            tp_sublabel.configure(text='')
        else:
            sl_entry.configure(highlightbackground="#0000ff")
            try:
                db.execute(f"select mrpt from users where username = '{username}'")
                mrpt = db.fetchall()[0][0]
                tp = float(sl_entry.get())*2
                tp_sublabel.configure(text=f'min: {tp}%')
                sl_en = float(sl_entry.get()); sl_en = sl_en/100
                lev = float(mrpt)/sl_en; lev=str(lev); real,frac=lev.split('.'); lev = real + '.' + frac[0:2]
                lev_sublabel.configure(text=f'max: {lev}') 
            except:
                tp_sublabel.configure(text='')
                lev_sublabel.configure(text='max: 1')
        if tp_entry.get()=='':
            tp_entry.configure(highlightbackground="#ff0000")
            rr_entry.delete(0,'end')
            rr_entry.insert(END,0)
        else:
            tp_entry.configure(highlightbackground="#0000ff")
            try:
                rr = float(tp_entry.get())/float(sl_entry.get())
                rr=str(rr); real,frac=rr.split('.'); rr = real + '.' + frac[0:2]
                rr_entry.delete(0,'end')
                rr_entry.insert(END,rr)
            except:
                rr_entry.delete(0,'end')
                rr_entry.insert(END,0)
        if rr_entry.get()=='':
            rr_entry.configure(highlightbackground="#ff0000")
        else:
            rr_entry.configure(highlightbackground="#0000ff")
        if close_entry.get()=='' or close_entry.get()=='0':
            pnlp_entry.delete(0,'end')
            pnl_entry.delete(0,'end')
            pnlp_entry.insert(END,0)
            pnl_entry.insert(END,0) 
        else:
            try:
                pnlp_entry.delete(0,'end')
                pnl_entry.delete(0,'end')
                pnlp = ((float(close_entry.get())-float(entry_entry.get()))/float(entry_entry.get()))*100; pnlp = pnlp*float(lev_entry.get())
                if position_type.get()==2:
                    pnlp *= -1
                pnlp1=str(pnlp); real,frac=pnlp1.split('.'); pnlp1 = real + '.' + frac[0:2]
                pnlp1 = float(pnlp1)
                pnlp_entry.insert(END,pnlp1)
                if vol_entry.get()=='':
                    vol = 0
                else:
                    vol = float(vol_entry.get())
                pnl = vol*(pnlp/100); pnl=str(pnl); real,frac=pnl.split('.'); pnl = real + '.' + frac[0:2]
                pnl_entry.insert(END,pnl) 
            except:
                pnlp_entry.delete(0,'end')
                pnl_entry.delete(0,'end')
                pnlp_entry.insert(END,0)
                pnl_entry.insert(END,0) 

    position_type = IntVar(user_window) 
    position_type.set(1)
    long = Radiobutton(user_window,text="Long",variable = position_type, value=1,fg="#51ae6a",bg='#ffffff',font=('Calibri',9))
    long.place(x=100,y=351)
    short = Radiobutton(user_window,text="Short",variable = position_type, value=2,fg="#c73839",bg='#ffffff',font=('Calibri',9))
    short.place(x=155,y=351) 

    asset_label = Label(user_window,text='Asset',bg="#e8e4e8",font=('Calibri',12)) 
    asset_label.place(x=30,y=390) 
    asset_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    asset_entry.place(x=30,y=420)
    asset_entry.bind("<KeyRelease>",add_trade_entry_check)
    vol_label = Label(user_window,text='Vol',bg="#e8e4e8",font=('Calibri',12))
    vol_label.place(x=100,y=390) 
    vol_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    vol_entry.place(x=100,y=420)
    vol_entry.bind("<KeyRelease>",add_trade_entry_check)
    entry_label = Label(user_window,text='Entry',bg="#e8e4e8",font=('Calibri',12))
    entry_label.place(x=170,y=390) 
    entry_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    entry_entry.place(x=170,y=420)
    entry_entry.bind("<KeyRelease>",add_trade_entry_check)
    sl_label = Label(user_window,text='SL',bg="#e8e4e8",font=('Calibri',12))
    sl_label.place(x=240,y=390) 
    sl_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    sl_entry.place(x=240,y=420)
    sl_entry.bind("<KeyRelease>",add_trade_entry_check)
    tp_label = Label(user_window,text='TP',bg="#e8e4e8",font=('Calibri',12))
    tp_label.place(x=310,y=390) 
    tp_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    tp_entry.place(x=310,y=420)
    tp_entry.bind("<KeyRelease>",add_trade_entry_check)
    rr_label = Label(user_window,text='RR',bg="#e8e4e8",font=('Calibri',12))
    rr_label.place(x=380,y=390) 
    rr_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    rr_entry.place(x=380,y=420)
    rr_entry.bind("<KeyRelease>",add_trade_entry_check)
    lev_label = Label(user_window,text='Lev',bg="#e8e4e8",font=('Calibri',12)) 
    lev_label.place(x=450,y=390) 
    lev_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    lev_entry.place(x=450,y=420)
    close_label = Label(user_window,text='Close',bg="#e8e4e8",font=('Calibri',12))
    close_label.place(x=520,y=390) 
    close_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    close_entry.place(x=520,y=420)
    close_entry.bind("<KeyRelease>",add_trade_entry_check)
    pnlp_label = Label(user_window,text='PNLP',bg="#e8e4e8",font=('Calibri',12))
    pnlp_label.place(x=590,y=390) 
    pnlp_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1)
    pnlp_entry.place(x=590,y=420)
    pnl_label = Label(user_window,text='PNL',bg="#e8e4e8",font=('Calibri',12))
    pnl_label.place(x=660,y=390) 
    pnl_entry = Entry(user_window,width=10,highlightbackground="#0000ff",highlightthickness=1) 
    pnl_entry.place(x=660,y=420)

    lev_entry.insert(END,1) 
    close_entry.insert(END,0)
    pnlp_entry.insert(END,0)
    pnl_entry.insert(END,0)

    mrpt_sublabel = Label(user_window,text=f'MRPT: {mrpt_str}%',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    mrpt_sublabel.place(x=235,y=441)
    asset_ex_label = Label(user_window,text='Ex: EUR/USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    asset_ex_label.place(x=30,y=441)
    vpt_sublabel = Label(user_window,text=f'VPT: ${vpt}',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    vpt_sublabel.place(x=95,y=441)
    tp_sublabel = Label(user_window,text='',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    tp_sublabel.place(x=315,y=441)
    decimal_label1 = Label(user_window,text='min: 2',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    decimal_label1.place(x=380,y=441)
    lev_sublabel = Label(user_window,text=f'max: 1',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    lev_sublabel.place(x=450,y=441) 
    rr_sublabel = Label(user_window,text='%',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    rr_sublabel.place(x=590,y=441)
    pnl_sublabel = Label(user_window,text='USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    pnl_sublabel.place(x=660,y=441)
    entry_sublabel = Label(user_window,text='USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    entry_sublabel.place(x=170,y=441)
    close_sublabel = Label(user_window,text='USD',fg="#6e655f",bg="#e8e4e8",font=('Calibri',8))
    close_sublabel.place(x=520,y=441)

    add_trade_button = Button(user_window,text='Add',bg="#216263",fg="#ffffff",command=lambda:add_trade_(username))
    add_trade_button.place(x=736,y=415) 

    user_window.grab_set()

login_frame = LabelFrame(tk,width=230,height=125,bg="#e0f0fd",highlightbackground="#000000",highlightthickness=1,borderwidth=0)
login_frame.place(x=267,y=100)

def login_switch_():
    user_confirm_button.place(x=360,y=210)
    user_create_button.place(x=1000,y=20)
    create_switch.configure(bg="#e0f0fd",fg="#000000")
    login_switch.configure(bg="#000000",fg="#ffffff")

def create_switch_():
    user_create_button.place(x=357,y=210)
    user_confirm_button.place(x=1000,y=20)
    create_switch.configure(bg="#000000",fg="#ffffff")
    login_switch.configure(bg="#e0f0fd",fg="#000000")

confidential1 = StringVar(tk) 

user_label = Label(tk,text='username',width=10,bg="#e0f0fd")
user_label.place(x=280,y=140)
user_entry = Entry(tk,width=20,highlightthickness=1,highlightbackground="#0000ff") 
user_entry.place(x=350,y=143)
user_entry.bind("<KeyRelease>",entry_check_login)
pass_label = Label(tk,text='password',width=10,bg="#e0f0fd")
pass_label.place(x=280,y=170)
pass_entry = Entry(tk,width=20,highlightthickness=1,highlightbackground="#0000ff",textvariable=confidential1, show = "*")
pass_entry.place(x=350,y=170)
pass_entry.bind("<KeyRelease>",entry_check_login)
user_confirm_button = Button(tk,text="Login",width=5,command= find_account) 
user_confirm_button.place(x=360,y=210)

# create_user_label = Label(tk,text='username',width=10,bg="#e0f0fd")
# create_user_label.place(x=397,y=150)
# create_user_entry = Entry(tk,width=20,highlightthickness=1,highlightbackground="#0000ff") 
# create_user_entry.place(x=467,y=153)
# create_user_entry.bind("<KeyRelease>",entry_check_create)
# create_pass_label = Label(tk,text='password',width=10,bg="#e0f0fd")
# create_pass_label.place(x=397,y=180)
# create_pass_entry = Entry(tk,width=20,highlightthickness=1,highlightbackground="#0000ff")
# create_pass_entry.place(x=467,y=180)
# create_pass_entry.bind("<KeyRelease>",entry_check_create)

user_create_button = Button(tk,text="Sign up",command= create_account) 

login_switch = Button(tk,text='Login',width=8,bg="#000000",fg="#ffffff",font=('Times',15),highlightthickness=1,highlightbackground="#000000",command=login_switch_)
login_switch.place(x=285,y=80)

create_switch = Button(tk,text='Sign up',width=8,bg="#e0f0fd",font=('Times',15),highlightthickness=1,highlightbackground="#000000",command=create_switch_)
create_switch.place(x=380,y=80)

p_label = Label(tk,text='P',bg="#e0f0fd",font=('Times',100))
p_label.place(x=40,y=318)

l_label = Label(tk,text='L',bg="#e0f0fd",font=('Times',100))
l_label.place(x=150,y=318)

a_label = Label(tk,text='A',bg="#e0f0fd",font=('Times',100))
a_label.place(x=290,y=318)

n_label = Label(tk,text='N',bg="#e0f0fd",font=('Times',100))
n_label.place(x=420,y=318)

x_label = Label(tk,text='X',bg="#e0f0fd",font=('Times',100))
x_label.place(x=600,y=318)

tk.mainloop()
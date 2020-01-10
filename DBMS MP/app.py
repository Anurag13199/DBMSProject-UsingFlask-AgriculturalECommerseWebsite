from datetime import datetime
from flask import Blueprint,Flask,request, render_template, redirect, url_for,jsonify,g,session
from flask_mysqldb import MySQL
import os
from os import path
import json
from random import randint
from werkzeug import secure_filename


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'eamp'

mysql = MySQL(app)

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return render_template('index.html')

@app.route('/',methods=['GET','POST'])
def index():
    if 'user' in session:
        name= session['user']
        customer_info = get_cid_info(name)
        return render_template('index.html',name= name,customer_info= customer_info)
    return render_template('index.html')

@app.route('/manage',methods=['GET','POST'])
def manage():
    if 'user' in session:
        name= session['user']
        cur = mysql.connection.cursor()
        hj= cur.execute("SELECT * FROM orders")
        hj = [dict(oid=col[0],cost=col[1],daddress=col[2],cid=col[3],pid=col[4],quantity=col[5],tcost=col[6]) for col in cur.fetchall()]
        rj= cur.execute("SELECT * FROM subap")
        rj = [dict(name=col[0],addr=col[1],ainc=col[2],cid=col[3],email=col[4],adpf=col[5],inpf=col[6]) for col in cur.fetchall()]
        return render_template('manage.html',hj= hj,rj= rj)
    return render_template('index.html')


@app.route('/products',methods=['GET','POST'])
def products():
    if 'user' in session:
        name = session['user']
        cur = mysql.connection.cursor()
        hj= cur.execute("SELECT * FROM product")
        hj = [dict(pid=col[0],pname=col[1],desc=col[2],ncost=col[3],scost=col[4],pimg=col[5]) for col in cur.fetchall()]
        customer_info = get_cid_info(name)
        for i in hj:
            kl = i['desc'].split(';')
            i['description'] = kl
        print(hj)
        return render_template('products.html',hj=hj,name=name,customer_info=customer_info)
    cur = mysql.connection.cursor()
    hj= cur.execute("SELECT * FROM product")
    hj = [dict(pid=col[0],pname=col[1],desc=col[2],ncost=col[3],scost=col[4],pimg=col[5]) for col in cur.fetchall()]
    for i in hj:
        kl = i['desc'].split(';')
        i['description'] = kl
    print(hj)
    return render_template('products.html',hj=hj)

@app.route('/access',methods=['GET','POST'])
def access():
    if 'user' in session:
        name = session['user']
        cid= request.form['cid'];
        sub= request.form['subsidy']
        cur = mysql.connection.cursor()
        print(cid,sub)
        hj=cur.execute("UPDATE customer SET subsidy = (%s) WHERE cid='"+cid+"'",(sub))
        hj=cur.execute("DELETE from subap WHERE cid='"+cid+"'")
        mysql.connection.commit()
        return redirect(url_for('manage'))
    return redirect(url_for('index'))



@app.route('/order_placed',methods=['GET','POST'])
def order_placed():
    if 'user' in session:
        name = session['user']
        pid = request.form['pid']
        cid = request.form['cid']
        cost = request.form['cost']
        quantity = request.form['quantity']
        print(cost)
        customer_info = get_cid_info(cid)
        cost1 = int(cost)
        cur = mysql.connection.cursor()
        hj= cur.execute("INSERT INTO orders(pid,cid,cost,daddress,quantity) values(%s,%s,%s,%s,%s)",(pid,cid,cost1,customer_info[0]['address'],quantity))
        mysql.connection.commit()
        return render_template('osuccess.html')
    return "Not Logged In"

@app.route('/orders',methods=['GET','POST'])
def orders():
    if 'user' in session:
        name = session['user']
        customer_info = get_cid_info(name)
        cur = mysql.connection.cursor()
        orders = cur.execute("SELECT pid,daddress,tcost,oid,cid,quantity FROM orders where cid='"+str(int(name))+"'")
        orders = [dict(pid=col[0],daddress=col[1],cost=col[2],oid=col[3],cid=col[4],quantity=col[5]) for col in cur.fetchall()]
        return render_template('orders.html',name=name,customer_info=customer_info,orders=orders)
    return "Not Logged In"

@app.route('/success',methods=['GET','POST'])
def success():
    if 'user' in session:
        name = session['user']
        customer_info = get_cid_info(name)
        cur = mysql.connection.cursor()
        return render_template('osuccess.html')

@app.route('/pchange',methods=['GET','POST'])
def pchange():
    if 'user' in session:
        name = session['user']
        customer_info = get_cid_info(name)
        cur = mysql.connection.cursor()
        return render_template('pchange.html')

@app.route('/pch',methods=['GET','POST'])
def pch():
    if 'user' in session:
        pas1= request.form['cpd']
        pas2= request.form['npd']
        name = session['user']
        cur = mysql.connection.cursor()
        customer_info = get_cid_info(name)
        if customer_info[0]['password'] == pas1:
            hj=cur.execute("UPDATE customer SET password = (%s) WHERE cid='"+str(int(name))+"'",[pas2])
            mysql.connection.commit()
            return redirect(url_for('account'))
        else:
            return 'Enter Correct Password'


@app.route('/account',methods=['GET','POST'])
def account():
    if 'user' in session:
        name = session['user']
        ci = get_cid_info(name)
        cur = mysql.connection.cursor()
        return render_template('account.html', ci=ci)


@app.route('/sub_ap',methods=['GET','POST'])
def sub_ap():
    if 'user' in session:
        name = session['user']
        email = request.form['email']
        ainc = request.form['ainc']
        image_one = request.files['adpf']
        file_name1 = secure_filename(image_one.filename)
        filename1 = secure_filename(image_one.filename)
        image_one.save(os.path.join('./static/images/',filename1))
        thr1 = '/static/images/'+filename1
        data = [thr1]
        image_one = request.files['income']
        file_name1 = secure_filename(image_one.filename)
        filename1 = secure_filename(image_one.filename)
        image_one.save(os.path.join('./static/images/',filename1))
        thr1 = '/static/images/'+filename1
        data1 = [thr1]
        customer_info = get_cid_info(name)
        cur = mysql.connection.cursor()
        hj= cur.execute("INSERT INTO subap(name,email,addr,ainc,adpf,inpf,cid) values(%s,%s,%s,%s,%s,%s,%s)",(customer_info[0]['nam'],customer_info[0]['email'],customer_info[0]['address'],ainc,data,data1,customer_info[0]['cid']))
        mysql.connection.commit()
        return redirect(url_for('index'))
    return "login to continue"

@app.route('/register_saved',methods=['GET','POST'])
def register_saved():
    namef = request.form['namef']
    email = request.form['email']
    addrf = request.form['addrf']
    # bday = request.form['bday']
    passwd = request.form['passwd']
    phnno = request.form['phnno']
    fg= [passwd,addrf,namef,phnno,email]
    conn = mysql.connection.cursor()
    conn.execute("INSERT INTO customer(password,address,name,phno,email) values(%s,%s,%s,%s,%s)",(passwd,addrf,namef,phnno,email))
    mysql.connection.commit()
    hj= conn.execute("SELECT * FROM customer where email='"+email+"'")
    hj = [dict(cid=col[0]) for col in conn.fetchall()]
    print(hj)
    session['user'] = hj[0]['cid']
    return redirect(url_for('index'))

def get_cid_info(cid):
    conn = mysql.connection.cursor()
    hj= conn.execute("CALL new_procedure('"+str(int(cid))+"') ")
    hj = [dict(cid=col[0],email=col[1],password=col[2],address=col[3],subsidy=col[4],nam=col[5],ph=col[6]) for col in conn.fetchall()]
    print(type(hj[0]['subsidy']))
    return hj

@app.route('/login_add',methods=['GET','POST'])
def login_add():
    email = request.form['email']
    password = request.form['password']
    conn = mysql.connection.cursor()
    hj= conn.execute("SELECT cid,email,password FROM customer where email='"+email+"'")
    hj = [dict(cid=col[0],email=col[1],password=col[2]) for col in conn.fetchall()]
    print(hj)
    if hj:
        if hj[0]['email'] == email and hj[0]['password'] == password:
            session['user'] = hj[0]['cid']
            return redirect(url_for('index'))
        else:
            return "Incorrect Password"
    else:
        return "Username doesn't exist. Register to continue"


@app.route('/mlogadd',methods=['GET','POST'])
def mlogadd():
    email = request.form['log']
    password = request.form['pwd']
    conn = mysql.connection.cursor()
    hj= conn.execute("SELECT uid,passwd,name,addr FROM management where uid='"+email+"'")
    hj = [dict(uid=col[0],passwd=col[1],name=col[2],addr=col[3]) for col in conn.fetchall()]
    print(hj)
    if hj:
        if hj[0]['uid'] == email and hj[0]['passwd'] == password:
            session['user'] = hj[0]['uid']
            return redirect(url_for('manage'))
        else:
            return "Enter Correct Password"
    else:
        return "You are not authorised to access"


@app.route('/apply',methods=['GET','POST'])
def apply():
    if 'user' in session:
        name = session['user']
        cur = mysql.connection.cursor()
        customer_info = get_cid_info(name)
        return render_template('apply.html',customer_info=customer_info)
    return redirect(url_for('index'))

@app.route('/register',methods=['GET','POST'])
def register():
    return render_template('register.html')

@app.route('/mlogin',methods=['GET','POST'])
def mlogin():
    return render_template('mlogin.html')


if __name__ == '__main__':
    app.run(debug=True)

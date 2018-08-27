#!/usr/bin/python 
import sys
# working inside the lib
sys.path.append('..')
import cqparts_bucket
from cqparts_bucket import * 
import cqparts.search as cs
from cqparts.display import display

from flask import Flask, jsonify, abort , render_template

from anytree import Node , RenderTree , NodeMixin
from anytree.search import findall
from anytree.resolver import Resolver

from collections import OrderedDict
app = Flask(__name__)

class thing(NodeMixin):
    def __init__(self,name,parent=None,**kwargs):
        super(thing,self).__init__()
        self.name = name
        self.parent = parent
        self.__dict__.update(kwargs)

    def get_path(self):
        args = "%s" % self.separator.join([""] + [str(node.name) for node in self.path])
        return str(args)

    def info(self):
        val = {'path':self.get_path(),'name':self.name}
        return val 

    def dir(self):
        l = []
        for i in self.children:
            l.append(i.info())
        return l

    def __repr__(self):
        return self.get_path()

class directory():
    def __init__(self,base,name):
        d = cs.index[name]
        self.names = d.keys() #top level
        self.d = d
        self.res = Resolver('name')
        self.k = OrderedDict() 
        self.base = base
        self.root = thing(base)
        self.build()

    def build(self):
        for i in self.d:
            b = thing(i,parent=self.root)
            for k in self.d[i]:
                thing(k.__name__,parent=b,c=k)
                self.k[self.base+'/'+i+'/'+k.__name__] = k

    def children(self,path):
        r = self.res.get(self.root,path)
        print r

    def items(self):
        return self.k.keys()

    def exists(self,key):
        if key in self.k:
            return True
        return False

    def prefix(self,key):
        v = self.res.get(self.root,'/'+key)
        return v.dir()

    def __getitem__(self,key):
        if self.exists(key) == False:
            abort(404)
        l = []
        for i in self.k[key]:
            l.append(i.__name__)
        return l

    def params(self,key):
        if self.exists(key) == False:
            abort(404)
        p = self.k[key]()
        display(p)
        app.logger.error(p)
        d = {}
        pi = p.params().items()
        for i in pi:
            if isinstance(i[1],float):
                d[i[0]] = i[1]
        return d


#d = directory(cqparts_bucket._namespace,'export')
d = directory('root','export')
print(RenderTree(d.root))

@app.route('/')
def base():
    return render_template('list.html',items=d.root.dir())

@app.route('/list')
def list():
    return jsonify(d.items())

@app.route('/list/<path:modelname>')
def subcat(modelname):
    return render_template('list.html',items=d.prefix(modelname))

@app.route('/params/<path:modelname>')
def show_model(modelname):
    app.logger.error(modelname)
    ob = d.params(modelname)
    return jsonify(ob)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8089)

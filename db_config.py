from models import db, mdb, Function, Semantic
import random

"""Настрока таблиц для баз данных и заполнение тестовой информацией для демонстрации
"""

db.drop_all()
db.create_all()
mdb.drop_all()
mdb.create_all()

functions_and_semantics = [
    ['cx_OracleTools', 'Python'],
    ['Quota Monitor', 'Python', 'GTK+'],
    ['PyS60', 'Python'],
    ['FreeCAD', 'Python', 'Qt'],
    ['QGoogleTranslate', 'Qt'],
    ['gscan2pdf', 'GTK+', 'Perl'],
    ['K-3D', 'GTK+'],
    ['Moonshiner', 'GTK+', 'Python'],
    ['PyJudo', 'Python', 'wxWidgets'],
    ['OpenCollab', 'wxWidgets'],
    ['Christine Media Player', 'GTK+', 'Python'],
    ['rover', 'GTK+', 'Perl'],
    ['PyDingo', 'Python', 'Qt'],
    ['Crumena', 'Python', 'wxWidgets'],
    ['wxMathPlot', 'wxWidgets'],
    ['QuteCsound', 'Qt'],
    ['Crow Designer', 'GTK+'],
    ['Zero Install', 'GTK+', 'Python'],
    ['Yabause', 'GTK+', 'Qt'],
    ['Kephra', 'Perl', 'wxWidgets'],
    ['gxconsole', 'GTK+'],
    ['gmusicbrowser', 'GTK+', 'Perl'],
    ['CarDriving2D', 'Java'],
    ['Frinika', 'Java'],
    ['Talend Open Studio', 'Java', 'Perl'],
    ['System and Network Monitor', 'Perl'],
    ['boost_graph', 'Boost', 'Python'],
    ['POCO C++ Libraries', 'Boost'],
    ['Skip xml iarchive', 'Boost'],
    ['C++ Python language bindings', 'Boost', 'Python'],
    ['ACE Chat Server', 'ACE'],
    ['Online Transaction Processing Platform', 'ACE'],
    ['Tcl/Tk vector drawing library', 'Tcl/Tk'],
    ['CrowTDE', 'Tcl/Tk'],
    ['MyJSQLView', 'Java']
]

random.shuffle(functions_and_semantics)
i = 1
for q in functions_and_semantics:
    r1 = Function.query.filter_by(name=q[1]).first()
    if len(q)==3:
        r2 = Function.query.filter_by(name=q[2]).first()
        if r1 is None and r2 is None:
            aa = Function(name=q[1])
            aaa = Function(name=q[2])
            qq = Semantic(semantic=q[0])
            db.session.add(qq)
            db.session.add(aaa)
            db.session.add(aa)
            db.session.commit()
            qq.functions.append(aa)
            db.session.add(qq)
            db.session.commit()
            qq.functions.append(aaa)
            db.session.add(qq)
            db.session.commit()
        elif r1 is not None and r2 is None:
            aaa = Function(name=q[2])
            qq = Semantic(semantic=q[0])
            db.session.add(aaa)
            db.session.add(qq)
            db.session.commit()
            qq.functions.append(r1)
            db.session.add(qq)
            db.session.commit()
            qq.functions.append(aaa)
            db.session.add(qq)
            db.session.commit()
        elif r1 is None and r2 is not None:
            aa = Function(name=q[1])
            qq = Semantic(semantic=q[0])
            db.session.add(aa)
            db.session.add(qq)
            db.session.commit()
            qq.functions.append(aa)
            db.session.add(qq)
            db.session.commit()
            qq.functions.append(r2)
            db.session.add(qq)
            db.session.commit()
        else:
            qq = Semantic(semantic=q[0])
            db.session.add(qq)
            db.session.commit()
            qq.functions.append(r1)
            db.session.add(qq)
            db.session.commit()
            qq.functions.append(r2)
            db.session.add(qq)
            db.session.commit()
    else:
        if r1 is None:
            aa = Function(name=q[1])
            qq = Semantic(semantic=q[0])
            db.session.add(qq)
            db.session.add(aa)
            db.session.commit()
            qq.functions.append(aa)
            db.session.add(qq)
            db.session.commit()
        else:
            qq = Semantic(semantic=q[0])
            db.session.add(qq)
            qq.functions.append(r1)
            db.session.add(qq)
            db.session.commit()

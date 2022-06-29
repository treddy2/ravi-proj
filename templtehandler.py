from flask import render_template, session


class templtehandler():
    def er_user_templ(self):
        return render_template("error.html",
                               sign_user=session['user_name'], conf="nav-link disabled",
                               conf_link="nav-link",
                               login=session['login'], dropdown_toggle="dropdown-toggle"
                               )

    def er_admin_templ(self):
        return render_template("error.html", sign_user=session['user_name'], conf="nav-link",
                               login=session['login'],
                               dropdown_toggle="dropdown-toggle"
                               )



tempInst = templtehandler()


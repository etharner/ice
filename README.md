# ice
## Installation

```sh
$ git clone https://github.com/etharner/ice.git
```

You have to install Python 3.4+.

Required Python modules:
- Django 1.8+
- numpy
- scipy
- matplotlib
- lxml

Also install any server you want (for example, Apache or nginx).

You must include path to WSGI (www/wsgi.py) in server's sites configuration.

## Apache2 example (/var/www/ice - project folder)
```
WSGIPythonPath /var/www/ice
<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com

        Alias /static/ /var/www/ice/static/

        <Directory /var/www/ice/static>
                Require all granted
        </Directory>

        WSGIScriptAlias / /var/www/ice/www/wsgi.py

        <Directory /var/www/ice/www>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>
```
## Dont forget to run ./manage.py collectstatic!

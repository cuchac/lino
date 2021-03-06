Configure Apache for HTTP authentication
========================================

See also :doc:`/topics/auth`

Here is how I configured Apache using basic HTTP authentication 
for the demo sites. 
In a production site you'll probably use more secure 
authentication methods.
My source was http://httpd.apache.org/docs/2.0/howto/auth.html.

Create a local directory for the flatfile user database::

  # mkdir /usr/local/django/myproject/htpasswd

Create a first user::

  # htpasswd -c /usr/local/django/myproject/htpasswd/passwords root

Create more users::

  # htpasswd /usr/local/django/myproject/htpasswd/passwords user


Create a groups file :file:`nano/usr/local/django/myproject/htpasswd/groups` with the following content::

  lino: root user

Then, in your Apache config file (:file:`/etc/apache2/sites-available/default`)::

  <Directory />
    AuthType Basic
    AuthName "Lino demo"
    AuthUserFile /usr/local/django/myproject/htpasswd/passwords
    AuthGroupFile /usr/local/django/myproject/htpasswd/groups
    Require group lino
    AllowOverride None 
  </Directory>



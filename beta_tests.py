import gettext

# Set the locale directory and the domain name (the name of your .mo files)
locale_dir = 'locales'
domain = 'VidFetch_Discord_Bot'
gettext.bindtextdomain(domain, locale_dir)
gettext.textdomain(domain)

# Use the _ function as an alias for gettext.gettext
_ = gettext.gettext

# Set the desired language, e.g., based on user settings or system settings
language = 'de'  # German
gettext.translation(domain, locale_dir, languages="en").install()
# Now you can use the _ function to translate strings in your program
print(_('help'))
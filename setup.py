# coding: utf-8
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='vertexertex',
    version='0.1',
    description='',
    author='',
    author_email='',
    #url='',
    install_requires=[
        "TurboGears2 >= 2.0b7",
        "Babel >=0.9.4",
        #can be removed iif use_toscawidgets = False
        "ToscaWidgets >= 0.9.1",        
                ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'vertexertex': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'vertexertex': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = vertex

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)

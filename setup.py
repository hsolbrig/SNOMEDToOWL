
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# typing library was introduced as a core module in version 3.5.0
requires = ["dirlistproc", "jsonasobj", "rdflib"]
if sys.version_info < (3, 5):
    requires.append("typing")

setup(
    name='SNOMEDToOWL',
    version='0.0.3',
    packages=['SNOMEDCTToOWL', 'SNOMEDCTToOWL.RF2Files'],
    url='http://github.com/hsolbrig/SNOMEDToOWL',
    license='Apache License 2.0',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='"Spackman OWL" transformation test and validation tool',
    long_description='Document and test SNOMED RF2 to OWL transformations',
    install_requires=requires,
    scripts=['scripts/RF2Filter', 'scripts/SNOMEDToOWL'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only']
)

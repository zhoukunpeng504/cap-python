#coding:utf-8
# write  by  zhou
from setuptools import  setup,find_packages
setup(
    name="cap-python",
    packages=list(set(list(find_packages())+["twisted.plugins"])),
    version='0.0.1',
    install_requires=["setuptools",
                      "MySQL-python",
                      "twisted==15.3.0",
                      "txscheduling",
                      "psutil",
                      "django==1.4.22"],
    include_package_data=True
)
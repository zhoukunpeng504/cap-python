#coding:utf-8
# write  by  zhou
from setuptools import  setup,find_packages
setup(
    name="cap-python",
    packages=list(set(list(find_packages())+["twisted.plugins"])),
    version='0.1.15',
    install_requires=["setuptools",
                      "MySQL-python",
                      "twisted==15.3.0",
                      "txscheduling",
                      "psutil",
                      "django==1.4.22",
                      'netifaces',
                      'PyCrypto==2.6',
                      'cloudpickle',
                      "gittle==0.5.0",
                      "pyquery"],
    include_package_data=True,
    url="https://github.com/zhoukunpeng504/cap-python",
    author='zhoukunpeng',
    author_email="18749679769@163.com",
    entry_points={
          'console_scripts': ['cap-all-start = cap.sbin.all_start:main',
                              'cap-all-stop = cap.sbin.all_stop:main',
                              'cap-worker-start = cap.sbin.worker_start:main',
                              'cap-worker-stop = cap.sbin.worker_stop:main']
    }
)

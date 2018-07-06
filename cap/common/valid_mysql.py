#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/11.
# ---------------------------------
from warnings import filterwarnings
import MySQLdb
filterwarnings('ignore', category = MySQLdb.Warning)
import  MySQLdb
# create  table sql list
create_table_sql_list=[
            '''CREATE TABLE  if not EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE  if not EXISTS  `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE if not EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_e4470c6e` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_728de91f` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8; ''',

    '''CREATE TABLE if not EXISTS `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_bda51c3c` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `group_id_refs_id_3cea63fe` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_a7792de1` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;''',



'''CREATE TABLE if not EXISTS `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;''',

'''CREATE TABLE if not EXISTS  `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_fbfc09f1` (`user_id`),
  KEY `auth_user_groups_bda51c3c` (`group_id`),
  CONSTRAINT `group_id_refs_id_f0ee9890` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_831107f1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE if not EXISTS `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_fbfc09f1` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_67e79cb` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_f2045483` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE  if not EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_fbfc09f1` (`user_id`),
  KEY `django_admin_log_e4470c6e` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_288599e6` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c8665aa` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;''',



    '''CREATE TABLE if not EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_c25c2c28` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;''',

    '''CREATE TABLE if not EXISTS  `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;''',
    '''CREATE TABLE  if not exists  `cap_crontask` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `addtime` int(11) NOT NULL,
  `uptime` int(11) NOT NULL DEFAULT '0',
  `rule` varchar(50) NOT NULL,
  `status` int(11) NOT NULL,
  `repo_id` int(10) unsigned NOT NULL,
  `version` varchar(50) NOT NULL DEFAULT '',
  `pre_build` varchar(200) NOT NULL,
  `info` varchar(300) NOT NULL,
  `owner` varchar(300) NOT NULL,
  `run_cmd` varchar(500) NOT NULL,
  `run_times` int(10) unsigned NOT NULL,
  `worker_id` int(10) unsigned NOT NULL DEFAULT '0',
  `group_id` int(11) unsigned NOT NULL DEFAULT '0',
  `runlog_rid` int(11) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`tid`),
  KEY `cap_crontask_52094d6e` (`name`),
  KEY `cap_crontask_c9ad71dd` (`status`),
  KEY `cap_crontask_4741fd1b` (`owner`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8''',
    '''CREATE TABLE  if not exists  `cap_deamontask` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `addtime` int(11) NOT NULL,
  `uptime` int(11) NOT NULL DEFAULT '0',
  `status` int(11) NOT NULL,
  `version` varchar(50) NOT NULL DEFAULT '',
  `pre_build` varchar(200) NOT NULL,
  `info` varchar(300) NOT NULL,
  `owner` varchar(300) NOT NULL,
  `run_cmd` varchar(500) NOT NULL,
  `run_times` int(10) unsigned NOT NULL,
  `repo_id` int(10) unsigned NOT NULL DEFAULT '0',
  `worker_id` int(11) unsigned NOT NULL DEFAULT '0',
  `group_id` int(11) unsigned NOT NULL DEFAULT '0',
  `runlog_rid` int(11) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`tid`),
  KEY `cap_deamontask_52094d6e` (`name`),
  KEY `cap_deamontask_4741fd1b` (`owner`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8''',
    '''CREATE TABLE if not exists  `cap_group` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL DEFAULT '',
  `addtime` int(11) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8''',
    '''CREATE TABLE if not exists  `cap_repo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(10) unsigned NOT NULL,
  `repo_url` varchar(200) NOT NULL,
  `user` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `addtime` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `repo_url` (`repo_url`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8''',
'''CREATE TABLE  if not exists  `cap_runlog` (
  `rid` int(11) NOT NULL AUTO_INCREMENT,
  `tid` int(11) NOT NULL,
  `type` varchar(30) NOT NULL,
  `repo_url` varchar(100) NOT NULL,
  `version` varchar(100) NOT NULL,
  `addtime` int(11) NOT NULL,
  `begintime` int(11) NOT NULL,
  `endtime` int(11) NOT NULL DEFAULT '0',
  `status` int(11) NOT NULL,
  `stderror` longtext NOT NULL,
  `stdout` longtext NOT NULL,
  PRIMARY KEY (`rid`),
  KEY `cap_runlog_e03e823b` (`tid`),
  KEY `cap_runlog_f0bd6439` (`type`),
  KEY `cap_runlog_52094d6fd` (`addtime`)
) ENGINE=InnoDB AUTO_INCREMENT=51962 DEFAULT CHARSET=utf8''',
    '''CREATE TABLE if not exists  `cap_worker` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(100) NOT NULL,
  `addtime` int(10) unsigned NOT NULL,
  `heartbeat` int(11) unsigned NOT NULL DEFAULT '0',
  `work_dir` varchar(50) NOT NULL DEFAULT '',
  `total_cpu` int(4) unsigned NOT NULL DEFAULT '0',
  `total_mem` int(10) unsigned NOT NULL DEFAULT '0',
  `platform` varchar(300) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8''',
'''CREATE TABLE if not exists `cap_worker_cpumem_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `addtime` int(11) unsigned NOT NULL DEFAULT '0',
  `work_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cpu_percent` int(5) unsigned NOT NULL DEFAULT '0',
  `mem_percent` int(5) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `cap_worker_cpumen_log_work_id_index` (`work_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19300 DEFAULT CHARSET=utf8''',
    '''CREATE TABLE if not exists `pub_log` (
  `pubid` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(10) unsigned NOT NULL,
  `target_type` varchar(20) NOT NULL,
  `addtime` int(10) unsigned NOT NULL,
  `finishtime` int(10) unsigned NOT NULL,
  `stdout` longtext NOT NULL,
  `stderr` longtext NOT NULL,
  `state` int(10) unsigned NOT NULL,
  PRIMARY KEY (`pubid`)
) ENGINE=InnoDB AUTO_INCREMENT=187 DEFAULT CHARSET=utf8''',
'''INSERT ignore INTO django_content_type (id, name, app_label, model) VALUES 
        (1, 'permission', 'auth', 'permission'),
         (2, 'group', 'auth', 'group'),
         (3, 'user', 'auth', 'user'),
        (4, 'content type', 'contenttypes', 'contenttype'),
        (5, 'session', 'sessions', 'session'),
         (6, 'site', 'sites', 'site'),
         (7, 'log entry', 'admin', 'logentry'),
         (8, 'worker', 'cap', 'worker'),
         (9, 'repo', 'cap', 'repo'),
         (10, 'pub log', 'cap', 'publog'),
         (11, '计划任务', 'cap', 'crontask'),
         (12, '计划任务', 'cap', 'deamontask'),
         (13, '运行日志', 'cap', 'runlog');''',
            '''INSERT ignore  INTO auth_permission (id, name, content_type_id, codename) VALUES
   (1, 'Can add permission', 1, 'add_permission')  ,
   (2, 'Can change permission', 1, 'change_permission')  ,
   (3, 'Can delete permission', 1, 'delete_permission')  ,
   (4, 'Can add group', 2, 'add_group')  ,
   (5, 'Can change group', 2, 'change_group')  ,
   (6, 'Can delete group', 2, 'delete_group')  ,
   (7, 'Can add user', 3, 'add_user')  ,
   (8, 'Can change user', 3, 'change_user')  ,
   (9, 'Can delete user', 3, 'delete_user')  ,
   (10, 'Can add content type', 4, 'add_contenttype')  ,
   (11, 'Can change content type', 4, 'change_contenttype')  ,
   (12, 'Can delete content type', 4, 'delete_contenttype')  ,
   (13, 'Can add session', 5, 'add_session')  ,
   (14, 'Can change session', 5, 'change_session')  ,
   (15, 'Can delete session', 5, 'delete_session')  ,
   (16, 'Can add site', 6, 'add_site')  ,
   (17, 'Can change site', 6, 'change_site')  ,
   (18, 'Can delete site', 6, 'delete_site')  ,
   (19, 'Can add log entry', 7, 'add_logentry')  ,
   (20, 'Can change log entry', 7, 'change_logentry')  ,
   (21, 'Can delete log entry', 7, 'delete_logentry')  ,
   (22, 'Can add worker', 8, 'add_worker')  ,
   (23, 'Can change worker', 8, 'change_worker')  ,
   (24, 'Can delete worker', 8, 'delete_worker')  ,
   (25, 'Can add repo', 9, 'add_repo')  ,
   (26, 'Can change repo', 9, 'change_repo')  ,
   (27, 'Can delete repo', 9, 'delete_repo')  ,
   (28, 'Can add pub log', 10, 'add_publog')  ,
   (29, 'Can change pub log', 10, 'change_publog')  ,
   (30, 'Can delete pub log', 10, 'delete_publog')  ,
   (31, 'Can add 计划任务', 11, 'add_crontask')  ,
   (32, 'Can change 计划任务', 11, 'change_crontask')  ,
   (33, 'Can delete 计划任务', 11, 'delete_crontask')  ,
   (34, 'Can add 计划任务', 12, 'add_deamontask')  ,
   (35, 'Can change 计划任务', 12, 'change_deamontask')  ,
   (36, 'Can delete 计划任务', 12, 'delete_deamontask')  ,
   (37, 'Can add 运行日志', 13, 'add_runlog')  ,
   (38, 'Can change 运行日志', 13, 'change_runlog')  ,
   (39, 'Can delete 运行日志', 13, 'delete_runlog');''',
    '''insert ignore into django_site values(1,"example.com","example.com");''',

    '''
    INSERT ignore  INTO auth_user (id, username, first_name, last_name, email, password, is_staff,
     is_active, is_superuser, last_login, date_joined) VALUES (
     1, 'admin', '', '', '18749679769@163.com', 
     'pbkdf2_sha256$10000$1X58MsOvjyOa$/S7paomFlNanSgEyuwG0QqaFlOVf97DepE0O5eD3YQo=', 
     1, 1, 1, '2018-06-05 15:39:13', '2018-06-05 15:39:13');''',


    '''INSERT ignore INTO cap_group (id, name, addtime) VALUES (1, '默认', 1528706232);''',

    '''INSERT ignore INTO django_site (id, domain, name) VALUES (1, 'example.com', 'example.com');'''
]

def valid(host,port,db,user,passwd):
    for i in create_table_sql_list:
        conn = MySQLdb.connect(host=host, port=port, user=user, db=db, passwd=passwd, charset="utf8")
        cursor = conn.cursor()
        try:
            cursor.execute(i)
        except Exception as e :
            print "异常：" ,str(e)
            return False
        cursor.close()
        conn.commit()
        conn.close()
    return True

if __name__ == '__main__':
    print valid("192.168.14.90",3306,"cap","spider","123456")

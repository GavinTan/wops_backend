/*
SQLyog Ultimate v13.1.1 (64 bit)
MySQL - 8.0.17 : Database - wops1
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`wops1` /*!40100 DEFAULT CHARACTER SET utf8 */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `wops1`;

/*Table structure for table `assets_asset` */

DROP TABLE IF EXISTS `assets_asset`;

CREATE TABLE `assets_asset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL,
  `ip` varchar(120) DEFAULT NULL,
  `desc` longtext,
  `update_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `tree_node_id` int(11) NOT NULL,
  `proxy_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_asset_tree_node_id_2d4a5ad6_fk_assets_treenodes_id` (`tree_node_id`),
  KEY `assets_asset_proxy_id_d6813e15_fk_assets_proxy_id` (`proxy_id`),
  CONSTRAINT `assets_asset_proxy_id_d6813e15_fk_assets_proxy_id` FOREIGN KEY (`proxy_id`) REFERENCES `assets_proxy` (`id`),
  CONSTRAINT `assets_asset_tree_node_id_2d4a5ad6_fk_assets_treenodes_id` FOREIGN KEY (`tree_node_id`) REFERENCES `assets_treenodes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

/*Data for the table `assets_asset` */

insert  into `assets_asset`(`id`,`name`,`ip`,`desc`,`update_time`,`create_time`,`tree_node_id`,`proxy_id`) values 
(5,'aa','172.16.7.15','很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的很长的','2021-08-13 06:25:34.311890','2021-08-12 10:02:40.779650',42,2),
(6,'aa','23.45.61.92','111','2021-08-13 07:05:46.691978','2021-08-13 06:53:23.513962',25,2),
(7,'g1','180.76.76.76',NULL,'2021-08-17 02:39:21.639059','2021-08-17 02:39:21.639090',25,3);

/*Table structure for table `assets_proxy` */

DROP TABLE IF EXISTS `assets_proxy`;

CREATE TABLE `assets_proxy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(120) NOT NULL,
  `account` json DEFAULT NULL,
  `desc` longtext,
  `update_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `platform_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assets_proxy_ip_7221c04d` (`ip`),
  KEY `assets_proxy_platform_id_1e34ed3b_fk_assets_proxyplatform_id` (`platform_id`),
  CONSTRAINT `assets_proxy_platform_id_1e34ed3b_fk_assets_proxyplatform_id` FOREIGN KEY (`platform_id`) REFERENCES `assets_proxyplatform` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

/*Data for the table `assets_proxy` */

insert  into `assets_proxy`(`id`,`ip`,`account`,`desc`,`update_time`,`create_time`,`platform_id`) values 
(2,'172.16.7.14','[{\"password\": \"321456\", \"username\": \"user01\"}]',NULL,'2021-08-12 09:24:09.907147','2021-08-12 09:24:09.907186',16),
(3,'111.111.11.1','[{\"password\": \"32434\", \"username\": \"11\"}]',NULL,'2021-08-17 02:39:12.693798','2021-08-17 02:39:12.693821',17);

/*Table structure for table `assets_proxyplatform` */

DROP TABLE IF EXISTS `assets_proxyplatform`;

CREATE TABLE `assets_proxyplatform` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account` json DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `desc` longtext,
  `update_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `name` varchar(120) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

/*Data for the table `assets_proxyplatform` */

insert  into `assets_proxyplatform`(`id`,`account`,`address`,`desc`,`update_time`,`create_time`,`name`) values 
(17,'[{\"password\": \"123\", \"username\": \"aa\"}]','http://qq.com',NULL,'2021-08-17 02:38:52.598488','2021-08-17 02:38:52.598519','测试11');

/*Table structure for table `assets_treenodes` */

DROP TABLE IF EXISTS `assets_treenodes`;

CREATE TABLE `assets_treenodes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(120) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `parent` varchar(60) NOT NULL,
  `key` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `assets_treenodes_key_1e033554_uniq` (`key`),
  KEY `assets_treenodes_name_97f96577` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;

/*Data for the table `assets_treenodes` */

insert  into `assets_treenodes`(`id`,`title`,`update_time`,`create_time`,`parent`,`key`) values 
(25,'Default1','2021-08-10 08:10:33.036880','2021-08-10 06:30:03.738362','0','0-0'),
(42,'bbb1','2021-08-10 08:10:25.165087','2021-08-10 06:48:08.325490','0-0','0-0-0');

/*Table structure for table `auth_group` */

DROP TABLE IF EXISTS `auth_group`;

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `auth_group` */

/*Table structure for table `auth_group_permissions` */

DROP TABLE IF EXISTS `auth_group_permissions`;

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `auth_group_permissions` */

/*Table structure for table `auth_permission` */

DROP TABLE IF EXISTS `auth_permission`;

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8;

/*Data for the table `auth_permission` */

insert  into `auth_permission`(`id`,`name`,`content_type_id`,`codename`) values 
(1,'Can add permission',1,'add_permission'),
(2,'Can change permission',1,'change_permission'),
(3,'Can delete permission',1,'delete_permission'),
(4,'Can view permission',1,'view_permission'),
(5,'Can add group',2,'add_group'),
(6,'Can change group',2,'change_group'),
(7,'Can delete group',2,'delete_group'),
(8,'Can view group',2,'view_group'),
(9,'Can add content type',3,'add_contenttype'),
(10,'Can change content type',3,'change_contenttype'),
(11,'Can delete content type',3,'delete_contenttype'),
(12,'Can view content type',3,'view_contenttype'),
(13,'Can add session',4,'add_session'),
(14,'Can change session',4,'change_session'),
(15,'Can delete session',4,'delete_session'),
(16,'Can view session',4,'view_session'),
(17,'Can add KVM宿主机',5,'add_nodes'),
(18,'Can change KVM宿主机',5,'change_nodes'),
(19,'Can delete KVM宿主机',5,'delete_nodes'),
(20,'Can view KVM宿主机',5,'view_nodes'),
(21,'Can add 虚拟机',6,'add_domains'),
(22,'Can change 虚拟机',6,'change_domains'),
(23,'Can delete 虚拟机',6,'delete_domains'),
(24,'Can view 虚拟机',6,'view_domains'),
(25,'Can add 用户列表',7,'add_user'),
(26,'Can change 用户列表',7,'change_user'),
(27,'Can delete 用户列表',7,'delete_user'),
(28,'Can view 用户列表',7,'view_user'),
(29,'Can add log entry',8,'add_logentry'),
(30,'Can change log entry',8,'change_logentry'),
(31,'Can delete log entry',8,'delete_logentry'),
(32,'Can view log entry',8,'view_logentry'),
(33,'Can add crontab',9,'add_crontabschedule'),
(34,'Can change crontab',9,'change_crontabschedule'),
(35,'Can delete crontab',9,'delete_crontabschedule'),
(36,'Can view crontab',9,'view_crontabschedule'),
(37,'Can add interval',10,'add_intervalschedule'),
(38,'Can change interval',10,'change_intervalschedule'),
(39,'Can delete interval',10,'delete_intervalschedule'),
(40,'Can view interval',10,'view_intervalschedule'),
(41,'Can add periodic task',11,'add_periodictask'),
(42,'Can change periodic task',11,'change_periodictask'),
(43,'Can delete periodic task',11,'delete_periodictask'),
(44,'Can view periodic task',11,'view_periodictask'),
(45,'Can add periodic tasks',12,'add_periodictasks'),
(46,'Can change periodic tasks',12,'change_periodictasks'),
(47,'Can delete periodic tasks',12,'delete_periodictasks'),
(48,'Can view periodic tasks',12,'view_periodictasks'),
(49,'Can add solar event',13,'add_solarschedule'),
(50,'Can change solar event',13,'change_solarschedule'),
(51,'Can delete solar event',13,'delete_solarschedule'),
(52,'Can view solar event',13,'view_solarschedule'),
(53,'Can add clocked',14,'add_clockedschedule'),
(54,'Can change clocked',14,'change_clockedschedule'),
(55,'Can delete clocked',14,'delete_clockedschedule'),
(56,'Can view clocked',14,'view_clockedschedule'),
(57,'Can add KVM宿主机',15,'add_treenodes'),
(58,'Can change KVM宿主机',15,'change_treenodes'),
(59,'Can delete KVM宿主机',15,'delete_treenodes'),
(60,'Can view KVM宿主机',15,'view_treenodes'),
(61,'Can add 资产',16,'add_asset'),
(62,'Can change 资产',16,'change_asset'),
(63,'Can delete 资产',16,'delete_asset'),
(64,'Can view 资产',16,'view_asset'),
(65,'Can add 代理',17,'add_proxy'),
(66,'Can change 代理',17,'change_proxy'),
(67,'Can delete 代理',17,'delete_proxy'),
(68,'Can view 代理',17,'view_proxy'),
(69,'Can add 代理平台',18,'add_proxyplatform'),
(70,'Can change 代理平台',18,'change_proxyplatform'),
(71,'Can delete 代理平台',18,'delete_proxyplatform'),
(72,'Can view 代理平台',18,'view_proxyplatform'),
(73,'Can add 虚拟机',6,'add_vminstance'),
(74,'Can change 虚拟机',6,'change_vminstance'),
(75,'Can delete 虚拟机',6,'delete_vminstance'),
(76,'Can view 虚拟机',6,'view_vminstance'),
(77,'Can add KVM宿主机',5,'add_vmserver'),
(78,'Can change KVM宿主机',5,'change_vmserver'),
(79,'Can delete KVM宿主机',5,'delete_vmserver'),
(80,'Can view KVM宿主机',5,'view_vmserver');

/*Table structure for table `auth_user` */

DROP TABLE IF EXISTS `auth_user`;

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `name` varchar(20) NOT NULL,
  `phone` varchar(11) NOT NULL,
  `address` varchar(200) NOT NULL,
  `role` json NOT NULL,
  `avatar` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

/*Data for the table `auth_user` */

insert  into `auth_user`(`id`,`password`,`last_login`,`is_superuser`,`username`,`first_name`,`last_name`,`email`,`is_staff`,`is_active`,`date_joined`,`name`,`phone`,`address`,`role`,`avatar`) values 
(1,'pbkdf2_sha256$260000$Xtb8XXLgiVk5Tp761Q6Hjg$CszS9aIQYM0lWiszLWa9G+XtQ5IDzI1eXi1kL4uoldg=','2022-11-02 03:27:07.069535',1,'admin','','','',1,1,'2021-06-11 08:14:13.158231','admin','','','[]','https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png');

/*Table structure for table `auth_user_groups` */

DROP TABLE IF EXISTS `auth_user_groups`;

CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `auth_user_groups` */

/*Table structure for table `auth_user_user_permissions` */

DROP TABLE IF EXISTS `auth_user_user_permissions`;

CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `auth_user_user_permissions` */

/*Table structure for table `django_admin_log` */

DROP TABLE IF EXISTS `django_admin_log`;

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `django_admin_log` */

/*Table structure for table `django_celery_beat_clockedschedule` */

DROP TABLE IF EXISTS `django_celery_beat_clockedschedule`;

CREATE TABLE `django_celery_beat_clockedschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `clocked_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `django_celery_beat_clockedschedule` */

/*Table structure for table `django_content_type` */

DROP TABLE IF EXISTS `django_content_type`;

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

/*Data for the table `django_content_type` */

insert  into `django_content_type`(`id`,`app_label`,`model`) values 
(8,'admin','logentry'),
(16,'assets','asset'),
(17,'assets','proxy'),
(18,'assets','proxyplatform'),
(15,'assets','treenodes'),
(2,'auth','group'),
(1,'auth','permission'),
(3,'contenttypes','contenttype'),
(14,'django_celery_beat','clockedschedule'),
(9,'django_celery_beat','crontabschedule'),
(10,'django_celery_beat','intervalschedule'),
(11,'django_celery_beat','periodictask'),
(12,'django_celery_beat','periodictasks'),
(13,'django_celery_beat','solarschedule'),
(6,'kvm','vminstance'),
(5,'kvm','vmserver'),
(4,'sessions','session'),
(7,'user','user');

/*Table structure for table `django_migrations` */

DROP TABLE IF EXISTS `django_migrations`;

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8;

/*Data for the table `django_migrations` */

insert  into `django_migrations`(`id`,`app`,`name`,`applied`) values 
(1,'contenttypes','0001_initial','2021-06-11 08:05:42.404112'),
(2,'contenttypes','0002_remove_content_type_name','2021-06-11 08:05:43.563271'),
(3,'auth','0001_initial','2021-06-11 08:05:44.658472'),
(4,'auth','0002_alter_permission_name_max_length','2021-06-11 08:05:51.440546'),
(5,'auth','0003_alter_user_email_max_length','2021-06-11 08:05:51.509946'),
(6,'auth','0004_alter_user_username_opts','2021-06-11 08:05:51.547720'),
(7,'auth','0005_alter_user_last_login_null','2021-06-11 08:05:51.595019'),
(8,'auth','0006_require_contenttypes_0002','2021-06-11 08:05:51.641541'),
(9,'auth','0007_alter_validators_add_error_messages','2021-06-11 08:05:51.693171'),
(10,'auth','0008_alter_user_username_max_length','2021-06-11 08:05:51.734374'),
(11,'auth','0009_alter_user_last_name_max_length','2021-06-11 08:05:51.777663'),
(12,'auth','0010_alter_group_name_max_length','2021-06-11 08:05:52.703117'),
(13,'auth','0011_update_proxy_permissions','2021-06-11 08:05:52.760318'),
(14,'auth','0012_alter_user_first_name_max_length','2021-06-11 08:05:52.818905'),
(15,'kvm','0001_initial','2021-06-11 08:05:53.722290'),
(16,'sessions','0001_initial','2021-06-11 08:05:57.039651'),
(17,'user','0001_initial','2021-06-11 08:05:59.109799'),
(18,'admin','0001_initial','2021-07-21 06:49:05.171718'),
(19,'admin','0002_logentry_remove_auto_add','2021-07-21 06:49:07.821138'),
(20,'admin','0003_logentry_add_action_flag_choices','2021-07-21 06:49:07.909218'),
(21,'django_celery_beat','0001_initial','2021-07-21 09:15:17.072109'),
(22,'django_celery_beat','0002_auto_20161118_0346','2021-07-21 09:15:21.175209'),
(23,'django_celery_beat','0003_auto_20161209_0049','2021-07-21 09:15:22.906372'),
(24,'django_celery_beat','0004_auto_20170221_0000','2021-07-21 09:15:23.038331'),
(25,'django_celery_beat','0005_add_solarschedule_events_choices','2021-07-21 09:15:23.091720'),
(26,'django_celery_beat','0006_auto_20180322_0932','2021-07-21 09:15:26.548807'),
(27,'django_celery_beat','0007_auto_20180521_0826','2021-07-21 09:15:27.524014'),
(28,'django_celery_beat','0008_auto_20180914_1922','2021-07-21 09:15:27.674876'),
(29,'django_celery_beat','0006_auto_20180210_1226','2021-07-21 09:15:27.836965'),
(30,'django_celery_beat','0006_periodictask_priority','2021-07-21 09:15:31.160175'),
(31,'django_celery_beat','0009_periodictask_headers','2021-07-21 09:15:33.113285'),
(32,'django_celery_beat','0010_auto_20190429_0326','2021-07-21 09:15:40.361310'),
(33,'django_celery_beat','0011_auto_20190508_0153','2021-07-21 09:15:43.302092'),
(34,'django_celery_beat','0012_periodictask_expire_seconds','2021-07-21 09:15:44.617945'),
(35,'django_celery_beat','0013_auto_20200609_0727','2021-07-21 09:15:44.652605'),
(36,'django_celery_beat','0014_remove_clockedschedule_enabled','2021-07-21 09:15:45.413397'),
(37,'django_celery_beat','0015_edit_solarschedule_events_choices','2021-07-21 09:15:45.501226'),
(38,'kvm','0002_auto_20210721_1449','2021-07-21 09:15:47.539103'),
(39,'kvm','0003_auto_20210727_1140','2021-07-27 03:40:21.997287'),
(40,'kvm','0004_auto_20210803_1514','2021-08-03 07:14:46.021372'),
(41,'assets','0001_initial','2021-08-04 07:55:05.324638'),
(42,'assets','0002_auto_20210804_1600','2021-08-04 08:00:27.873108'),
(43,'assets','0003_asset','2021-08-04 08:18:31.949996'),
(44,'assets','0004_auto_20210806_1457','2021-08-06 06:58:02.424558'),
(45,'assets','0005_remove_treenodes_key','2021-08-06 07:15:10.138136'),
(46,'assets','0006_treenodes_key','2021-08-09 08:04:56.423201'),
(47,'assets','0007_auto_20210810_1028','2021-08-10 02:28:51.367995'),
(48,'assets','0008_auto_20210810_1121','2021-08-10 03:22:02.343885'),
(49,'assets','0009_asset_tree_node','2021-08-10 06:48:18.904203'),
(50,'assets','0010_auto_20210810_1500','2021-08-10 07:00:35.574104'),
(51,'assets','0011_proxy_proxyplatform','2021-08-11 06:15:07.731332'),
(52,'assets','0012_auto_20210811_1425','2021-08-11 06:26:01.642571'),
(53,'assets','0013_auto_20210811_1527','2021-08-11 07:27:41.451969'),
(54,'assets','0014_proxy_platform','2021-08-11 07:35:03.208186'),
(55,'assets','0015_asset_proxy','2021-08-12 09:37:50.336695'),
(56,'kvm','0005_domains_ip','2021-08-17 07:07:30.115868'),
(57,'kvm','0006_domains_proxy1','2021-08-17 08:00:28.551463'),
(58,'kvm','0007_remove_domains_proxy1','2021-08-17 08:00:46.552488'),
(59,'kvm','0008_domains_http_proxy','2021-08-17 08:03:07.767867'),
(60,'kvm','0009_auto_20210819_1741','2021-08-19 09:42:07.585787'),
(61,'kvm','0010_auto_20210819_1744','2021-08-19 09:44:45.548114'),
(62,'kvm','0011_auto_20210819_1749','2021-08-19 09:49:10.377000'),
(63,'kvm','0012_auto_20210907_1440','2021-09-07 06:40:21.454818'),
(64,'kvm','0013_auto_20210907_1450','2021-09-07 06:50:46.813268'),
(65,'kvm','0014_vmserver_conn_port','2021-09-10 07:10:25.875207'),
(66,'kvm','0015_vminstance_desc','2021-09-15 07:40:03.925819'),
(67,'kvm','0016_auto_20210930_1816','2021-09-30 10:16:36.122511'),
(68,'kvm','0017_auto_20211007_1606','2021-10-07 08:07:04.367787');

/*Table structure for table `django_session` */

DROP TABLE IF EXISTS `django_session`;

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `django_session` */

/*Table structure for table `kvm_vminstance` */

DROP TABLE IF EXISTS `kvm_vminstance`;

CREATE TABLE `kvm_vminstance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `console_type` varchar(20) DEFAULT NULL,
  `console_port` varchar(20) DEFAULT NULL,
  `networks` json NOT NULL,
  `disks` json NOT NULL,
  `uuid` varchar(36) DEFAULT NULL,
  `vid` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `update_time` datetime(6) DEFAULT NULL,
  `create_time` datetime(6) DEFAULT NULL,
  `server_id` int(11) NOT NULL,
  `vcpu` int(11) DEFAULT NULL,
  `ip` varchar(120) DEFAULT NULL,
  `http_proxy_id` int(11) DEFAULT NULL,
  `desc` longtext,
  `max_memory` varchar(20) DEFAULT NULL,
  `max_vcpu` int(11) DEFAULT NULL,
  `memory` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `kvm_domains_name_63f9abe1` (`name`),
  KEY `kvm_domains_http_proxy_id_15c9f961_fk_assets_proxy_id` (`http_proxy_id`),
  KEY `kvm_vminstance_server_id_8c68b3d6_fk_kvm_vmserver_id` (`server_id`),
  CONSTRAINT `kvm_domains_http_proxy_id_15c9f961_fk_assets_proxy_id` FOREIGN KEY (`http_proxy_id`) REFERENCES `assets_proxy` (`id`),
  CONSTRAINT `kvm_vminstance_server_id_8c68b3d6_fk_kvm_vmserver_id` FOREIGN KEY (`server_id`) REFERENCES `kvm_vmserver` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8;

/*Data for the table `kvm_vminstance` */

insert  into `kvm_vminstance`(`id`,`name`,`console_type`,`console_port`,`networks`,`disks`,`uuid`,`vid`,`status`,`update_time`,`create_time`,`server_id`,`vcpu`,`ip`,`http_proxy_id`,`desc`,`max_memory`,`max_vcpu`,`memory`) values 
(30,'g1','vnc','5908','[{\"mac\": \"52:54:00:98:dd:4c\", \"nic\": \"br0\", \"type\": \"bridge\", \"model\": \"virtio\"}]','[{\"bus\": \"virtio\", \"dev\": \"vdc\", \"file\": \"/data/g1.img\", \"size\": \"30.0 GB\", \"type\": \"file\", \"used\": \"9.2 GB\", \"device\": \"disk\", \"format\": \"qcow2\", \"readonly\": false}, {\"bus\": \"ide\", \"dev\": \"hda\", \"file\": \"/data/cn_windows_7_ultimate_with_sp1_x64_dvd_u_677408.iso\", \"size\": \"3.2 GB\", \"type\": \"file\", \"used\": \"3.2 GB\", \"device\": \"cdrom\", \"format\": \"raw\", \"readonly\": true}, {\"bus\": \"fdc\", \"dev\": \"fda\", \"file\": \"/data/virtio-win-0.1.171_amd64.vfd\", \"size\": \"2.8 MB\", \"type\": \"file\", \"used\": \"2.8 MB\", \"device\": \"floppy\", \"format\": \"raw\", \"readonly\": true}]','0be77a39-5e48-460e-bdb3-03b91ef3604c',-1,5,'2021-10-07 10:32:00.598586','2021-09-16 09:58:07.333014',33,2,'',NULL,'测试windows01','2 GB',2,'2 GB'),
(36,'aa21','vnc','-1','[{\"mac\": \"52:54:00:1e:ba:94\", \"nic\": \"br0\", \"type\": \"bridge\", \"model\": \"rtl8139\"}]','[{\"bus\": \"virtio\", \"dev\": \"vda\", \"file\": \"/data/a1.img\", \"size\": \"20.0 GB\", \"type\": \"file\", \"used\": \"1.6 GB\", \"device\": \"disk\", \"format\": \"qcow2\", \"readonly\": false}, {\"bus\": \"ide\", \"dev\": \"hda\", \"file\": \"/data/CentOS-7-x86_64-Minimal-2003.iso\", \"size\": \"1.0 GB\", \"type\": \"file\", \"used\": \"1.0 GB\", \"device\": \"cdrom\", \"format\": \"raw\", \"readonly\": true}]','059a80dc-66d1-4c3a-9331-ffa075b20b33',-1,5,'2021-10-07 10:32:00.367876','2021-09-27 09:54:00.580007',33,3,NULL,NULL,'测试linux01','3 GB',4,'2 GB'),
(41,'a123','vnc','5900','[{\"mac\": \"52:54:00:91:b9:db\", \"nic\": \"virbr0\", \"type\": \"bridge\", \"model\": \"virtio\"}]','[{\"bus\": \"virtio\", \"dev\": \"vda\", \"file\": \"/data/kvm/a123.img\", \"size\": \"30.0 GB\", \"type\": \"file\", \"used\": \"200.0 KB\", \"device\": \"disk\", \"format\": \"qcow2\", \"readonly\": false}]','a7fbcd6d-e3e9-4bc0-bee9-0accae0d7ce2',2,1,'2022-11-02 03:34:20.955201','2021-10-19 10:14:00.327399',38,2,NULL,NULL,' ','2 GB',2,'2 GB');

/*Table structure for table `kvm_vmserver` */

DROP TABLE IF EXISTS `kvm_vmserver`;

CREATE TABLE `kvm_vmserver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(120) DEFAULT NULL,
  `host` varchar(20) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(200) DEFAULT NULL,
  `conn_type` int(11) NOT NULL,
  `cpu` int(11) DEFAULT NULL,
  `memory` varchar(20) DEFAULT NULL,
  `memory_usage` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `conn_port` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `host` (`host`),
  KEY `kvm_nodes_name_b0da5986` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8;

/*Data for the table `kvm_vmserver` */

insert  into `kvm_vmserver`(`id`,`name`,`host`,`username`,`password`,`conn_type`,`cpu`,`memory`,`memory_usage`,`status`,`update_time`,`create_time`,`conn_port`) values 
(33,'t1','192.168.8.223','root','abcu123456',2,8,'4 GB',8,0,'2021-10-19 11:29:02.723898','2021-09-13 02:36:52.413863',22),
(38,'aa','192.168.8.192','root',NULL,1,8,'12 GB',12,1,'2021-10-19 11:29:00.126985','2021-10-19 08:42:02.119157',16509);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

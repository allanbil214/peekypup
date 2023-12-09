-- --------------------------------------------------------
-- Host:                         localhost
-- Server version:               10.4.21-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for picturefy
CREATE DATABASE IF NOT EXISTS `picturefy` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `picturefy`;

-- Dumping structure for table picturefy.funnyline
CREATE TABLE IF NOT EXISTS `funnyline` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `line` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table picturefy.funnyline: ~22 rows (approximately)
/*!40000 ALTER TABLE `funnyline` DISABLE KEYS */;
INSERT INTO `funnyline` (`id`, `line`) VALUES
	(1, 'The stuff you’ll see everywhere else tomorrow.'),
	(2, 'Apply directly to the forehead.'),
	(3, 'Be the memes you want to see in the world.'),
	(4, 'The dankest memes, or your money back!'),
	(5, '12345 is a bad password! '),
	(6, '150% hyperbole! '),
	(7, '90% bug free! '),
	(8, '"Almost never" is an interesting concept! '),
	(9, 'Any computer is a laptop if you\'re brave enough! '),
	(10, 'Bringing home the bacon! '),
	(11, ' 	Ceci n\'est pas une title screen! '),
	(12, 'Flavor with no seasoning! '),
	(13, 'Funk soul brother! '),
	(14, 'Less addictive than TV Tropes! '),
	(15, 'Lives in a pineapple under the sea! '),
	(16, 'Made by "real" people! '),
	(17, 'Rule #1: it\'s never my fault '),
	(18, 'Something\'s not quite right... '),
	(19, 'Strange, but not a stranger! '),
	(20, 'What do you expect? '),
	(21, 'The perfect site doesn’t exi-'),
	(22, 'Not corpo-rat owned!');
/*!40000 ALTER TABLE `funnyline` ENABLE KEYS */;

-- Dumping structure for table picturefy.image
CREATE TABLE IF NOT EXISTS `image` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(50) DEFAULT '',
  `desc` text DEFAULT '',
  `user_id` int(11) DEFAULT NULL,
  `filename` text NOT NULL,
  `input_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_image_users` (`user_id`),
  CONSTRAINT `FK_image_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table picturefy.image: ~14 rows (approximately)
/*!40000 ALTER TABLE `image` DISABLE KEYS */;
INSERT INTO `image` (`id`, `title`, `desc`, `user_id`, `filename`, `input_date`) VALUES
	(1, 'dog salada', 'lmaoo dog saladaaa', NULL, 'dog_salad.jpg', '2022-06-01 07:11:57'),
	(2, 'finally scientist found color', '', NULL, 'finally_color.png', '2022-06-01 07:12:00'),
	(3, 'Guy Standing sitting', 'A guy named Guy Standing is sitting on a chair.', NULL, 'guy_standing_sitting.webp', '2022-06-01 07:12:03'),
	(4, 'Skyrim Khajiit standing on Sheogorath', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum', 2, 'khajit_sheo.jpg', '2022-06-01 07:12:05'),
	(5, 'Linus Profile', '', NULL, 'linus_i_showed_you_my_ram.jpg', '2022-06-08 19:28:01'),
	(6, 'srgrafo waking up', 'tis a jif', NULL, 'me_everyday.gif', '2022-06-01 07:12:08'),
	(7, 'teletubies todd howard', 'buy skyrim again, and again, and again.', 2, 'TeleTodd.png', '2022-06-04 07:12:09'),
	(8, 'pope with plant', '', NULL, 'pope_plant.jpg', '2022-06-01 07:12:09'),
	(9, 'it\'s all good, man!', 'jimmy mcgill says "it\'s all good, man!" which can be interpreted as "Saul Goodman"', 1, 'saul_goodman.gif', '2022-06-01 07:12:08'),
	(10, 'jimmy peeking', '', 1, 'jimmy_peeking.gif', '2022-06-04 07:14:09'),
	(11, 'milet album cover Visions', 'listen to her music, it\'s good.', NULL, 'milet.jpg', '2022-06-01 07:12:07'),
	(13, 'walter white funny face', '', 1, 'walter_white.gif', '2022-06-08 20:32:26'),
	(14, 'Creepy Ugly Sonic', 'holy cow, that teeth....', 1, 'SonicSwift___Chip_n_Dale_Rescue_Rangers___UGLY_SONIC_Scenes_[qLFGUNTWBQU___1516x852___0m59s].png', '2022-06-09 09:57:09'),
	(16, 'Milet Wallpaper', 'she\'s cute...', NULL, 'output.jpg', '2022-06-09 11:51:37');
/*!40000 ALTER TABLE `image` ENABLE KEYS */;

-- Dumping structure for table picturefy.image_tags
CREATE TABLE IF NOT EXISTS `image_tags` (
  `image_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  KEY `FK_image_tags_image` (`image_id`),
  KEY `FK_image_tags_tags` (`tag_id`),
  CONSTRAINT `FK_image_tags_image` FOREIGN KEY (`image_id`) REFERENCES `image` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_image_tags_tags` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table picturefy.image_tags: ~14 rows (approximately)
/*!40000 ALTER TABLE `image_tags` DISABLE KEYS */;
INSERT INTO `image_tags` (`image_id`, `tag_id`) VALUES
	(2, 3),
	(3, 2),
	(5, 4),
	(4, 1),
	(6, 5),
	(7, 7),
	(1, 6),
	(8, 8),
	(9, 9),
	(10, 2),
	(11, 10),
	(13, 9),
	(14, 13),
	(16, 11);
/*!40000 ALTER TABLE `image_tags` ENABLE KEYS */;

-- Dumping structure for table picturefy.tags
CREATE TABLE IF NOT EXISTS `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table picturefy.tags: ~16 rows (approximately)
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` (`id`, `tag_name`) VALUES
	(1, 'Gaming'),
	(2, 'Funny'),
	(3, 'Science'),
	(4, 'Tech'),
	(5, 'Anime'),
	(6, 'Food'),
	(7, 'Cosplay'),
	(8, 'Plant'),
	(9, 'TV'),
	(10, 'Music'),
	(11, 'Wallpaper'),
	(12, 'zxc'),
	(13, 'Creepy'),
	(14, 'zxc asdqwe'),
	(15, 'qw ascz'),
	(16, 'qw ascz zxc');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;

-- Dumping structure for table picturefy.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `reg_time` date NOT NULL,
  `isadmin` int(11) NOT NULL DEFAULT 0,
  `email` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table picturefy.users: ~3 rows (approximately)
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` (`id`, `username`, `password`, `reg_time`, `isadmin`, `email`) VALUES
	(1, 'admin', 'admin', '2022-05-30', 1, 'admin@admin.com'),
	(2, 'allan', 'allan', '2022-06-09', 0, 'allan@bil.faqih'),
	(12, 'asd', 'asd', '2022-06-09', 0, 'asd@asd.com');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

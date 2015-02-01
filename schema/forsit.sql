-- phpMyAdmin SQL Dump
-- version 3.4.10.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Feb 01, 2015 at 03:37 PM
-- Server version: 5.5.41
-- PHP Version: 5.4.36-1+deb.sury.org~precise+2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `forsit`
--

-- --------------------------------------------------------

--
-- Table structure for table `activity`
--

CREATE TABLE IF NOT EXISTS `activity` (
  `handle` varchar(100) NOT NULL,
  `pid` varchar(100) NOT NULL,
  `attempt_count` int(11) NOT NULL DEFAULT '0',
  `status` int(11) NOT NULL DEFAULT '0',
  `difficulty` double NOT NULL DEFAULT '0',
  `uid` int(11) NOT NULL DEFAULT '0',
  `created_at` int(12) NOT NULL DEFAULT '0',
  KEY `handle` (`handle`),
  KEY `pid` (`pid`),
  KEY `status` (`status`),
  KEY `created_at` (`created_at`),
  KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `activity_concept`
--

CREATE TABLE IF NOT EXISTS `activity_concept` (
  `handle` varchar(100) NOT NULL,
  `pid` varchar(100) NOT NULL,
  `attempt_count` int(11) NOT NULL DEFAULT '0',
  `status` int(11) NOT NULL DEFAULT '0',
  `difficulty` double NOT NULL DEFAULT '0',
  `uid` int(11) NOT NULL DEFAULT '0',
  `created_at` bigint(20) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `problem`
--

CREATE TABLE IF NOT EXISTS `problem` (
  `pid` varchar(50) NOT NULL,
  `name` varchar(200) NOT NULL,
  `contestId` varchar(50) NOT NULL,
  `points` int(11) NOT NULL,
  `correct_count` int(11) NOT NULL,
  `attempt_count` int(11) NOT NULL DEFAULT '-1',
  `time` int(11) NOT NULL,
  `isdeleted` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`pid`),
  KEY `name` (`name`),
  KEY `pid` (`pid`),
  KEY `contestId` (`contestId`),
  KEY `points` (`points`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `problem_reco`
--

CREATE TABLE IF NOT EXISTS `problem_reco` (
  `uid` varchar(100) NOT NULL,
  `base_pid` varchar(100) NOT NULL,
  `status` int(11) NOT NULL,
  `reco_pid` varchar(100) NOT NULL,
  `score` double NOT NULL,
  `time_created` int(11) NOT NULL,
  `time_updated` int(11) NOT NULL,
  `is_deleted` int(11) NOT NULL,
  `state` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `ptag`
--

CREATE TABLE IF NOT EXISTS `ptag` (
  `pid` varchar(50) NOT NULL,
  `tag` varchar(100) NOT NULL,
  PRIMARY KEY (`pid`,`tag`),
  KEY `tag` (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `tag`
--

CREATE TABLE IF NOT EXISTS `tag` (
  `tag` varchar(100) NOT NULL,
  `description` varchar(250) NOT NULL,
  `time` int(11) NOT NULL,
  `count` int(11) NOT NULL,
  PRIMARY KEY (`tag`),
  UNIQUE KEY `tag` (`tag`,`description`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `erd_handle` varchar(50) NOT NULL,
  `cfs_handle` varchar(50) NOT NULL,
  `erd_score` double NOT NULL,
  `cfs_score` double NOT NULL,
  PRIMARY KEY (`uid`),
  KEY `erd_handle` (`erd_handle`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `user_reco`
--

CREATE TABLE IF NOT EXISTS `user_reco` (
  `uid` varchar(100) NOT NULL,
  `pid` varchar(100) NOT NULL,
  `time_created` int(11) NOT NULL,
  `time_updated` int(11) NOT NULL,
  `is_deleted` int(11) NOT NULL,
  `state` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `user_tag_score`
--

CREATE TABLE IF NOT EXISTS `user_tag_score` (
  `handle` varchar(100) NOT NULL,
  `tag` varchar(100) NOT NULL,
  `score` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ptag`
--
ALTER TABLE `ptag`
  ADD CONSTRAINT `ptag_ibfk_2` FOREIGN KEY (`tag`) REFERENCES `tag` (`tag`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

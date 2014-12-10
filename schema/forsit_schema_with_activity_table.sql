-- phpMyAdmin SQL Dump
-- version 3.5.8.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 24, 2014 at 11:42 PM
-- Server version: 5.5.34-0ubuntu0.13.04.1
-- PHP Version: 5.4.9-4ubuntu2.4

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
  `created_at` int(12) NOT NULL DEFAULT '0'
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
  PRIMARY KEY (`pid`)
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

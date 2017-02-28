-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Feb 28, 2017 at 09:10 PM
-- Server version: 5.7.17-0ubuntu0.16.04.1
-- PHP Version: 7.0.15-0ubuntu0.16.04.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `forsit`
--

-- --------------------------------------------------------

--
-- Table structure for table `tag`
--

CREATE TABLE `tag` (
  `tag` varchar(100) NOT NULL,
  `description` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `time` int(11) NOT NULL,
  `count` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `tag`
--

INSERT INTO `tag` (`tag`, `description`, `time`, `count`) VALUES
('2-sat', '2-satisfiability', 1488295855, 8),
('binary search', 'Binary search', 1488295855, 266),
('bitmasks', 'Bitmasks', 1488295855, 104),
('brute force', 'Brute force', 1488295855, 466),
('chinese remainder theorem', 'Сhinese remainder theorem', 1488295855, 6),
('combinatorics', 'Combinatorics', 1488295855, 154),
('constructive algorithms', 'Constructive algorithms', 1488295855, 342),
('data structures', 'Heaps, binary search trees, segment trees, hash tables, etc', 1488295855, 445),
('dfs and similar', 'Dfs and similar', 1488295855, 290),
('divide and conquer', 'Divide and Conquer', 1488295855, 61),
('dp', 'Dynamic programming', 1488295855, 606),
('dsu', 'Disjoint set union', 1488295855, 111),
('expression parsing', 'Parsing expression grammar', 1488295855, 30),
('fft', 'Fast Fourier transform', 1488295855, 11),
('flows', 'Graph network flows', 1488295855, 40),
('games', 'Games, Sprague–Grundy theorem', 1488295855, 54),
('geometry', 'Geometry, computational geometry', 1488295855, 155),
('graph matchings', 'Graph matchings, König\'s theorem, vertex cover of bipartite graph', 1488295855, 23),
('graphs', 'Graphs', 1488295855, 226),
('greedy', 'Greedy algorithms', 1488295855, 580),
('hashing', 'Hashing, hashtables', 1488295855, 71),
('implementation', 'Implementation problems, programming technics, simulation', 1488295855, 1014),
('math', 'Mathematics including integration, differential equations, etc', 1488295855, 583),
('matrices', 'Matrix multiplication, determinant, Cramer\'s rule, systems of linear equations', 1488295855, 45),
('meet-in-the-middle', 'Meet-in-the-middle', 1488295855, 13),
('number theory', 'Number theory: Euler function, GCD, divisibility, etc', 1488295855, 158),
('probabilities', 'Probabilities, expected values, statistics, random variables, etc', 1488295855, 82),
('schedules', 'Scheduling Algorithms', 1488295855, 5),
('shortest paths', 'Shortest paths on weighted and unweighted graphs', 1488295855, 72),
('sortings', 'Sortings, orderings', 1488295855, 281),
('string suffix structures', 'Suffix arrays, suffix trees, suffix automatas, etc', 1488295855, 38),
('strings', 'Prefix- and Z-functions, suffix structures, Knuth–Morris–Pratt algorithm, etc', 1488295855, 185),
('ternary search', 'Ternary search', 1488295855, 16),
('trees', 'Trees', 1488295855, 187),
('two pointers', 'Two pointers', 1488295855, 122);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tag`
--
ALTER TABLE `tag`
  ADD PRIMARY KEY (`tag`),
  ADD UNIQUE KEY `tag` (`tag`,`description`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

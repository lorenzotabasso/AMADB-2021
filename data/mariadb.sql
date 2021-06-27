CREATE TABLE `sentiment`
(
    `name` char(16) COLLATE utf8mb4_unicode_ci NOT NULL,
    PRIMARY KEY (`name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;

CREATE TABLE `token`
(
    `id`   int(11)                          NOT NULL AUTO_INCREMENT,
    `type` int(1)                           NOT NULL,
    `text` varchar(256) COLLATE utf8mb4_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;

CREATE TABLE `tweet`
(
    `id`           int(11)                             NOT NULL AUTO_INCREMENT,
    `sentiment_id` char(16) COLLATE utf8mb4_unicode_ci NOT NULL,
    PRIMARY KEY (`id`),
    KEY `sentiment_id` (`sentiment_id`),
    CONSTRAINT `tweet_ibfk_3` FOREIGN KEY (`sentiment_id`) REFERENCES `sentiment` (`name`) ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;

CREATE TABLE `lexical_resource`
(
    `id`           int(11)                                NOT NULL AUTO_INCREMENT,
    `name`         varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL,
    `sentiment_id` char(16) COLLATE utf8mb4_unicode_ci    NOT NULL,
    PRIMARY KEY (`id`),
    KEY `sentiment_id` (`sentiment_id`),
    CONSTRAINT `lexical_resource_ibfk_2` FOREIGN KEY (`sentiment_id`) REFERENCES `sentiment` (`name`) ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;

CREATE TABLE `contained_in`
(
    `id`             int(11) NOT NULL AUTO_INCREMENT,
    `tweet_id`       int(11) NOT NULL,
    `token_id`       int(11) NOT NULL,
    `part_of_speech` char(4) COLLATE utf8mb4_unicode_ci DEFAULT 'NULL',
    PRIMARY KEY (`id`),
    KEY `token_id` (`token_id`),
    KEY `tweet_id` (`tweet_id`),
    CONSTRAINT `contained_in_ibfk_4` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON UPDATE CASCADE,
    CONSTRAINT `contained_in_ibfk_5` FOREIGN KEY (`token_id`) REFERENCES `token` (`id`) ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;

CREATE TABLE `in_resource`
(
    `token_id`            int(11) NOT NULL,
    `lexical_resource_id` int(11) NOT NULL,
    PRIMARY KEY (`token_id`, `lexical_resource_id`),
    KEY `lexical_resource_id` (`lexical_resource_id`),
    CONSTRAINT `in_resource_ibfk_4` FOREIGN KEY (`token_id`) REFERENCES `token` (`id`) ON UPDATE CASCADE,
    CONSTRAINT `in_resource_ibfk_5` FOREIGN KEY (`lexical_resource_id`) REFERENCES `lexical_resource` (`id`) ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_bin;